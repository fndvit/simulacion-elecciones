"""
Comprobación de cordura de datos/app_data.json antes de publicar. Si algo no cuadra, sale con error y el
workflow no publica: la página en línea sigue siendo la del último día bueno.
"""
import json, os, sys

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
a = json.load(open(os.path.join(D, 'app_data.json')))
errs = []
S = a.get('S', {})
tot = sum(S.values())
if not 90 <= tot <= 101:
    errs.append(f'la suma de la media nacional es {tot:.1f} %')
for k in ('PP', 'PSOE', 'VOX'):
    if not 5 <= S.get(k, 0) <= 50:
        errs.append(f'{k} en la media: {S.get(k)}')
if len(a.get('prov', [])) != 52:
    errs.append(f'{len(a.get("prov", []))} circunscripciones (deberían ser 52)')
seats = sum(p['seats'] for p in a.get('prov', []))
if seats != 350:
    errs.append(f'{seats} escaños (deberían ser 350)')
if len(a.get('polls', [])) < 50:
    errs.append(f'solo {len(a.get("polls", []))} encuestas en la app')
if errs:
    print('Datos de la app NO válidos:\n- ' + '\n- '.join(errs), file=sys.stderr)
    sys.exit(1)
print(f'app_data.json correcto: {len(a["polls"])} encuestas, 52 circunscripciones, 350 escaños, fecha {a["today"]}')
