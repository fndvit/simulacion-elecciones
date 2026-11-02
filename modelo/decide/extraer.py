"""Corpus de cada programa (programas.json) → datos/decide/frases.csv: cada cuasi-frase con su sección, su página
(si viene de un PDF propio) y los temas del cuestionario a los que puede referirse.

Para cada partido se usa, por este orden: datos/programas/<PARTIDO>_<edicion>.csv (salida de pdf_a_corpus.py) o
datos/programas/<mp_id>_<edicion>.csv (corpus del Manifesto Project). Si no hay ninguno, el partido no aparece.
python3 modelo/decide/extraer.py"""
import csv, json, os, re, sys
HERE = os.path.dirname(__file__)
sys.path.insert(0, HERE)
from temas import TEMAS, KW_ROM
BASE = os.path.join(HERE, '..', '..', 'datos')
CFG = json.load(open(os.path.join(HERE, 'programas.json'), encoding='utf-8'))
ED = CFG['edicion']


def fuente(party):
    c = CFG['partidos'][party]
    for f in (f'{party}_{ED}.csv', f"{c['mp_id']}_{ED}.csv"):
        p = os.path.join(BASE, 'programas', f)
        if os.path.exists(p): return p
    return None


if __name__ == '__main__':
    out = csv.writer(open(os.path.join(BASE, 'decide', 'frases.csv'), 'w', newline='', encoding='utf-8'))
    out.writerow(['party', 'fuente', 'i', 'code', 'seccion', 'temas', 'text', 'text_en', 'page'])
    pat = {k: re.compile(v['kw'], re.I) for k, v in TEMAS.items()}
    rom = {k: re.compile(v, re.I) for k, v in KW_ROM.items()}
    for party in CFG['partidos']:
        f = fuente(party)
        if not f:
            print(f'{party}: sin corpus para {ED}'); continue
        rows = list(csv.DictReader(open(f, encoding='utf-8')))
        sec, n = '', 0
        for i, r in enumerate(rows):
            code = (r.get('cmp_code') or '').strip()
            if code == 'H':
                sec = r['text'].strip(); continue
            if code in ('NA', '', '0', '000'): continue
            en = r.get('text_en') if r.get('text_en') not in (None, '', 'NA') else ''
            if en:
                m = lambda k, t: pat[k].search(t); txt = en
            else:  # no translation: Spanish / Catalan / Galician stems on the original text
                m = lambda k, t: rom[k].search(t); txt = r['text']
            ctx = txt + ' ' + sec
            tags = [k for k, v in TEMAS.items() if m(k, txt) or (code in v.get('codes', []) and m(k, ctx))]
            out.writerow([party, os.path.basename(f), i, code, sec, '|'.join(tags), r['text'].strip(), (en or '').strip(), r.get('page', '')])
            n += 1
        print(f'{party}: {n} frases de {os.path.basename(f)}')
