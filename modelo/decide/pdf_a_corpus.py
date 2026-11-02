"""PDF de un programa electoral → corpus con el formato del Manifesto Project.

  python3 modelo/decide/pdf_a_corpus.py PP            # un partido de programas.json
  python3 modelo/decide/pdf_a_corpus.py --todos       # todos los que tengan PDF

Salida: datos/programas/<PARTIDO>_<edición>.csv con las columnas del corpus del Manifesto Project
(text, text_en, cmp_code, eu_code) más `page` (página del PDF, para citar) y `conf` (probabilidad de la categoría).
Las cabeceras de sección van como cmp_code = H, igual que en el corpus original.

Pasos
 1. Texto por página con pdfplumber, con tamaño y tipo de letra de cada palabra.
 2. Se quitan cabeceras y pies repetidos y los números de página.
 3. Títulos: líneas cortas en letra mayor que el cuerpo (o en negrita y sin punto final) → H.
 4. Párrafos → cuasi-frases, con las reglas del manual de codificación del Manifesto Project en lo que se puede
    automatizar: una frase por unidad; los puntos y coma, los dos puntos que abren una lista y cada viñeta o
    número de una enumeración abren una cuasi-frase nueva; los fragmentos de menos de 4 palabras se unen al anterior.
 5. Cada cuasi-frase se codifica con codificador.py (entrenado con el corpus del Manifesto Project).
Las de `conf` < 0,35 conviene revisarlas a mano si se usan como cita.
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(__file__)
BASE = os.path.join(HERE, '..', '..', 'datos')
CFG = json.load(open(os.path.join(HERE, 'programas.json'), encoding='utf-8'))

BULLET = r'[•●▪■◆◦·\-–—►✓]'
ENUM = r'(\d{1,3}[.)]|[a-z][.)]|[ivx]{1,4}[.)])'


def lines_of(pdf):
    """[(page, y, size, bold, text)] por línea, sin cabeceras/pies repetidos ni números de página."""
    import pdfplumber
    out = []
    with pdfplumber.open(pdf) as doc:
        for pn, page in enumerate(doc.pages, 1):
            H = page.height
            words = page.extract_words(extra_attrs=['size', 'fontname'], keep_blank_chars=False, use_text_flow=True)
            rows = defaultdict(list)
            for w in words:
                rows[round(w['top'] / 2.5)].append(w)
            for k in sorted(rows):
                ws = sorted(rows[k], key=lambda w: w['x0'])
                text = ' '.join(w['text'] for w in ws).strip()
                if not text: continue
                size = Counter(round(w['size'], 1) for w in ws).most_common(1)[0][0]
                bold = sum(('Bold' in w['fontname'] or 'Black' in w['fontname'] or 'Heavy' in w['fontname']) for w in ws) > len(ws) / 2
                out.append(dict(page=pn, y=ws[0]['top'] / H, x=ws[0]['x0'], size=size, bold=bold, text=text))
    # running headers/footers and side markers: short lines (digits removed) repeated on many pages, wherever they are
    npages = max(l['page'] for l in out) if out else 1
    key = lambda l: re.sub(r'\b[IVXL]+\b', '#', re.sub(r'\d+', '#', l['text']))
    pages_of = defaultdict(set)
    for l in out:
        if len(l['text'].split()) <= 6: pages_of[key(l)].add(l['page'])
    rep = {k for k, ps in pages_of.items() if len(ps) >= max(3, npages * 0.15)}
    clean = []
    for l in out:
        k = key(l)
        if k in rep: continue
        if re.fullmatch(r'[#/\s.|·–-]*', k): continue           # page numbers, «/77», lone dots
        clean.append(l)
    return clean


def blocks(lines):
    """Agrupa líneas en títulos y párrafos. Devuelve [(kind, page, text)] con kind 'H' o 'P'."""
    if not lines: return []
    body = Counter(l['size'] for l in lines).most_common(1)[0][0]
    ends = ('.', ':', ';', ',', '?', '!')
    def head(i):
        l = lines[i]; t = l['text']
        if len(t.split()) > 18 or re.match(rf'^({BULLET}|{ENUM})\s', t) or t[:1].islower(): return False
        if l['size'] >= body * 1.18: return True
        if not l['bold'] or t.endswith(ends) or len(t.split()) > 12: return False
        # a bold line is a title only if it stands alone: the text before it closed a sentence (or was a title)
        # and the line after it is not bold body text continuing the same sentence
        prev = lines[i - 1] if i else None
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        prev_ok = prev is None or prev['text'].endswith(ends) or prev['size'] >= body * 1.18 or prev['bold']
        nxt_ok = nxt is None or not nxt['text'][:1].islower()
        return prev_ok and nxt_ok
    out, cur, prev = [], None, None
    for i, l in enumerate(lines):
        t = l['text']
        is_head = head(i)
        starts_item = re.match(rf'^({BULLET}|{ENUM})\s', t) is not None
        new_par = (cur is None or prev is None or is_head != (cur[0] == 'H') or starts_item or l['page'] != prev['page'] and cur[2].endswith('.')
                   or abs(l['size'] - prev['size']) > 0.6 or (cur[0] == 'P' and cur[2].endswith(('.', ':')) and l['x'] - prev['x'] > 8))
        if new_par:
            if cur: out.append(cur)
            cur = ['H' if is_head else 'P', l['page'], t]
        else:
            # join lines, undoing hyphenation at line ends
            cur[2] = cur[2][:-1] + t if re.search(r'[a-záéíóúñç]-$', cur[2]) and t[:1].islower() else cur[2] + ' ' + t
        prev = l
    out.append(cur)
    # consecutive title lines form one title
    merged = []
    for b in out:
        if merged and b[0] == 'H' and merged[-1][0] == 'H' and merged[-1][1] == b[1]: merged[-1][2] += ' ' + b[2]
        else: merged.append(b)
    return merged


SPLIT = re.compile(r'(?<=[.!?;])\s+(?=[«"“(¿¡]?[A-ZÁÉÍÓÚÑÇÀÈÒ0-9•●▪■–—-])|(?<=:)\s+(?=' + BULLET + r'|' + ENUM + r'\s)|\s+(?=' + BULLET + r'\s)')


def quasi(text):
    """Párrafo → cuasi-frases."""
    parts = [p.strip() for p in SPLIT.split(text) if p and p.strip()]
    out = []
    for p in parts:
        p = re.sub(rf'^{BULLET}\s*', '', p).strip()
        if not p: continue
        if out and len(p.split()) < 4: out[-1] += ' ' + p
        else: out.append(p)
    return out


def procesar(party, pdf=None, edicion=None):
    c = CFG['partidos'][party]
    pdf = pdf or os.path.join(BASE, 'programas', 'pdf', c['pdf'])
    edicion = edicion or CFG['edicion']
    if not os.path.exists(pdf): raise SystemExit(f'falta {pdf}')
    rows, secs = [], []
    sec = ''
    for kind, page, text in blocks(lines_of(pdf)):
        text = re.sub(r'\s+', ' ', text).strip()
        if re.search(r'\.{5,}', text) or len(re.sub(r'[^\wáéíóúñç]', '', text)) < 3: continue   # índice, restos
        if kind == 'H':
            sec = text; rows.append(dict(text=text, page=page, cmp_code='H')); continue
        for q in quasi(text):
            rows.append(dict(text=q, page=page, cmp_code=None)); secs.append((len(rows) - 1, sec))
    from codificador import cargar, codificar
    m = cargar()
    idx = [i for i, _ in secs]
    codes, conf = codificar(m, [rows[i]['text'] for i in idx], [s for _, s in secs])
    for i, cd, cf in zip(idx, codes, conf):
        rows[i]['cmp_code'] = cd; rows[i]['conf'] = round(float(cf), 3)
    out = os.path.join(BASE, 'programas', f"{party}_{edicion}.csv")
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['text', 'text_en', 'cmp_code', 'eu_code', 'page', 'conf'])
        w.writeheader()
        for r in rows: w.writerow(dict(text=r['text'], text_en='', cmp_code=r['cmp_code'], eu_code='', page=r['page'], conf=r.get('conf', '')))
    n = sum(1 for r in rows if r['cmp_code'] != 'H')
    low = sum(1 for r in rows if r.get('conf', 1) < 0.35)
    print(f'{party}: {n} cuasi-frases, {len(rows) - n} títulos, {low} dudosas (conf < 0,35) → {out}')
    return out


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    todos = [p for p, c in CFG['partidos'].items() if c.get('pdf') and os.path.exists(os.path.join(BASE, 'programas', 'pdf', c['pdf']))]
    a = sys.argv[1:]
    opt = lambda k: a[a.index(k) + 1] if k in a else None   # --pdf ruta --edicion AAAAMM (pruebas)
    if '--todos' in a:
        for p in todos: procesar(p)
    else:
        procesar(a[0], opt('--pdf'), opt('--edicion'))
