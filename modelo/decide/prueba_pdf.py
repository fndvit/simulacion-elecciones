"""python3 modelo/decide/prueba_pdf.py PSOE 33320 datos/programas/pdf/PSOE_2023.pdf
Prueba de la cadena PDF → corpus con un programa que el Manifesto Project ya codificó:
segmenta y codifica el PDF con un codificador entrenado SIN ese programa y lo compara con la versión del MP."""
import csv, glob, os, re, sys, difflib
sys.path.insert(0, 'modelo/decide')
import codificador, pdf_a_corpus
party, mid, pdf = sys.argv[1], sys.argv[2], sys.argv[3]
files = [f for f in sorted(glob.glob('datos/programas/[0-9]*_202307.csv')) if not os.path.basename(f).startswith(mid)]
T, S, Y, _ = codificador.corpus(files)
m = codificador.build(); m.fit(list(zip(T, S)), Y)
codificador.cargar = lambda: m
out = pdf_a_corpus.procesar(party, pdf, 'prueba')
ours = [r for r in csv.DictReader(open(out, encoding='utf-8')) if r['cmp_code'] != 'H']
mp = [r for r in csv.DictReader(open(f'datos/programas/{mid}_202307.csv', encoding='utf-8')) if r['cmp_code'] not in ('H',)]
n = lambda t: re.sub(r'[^a-záéíóúñüç0-9]+', ' ', t.lower()).strip()
# map each MP quasi-sentence to the one of ours that contains it best
idx = {}
for i, r in enumerate(ours):
    for w in set(n(r['text']).split()): idx.setdefault(w, set()).add(i)
hit = same = same_dom = coded = 0; exact_seg = 0
for r in mp:
    t = n(r['text']);
    if len(t.split()) < 3: continue
    cands = Counter = {}
    for w in t.split():
        for i in idx.get(w, ()): cands[i] = cands.get(i, 0) + 1
    if not cands: continue
    i = max(cands, key=cands.get)
    o = n(ours[i]['text'])
    if t in o or difflib.SequenceMatcher(None, t, o).ratio() > 0.8:
        hit += 1
        exact_seg += difflib.SequenceMatcher(None, t, o).ratio() > 0.9
        if r['cmp_code'] not in ('NA', '0', '000', ''):
            coded += 1; same += ours[i]['cmp_code'] == r['cmp_code']; same_dom += ours[i]['cmp_code'][:1] == r['cmp_code'][:1]
tot = sum(1 for r in mp if len(n(r['text']).split()) >= 3)
print(f'{party}: nuestras {len(ours)} cuasi-frases, MP {len(mp)}')
print(f'  frases del MP encontradas en nuestro texto: {hit}/{tot} = {hit/tot:.0%}; con el mismo corte: {exact_seg/tot:.0%}')
print(f'  misma categoría que el MP: {same/coded:.0%} (dominio {same_dom/coded:.0%}) en {coded} frases codificadas')
