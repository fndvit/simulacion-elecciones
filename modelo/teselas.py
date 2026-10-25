"""
Propuestas automáticas de cartograma de hexágonos (un hexágono por escaño), al estilo de los cartogramas
de mosaico (Cano, Buchin, Castermans, Pieterse, Sonke y Speckmann, 2015) y de los mapas de teselas
generados (McNeill y Hale, 2017):

1. Mapa de partida: el real, deformado en parte hacia el cartograma de difusión por escaños
   (cartograma.py). α = 0 es el mapa real; α = 1, el cartograma completo. Cuanto menos α, más se parece cada
   provincia a sí misma, y más hexágonos hay que mover después.
2. Se escala para que su superficie sea la de 350 hexágonos y se le superpone la rejilla de la app.
   Cada hexágono es de la provincia en la que cae su centro.
3. Ajuste: mientras alguna provincia tenga hexágonos de más o de menos, se busca el camino más corto entre
   una con falta y otra con sobra (o el mar), a través de provincias vecinas, y cada provincia del camino
   cede a la siguiente un hexágono de su frontera común. La que cede elige el hexágono más alejado de su
   centro y que no la parte en dos; la que recibe, el más cercano a su forma de partida. Así el recuento
   queda exacto y las provincias siguen enteras (salvo los archipiélagos).

Uso: python3 teselas.py  →  datos/teselas.json {alfa: {R, hexes}} y lo imprime resumido.
"""
import collections, json, math, os, sys
import numpy as np
from matplotlib.path import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cartograma as CG

D = CG.D
ISLANDS = {'07', '35', '38'}


def base_maps():
    """rings (real) and their cartogram positions, same vertices"""
    vor = json.load(open(os.path.join(D, 'vor.json')))
    app = json.load(open(os.path.join(D, 'app_data.json')))
    seats = {p['id']: p['seats'] for p in app['prov']}
    rings, ids = [], []
    for pid, d in vor['prov'].items():
        for pts, closed in CG.parse(d):
            if len(pts) >= 3: rings.append(CG.densify(pts, True, 4)); ids.append(pid)
    x0, y0, x1, y1 = vor['box']; w, h = x1 - x0, y1 - y0
    frame = (x0 - CG.PAD * w, y0 - CG.PAD * h, x1 + CG.PAD * w, y1 + CG.PAD * h)
    moved = rings
    for _ in range(4):
        moved, _e = CG.flow(moved, ids, seats, frame, np.zeros((0, 2)))
    return rings, moved, ids, seats


def grid(R):
    W, H = math.sqrt(3) * R, 1.5 * R
    pos = lambda r, c: (-200 + c * W + (W / 2 if r % 2 else 0), -200 + r * H)
    return W, H, pos


def nbs(r, c):
    e = r % 2 == 0
    return [(r, c + 1), (r + 1, c) if e else (r + 1, c + 1), (r + 1, c - 1) if e else (r + 1, c), (r, c - 1),
            (r - 1, c - 1) if e else (r - 1, c), (r - 1, c) if e else (r - 1, c + 1)]


def tile(alpha, rings0, rings1, ids, seats, R, hex_centre):
    W, H, pos = grid(R)
    hexA = 3 * math.sqrt(3) / 2 * R * R
    rings = [(1 - alpha) * a + alpha * b for a, b in zip(rings0, rings1)]
    tot = sum(CG.area(r) for r in rings)
    s = math.sqrt(350 * hexA / tot)
    allp = np.vstack(rings); cx, cy = allp.mean(0)
    rings = [np.c_[(r[:, 0] - cx) * s + hex_centre[0], (r[:, 1] - cy) * s + hex_centre[1]] for r in rings]
    # province centroid of its starting shape (largest part), for choosing tiles
    cen = {}
    for r, pid in zip(rings, ids):
        a = CG.area(r)
        if pid not in cen or a > cen[pid][1]: cen[pid] = (r.mean(0), a)
    cen = {k: v[0] for k, v in cen.items()}
    # initial assignment: centre of each hexagon inside a province
    allp = np.vstack(rings)
    rmin = int((allp[:, 1].min() + 200) / H) - 2; rmax = int((allp[:, 1].max() + 200) / H) + 2
    cmin = int((allp[:, 0].min() + 200) / W) - 2; cmax = int((allp[:, 0].max() + 200) / W) + 2
    cells = [(r, c) for r in range(rmin, rmax + 1) for c in range(cmin, cmax + 1)]
    P = np.array([pos(r, c) for r, c in cells])
    owner = {}
    for ring, pid in zip(rings, ids):
        inside = Path(ring).contains_points(P)
        for k in np.nonzero(inside)[0]: owner.setdefault(cells[k], pid)
    # every province gets at least the hexagon nearest its centre
    for pid in seats:
        if not any(v == pid for v in owner.values()):
            best = min(cells, key=lambda rc: (pos(*rc)[0] - cen[pid][0]) ** 2 + (pos(*rc)[1] - cen[pid][1]) ** 2 + (1e9 if rc in owner else 0))
            owner[best] = pid
    box = (rmin - 3, rmax + 3, cmin - 3, cmax + 3)

    def exterior():
        start = (box[0], box[2]); seen = {start}; st = [start]
        while st:
            x = st.pop()
            for y in nbs(*x):
                if box[0] <= y[0] <= box[1] and box[2] <= y[1] <= box[3] and y not in owner and y not in seen: seen.add(y); st.append(y)
        return seen

    # keep each mainland province's largest connected piece; the rest goes back to the pool
    for pid in seats:
        if pid in ISLANDS: continue
        mine = {k for k, v in owner.items() if v == pid}; comps = []
        while mine:
            k0 = mine.pop(); comp = {k0}; st = [k0]
            while st:
                x = st.pop()
                for y in nbs(*x):
                    if y in mine: mine.discard(y); comp.add(y); st.append(y)
            comps.append(comp)
        for comp in sorted(comps, key=len)[:-1]:
            for k in comp: del owner[k]
    # holes inside the land (not reachable from the open sea) go to the neighbour that owns most of their edge
    ext = exterior()
    for r in range(box[0], box[1] + 1):
        for c in range(box[2], box[3] + 1):
            k = (r, c)
            if k in owner or k in ext: continue
            around = collections.Counter(owner[y] for y in nbs(*k) if y in owner)
            if around: owner[k] = around.most_common(1)[0][0]
    count = collections.Counter(owner.values())
    d2 = lambda rc, pid: (pos(*rc)[0] - cen[pid][0]) ** 2 + (pos(*rc)[1] - cen[pid][1]) ** 2

    def connected_without(pid, rc):
        if pid in ISLANDS: return True
        mine = [k for k, v in owner.items() if v == pid and k != rc]
        if not mine: return False
        seen = {mine[0]}; st = [mine[0]]
        while st:
            x = st.pop()
            for y in nbs(*x):
                if y != rc and owner.get(y) == pid and y not in seen: seen.add(y); st.append(y)
        return len(seen) == len(mine)

    def border(a, b):
        """cells of a (None = sea) touching b"""
        out = set()
        for k, v in list(owner.items()) if a is not None else []:
            if v == a and any(owner.get(y) == b for y in nbs(*k)): out.add(k)
        if a is None:   # sea cells touching b
            for k, v in owner.items():
                if v == b:
                    for y in nbs(*k):
                        if y not in owner: out.add(y)
        return out

    def give(a, b):
        """a (province or None=sea) hands one cell to b (province or None=sea); True if done"""
        if b is None:   # a drops a coastal cell into the sea
            ext = exterior()
            cand = [k for k, v in owner.items() if v == a and any(y in ext for y in nbs(*k)) and connected_without(a, k)]
            if not cand: return False
            k = max(cand, key=lambda k: d2(k, a)); del owner[k]; return True
        cand = border(a, b)
        if a is not None: cand = [k for k in cand if connected_without(a, k)]
        if not cand: return False
        k = min(cand, key=lambda k: d2(k, b) - (0.5 * d2(k, a) if a is not None else 0))
        owner[k] = b; return True

    def adj(a):
        """neighbouring regions of province a, the sea as None"""
        out = set()
        for k, v in owner.items():
            if v != a: continue
            for y in nbs(*k):
                o = owner.get(y, None)
                if o != a: out.add(o)
        return out

    banned = set()

    def route(src, want, sea=False):
        """BFS through neighbouring regions from src to a region satisfying want(region), avoiding banned hops;
        the sea is a possible end only when `sea`"""
        prev = {src: src}; dq = collections.deque([src])
        while dq:
            x = dq.popleft()
            for y in sorted(adj(x), key=lambda v: (v is None, v or '')):
                if y in prev or (x, y) in banned or (y, x) in banned: continue
                if y is None and not sea: continue
                prev[y] = x
                if want(y): 
                    path = [y]
                    while path[-1] != src: path.append(prev[path[-1]])
                    return path[::-1]          # src … y
                if y is not None: dq.append(y)
        return None

    for _ in range(5000):
        count = collections.Counter(owner.values())
        err = {p: count[p] - seats[p] for p in seats}
        need = sorted([p for p in seats if err[p] < 0], key=lambda p: err[p])
        extra = sorted([p for p in seats if err[p] > 0], key=lambda p: -err[p])
        if not need and not extra: break
        moved = False
        for q in need:                         # pull a cell towards q from a surplus or the sea
            path = route(q, lambda y: y is not None and err.get(y, 0) > 0) or route(q, lambda y: y is None or err.get(y, 0) > 0, sea=True)
            if not path: continue
            for i in range(len(path) - 1):     # q ← path[1] ← path[2] … (receiving end first)
                if not give(path[i + 1], path[i]): banned.add((path[i + 1], path[i])); break
            else: moved = True
            if moved: break
        if not moved:
            for p in extra:                    # push a cell from p towards a deficit or the sea
                path = route(p, lambda y: y is not None and err.get(y, 0) < 0) or route(p, lambda y: y is None or err.get(y, 0) < 0, sea=True)
                if not path: continue
                for i in range(len(path) - 1):
                    if not give(path[i], path[i + 1]): banned.add((path[i], path[i + 1])); break
                else: moved = True
                if moved: break
        if moved: banned.clear()
        elif not banned: break
    count = collections.Counter(owner.values())
    bad = {p: count[p] - seats[p] for p in seats if count[p] != seats[p]}
    hexes = [dict(id=v, x=round(pos(r, c)[0], 2), y=round(pos(r, c)[1], 2), r=r, c=c) for (r, c), v in sorted(owner.items())]
    return dict(R=R, hexes=hexes), bad, {k: v.tolist() for k, v in []}, rings, ids


def outline(rings, ids):
    out = {}
    for r, pid in zip(rings, ids):
        out[pid] = out.get(pid, '') + 'M' + 'L'.join(f'{a:.1f},{b:.1f}' for a, b in r[::2]) + 'Z'
    return out


if __name__ == '__main__':
    hexd = json.load(open(os.path.join(D, 'hex.json')))
    R = hexd['R']
    centre = (np.mean([q['x'] for q in hexd['hexes']]), np.mean([q['y'] for q in hexd['hexes']]))
    rings0, rings1, ids, seats = base_maps()
    res = {}
    for a in (0.0, 0.35, 0.7, 1.0):
        lay, bad, _, rings, _ids = tile(a, rings0, rings1, ids, seats, R, centre)
        res[str(a)] = dict(layout=lay, outline=outline(rings, ids), bad=bad)
        print(f'α={a}: {len(lay["hexes"])} hexágonos, descuadres {bad}')
    json.dump(res, open(os.path.join(D, 'teselas.json'), 'w'), separators=(',', ':'))
