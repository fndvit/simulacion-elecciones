"""Codificador de cuasi-frases con las categorías del Manifesto Project (MARPOR, v5 con subcategorías).

Se entrena con el corpus anotado por el propio Manifesto Project (datos/programas/<mp_id>_<fecha>.csv, columna
cmp_code), en las lenguas en que están escritos los programas (castellano, catalán, gallego, euskera…).
Modelo: TF-IDF de n-gramas de caracteres + palabras (de la frase y, con menos peso, de su sección) y regresión
logística (SGD). Da la categoría más probable y su probabilidad (`conf`), para revisar las dudosas.

  python3 modelo/decide/codificador.py --evaluar   # validación dejando fuera un partido cada vez
  python3 modelo/decide/codificador.py --entrenar  # guarda datos/decide/codificador.joblib

Si el modelo propio del Manifesto Project (manifestoberta, xlm-roberta en HuggingFace) está disponible en
modelo/decide/manifestoberta/, conviene usarlo en su lugar: está entrenado con todo el corpus internacional.
Este clasificador es la alternativa ligera, sin GPU ni descargas.
"""
import csv, glob, os, re, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'datos')
MODEL = os.path.join(BASE, 'decide', 'codificador.joblib')
SKIP = {'H', 'NA', '', '0', '000', 'nan'}


def corpus(files=None):
    """(textos, secciones, códigos, partido) de los CSV anotados por el Manifesto Project."""
    T, S, Y, G = [], [], [], []
    for f in files or sorted(glob.glob(os.path.join(BASE, 'programas', '[0-9]*_[0-9]*.csv'))):
        mid = os.path.basename(f).split('_')[0]
        sec = ''
        for r in csv.DictReader(open(f, encoding='utf-8')):
            c = (r.get('cmp_code') or '').strip()
            if c == 'H':
                sec = r['text'].strip(); continue
            if c in SKIP: continue
            T.append(r['text'].strip()); S.append(sec); Y.append(c); G.append(mid)
    return T, S, Y, G


def norm(t):
    t = t.lower()
    t = re.sub(r'\d+([.,]\d+)?', ' 0 ', t)
    return t


def _sent(X): return [norm(x[0]) for x in X]
def _sect(X): return [norm(x[1]) for x in X]


def build():
    from sklearn.pipeline import make_pipeline, FeatureUnion
    from sklearn.preprocessing import FunctionTransformer
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import SGDClassifier
    feats = FeatureUnion([
        ('chars', make_pipeline(FunctionTransformer(_sent), TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 5), min_df=2, sublinear_tf=True, max_features=150000))),
        ('words', make_pipeline(FunctionTransformer(_sent), TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=2, sublinear_tf=True))),
        ('section', make_pipeline(FunctionTransformer(_sect), TfidfVectorizer(analyzer='word', min_df=2, sublinear_tf=True))),
    ], transformer_weights={'chars': 1.0, 'words': 0.6, 'section': 0.3})
    return make_pipeline(feats, SGDClassifier(loss='log_loss', alpha=2e-6, max_iter=30, tol=1e-4, n_jobs=-1, random_state=1))


def entrenar():
    import joblib
    T, S, Y, _ = corpus()
    m = build(); m.fit(list(zip(T, S)), Y)
    joblib.dump(m, MODEL)
    print(f'codificador entrenado con {len(T)} frases, {len(set(Y))} categorías → {MODEL}')
    return m


def cargar():
    import joblib
    return joblib.load(MODEL) if os.path.exists(MODEL) else entrenar()


def codificar(m, textos, secciones):
    P = m.predict_proba(list(zip(textos, secciones)))
    k = P.argmax(1)
    return [m.classes_[i] for i in k], P.max(1)


def evaluar():
    """Dejando fuera un programa cada vez: acierto de la categoría exacta, del dominio (primer dígito) y del sentido
    en los pares que usa direccion.py."""
    from collections import Counter
    T, S, Y, G = corpus()
    X = list(zip(T, S)); Y = np.array(Y); G = np.array(G)
    res = []
    for g in sorted(set(G)):
        tr, te = G != g, G == g
        m = build(); m.fit([x for x, b in zip(X, tr) if b], Y[tr])
        y, conf = codificar(m, [t for t, b in zip(T, te) if b], [s for s, b in zip(S, te) if b])
        y = np.array(y)
        exact = (y == Y[te]).mean(); dom = np.mean([a[0] == b[0] for a, b in zip(y, Y[te])])
        hi = conf >= 0.5
        res.append((g, te.sum(), exact, dom, hi.mean(), (y[hi] == Y[te][hi]).mean() if hi.any() else 0))
        print(f'{g}: n={te.sum():5}  exacta {exact:.2f}  dominio {dom:.2f}  conf≥0,5 en {hi.mean():.0%} con exacta {res[-1][5]:.2f}', flush=True)
    n = sum(r[1] for r in res)
    print(f'TOTAL ponderado: exacta {sum(r[1]*r[2] for r in res)/n:.2f}  dominio {sum(r[1]*r[3] for r in res)/n:.2f}')


if __name__ == '__main__':
    if '--evaluar' in sys.argv: evaluar()
    else: entrenar()
