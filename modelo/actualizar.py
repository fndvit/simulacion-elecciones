"""
Paso diario de datos: propone las encuestas nuevas para que una persona las apruebe.
Lo ejecuta el workflow de GitHub Actions; también se puede lanzar a mano.

1. Descarga la página de encuestas de la Wikipedia en español (fetch_polls.py) y anota la revisión exacta.
2. Valida lo descargado contra datos/polls.csv, la lista APROBADA. Si algo falla (red, cambio de formato,
   tabla a medias, valores absurdos), no se propone nada y se informa del motivo.
3. Compara con la lista aprobada: encuestas nuevas, cambiadas y retiradas. Cada nueva o cambiada se busca en
   la Wikipedia en inglés (fetch_en.py) para comprobar PP, PSOE y Vox.
4. Si hay cambios, escribe la lista propuesta en datos/polls.csv, la revisión usada en datos/fuente.json y el
   informe para la persona que revisa en revision.md. El workflow lo sube a la rama «encuestas-pendientes» y
   abre (o actualiza) un pull request; la web solo usa las encuestas cuando alguien lo aprueba (merge).

Nunca termina con error por culpa de los datos: escribe el resultado en GITHUB_OUTPUT (o en pantalla):
estado=ok|respaldo · cambios=si|no · motivo=… · nuevas · cambiadas · retiradas · difieren
"""
import csv, datetime as dt, glob, json, os, shutil, sys
import fetch_polls as F
import fetch_en as EN

HERE = os.path.dirname(os.path.abspath(__file__))
POLLS = os.path.join(HERE, '..', 'datos', 'polls.csv')
BACKUP_DIR = os.path.join(HERE, '..', 'datos', 'respaldo')
SOURCE = os.path.join(HERE, '..', 'datos', 'fuente.json')
REPORT = os.environ.get('REVISION_MD', os.path.join(HERE, '..', 'revision.md'))
KEEP = 30
SINCE = dt.date(2025, 10, 1)


def fetch_with_retries(tries=3, wait=60):
    import time
    for i in range(tries):
        try:
            return F.fetch_page()
        except Exception as e:
            if i == tries - 1:
                raise
            print(f'intento {i + 1} fallido ({e}); reintento en {wait} s', file=sys.stderr)
            time.sleep(wait)


def read_current():
    if not os.path.exists(POLLS):
        return []
    with open(POLLS, newline='') as f:
        return list(csv.DictReader(f, delimiter='|'))


def validate(new, old):
    """lista de problemas; vacía si lo descargado es aceptable"""
    errs = []
    if len(new) < 50:
        errs.append(f'solo {len(new)} encuestas (mínimo 50)')
    if old and len(new) < 0.9 * len(old):
        errs.append(f'{len(new)} encuestas frente a {len(old)} en el último fichero bueno (perdería más del 10 %)')
    if old and new:
        newest_old = max(r['end'] for r in old)
        newest_new = max(p['end'] for p in new).isoformat()
        if newest_new < newest_old:
            errs.append(f'la encuesta más reciente ({newest_new}) es anterior a la del último fichero bueno ({newest_old})')
    future = [p for p in new if p['end'] > dt.date.today() + dt.timedelta(days=1)]
    if future:
        errs.append(f'{len(future)} encuestas con fecha futura (p. ej. {future[0]["pollster"]}, {future[0]["end"]})')
    bad = [p for p in new if not (p['v'].get('PP') and p['v'].get('PSOE') and 5 <= p['v']['PP'] <= 60 and 5 <= p['v']['PSOE'] <= 60)]
    if len(bad) > 0.05 * max(1, len(new)):
        errs.append(f'{len(bad)} encuestas sin PP o PSOE válidos')
    for p in new:
        tot = sum(v for v in p['v'].values() if v)
        if tot > 115:
            errs.append(f'{p["pollster"]} ({p["end"]}) suma {tot:.0f} %'); break
    return errs


def out(**kv):
    lines = [f'{k}={v}' for k, v in kv.items()]
    path = os.environ.get('GITHUB_OUTPUT')
    if path:
        with open(path, 'a') as f:
            f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


def nn(n, one, many):
    return f'{n} {one if n == 1 else many}'


def fmt(x):
    return x.replace('.', ',') if x else '–'


def report(added, changed, removed, checks, es, en, en_err):
    """the pull request body, in Spanish, for the person who approves"""
    L = ['## Encuestas para revisar', '',
         f'Leídas de la [Wikipedia en español, revisión {es["revid"]}]({es["url"]}) ({es["timestamp"][:16].replace("T", " ")} UTC).']
    if en: L.append(f'Comprobadas con la [Wikipedia en inglés, revisión {en["revid"]}]({en["url"]}): PP, PSOE y Vox, misma empresa y fin de campo (±1 día).')
    else: L.append(f'**No se ha podido comprobar con la Wikipedia en inglés** ({en_err}). Revisa las cifras con la fuente.')
    L += ['', '| | Encuestadora | Fin de campo | Muestra | PP | PSOE | Vox | Sumar/FA | Fuente | Wikipedia en inglés |', '|---|---|---|---|---|---|---|---|---|---|']
    col = {k: i for i, k in enumerate(F.HEAD)}
    def line(kind, r, chk='', old=None):
        cell = lambda k: (f'{fmt(old[col[k]])} → **{fmt(r[col[k]])}**' if old and old[col[k]] != r[col[k]] else fmt(r[col[k]]))
        sumar = r[col['FA']] or r[col['SUMAR']]
        src = f'[enlace]({r[col["src"]]})' if r[col['src']] else 'sin enlace'
        return f'| {kind} | {r[0]} | {r[1]} | {cell("n")} | {cell("PP")} | {cell("PSOE")} | {cell("VOX")} | {fmt(sumar)} | {src} | {chk} |'
    for r, chk in added: L.append(line('Nueva', r, chk))
    for r, old, chk in changed: L.append(line('Cambiada', r, chk, old))
    for r in removed: L.append(line('Retirada', r, 'ya no está en la Wikipedia en español'))
    dif = sum(1 for c in checks if c == 'difiere')
    L += ['', f'**{nn(len(added), "nueva", "nuevas")}, {nn(len(changed), "cambiada", "cambiadas")}, {nn(len(removed), "retirada", "retiradas")}.**'
          + (f' {nn(dif, "no coincide", "no coinciden")} con la Wikipedia en inglés: revísala{"s" if dif > 1 else ""} con la fuente antes de aprobar.' if dif else ''),
          '', 'Al aprobar (merge), la web recalcula la media y se publica en unos minutos. Si una cifra está mal, corrígela en `datos/polls.csv` en esta rama antes de aprobar, o cierra el pull request para no usar estos cambios.',
          '', 'La rama se rehace cada mañana con lo que haya en Wikipedia: los cambios que no se hayan aprobado siguen apareciendo.']
    return '\n'.join(L) + '\n'


def main():
    old = read_current()
    try:
        es = fetch_with_retries()
        new = [p for p in F.parse(es['text'], today=dt.date.today()) if p['end'] >= SINCE]
    except Exception as e:  # red, API, HTML irreconocible…
        out(estado='respaldo', cambios='no', motivo=f'no se pudo descargar o leer Wikipedia: {type(e).__name__}: {e}'.replace('\n', ' ')[:300])
        return
    errs = validate(new, old)
    if errs:
        out(estado='respaldo', cambios='no', motivo='; '.join(errs)[:300])
        return
    # what changes with respect to the approved list (the source link alone is not a change)
    key = lambda r: (r[0], r[1])
    cur = {key(list(r.values())): [r.get(h, '') or '' for h in F.HEAD] for r in old}
    rows = [F.row(p) for p in new]
    nxt = {key(r): r for r in rows}
    bysrc = {key(F.row(p)): p for p in new}
    same = lambda a, b: a[:-1] == b[:-1]
    added_k = [k for k in nxt if k not in cur]
    changed_k = [k for k in nxt if k in cur and not same(nxt[k], cur[k])]
    removed_k = [k for k in cur if k not in nxt]
    if not (added_k or changed_k or removed_k):
        out(estado='ok', cambios='no', motivo=f'{len(new)} encuestas en Wikipedia, ninguna nueva ni cambiada')
        return
    try:
        en = EN.fetch(); en_polls = EN.parse(en['text']); en_err = ''
    except Exception as e:
        en, en_polls, en_err = None, [], f'{type(e).__name__}: {e}'.replace('\n', ' ')[:200]
    checks = []
    def check(k):
        c, txt = EN.compare(bysrc[k], en_polls) if en else ('sin comprobar', 'sin comprobar')
        checks.append(c); return txt
    added = [(nxt[k], check(k)) for k in added_k]
    changed = [(nxt[k], cur[k], check(k)) for k in changed_k]
    removed = [cur[k] for k in removed_k]
    # the proposal: the new list, a dated copy of the approved one, the revision read
    if os.path.exists(POLLS):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = dt.datetime.utcnow().strftime('%Y-%m-%d_%H%M')
        shutil.copyfile(POLLS, os.path.join(BACKUP_DIR, f'polls_{stamp}.csv'))
        for f in sorted(glob.glob(os.path.join(BACKUP_DIR, 'polls_*.csv')))[:-KEEP]:
            os.remove(f)
    F.write(new, POLLS)
    meta = lambda r: r and {k: r[k] for k in ('title', 'revid', 'timestamp', 'url')}
    json.dump(dict(wikipedia_es=meta(es), wikipedia_en=meta(en), leido=dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ'), licencia='CC BY-SA 4.0'),
              open(SOURCE, 'w'), ensure_ascii=False, indent=1)
    open(REPORT, 'w').write(report(added, changed, removed, checks, es, en, en_err))
    dif = sum(1 for c in checks if c == 'difiere')
    out(estado='ok', cambios='si', nuevas=len(added), cambiadas=len(changed), retiradas=len(removed), difieren=dif,
        motivo=f'{nn(len(added), "nueva", "nuevas")}, {nn(len(changed), "cambiada", "cambiadas")}, {nn(len(removed), "retirada", "retiradas")}'
               + (f'; {nn(dif, "no coincide", "no coinciden")} con la Wikipedia en inglés' if dif else ''))


if __name__ == '__main__':
    main()
