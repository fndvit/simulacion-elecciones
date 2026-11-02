"""Share of CIS respondents (barómetro 3582, oct. 2026) who name at least one of each topic's problems,
as a problem of Spain and as one that affects them personally (up to three answers each).
python3 modelo/decide/cis_temas.py  → datos/decide/cis_temas.json"""
import csv, io, json, os, sys, zipfile
sys.path.insert(0, os.path.dirname(__file__))
from temas import TEMAS
BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'datos')
z = zipfile.ZipFile(os.path.join(BASE, 'cis', 'MD3582.zip'))
rows = list(csv.DictReader(io.TextIOWrapper(z.open('3582_etiq.csv'), encoding='utf-8', errors='replace'), delimiter=';'))
K = lambda p: [f'{p}{i}: {l}' for i, l in ((1, 'Primer problema'), (2, 'Segundo problema'), (3, 'Tercer problema'))]
out = {}
for t, v in TEMAS.items():
    probs = set(v['cis'])
    # economía también recoge la subida de precios de la energía; empleo, el paro
    es = sum(1 for r in rows if probs & {r[k] for k in K('PESPANNA')}) / len(rows)
    pe = sum(1 for r in rows if probs & {r[k] for k in K('PPERSONAL')}) / len(rows)
    out[t] = dict(espana=round(100 * es, 1), personal=round(100 * pe, 1), problemas=sorted(probs))
json.dump(dict(estudio='CIS 3582, barómetro de octubre de 2026', n=len(rows), temas=out),
          open(os.path.join(BASE, 'decide', 'cis_temas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for t, v in sorted(out.items(), key=lambda x: -x[1]['espana'] - x[1]['personal']): print(f"{t:12} {v['espana']:5} {v['personal']:5}")
