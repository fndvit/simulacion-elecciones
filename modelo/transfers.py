"""
Transferencias de voto 2023 → proyección, con el CIS y nuestro modelo.

1. Patrón: el barómetro más reciente del CIS (microdatos en datos/cis/MD*.zip). Recuerdo de voto en las
   generales de 2023 (RECUERDO) × intención de voto hoy (INTENCIONG; si no sabe/no contesta, el partido por el
   que siente simpatía, SIMPATIA), ponderado (PESO). Los indecisos sin simpatía quedan fuera.
2. Partidos con pocos encuestados: su fila o columna se apoya más en un punto de partida neutro, con un peso
   n / (n + K). Una columna neutra reparte su origen como el electorado de 2023; una fila neutra es fiel a su
   partido en la proporción media y reparte el resto como el electorado de hoy.
3. España: el patrón se ajusta (IPF) para que las filas sumen el resultado real de 2023 —con la abstención sobre
   el censo de 2026— y las columnas la proyección.
4. Provincias: el patrón nacional ajustado es el punto de partida; se ajusta a los totales de cada provincia
   (resultado de 2023 y proyección). Un partido que no se presenta en una provincia es un cero.

Uso: from transfers import province_flows  → {prov_id: [[origen, destino, votos], ...]}
"""
import csv, glob, io, os, re, zipfile
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
ROWS = ['PSOE', 'SUMAR', 'ERC', 'BILDU', 'BNG', 'AA', 'PNV', 'JUNTS', 'CC', 'UPN', 'VOX', 'PP', 'OTROS', 'ABST']
COLS = ['PSOE', 'FA', 'COMP', 'PODEMOS', 'ERC', 'BILDU', 'BNG', 'AA', 'PNV', 'JUNTS', 'CC', 'UPN', 'AC', 'SALF', 'VOX', 'PP', 'OTROS', 'ABST']
# the same party on both sides (Sumar's heirs: FA, Compromís, Podemos)
SAME = {'PSOE': ['PSOE'], 'SUMAR': ['FA', 'COMP', 'PODEMOS'], 'ERC': ['ERC'], 'BILDU': ['BILDU'], 'BNG': ['BNG'], 'AA': ['AA'], 'PNV': ['PNV'],
        'JUNTS': ['JUNTS'], 'CC': ['CC'], 'UPN': ['UPN'], 'VOX': ['VOX'], 'PP': ['PP'], 'OTROS': ['OTROS'], 'ABST': ['ABST']}
# CIS codes → ours. 2023: blank → OTROS; null, no vote, too young / not entitled → ABST (2023 abstention is on the 2026 census)
REC = {1: 'PSOE', 2: 'PP', 3: 'VOX', 21: 'SUMAR', 101: 'AA', 503: 'CC', 901: 'ERC', 902: 'JUNTS', 1201: 'BNG', 1501: 'UPN', 1601: 'PNV',
       1602: 'BILDU', 9977: 'ABST', 9995: 'ABST', 9996: 'ABST', 9997: 'ABST'}
INT = {1: 'PSOE', 2: 'PP', 3: 'VOX', 4: 'PODEMOS', 8: 'PODEMOS', 7: 'FA', 9: 'FA', 21: 'FA', 29: 'FA', 30: 'FA', 103: 'FA', 903: 'FA', 1301: 'FA',
       1001: 'COMP', 28: 'SALF', 101: 'AA', 503: 'CC', 901: 'ERC', 902: 'JUNTS', 915: 'AC', 1201: 'BNG', 1501: 'UPN', 1601: 'PNV', 1602: 'BILDU',
       9977: 'ABST', 9997: 'ABST'}
NOANSWER = {9998, 9999}
K = 60          # respondents at which the survey and the neutral starting point weigh the same
# names of the barometers used (add the new one each month, with its zip)
TITLES = {'3582': 'Barómetro de octubre de 2026'}


def study_id(path):
    m = re.search(r'MD(\d+)', os.path.basename(path)); return m.group(1) if m else ''


def latest_zip():
    zs = sorted(glob.glob(os.path.join(D, 'cis', 'MD*.zip')), key=lambda p: int(study_id(p) or 0))
    if not zs: raise FileNotFoundError('no hay microdatos del CIS en datos/cis/MD*.zip')
    return zs[-1]


def survey(path=None):
    """weighted recall × intention counts and respondents per row / column"""
    path = path or latest_zip()
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith('_num.csv'))
        txt = z.read(name).decode('utf-8-sig')
    rd = csv.reader(io.StringIO(txt), delimiter=';')
    head = [h.split(':')[0].strip() for h in next(rd)]
    ix = {k: head.index(k) for k in ('RECUERDO', 'INTENCIONG', 'SIMPATIA', 'PESO')}
    num = lambda s: float(s.replace(',', '.')) if s.strip() else None
    M = np.zeros((len(ROWS), len(COLS))); nr = np.zeros(len(ROWS)); nc = np.zeros(len(COLS))
    for row in rd:
        rec, it, sim, w = (num(row[ix[k]]) for k in ('RECUERDO', 'INTENCIONG', 'SIMPATIA', 'PESO'))
        if rec is None or int(rec) in (9998, 9999): continue          # doesn't remember / no answer about 2023
        r = REC.get(int(rec), 'OTROS')
        it = int(it) if it is not None else 9999
        if it in NOANSWER:                                             # undecided: their sympathy, if any
            s = int(sim) if sim is not None else 9999
            if s in (9997, 9998, 9999): continue
            c = INT.get(s, 'OTROS')
        else:
            c = INT.get(it, 'OTROS')
        i, j = ROWS.index(r), COLS.index(c)
        M[i, j] += w; nr[i] += 1; nc[j] += 1
    study = study_id(path)
    return M, nr, nc, study


def rake(X, rows, cols, it=1000, tol=1e-7):
    X = X.copy()
    for _ in range(it):
        rs = X.sum(1); X *= np.divide(rows, rs, out=np.zeros_like(rows), where=rs > 0)[:, None]
        cs = X.sum(0); X *= np.divide(cols, cs, out=np.zeros_like(cols), where=cs > 0)[None, :]
        if np.abs(X.sum(1) - rows).max() <= tol * max(rows.sum(), 1): break
    return X


def margins(p):
    """a province's 2023 result (on its 2026 census) and its projection, as row and column totals"""
    t = p['r23']; L = dict.fromkeys(ROWS, 0.0)
    for k, v in t['v'].items(): L[k if k in L else 'OTROS'] += v * t['valid']
    L['OTROS'] += t['blank']; L['ABST'] = p['census'] - t['valid']
    V0 = p['census'] * p['t0'] * (1 - p['nr']); R = dict.fromkeys(COLS, 0.0)
    for k, v in p['s'].items(): R[k if k in R else 'OTROS'] += v * V0
    R['OTROS'] += p['bl'] * V0; R['ABST'] = p['census'] - V0
    return np.array([L[k] for k in ROWS]), np.array([R[k] for k in COLS])


def pattern(M, nr, nc, rows, cols):
    """the survey table, each thin row/column pulled toward a neutral starting point"""
    tot = M.sum()
    P = M / tot
    rsh = rows / rows.sum(); csh = cols / cols.sum()
    # columns: shrink each column's origin mix toward the 2023 electorate
    for j in range(len(COLS)):
        w = nc[j] / (nc[j] + K); m = P[:, j].sum()
        mix = P[:, j] / m if m > 0 else rsh
        P[:, j] = (w * mix + (1 - w) * rsh) * max(m, csh[j] * 0.01)
    # rows: shrink each row's destination mix toward "keeps the average loyalty, the rest like today's electorate"
    loyal = []
    for i, r in enumerate(ROWS):
        same = [COLS.index(c) for c in SAME[r]]
        if nr[i] >= K and r not in ('OTROS', 'ABST'): loyal.append(P[i, same].sum() / P[i].sum())
    lo = float(np.mean(loyal)) if loyal else 0.6
    for i, r in enumerate(ROWS):
        w = nr[i] / (nr[i] + K); m = P[i].sum()
        mix = P[i] / m if m > 0 else csh
        same = [COLS.index(c) for c in SAME[r]]
        neutral = csh * (1 - lo) / max(1e-9, 1 - csh[same].sum()); neutral[same] = lo * csh[same] / csh[same].sum()
        P[i] = (w * mix + (1 - w) * neutral) * max(m, rsh[i] * 0.01)
    return P, lo


def province_flows(app, path=None, min_votes=50):
    M, nr, nc, study = survey(path)
    marg = {p['id']: margins(p) for p in app['prov']}
    rows = sum(m[0] for m in marg.values()); cols = sum(m[1] for m in marg.values())
    P, lo = pattern(M, nr, nc, rows, cols)
    NAT = rake(P * rows.sum(), rows, cols)
    out = {}
    for pid, (r, c) in marg.items():
        X = rake(NAT * np.outer(r > 0, c > 0), r, c)        # parties absent on either side are zeros
        out[pid] = [[ROWS[i], COLS[j], int(round(X[i, j]))] for i in range(len(ROWS)) for j in range(len(COLS)) if X[i, j] >= min_votes]
    meta = dict(study=study, title=TITLES.get(study, f'estudio {study} del CIS'), n=int(nr.sum()), loyalty=round(lo, 3), nr=dict(zip(ROWS, nr.astype(int).tolist())), nc=dict(zip(COLS, nc.astype(int).tolist())))
    return out, meta, NAT


if __name__ == '__main__':
    import json, sys
    app = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(D, 'app_data.json')))
    flows, meta, NAT = province_flows(app, sys.argv[2] if len(sys.argv) > 2 else None)
    print(meta)
    tot = {}
    for fl in flows.values():
        for a, b, v in fl: tot[(a, b)] = tot.get((a, b), 0) + v
    show = ['PSOE', 'FA', 'COMP', 'PODEMOS', 'ERC', 'JUNTS', 'AC', 'SALF', 'VOX', 'PP', 'OTROS', 'ABST']
    print('suma de provincias, miles de votos\n' + ' ' * 7 + ''.join(f'{c[:7]:>8}' for c in show))
    for r in ROWS:
        print(f'{r:7}' + ''.join(f'{tot.get((r, c), 0) / 1e3:8.0f}' for c in show))
