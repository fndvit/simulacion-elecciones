"""
Paso diario de datos, a prueba de fallos. Lo ejecuta el workflow de GitHub Actions; también se puede lanzar a mano.

1. Descarga y lee las encuestas de Wikipedia (fetch_polls.py) en memoria, sin tocar datos/polls.csv.
2. Valida lo descargado contra el último fichero bueno. Si algo falla (red, cambio de formato en Wikipedia,
   tabla a medias, valores absurdos), NO se escribe nada: se sigue usando datos/polls.csv, que es el último
   bueno, y se informa del motivo.
3. Si todo es correcto y hay cambios, guarda una copia fechada del fichero anterior en datos/respaldo/
   (se conservan las 30 más recientes) y escribe el nuevo datos/polls.csv.

Nunca termina con error por culpa de los datos: escribe el resultado en GITHUB_OUTPUT (o en pantalla) para que
el workflow decida:  estado=ok|respaldo · cambios=si|no · motivo=…
"""
import csv, datetime as dt, glob, os, shutil, sys
import fetch_polls as F

HERE = os.path.dirname(os.path.abspath(__file__))
POLLS = os.path.join(HERE, '..', 'datos', 'polls.csv')
BACKUP_DIR = os.path.join(HERE, '..', 'datos', 'respaldo')
KEEP = 30
SINCE = dt.date(2025, 10, 1)


def fetch_with_retries(tries=3, wait=60):
    import time
    for i in range(tries):
        try:
            return F.fetch()
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


def main():
    old = read_current()
    try:
        text = fetch_with_retries()
        new = [p for p in F.parse(text, today=dt.date.today()) if p['end'] >= SINCE]
    except Exception as e:  # red, API, HTML irreconocible…
        out(estado='respaldo', cambios='no', motivo=f'no se pudo descargar o leer Wikipedia: {type(e).__name__}: {e}'.replace('\n', ' ')[:300])
        return
    errs = validate(new, old)
    if errs:
        out(estado='respaldo', cambios='no', motivo='; '.join(errs)[:300])
        return
    tmp = POLLS + '.tmp'
    F.write(new, tmp)
    with open(tmp) as a:
        fresh = a.read()
    current = open(POLLS).read() if os.path.exists(POLLS) else ''
    if fresh == current:
        os.remove(tmp)
        out(estado='ok', cambios='no', motivo=f'{len(new)} encuestas, sin novedades')
        return
    # copia fechada del último fichero bueno antes de sustituirlo
    if current:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        stamp = dt.datetime.utcnow().strftime('%Y-%m-%d_%H%M')
        shutil.copyfile(POLLS, os.path.join(BACKUP_DIR, f'polls_{stamp}.csv'))
        for f in sorted(glob.glob(os.path.join(BACKUP_DIR, 'polls_*.csv')))[:-KEEP]:
            os.remove(f)
    os.replace(tmp, POLLS)
    added = len(new) - len(old)
    out(estado='ok', cambios='si', motivo=f'{len(new)} encuestas ({added:+d}); la más reciente: {new[0]["pollster"]}, {new[0]["end"]}')


if __name__ == '__main__':
    main()
