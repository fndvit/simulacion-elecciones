"""
Segunda fuente para la comprobación cruzada: la tabla de encuestas de la Wikipedia en inglés
(«Opinion polling for the next Spanish general election»; la API sigue la redirección si cambia de nombre).

Solo se usa para comparar: cada encuesta nueva o cambiada en la Wikipedia en español se busca aquí (misma
empresa, fin de campo con ±1 día de diferencia) y se comparan PP, PSOE y Vox. No entra nunca en la media.

Formato de la tabla inglesa: «Polling firm/Commissioner», «Fieldwork date» sin año («15 Jul–28 Aug»,
«26–27 Aug»), «Sample size», «Turnout», un partido por columna (cabecera con enlace al partido) y «Lead».
Las filas van de la más reciente a la más antigua; el año se deduce de ese orden.
"""
import datetime as dt, re, unicodedata, urllib.parse
from lxml import html as LH
import fetch_polls as F

PAGE = 'Opinion_polling_for_the_next_Spanish_general_election'
MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
# header cell (link title / href / text, lower case) → party
PARTY_KEYS = [("people's party", 'PP'), ('people%27s_party', 'PP'), ('socialist', 'PSOE'), ('psoe', 'PSOE'), ('vox', 'VOX'), ('sumar', 'SUMAR')]
CHECK = ('PP', 'PSOE', 'VOX')


def fetch():
    return F.fetch_page(PAGE, 'en')


def firm_key(name):
    """«EM-Analytics/Electomanía» → «emanalytics»; «CIS (Logoslab)» stays apart from «CIS»"""
    base = name if name.startswith('CIS') else name.split('/')[0]
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9()]', '', base)


def _party(th):
    bits = ' '.join([th.text_content()] + th.xpath('.//a/@title') + [urllib.parse.unquote(h) for h in th.xpath('.//a/@href')]).lower()
    return next((k for p, k in PARTY_KEYS if p in bits), None)


def _day_month(fw):
    last = re.split(r'[–—-]', fw.replace(' ', ' '))[-1].strip().lower()
    m = re.match(r'(\d{1,2})\s+([a-z]{3})', last)
    if m: return int(m.group(1)), MONTHS.get(m.group(2))
    m = re.match(r'(\d{1,2})$', last)                                # «26–27 Aug»: month only on the left? (rare)
    mon = re.search(r'([a-z]{3})', fw.lower())
    return (int(m.group(1)), MONTHS.get(mon.group(1))) if m and mon else (None, None)


def parse(html_text, today=None):
    today = today or dt.date.today()
    doc = LH.fromstring(html_text)
    out, year, prev = [], today.year, None
    for table in doc.xpath('//table[contains(@class, "wikitable")]'):
        g = F.grid(table)
        if not g: continue
        head = g[0]
        labels = [(c.text_content() if hasattr(c, 'text_content') else str(c)).strip().lower() for c, _ in head]
        if not any('fieldwork' in l for l in labels): continue
        i_firm = next(i for i, l in enumerate(labels) if 'polling firm' in l or 'pollster' in l or 'commissioner' in l) if any('polling' in l or 'commissioner' in l for l in labels) else 0
        i_fw = next(i for i, l in enumerate(labels) if 'fieldwork' in l)
        cols = {}
        for i, (c, _) in enumerate(head):
            if hasattr(c, 'xpath'):
                k = _party(c)
                if k and k not in cols.values(): cols[i] = k
        if 'PP' not in cols.values(): continue
        for r in g[1:]:
            if len(r) <= max(cols): continue
            name = re.sub(r'\s+', ' ', str(r[i_firm][0])).strip()
            if not name or name.lower().startswith(('general election', 'election', '20')): continue
            d, mon = _day_month(str(r[i_fw][0]))
            if not d or not mon: continue
            if prev and mon > prev and mon - prev > 6: year -= 1        # going down the table: Jan → Dec means the year before
            if prev is None and (mon, d) > (today.month, today.day): year = today.year - 1
            prev = mon
            try: end = dt.date(year, mon, d)
            except ValueError: continue
            v = {k: F.num(str(r[i][0])) for i, k in cols.items()}
            if v.get('PP') is None: continue
            out.append(dict(pollster=name, firm=firm_key(name), end=end, v=v))
    return out


def match(p, en, days=1):
    """the English row for a Spanish poll, or None"""
    fk = firm_key(p['pollster'])
    cands = [q for q in en if q['firm'] == fk and abs((q['end'] - p['end']).days) <= days]
    return min(cands, key=lambda q: abs((q['end'] - p['end']).days)) if cands else None


def compare(p, en, tol=0.15):
    """('coincide' | 'difiere' | 'no figura', text)"""
    q = match(p, en)
    if not q: return 'no figura', 'no figura en la Wikipedia en inglés'
    diffs = [f'{k} {q["v"][k]:g}'.replace('.', ',') for k in CHECK
             if p['v'].get(k) is not None and q['v'].get(k) is not None and abs(p['v'][k] - q['v'][k]) > tol]
    if diffs: return 'difiere', 'en inglés: ' + ', '.join(diffs)
    return 'coincide', 'coincide'
