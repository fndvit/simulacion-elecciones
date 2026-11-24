import csv, math, os, re, datetime as dt, json, statistics as st
D = os.path.join(os.path.dirname(__file__), '..', 'datos')
# the date the average is computed for: today (or SIM_TODAY=YYYY-MM-DD to reproduce a past run)
TODAY = dt.date.fromisoformat(os.environ['SIM_TODAY']) if os.environ.get('SIM_TODAY') else dt.date.today()
PARTIES = ['PP','PSOE','VOX','SUMAR','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','AA','PODEMOS','SALF','AC']
RES23 = {'PSOE':31.68,'PP':33.06,'VOX':12.38,'SUMAR':12.33}
HALF_LIFE = 14.0       # days: weight halves every two weeks (campaign-period decay)
HE_WINDOW = 21         # days either side used to build the house-effect comparison average
SAMPLE_CAP = 5000      # interviews: beyond this, a bigger sample adds no weight (538's default cap; 3000 until 13 Nov 2026)
HE_SHRINK = 4          # pseudo-polls of shrinkage toward zero house effect
UNRATED = 0.85
AC_TO = {'JUNTS': 0.23, 'VOX': 0.22}   # CEO 2nd wave 2026 as reported by Ara (the CEO does not publish the table; other outlets differ)

MESES = {m: i + 1 for i, m in enumerate(['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'])}

def start_of(fw, end):
    """First day of fieldwork from «26 Oct–7 Nov», «1–6 Nov» or «7 Nov» (year taken from the last day).
    Unreadable or empty (as in the historical polls) → the last day itself."""
    s = (fw or '').replace('\xa0', ' ').strip()
    a = re.split(r'\s*[–-]\s*', s)[0] if s else ''
    m = re.match(r'^(\d{1,2})(?:\s+([A-Za-zÁÉÍÓÚáéíóú]{3}))?', a)
    if not m: return end
    mon = MESES.get(m.group(2)[:3].capitalize()) if m.group(2) else end.month
    if not mon: return end
    y = end.year - 1 if mon > end.month else end.year
    try: d = dt.date(y, mon, int(m.group(1)))
    except ValueError: return end
    return d if d <= end else end

def mid_age(r, at):
    """Age in days of a poll on date «at», counted from its date: the centre of its fieldwork weighted by
    interviews (see centre_back). A 15-day cumulative release is mostly older than its last day."""
    return (at - r['end']).days + r.get('back', (r['end'] - r['start']).days / 2)

def centre_back(r, earlier):
    """Days from the last day of fieldwork back to the poll's date. Earlier releases of the same cumulative
    tracker (same first day, fewer interviews) say how many interviews were done by each date: each batch of
    new interviews sits at the centre of its own stretch of fieldwork, and the poll's date is the mean of those
    centres weighted by interviews. Without earlier releases, all interviews are spread evenly: the central day."""
    day = dt.timedelta(days=1)
    cps = sorted((o for o in earlier if o['start'] == r['start'] and o['n'] and r['n'] and o['n'] < r['n']),
                 key=lambda o: o['end'])
    pts, prev_end, prev_n = [], r['start'] - day, 0
    for o in cps + [r]:
        if not o['n'] or o['n'] <= prev_n or o['end'] <= prev_end: continue
        a = (prev_end + day).toordinal()
        pts.append((o['n'] - prev_n, a + (o['end'].toordinal() - a) / 2))
        prev_end, prev_n = o['end'], o['n']
    if not pts: return (r['end'] - r['start']).days / 2
    return r['end'].toordinal() - sum(n * c for n, c in pts) / sum(n for n, _ in pts)

def superseded(rows):
    """A): releases of the same firm whose fieldwork is mostly inside a newer release are the same interviews
    counted again (cumulative trackers: SW Demoscopia, SocioMétrica's panel…). Walking from the newest release
    back, an older one is dropped when it shares more than half of its fieldwork days with a release already
    kept. Sharing one day (Sigma Dos 29–30 Oct and 30 Oct–6 Nov) does not drop it.
    Polls without fieldwork dates are always kept. Returns (kept, dropped); kept releases are copies carrying
    «back», the days from their last day of fieldwork back to their date (centre_back)."""
    kept, dropped, by = [], [], {}
    for r in sorted(rows, key=lambda r: (r['end'], r['n'] or 0, r['start']), reverse=True):
        if not r['fw']: kept.append(r); continue   # no fieldwork dates (historical polls): nothing to compare
        days = (r['end'] - r['start']).days + 1
        hit = next((o for o in by.get(r['firm'], [])
                    if 2 * ((min(r['end'], o['end']) - max(r['start'], o['start'])).days + 1) > days), None)
        if hit: dropped.append((r, hit)); continue
        by.setdefault(r['firm'], []).append(r); kept.append(r)
    earlier = {}
    for r, o in dropped: earlier.setdefault(id(o), []).append(r)
    kept = [dict(r, back=centre_back(r, earlier.get(id(r), []))) for r in kept]
    return kept, dropped

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
        # Aliança Catalana does not stand on 29N (announced 5 Oct 2026). The few polls that gave it a figure move
        # it as reported from the CEO: 23 % to Junts, 22 % to Vox; the rest stays with «otros».
        if v['AC'] is not None:
            if v['JUNTS'] is not None: v['JUNTS'] += AC_TO['JUNTS'] * v['AC']
            if v['VOX'] is not None: v['VOX'] += AC_TO['VOX'] * v['AC']
            v['AC'] = None
        f = firm(r['pollster'])
        # the CIS counts once per barometer: its own estimate. Third-party re-estimates of its microdata
        # («CIS (Target Point)»…) are the same interviews, so they are kept in polls.csv but left out.
        if f.startswith('CIS ('): continue
        end = dt.date.fromisoformat(r['end'])
        rows.append(dict(pollster=r['pollster'], firm=f, end=end, start=start_of(r['fw'], end), fw=r['fw'],
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
    # only what was published by «at», and each cumulative tracker once: its latest release on that date
    rows = superseded([r for r in rows if r['end'] <= at])[0]
    # frequency: firms polling often share their weight (1/√k)
    fk = lambda f: f
    recent = {}
    for r in rows:
        if mid_age(r, at) <= 30: recent[fk(r['firm'])] = recent.get(fk(r['firm']), 0) + 1
    out, detail = {}, []
    for r in rows:
        age = mid_age(r, at)
        w_rec = 0.5 ** (age / HALF_LIFE)
        n = min(r['n'] or 800, SAMPLE_CAP)
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
    Mean residual per firm & party, shrunk toward 0 by k/(k+HE_SHRINK). Superseded releases of cumulative trackers
    are left out (they would count the same interviews several times), and polls are dated by their central day."""
    rows = superseded(rows)[0]
    md = lambda r: r['end'] - dt.timedelta(days=r['back'])
    res = {}
    for r in rows:
        for p in PARTIES:
            x = r['v'][p]
            if x is None: continue
            items = [(o['v'][p], 0.5 ** (abs((md(o) - md(r)).days) / 7) * math.sqrt(min(o['n'] or 800, SAMPLE_CAP) / 1000))
                     for o in rows if o['firm'] != r['firm'] and o['v'][p] is not None and abs((md(o) - md(r)).days) <= HE_WINDOW]
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
    print('superseded (same interviews as a newer release):')
    for r, o in sorted(superseded([r for r in rows if r['end'] <= TODAY])[1], key=lambda x: x[0]['end'], reverse=True):
        print(f"  {r['pollster']:32s} {r['fw']:16s} n={r['n']}  →  {o['fw']} n={o['n']}")
