"""python3 buscar.py 'regex' [party,...] [max per party] — search frases.csv (original text and text_en)."""
import csv, re, sys, os, collections
f = os.path.join(os.path.dirname(__file__), '..', '..', 'datos', 'decide', 'frases.csv')
pat = re.compile(sys.argv[1], re.I)
ps = sys.argv[2].split(',') if len(sys.argv) > 2 and sys.argv[2] else None
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 6
n = collections.Counter()
for r in csv.DictReader(open(f, encoding='utf-8')):
    if ps and r['party'] not in ps: continue
    if r['party'] in ('IU', 'ECP') and not ps: continue
    if pat.search(r['text']) or pat.search(r['text_en']):
        n[r['party']] += 1
        if n[r['party']] <= mx:
            print(f"{r['party']:5} {r['i']:>5} [{r['code']}] {r['text'][:260]}")
print('#', dict(n))
