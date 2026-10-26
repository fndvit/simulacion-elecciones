"""Historical nationwide polls (English Wikipedia) for the backtest: April 2019, November 2019 and 2023.
Writes datos/hist_polls.csv: election|pollster|end|n|PP|PSOE|VOX|SUM|CS|ERC|JUNTS|BILDU|PNV|BNG|CC
SUM = the space left of PSOE that ran together later (UP + Más País + Compromís in 2019; Sumar + Podemos in 2023).
Only vote-estimate tables (they have a «Turnout» column); direct-intention tables are skipped."""
import csv, datetime as dt, json, os, re, sys, urllib.parse, urllib.request
from lxml import html as LH

D = os.path.join(os.path.dirname(__file__), '..', 'datos')
PAGES = {'g2019a': ('Opinion_polling_for_the_April_2019_Spanish_general_election', dt.date(2019, 4, 28)),
         'g2019n': ('Opinion_polling_for_the_November_2019_Spanish_general_election', dt.date(2019, 11, 10)),
         'g2023': ('Opinion_polling_for_the_2023_Spanish_general_election', dt.date(2023, 7, 23))}
# column ← article slug prefix
SLUG = [('Spanish_Socialist', 'PSOE'), ("People%27s_Party", 'PP'), ('Vox', 'VOX'), ('Citizens_(Spanish', 'CS'),
        ('Unidas_Podemos', 'SUM'), ('Unidos_Podemos', 'SUM'), ('Podemos_(Spanish', 'SUM'), ('Sumar_(electoral', 'SUM'),
        ('M%C3%A1s_Pa%C3%ADs', 'SUM'), ('Coalici%C3%B3_Comprom%C3%ADs', 'SUM'), ('Comprom%C3%ADs', 'SUM'),
        ('Republican_Left_of_Catalonia', 'ERC'), ('Together_for_Catalonia', 'JUNTS'), ('Catalan_European_Democratic', 'JUNTS'),
        ('EH_Bildu', 'BILDU'), ('Basque_Nationalist', 'PNV'), ('Galician_Nationalist', 'BNG'), ('Canarian_Coalition', 'CC')]
COLS = ['PP', 'PSOE', 'VOX', 'SUM', 'CS', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC']
MON = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}


def first_line(td):
    for s in td.xpath('.//sup|.//style'): s.drop_tree()
    for br in td.xpath('.//br'): br.tail = '\n' + (br.tail or '')
    lines = [l.strip() for l in td.text_content().replace('​', '').split('\n') if l.strip()]
    return lines[0] if lines else ''


def num(s):
    m = re.match(r'^\s*(\d+(?:\.\d+)?)', s.replace(',', '.')) if s and not s.startswith('?') else None
    return float(m.group(1)) if m else None


def end_date(s, year):
    """«12–17 Jun» / «30 May–3 Jun» / «28 Dec 2018–3 Jan 2019» → (day, month, explicit year or None) of the end"""
    s = s.replace('\xa0', ' ')
    m = re.findall(r'(\d{1,2})\s+([A-Z][a-z]{2})(?:\s+(\d{4}))?', s)
    if not m: return None
    d, mo, y = m[-1]
    if mo not in MON: return None
    return int(d), MON[mo], int(y) if y else None


def grid(tb):
    """expand rowspan/colspan into a list of rows of (cell element, is_spanned_copy)"""
    out, carry = [], {}
    for tr in tb.xpath('./tr|./tbody/tr'):
        row, col = [], 0
        cells = tr.xpath('./td|./th')
        it = iter(cells)
        while True:
            if col in carry and carry[col][1] > 0:
                el, left = carry[col]; row.append((el, True)); carry[col] = (el, left - 1); col += 1; continue
            c = next(it, None)
            if c is None: break
            span, rs = int(c.get('colspan', 1)), int(c.get('rowspan', 1))
            for k in range(span):
                row.append((c, False))
                if rs > 1: carry[col] = (c, rs - 1)
                col += 1
        while col in carry and carry[col][1] > 0:
            el, left = carry[col]; row.append((el, True)); carry[col] = (el, left - 1); col += 1
        out.append(row)
    return out


def parse(e):
    page, eday = PAGES[e]
    path = os.path.join(D, 'wiki_' + e + '.json')
    if not os.path.exists(path):
        url = 'https://en.wikipedia.org/w/api.php?action=parse&format=json&formatversion=2&prop=text&page=' + page
        req = urllib.request.Request(url, headers={'User-Agent': 'simulador-29n/1.0 (fndvit)'})
        json.dump(json.load(urllib.request.urlopen(req, timeout=60)), open(path, 'w'))
    doc = LH.fromstring(json.load(open(path))['parse']['text'])
    rows = []
    for tb in doc.xpath('//table[contains(@class,"wikitable")]'):
        g = grid(tb)
        if not g: continue
        head = [c for c, _ in g[0]]
        labels = [h.text_content().strip() for h in head]
        if 'Fieldwork date' not in labels or 'Turnout' not in labels: continue
        cmap = {}
        for i, h in enumerate(head):
            a = h.xpath('.//a/@href')
            if not a: continue
            slug = a[0].split('/wiki/')[-1]
            for pre, k in SLUG:
                if slug.startswith(pre): cmap.setdefault(i, k); break
        iF, iN = labels.index('Fieldwork date'), labels.index('Sample size')
        year, prev = eday.year, eday.month
        for r in g[1:]:
            if len(r) <= max(cmap or {0: 0}): continue
            pol_el, spanned = r[0]
            pol = first_line(pol_el)
            if spanned or not pol or 'election' in pol.lower() or 'EP election' in pol: continue
            de = end_date(first_line(r[iF][0]), year)
            if not de: continue
            d, mo, y = de
            if y: year = y
            elif mo > prev + 1: year -= 1           # going back across New Year
            prev = mo
            date = dt.date(year, mo, d)
            if date >= eday: continue
            v = {k: None for k in COLS}
            used = set()
            for i, k in cmap.items():
                el = r[i][0]
                if (k, id(el)) in used: continue          # a cell spanning two columns of the same family counts once
                used.add((k, id(el)))
                x = num(first_line(el))
                if x is not None: v[k] = (v[k] or 0) + x
            if v['PP'] is None or v['PSOE'] is None: continue
            n = re.sub(r'[^\d]', '', first_line(r[iN][0]))
            rows.append(dict(election=e, pollster=re.sub(r'\[.*?\]', '', pol).strip(), end=date.isoformat(),
                             n=int(n) if n else '', **{k: '' if x is None else round(x, 2) for k, x in v.items()}))
    # same poll in two tables → keep the first
    seen, out = set(), []
    for r in rows:
        key = (r['pollster'], r['end'])
        if key in seen: continue
        seen.add(key); out.append(r)
    return out


if __name__ == '__main__':
    allrows = []
    for e in PAGES:
        r = parse(e); allrows += r
        print(e, len(r), 'polls', min(x['end'] for x in r), '→', max(x['end'] for x in r), file=sys.stderr)
    with open(os.path.join(D, 'hist_polls.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, ['election', 'pollster', 'end', 'n'] + COLS, delimiter='|'); w.writeheader(); w.writerows(allrows)
