"""
Garantiza que la web solo usa encuestas APROBADAS.

Una lista de encuestas está aprobada cuando llega a main al fusionar (merge) un pull request: el de revisión
que abre el workflow cada mañana, o cualquier otro. Si datos/polls.csv cambia en main por otra vía (un commit
directo, por ejemplo tras lanzar actualizar.py en local), ese cambio no se usa: este script repone en el
directorio de trabajo datos/polls.csv y datos/fuente.json tal como estaban en el último commit aprobado, y
avisa. El cambio sin aprobar sigue en el historial; para usarlo, hay que proponerlo en un pull request.

Lo usan los dos trabajos del workflow, antes de comparar (revisar) y antes de calcular (publicar).
Necesita el historial completo (checkout con fetch-depth: 0), GITHUB_REPOSITORY y GH_TOKEN.
Para probarlo sin GitHub: APROBADOS="sha1,sha2" da la lista de commits que cuentan como aprobados.

Escribe en GITHUB_OUTPUT: aprobada=<sha> · sin_aprobar=si|no · commits=<los commits sin aprobar>
"""
import json, os, subprocess, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FILES = ['datos/polls.csv', 'datos/fuente.json']


def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def blob(rev, path):
    """a file exactly as it was in a commit (bytes)"""
    return subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT, check=True, capture_output=True).stdout


def merged_pr(sha):
    """the pull request merged into main that brought this commit, or None"""
    test = os.environ.get('APROBADOS')
    if test is not None:
        return {'number': 0} if sha in test.split(',') else None
    repo, token = os.environ['GITHUB_REPOSITORY'], os.environ.get('GH_TOKEN')
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'simulador-29n',
               **({'Authorization': f'Bearer {token}'} if token else {})}
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/commits/{sha}/pulls', headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        prs = json.load(r)
    return next((p for p in prs if p.get('merged_at') and p['base']['ref'] == 'main'), None)


def out(**kv):
    lines = [f'{k}={v}' for k, v in kv.items()]
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a') as f: f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


def main():
    shas = git('log', '--format=%H', '--', 'datos/polls.csv').split()
    unapproved, approved = [], None
    for sha in shas:                                   # newest first
        if merged_pr(sha): approved = sha; break
        unapproved.append(sha)
    if not approved:
        print('::warning title=Lista aprobada::ningún pull request fusionado ha cambiado datos/polls.csv; se usa la de main tal cual')
        out(aprobada='', sin_aprobar='no', commits='')
        return
    head = git('rev-parse', 'HEAD:datos/polls.csv')
    if not unapproved or git('rev-parse', f'{approved}:datos/polls.csv') == head:
        out(aprobada=approved, sin_aprobar='no', commits='')
        return
    for f in FILES:
        with open(os.path.join(ROOT, f), 'wb') as fh:
            fh.write(blob(approved, f))
    short = ' '.join(s[:7] for s in unapproved)
    print(f'::warning title=Encuestas sin aprobar::datos/polls.csv cambió en main sin pull request ({short}); se usa la lista aprobada en {approved[:7]}')
    out(aprobada=approved, sin_aprobar='si', commits=short)


if __name__ == '__main__':
    main()
