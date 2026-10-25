"""
Descarga las encuestas de Wikipedia y regenera datos/polls.csv.

Fuente: es.wikipedia.org — «Encuestas de opinión para las elecciones generales de España de 2026»
(API action=parse). Se leen las tablas de intención de voto (las que tienen columna «Trabajo de campo»),
se expanden rowspan/colspan, y cada fila queda como: encuestadora, fecha de fin, campo, muestra y % por partido.

Reglas (las que hacen falta porque Wikipedia no es uniforme):
- El año sale del encabezado (h2/h3/h4) que precede a cada tabla; «27 Dic–3 Ene» acaba en enero de ese año.
- Una fila cuya celda de encuestadora viene de un rowspan es una reestimación de la fila anterior
  Si la fila madre se llama «CIS/Restimación X», la madre es «CIS» (estimación oficial) y la hija «CIS (X)».
  Cualquier otra subfila (segunda estimación de la misma casa) se descarta.
- Se descartan filas sin fecha de fin legible, filas de resultados («Elecciones …»), encuestas internas
  de partidos y duplicados exactos.
- Un valor de partido absurdo (> 2,5 veces y > 6 puntos por encima de la mediana de ese partido en los
  30 días alrededor) se deja en blanco y se registra en el log.

Cada encuesta guarda también su fuente (columna «src»): el primer enlace externo de su nota en Wikipedia.

Uso:  python3 modelo/fetch_polls.py             (descarga y escribe datos/polls.csv)
      python3 modelo/fetch_polls.py --html f.html (parsea un HTML local; para tests)
"""
import argparse, csv, datetime as dt, json, os, re, statistics as st, sys, urllib.parse, urllib.request
from lxml import html as LH

PAGE = 'Encuestas_de_opinión_para_las_elecciones_generales_de_España_de_2026'
API = 'https://es.wikipedia.org/w/api.php?action=parse&format=json&formatversion=2&prop=text&page=' + urllib.parse.quote(PAGE)
OUT = os.path.join(os.path.dirname(__file__), '..', 'datos', 'polls.csv')
COLS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'FA', 'COMP', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPN', 'AA', 'PODEMOS', 'SALF', 'AC']
# party column ← Wikipedia article slug (prefix match on the decoded /wiki/ link)
SLUG = [('Partido_Popular', 'PP'), ('Partido_Socialista_Obrero', 'PSOE'), ('Vox', 'VOX'), ('Sumar', 'SUMAR'),
        ('Frente_Amplio', 'FA'), ('Compromís', 'COMP'), ('Esquerra_Republicana', 'ERC'), ('Junts', 'JUNTS'),
        ('EH_Bildu', 'BILDU'), ('Partido_Nacionalista_Vasco', 'PNV'), ('Bloque_Nacionalista_Galego', 'BNG'),
        ('Coalición_Canaria', 'CC'), ('Unión_del_Pueblo_Navarro', 'UPN'), ('Adelante_Andalucía', 'AA'),
        ('Podemos', 'PODEMOS'), ('SALF', 'SALF'), ('Se_Acabó_La_Fiesta', 'SALF'), ('Aliança_Catalana', 'AC')]
MONTHS = {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12}
PARTY_INTERNAL = {'Sumar', 'PSOE', 'PP', 'Vox', 'Podemos'}  # polls commissioned and published by a party


def log(*a):
    print(*a, file=sys.stderr)


UA = {'User-Agent': 'simulador-29n/1.0 (datos electorales; contacto: fndvit)'}


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def fetch_page(page=PAGE, lang='es'):
    """the page's HTML and the exact revision read: {text, revid, timestamp, title, url}"""
    base = f'https://{lang}.wikipedia.org/w/api.php?format=json&formatversion=2'
    p = _get(base + '&action=parse&prop=text|revid&redirects=1&page=' + urllib.parse.quote(page))['parse']
    rev = _get(base + f'&action=query&prop=revisions&rvprop=ids|timestamp&revids={p["revid"]}')
    ts = rev['query']['pages'][0]['revisions'][0]['timestamp']
    return dict(text=p['text'], revid=p['revid'], timestamp=ts, title=p['title'],
                url=f'https://{lang}.wikipedia.org/w/index.php?oldid={p["revid"]}')


def fetch():
    return fetch_page()['text']


def cell_text(td):
    """first line of a cell (the vote %, not the seats under it), footnotes removed"""
    for sup in td.xpath('.//sup'):
        sup.drop_tree()
    for br in td.xpath('.//br'):
        br.tail = '\n' + (br.tail or '')
    for p in td.xpath('.//p'):
        p.text = '\n' + (p.text or '')
    txt = td.text_content().replace('​', '')
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    return lines[0] if lines else ''


def grid(table):
    """expand rowspan/colspan → list of rows of (text, own) where own=False means 'spanned from above'"""
    rows, carry = [], {}
    for tr in table.xpath('./tbody/tr|./tr'):
        cells, col = [], 0
        tds = list(tr.xpath('./td|./th'))
        out = {}
        while tds or any(c >= col for c in carry):
            if col in carry:
                txt, left = carry[col]
                out[col] = (txt, False)
                if left > 1: carry[col] = (txt, left - 1)
                else: del carry[col]
                col += 1
                continue
            if not tds: break
            td = tds.pop(0)
            txt = cell_text(td) if td.tag == 'td' else td
            span_c, span_r = int(td.get('colspan', 1)), int(td.get('rowspan', 1))
            for k in range(span_c):
                out[col + k] = (txt, True)
                if span_r > 1: carry[col + k] = (txt, span_r - 1)
            col += span_c
        rows.append([out[i] for i in sorted(out)])
    return rows


def header_parties(table):
    th = table.xpath('./tbody/tr[1]/th|./tr[1]/th')
    cols = []
    for h in th:
        a = h.xpath('.//a[starts-with(@href, "/wiki/")]')
        key = None
        if a:
            slug = urllib.parse.unquote(a[0].get('href').split('/wiki/')[1])
            key = next((k for p, k in SLUG if slug.startswith(p)), None)
        cols.append(key)
    return cols  # aligned with header cells (the 4 rowspan'd lead columns are None)


def year_before(el):
    node = el
    while node is not None:
        prev = node.getprevious()
        while prev is not None:
            m = re.search(r'\b(20\d\d)\b', prev.text_content()) if prev.tag in ('h2', 'h3', 'h4') or 'mw-heading' in (prev.get('class') or '') else None
            if m: return int(m.group(1))
            prev = prev.getprevious()
        node = node.getparent()
    return None


def end_date(fw, year):
    s = fw.replace('—', '-').replace('–', '-').lower()
    parts = [p.strip() for p in s.split('-') if p.strip()]
    if not parts: return None
    m = re.match(r'(\d{1,2})\s*(?:de\s+)?([a-zé]{3,})?', parts[-1])
    if not m: return None
    mon = m.group(2) or (re.search(r'([a-z]{3})', s) or [None, None])[1]
    mon = MONTHS.get((mon or '')[:3])
    if not mon or not year: return None
    try: return dt.date(year, mon, int(m.group(1)))
    except ValueError: return None


def num(t):
    t = re.sub(r"[^\d.,]", '', t.replace(',', '.'))
    try: return float(t) if t else None
    except ValueError: return None


def references(doc):
    """footnote id → first external link (the outlet that published the poll)"""
    out = {}
    for li in doc.xpath('//li[starts-with(@id, "cite_note")]'):
        a = li.xpath('.//a[starts-with(@href, "http")]')
        if a: out[li.get('id')] = a[0].get('href')
    return out


def parse(html_text, today=None):
    doc = LH.fromstring(html_text)
    refs = references(doc)
    polls = []
    for table in doc.xpath('//table[contains(@class, "wikitable")]'):
        head = ' '.join(h.text_content() for h in table.xpath('./tbody/tr[1]/th|./tr[1]/th'))
        if 'Trabajo de campo' not in head: continue
        year = year_before(table)
        parties = [p for p in header_parties(table)[4:] if True]
        # each row's source, read before cell_text() strips the footnote marks
        row_src = []
        for tr in table.xpath('./tbody/tr|./tr'):
            ids = [h.lstrip('#') for h in tr.xpath('.//sup//a[starts-with(@href, "#cite_note")]/@href')]
            row_src.append(next((refs[i] for i in ids if i in refs), ''))
        g = grid(table)
        mother = mother_src = None
        for ri, r in enumerate(g[2:], start=2):
            src = row_src[ri] if ri < len(row_src) else ''
            if r and r[0][1]: mother_src = src
            src = src or mother_src or ''
            if len(r) < 4 + len(parties): continue
            (pol, pol_own), (fw, _), (n, _), _ = r[0], r[1], r[2], r[3]
            pol = re.sub(r'\s+', ' ', pol).strip()
            if pol_own:
                mother = pol
                name = pol
                m = re.match(r'CIS\s*/\s*Re?e?s?timaci[oó]n\s+(.*)', pol, re.I)
                if m: name = 'CIS'
            else:
                m = re.match(r'CIS\s*/\s*Re?e?s?timaci[oó]n\s+(.*)', mother or '', re.I)
                if not m: log('subfila descartada (segunda estimación de', mother, ')'); continue
                name = f'CIS ({m.group(1).strip()})'
            if pol.lower().startswith('elecciones') or name.split('/')[0].strip() in PARTY_INTERNAL: continue
            end = end_date(fw, year)
            if not end: log('sin fecha:', name, fw); continue
            if today and end > today: end = end.replace(year=end.year - 1)
            vals = {k: None for k in COLS}
            for k, (txt, _) in zip(parties, r[4:4 + len(parties)]):
                if k: vals[k] = num(txt)
            if vals['PP'] is None and vals['PSOE'] is None: continue  # seats-only / bloc tables
            if vals['FA'] is not None or vals['COMP'] is not None:
                vals['SUMAR'] = None  # FA/Compromís split already given
            polls.append(dict(pollster=name, end=end, fw=fw, n=int(re.sub(r'\D', '', n)) if re.sub(r'\D', '', n) else None, v=vals, src=src))
    # dedupe exact repeats
    seen, out = set(), []
    for p in polls:
        key = (p['pollster'], p['end'], tuple(p['v'][k] for k in COLS))
        if key in seen: continue
        seen.add(key); out.append(p)
    # implausible single values
    for p in out:
        for k in COLS:
            x = p['v'][k]
            if x is None: continue
            near = [q['v'][k] for q in out if q is not p and q['v'][k] is not None and abs((q['end'] - p['end']).days) <= 30]
            if len(near) >= 3:
                med = st.median(near)
                if x > 2.5 * med and x - med > 6:
                    log(f'valor descartado: {p["pollster"]} {p["end"]} {k}={x} (mediana {med})'); p['v'][k] = None
    out.sort(key=lambda p: p['end'], reverse=True)
    return out


HEAD = ['pollster', 'end', 'fw', 'n'] + COLS + ['src']


def row(p):
    """a poll as the strings written to polls.csv"""
    return [p['pollster'], p['end'].isoformat(), p['fw'], str(p['n'] or '')] + ['' if p['v'][k] is None else f"{p['v'][k]:g}" for k in COLS] + [p.get('src', '')]


def write(polls, path=OUT):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f, delimiter='|')
        w.writerow(HEAD)
        for p in polls: w.writerow(row(p))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--html'); ap.add_argument('--out', default=OUT); ap.add_argument('--since', default='2025-10-01')
    a = ap.parse_args()
    text = open(a.html).read() if a.html else fetch()
    polls = [p for p in parse(text, today=dt.date.today()) if p['end'] >= dt.date.fromisoformat(a.since)]
    write(polls, a.out)
    log(f'{len(polls)} encuestas → {a.out}; la más reciente: {polls[0]["pollster"]} ({polls[0]["end"]})')
