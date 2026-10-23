import csv, math, os, re, datetime as dt, json, statistics as st
D = os.path.join(os.path.dirname(__file__), '..', 'datos')
# the date the average is computed for: today (or SIM_TODAY=YYYY-MM-DD to reproduce a past run)
TODAY = dt.date.fromisoformat(os.environ['SIM_TODAY']) if os.environ.get('SIM_TODAY') else dt.date.today()
PARTIES = ['PP','PSOE','VOX','SUMAR','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','AA','PODEMOS','SALF','AC']
RES23 = {'PSOE':31.68,'PP':33.06,'VOX':12.38,'SUMAR':12.33}
HALF_LIFE = 14.0       # days: weight halves every two weeks (campaign-period decay)
HE_WINDOW = 21         # days either side used to build the house-effect comparison average
HE_SHRINK = 4          # pseudo-polls of shrinkage toward zero house effect
UNRATED = 0.85

def firm(name):
    if name.startswith('CIS'):   # «CIS» = official estimate; «CIS (X)» = X's re-estimate of the CIS microdata
        m = re.match(r'CIS\s*\((.*)\)', name)
        return f'CIS ({m.group(1).strip().replace(" Del ", " del ")})' if m else 'CIS'
    base = name.split('/')[0].strip()
    alias = {'ElectoPanel':'EM-Analytics','Data10':'Data10','Hamalgama Métrica':'Hamalgama Métrica','Ateneo del Dato':'Ateneo del Dato'}
    return alias.get(base, base)

def load():
    rows = []
    for r in csv.DictReader(open(os.path.join(D, 'polls.csv')), delimiter='|'):
        v = {}
        for k in ['PP','PSOE','VOX','SUMAR','FA','COMP','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','AA','PODEMOS','SALF','AC']:
            v[k] = float(r[k]) if r[k] else None
        comp_split = None
        if v['FA'] is not None:
            v['SUMAR'] = v['FA'] + (v['COMP'] or 0)
            if v['COMP']: comp_split = v['COMP'] / v['SUMAR']
        rows.append(dict(pollster=r['pollster'], firm=firm(r['pollster']), end=dt.date.fromisoformat(r['end']), fw=r['fw'],
                         n=int(r['n']) if r['n'] else None, v={k: v[k] for k in PARTIES}, comp_split=comp_split))
    return rows

def ratings():
    """Pollster accuracy in the 2023 general election (final published poll, 4 main parties):
    weight = (mean MAE of all firms / firm MAE)^2, clipped to [0.6, 1.4]."""
    mae = {}
    for r in csv.DictReader(open(os.path.join(D, 'polls2023_final.csv')), delimiter='|'):
        mae[r['pollster']] = sum(abs(float(r[k]) - RES23[k]) for k in RES23) / 4
    m = st.mean(mae.values())
    w = {k: max(0.6, min(1.4, (m / x) ** 2)) for k, x in mae.items()}
    return mae, w

def rating_for(firm_name, w):
    if firm_name.startswith('CIS ('): return UNRATED, None   # third-party re-estimates of CIS microdata
    if firm_name == 'CIS': return w['CIS'], 'CIS'
    for k in w:
        if firm_name.startswith(k) or k.startswith(firm_name): return w[k], k
    return UNRATED, None

def wavg(items):
    s = sum(w for _, w in items)
    return sum(x * w for x, w in items) / s if s else None

def average(rows, at=TODAY, he=None, use_rating=True):
    mae, rw = ratings()
    # frequency: firms polling often share their weight (1/√k). All CIS-based estimates come from the
    # same monthly survey, so they share one budget.
    fk = lambda f: 'CIS' if f.startswith('CIS') else f
    recent = {}
    for r in rows:
        if 0 <= (at - r['end']).days <= 30: recent[fk(r['firm'])] = recent.get(fk(r['firm']), 0) + 1
    out, detail = {}, []
    for r in rows:
        age = (at - r['end']).days
        if age < 0: continue
        w_rec = 0.5 ** (age / HALF_LIFE)
        n = min(r['n'] or 800, 3000)
        w_n = math.sqrt(n / 1000)
        w_r = rating_for(r['firm'], rw)[0] if use_rating else 1
        w_f = 1 / math.sqrt(max(1, recent.get(fk(r['firm']), 1)))
        w = w_rec * w_n * w_r * w_f
        detail.append((r, w, dict(rec=w_rec, n=w_n, rating=w_r, freq=w_f)))
    for p in PARTIES:
        items = []
        for r, w, _ in detail:
            x = r['v'][p]
            if x is None: continue
            if he: x -= he.get(r['firm'], {}).get(p, 0)
            items.append((x, w))
        out[p] = wavg(items)
    return out, detail

def house_effects(rows):
    """For each poll, compare to a recency-weighted average of OTHER firms' polls within ±HE_WINDOW days.
    Mean residual per firm & party, shrunk toward 0 by k/(k+HE_SHRINK)."""
    res = {}
    for r in rows:
        for p in PARTIES:
            x = r['v'][p]
            if x is None: continue
            items = [(o['v'][p], 0.5 ** (abs((o['end'] - r['end']).days) / 7) * math.sqrt(min(o['n'] or 800, 3000) / 1000))
                     for o in rows if o['firm'] != r['firm'] and o['v'][p] is not None and abs((o['end'] - r['end']).days) <= HE_WINDOW]
            if len(items) < 3: continue
            res.setdefault(r['firm'], {}).setdefault(p, []).append(x - wavg(items))
    he = {}
    for f, d in res.items():
        he[f] = {p: (st.mean(v) * len(v) / (len(v) + HE_SHRINK)) for p, v in d.items()}
    counts = {f: max(len(v) for v in d.values()) for f, d in res.items()}
    return he, counts

if __name__ == '__main__':
    rows = load()
    mae, rw = ratings()
    he, counts = house_effects(rows)
    raw, _ = average(rows)
    adj, detail = average(rows, he=he)
    print('ratings', {k: round(v, 2) for k, v in rw.items()})
    for f in sorted(he, key=lambda f: -counts[f]):
        print(f'{f:28s} n={counts[f]:3d}', ' '.join(f'{p}:{he[f].get(p,0):+.1f}' for p in ['PP','PSOE','VOX','SUMAR','PODEMOS','SALF']))
    print('raw ', {k: round(v, 2) for k, v in raw.items() if v})
    print('adj ', {k: round(v, 2) for k, v in adj.items() if v})
    splits = [r['comp_split'] for r in rows if r['comp_split']]
    print('comp split', splits)
    top = sorted(detail, key=lambda d: -d[1])[:12]
    for r, w, c in top: print(f"{r['pollster']:32s} {r['end']} w={w:.3f}", {k: round(v, 2) for k, v in c.items()})
