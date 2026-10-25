"""
Cartograma de difusión de las provincias, con el área proporcional a los escaños (método de flujo rápido de
Gastner, Seguy y More, 2018, sucesor del de Gastner y Newman, 2004). Es el paso previo de la técnica de
Ralph Straumann para hacer un cartograma de hexágonos: primero se deforma el mapa según el peso de cada
provincia y después se le superpone la rejilla de hexágonos. Aquí sirve de referencia en el editor del
cartograma: está escalado para que cada escaño ocupe el área de un hexágono.

Entrada: datos/vor.json (contornos de provincia y de comunidad en el espacio del cartograma, con Canarias en
su recuadro) y los escaños de datos/app_data.json. Salida: datos/cartograma.json {prov: {id: d}, ca: d, error}.
"""
import json, os, re
import numpy as np
from scipy.fft import dctn, idctn
from scipy.ndimage import map_coordinates
from matplotlib.path import Path

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
L = 512                    # rejilla de densidad
PAD = 0.35                 # margen de mar alrededor (fracción del tamaño)


def parse(d):
    """'M..L..Z' → lista de anillos [(n,2) array, cerrado?]"""
    out = []
    for part in re.findall(r'M[^M]*', d):
        closed = part.rstrip().endswith('Z')
        pts = np.array([[float(a), float(b)] for a, b in re.findall(r'(-?[\d.]+),(-?[\d.]+)', part)])
        if len(pts): out.append((pts, closed))
    return out


def densify(pts, closed, step):
    P = np.vstack([pts, pts[:1]]) if closed else pts
    out = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        n = max(1, int(np.ceil(np.hypot(*(b - a)) / step)))
        for k in range(1, n + 1): out.append(a + (b - a) * k / n)
    out = np.array(out)
    return out[:-1] if closed else out


def area(r):
    x, y = r[:, 0], r[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def flow(rings, ids, seats, frame, extra, tol=0.02):
    """one flow-based pass on grid coordinates: returns the moved rings and moved extra points"""
    (x0, y0, x1, y1) = frame
    sx, sy = (L - 1) / (x1 - x0), (L - 1) / (y1 - y0)
    tog = lambda P: np.c_[(P[:, 0] - x0) * sx, (P[:, 1] - y0) * sy]
    fromg = lambda G: np.c_[G[:, 0] / sx + x0, G[:, 1] / sy + y0]
    # density: seats / area inside each province, the land mean at sea
    gy, gx = np.mgrid[0:L, 0:L]
    cells = np.c_[gx.ravel() + 0.5, gy.ravel() + 0.5]
    rho = np.full(L * L, np.nan)
    A = {}
    for r, pid in zip(rings, ids): A[pid] = A.get(pid, 0) + area(tog(r))
    for r, pid in zip(rings, ids):
        inside = Path(tog(r)).contains_points(cells)
        rho[inside] = seats[pid] / A[pid]
    land = ~np.isnan(rho)
    rho[~land] = np.sum([seats[p] for p in A]) / sum(A.values())
    rho = rho.reshape(L, L)
    # diffusion in Fourier (cosine) space; v = −∇ρ/ρ
    R0 = dctn(rho, type=2, norm='ortho')
    ky, kx = np.meshgrid(np.arange(L), np.arange(L), indexing='ij')
    K2 = (np.pi ** 2) * (kx ** 2 + ky ** 2) / L ** 2

    def vel(P, t):
        rt = idctn(R0 * np.exp(-K2 * t), type=2, norm='ortho')
        gyr, gxr = np.gradient(rt)
        c = [P[:, 1] - 0.5, P[:, 0] - 0.5]
        r_ = map_coordinates(rt, c, order=1, mode='nearest')
        return np.c_[-map_coordinates(gxr, c, order=1, mode='nearest') / r_, -map_coordinates(gyr, c, order=1, mode='nearest') / r_]

    lens = [len(r) for r in rings]
    P = tog(np.vstack(rings + [extra]))
    t, dt = 0.0, 1e-2
    while t < 1e4:
        v0 = vel(P, t)
        pe = P + v0 * dt
        pc = P + 0.5 * (v0 + vel(pe, t + dt)) * dt
        if np.abs(pc - pe).max() > tol and dt > 1e-4: dt /= 2; continue
        P, t = pc, t + dt
        dt *= 1.25
        if np.abs(v0).max() * dt < 1e-3 and t > 50: break
    P = fromg(P)
    out, k = [], 0
    for n in lens: out.append(P[k:k + n]); k += n
    return out, P[k:]


def build():
    vor = json.load(open(os.path.join(D, 'vor.json')))
    app = json.load(open(os.path.join(D, 'app_data.json')))
    hexd = json.load(open(os.path.join(D, 'hex.json')))
    seats = {p['id']: p['seats'] for p in app['prov']}
    rings, ids = [], []
    for pid, d in vor['prov'].items():
        for pts, closed in parse(d):
            if len(pts) >= 3: rings.append(densify(pts, True, 4)); ids.append(pid)
    ca = [(densify(p, c, 4), c) for p, c in parse(vor['ca'])]
    capts = np.vstack([p for p, _ in ca])
    x0, y0, x1, y1 = vor['box']
    w, h = x1 - x0, y1 - y0
    frame = (x0 - PAD * w, y0 - PAD * h, x1 + PAD * w, y1 + PAD * h)
    for it in range(4):                       # a few passes shrink the remaining area error
        rings, capts = flow(rings, ids, seats, frame, capts)
        A = {}
        for r, pid in zip(rings, ids): A[pid] = A.get(pid, 0) + area(r)
        tot = sum(A.values()); err = max(abs(A[p] / tot - seats[p] / 350) / (seats[p] / 350) for p in A)
        print(f'pasada {it + 1}: error máximo de área {err:.1%}')
    # scale so one seat = one hexagon of area, centred on the hexagons
    R = hexd['R']; hexA = 3 * np.sqrt(3) / 2 * R * R
    s = np.sqrt(350 * hexA / tot)
    allp = np.vstack(rings)
    cx, cy = allp[:, 0].mean(), allp[:, 1].mean()
    hx = np.mean([q['x'] for q in hexd['hexes']]); hy = np.mean([q['y'] for q in hexd['hexes']])
    tr = lambda P: np.c_[(P[:, 0] - cx) * s + hx, (P[:, 1] - cy) * s + hy]
    pd = {}
    for r, pid in zip(rings, ids):
        Q = tr(r)
        pd[pid] = pd.get(pid, '') + 'M' + 'L'.join(f'{a:.1f},{b:.1f}' for a, b in Q) + 'Z'
    cad, k = '', 0
    capts = tr(capts)
    for p, c in ca:
        Q = capts[k:k + len(p)]; k += len(p)
        cad += 'M' + 'L'.join(f'{a:.1f},{b:.1f}' for a, b in Q) + ('Z' if c else '')
    out = dict(prov=pd, ca=cad, error=round(float(err), 4), metodo='Gastner–Seguy–More (flujo rápido), áreas ∝ escaños; 1 escaño = 1 hexágono')
    json.dump(out, open(os.path.join(D, 'cartograma.json'), 'w'), separators=(',', ':'))
    return out


if __name__ == '__main__':
    build()
