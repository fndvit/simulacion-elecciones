"""For each question/option, list up to N candidate sentences per party.
python3 evidencia.py [qid,...] [N] [party,...]"""
import csv, re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from preguntas import Q
f = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'decide', 'frases.csv')
rows = [r for r in csv.DictReader(open(f, encoding='utf-8')) if r['party'] not in ('IU', 'ECP')]
ids = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] else None
N = int(sys.argv[2]) if len(sys.argv) > 2 else 3
PS = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] else None
for q in Q:
    if ids and q['id'] not in ids: continue
    print(f"\n### {q['id']}: {q['q']}")
    for k, lab, rx in q['opts']:
        p = re.compile(rx, re.I); hits = {}
        for r in rows:
            if PS and r['party'] not in PS: continue
            if p.search(r['text']) or p.search(r['text_en']):
                hits.setdefault(r['party'], []).append(r)
        print(f"  -- {k}: {lab}  {{{', '.join(f'{a}:{len(b)}' for a,b in hits.items())}}}")
        for party, hs in hits.items():
            for r in hs[:N]:
                print(f"     {party:5} {r['i']:>5} [{r['code']}] {r['text'][:230]}")
