"""
Fuente PRINCIPAL de las encuestas (desde noviembre de 2026): la tabla de la Wikipedia en inglés,
«Opinion polling for the 2026 Spanish general election» (la API sigue la redirección si cambia de nombre).
La de la Wikipedia en español quedó desactualizada; ahora sirve para la comprobación cruzada (fetch_polls.py).

Formato de las tablas inglesas (sección «Voting intention estimates», una tabla por periodo):
«Polling firm/Commissioner», «Fieldwork date» sin año («15 Jul–28 Aug», «26–27 Aug»), «Sample size»,
«Turnout», un partido por columna (cabecera con enlace al artículo del partido) y «Lead».

Reglas:
- El año se deduce del orden: las filas van de la más reciente a la más antigua, tabla tras tabla; si el mes
  sube (enero → diciembre) es que se ha pasado al año anterior. «27 Dec–3 Jan» acaba en enero.
- Una cifra que ocupa varias columnas de partido es la de una lista conjunta: Frente Amplio + Compromís
  cuentan como Sumar; cualquier otra combinación, para el primer partido.
- Los partidos se reconocen por el enlace de la cabecera: Broad Front → Frente Amplio, Valencian Front →
  Compromís-Front Valencià, Sumar (antes de la ruptura), Aliança.cat, Se Acabó La Fiesta…
- Se descartan filas de resultados («… election»), encuestas encargadas por partidos («PSOE», «Sumar»,
  «SocioMétrica/PP»), subfilas (segunda estimación de la misma casa) y duplicados exactos.
- «CIS» es la estimación oficial; «CIS (X)», la reestimación de X con los microdatos (polls.py no la usa).
- Cada encuesta guarda su fuente: el primer enlace externo de su nota al pie.
"""
import datetime as dt, re, unicodedata, urllib.parse
from lxml import html as LH
import fetch_polls as F

PAGE = 'Opinion_polling_for_the_2026_Spanish_general_election'
MONTHS = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
# article linked from the column header → party (prefix of the /wiki/ slug)
SLUG = [("People's_Party_(Spain)", 'PP'), ('Spanish_Socialist_Workers', 'PSOE'), ('Vox_(political_party)', 'VOX'),
        ('Sumar', 'SUMAR'), ('Broad_Front_(Spain)', 'FA'), ('Valencian_Front', 'COMP'), ('Compromís', 'COMP'),
        ('Republican_Left_of_Catalonia', 'ERC'), ('Together_for_Catalonia', 'JUNTS'), ('EH_Bildu', 'BILDU'),
        ('Basque_Nationalist_Party', 'PNV'), ('Galician_Nationalist_Bloc', 'BNG'), ('Canarian_Coalition', 'CC'),
        ('Navarrese_People', 'UPN'), ('Adelante_Andalucía', 'AA'), ('Podemos', 'PODEMOS'), ('Se_Acabó_La_Fiesta', 'SALF'),
        ('Aliança', 'AC'), ('Catalan_Alliance', 'AC')]
# the fieldwork dates are kept as the site shows them, with Spanish month abbreviations
ES_MONTH = {'Jan': 'Ene', 'Apr': 'Abr', 'Aug': 'Ago', 'Dec': 'Dic'}
PARTY_INTERNAL = {'PP', 'PSOE', 'Vox', 'Sumar', 'Podemos'}   # polls commissioned and published by a party
CHECK = ('PP', 'PSOE', 'VOX')


def fetch():
    return F.fetch_page(PAGE, 'en')


def firm_key(name):
    """«EM-Analytics/Electomanía» → «emanalytics»; «CIS (Logoslab)» stays apart from «CIS»"""
    base = name if name.startswith('CIS') else name.split('/')[0]
    base = unicodedata.normalize('NFKD', base).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9()]', '', base)


def _party(th):
    for h in th.xpath('.//a[starts-with(@href, "/wiki/")]/@href'):
        slug = urllib.parse.unquote(h.split('/wiki/')[1])
        k = next((k for p, k in SLUG if slug.startswith(p)), None)
        if k: return k
    return None


def _end(fw):
    """(day, month, year or None) of the last fieldwork day"""
    s = fw.replace('\xa0', ' ').strip()
    last = re.split(r'[–—-]', s)[-1].strip().lower()
    m = re.match(r'(\d{1,2})(?:\s+([a-z]{3})[a-z]*)?(?:\s+(\d{4}))?', last)
    if not m: return None, None, None
    mon = m.group(2) or (re.search(r'([a-z]{3})', s.lower()) or [None, None])[1]
    return int(m.group(1)), MONTHS.get(mon or ''), int(m.group(3)) if m.group(3) else None


def _section(table):
    h = table.xpath('preceding::*[self::h2 or self::h3 or self::h4][1]')
    return h[0].text_content().strip().lower() if h else ''


def parse(html_text, today=None):
    today = today or dt.date.today()
    doc = LH.fromstring(html_text)
    refs = F.references(doc)
    polls, year, prev = [], today.year, None
    for table in doc.xpath('//table[contains(@class, "wikitable")]'):
        if 'voting intention' not in _section(table): continue        # not the seat projections, preferences…
        head = table.xpath('./tbody/tr[1]/th|./tr[1]/th')
        labels = [h.text_content().strip().lower() for h in head]
        if not any('fieldwork' in l for l in labels): continue
        # column index of each header cell (they may span), the party in it
        cols, i = {}, 0
        for h in head:
            k = _party(h)
            if k and k not in cols.values(): cols[i] = k
            i += F._span(h.get('colspan'))
        if 'PP' not in cols.values(): continue
        i_fw = next(j for j, l in enumerate(labels) if 'fieldwork' in l)
        i_n = next((j for j, l in enumerate(labels) if 'sample' in l), None)
        row_src = []
        for tr in table.xpath('./tbody/tr|./tr'):
            ids = [x.lstrip('#') for x in tr.xpath('.//sup//a[starts-with(@href, "#cite_note")]/@href')]
            row_src.append(next((refs[x] for x in ids if x in refs), ''))
        g = F.grid(table, spans=True)
        for ri, r in enumerate(g):
            if len(r) <= max(cols) or not r[0][1] or hasattr(r[0][0], 'tag'): continue   # header rows, subrows
            name = re.sub(r'\s+', ' ', str(r[0][0])).strip()
            if not name or 'election' in name.lower(): continue
            fw = re.sub(r'\s+', ' ', str(r[i_fw][0])).strip()
            d, mon, y = _end(fw)
            if not d or not mon: F.log('sin fecha:', name, fw); continue
            # going down the tables the dates go back in time: a month above the last one means the year before
            if y: year = y
            elif prev is None and (mon, d) > (today.month, today.day): year = today.year - 1
            elif prev and mon > prev and mon - prev > 6: year -= 1
            prev = mon
            try: end = dt.date(y or year, mon, d)
            except ValueError: continue
            parts = [x.strip() for x in name.split('/')]
            if parts[0] in PARTY_INTERNAL or (len(parts) > 1 and parts[-1] in PARTY_INTERNAL): continue
            vals = {k: None for k in F.COLS}
            for j, k in cols.items():
                c0, c1 = r[j][2], r[j][3]
                together = [cols[x] for x in range(c0, c1 + 1) if x in cols]
                if len(together) > 1:                          # one figure for a joint list over several columns
                    if j != c0: continue
                    k = 'SUMAR' if set(together) <= {'FA', 'COMP', 'SUMAR', 'PODEMOS'} else together[0]
                vals[k] = F.num(str(r[j][0]))
            if vals['PP'] is None and vals['PSOE'] is None: continue
            if vals['FA'] is not None or vals['COMP'] is not None: vals['SUMAR'] = None
            n = re.sub(r'\D', '', str(r[i_n][0])) if i_n is not None else ''
            fw_es = re.sub(r'\b(Jan|Apr|Aug|Dec)\b', lambda m: ES_MONTH[m.group(1)], fw)
            polls.append(dict(pollster=name, end=end, fw=fw_es, n=int(n) if n else None, v=vals,
                              src=row_src[ri] if ri < len(row_src) else ''))
    return F.clean(polls)


def match(p, others, days=1):
    """the row of the other source for a poll (same firm, last fieldwork day within ±days), or None"""
    fk = firm_key(p['pollster'])
    cands = [q for q in others if firm_key(q['pollster']) == fk and abs((q['end'] - p['end']).days) <= days]
    return min(cands, key=lambda q: abs((q['end'] - p['end']).days)) if cands else None


def compare(p, others, lang='en español', tol=0.15):
    """('coincide' | 'difiere' | 'no figura', text): PP, PSOE and Vox against the other Wikipedia"""
    q = match(p, others)
    if not q: return 'no figura', f'no figura en la Wikipedia {lang}'
    diffs = [f'{k} {q["v"][k]:g}'.replace('.', ',') for k in CHECK
             if p['v'].get(k) is not None and q['v'].get(k) is not None and abs(p['v'][k] - q['v'][k]) > tol]
    if diffs: return 'difiere', f'{lang}: ' + ', '.join(diffs)
    return 'coincide', 'coincide'
