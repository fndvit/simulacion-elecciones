"""Geographic seat map: every constituency split into as many cells as seats with a centroidal
Voronoi tessellation (k-means seeds, cells clipped to the province). Each cell is paired with one
hexagon of the cartogram (hex.json) so the app can morph one map into the other.

Output: datos/vor.json
  cells[i]  -> for hexagon i of hex.json: d (SVG path of the cell), ring (N points of its largest part,
               clockwise from the top, for the morph), c (centroid)
  prov[id]  -> outline path; ca -> community borders; sel[id] -> outline for the selection
  box       -> [x0, y0, x1, y1] of the map in the cartogram's coordinate space
Canarias is moved into the cartogram's inset box; Ceuta and Melilla, too small to see, become a dot.
"""
import json, os, math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon, MultiPoint, Point, box
from shapely.ops import unary_union, voronoi_diagram
from shapely.affinity import affine_transform
from scipy.cluster.vq import kmeans2
from scipy.optimize import linear_sum_assignment

D = os.path.join(os.path.dirname(__file__), '..', 'datos' if os.path.isdir(os.path.join(os.path.dirname(__file__), '..', 'datos')) else 'data')
polys = json.load(open(os.path.join(D, 'proj_polys.json')))
app = json.load(open(os.path.join(D, 'app_data.json')))
hexd = json.load(open(os.path.join(D, 'hex.json')))
R, HEX = hexd['R'], hexd['hexes']
SEATS = {p['id']: p['seats'] for p in app['prov']}
CA = {p['id']: p['ca'] for p in app['prov']}
NRING = 30
rng = np.random.default_rng(29)

def geom(k):
    g = MultiPolygon([Polygon(p[0], p[1:]) for p in polys[k]]).buffer(0)
    # drop islets too small to read (keeps every island of Baleares/Canarias that matters)
    parts = list(g.geoms) if g.geom_type == 'MultiPolygon' else [g]
    keep = [p for p in parts if p.area > max(0.004 * g.area, 0.5)] or [max(parts, key=lambda p: p.area)]
    return unary_union(keep).simplify(1.4, preserve_topology=True)

G = {k: geom(k) for k in polys}

# Canarias -> the cartogram's inset box (uniform scale, centred)
def hexbox(ids):
    xs = [h['x'] for h in HEX if h['id'] in ids]; ys = [h['y'] for h in HEX if h['id'] in ids]
    return min(xs) - R, min(ys) - R, max(xs) + R, max(ys) + R
can = unary_union([G['35'], G['38']])
bx0, by0, bx1, by1 = can.bounds
# the geographic map has room in the Atlantic, south-west of the peninsula: a larger inset than the cartogram's
CANBOX = (-20, 880, 430, 1100)
s = min((CANBOX[2] - CANBOX[0]) / (bx1 - bx0), (CANBOX[3] - CANBOX[1]) / (by1 - by0))
tx = (CANBOX[0] + CANBOX[2]) / 2 - s * (bx0 + bx1) / 2; ty = (CANBOX[1] + CANBOX[3]) / 2 - s * (by0 + by1) / 2
for k in ('35', '38'):
    G[k] = affine_transform(G[k], [s, 0, 0, s, tx, ty])
# Ceuta, Melilla: a dot at their real position
for k in ('51', '52'):
    G[k] = G[k].centroid.buffer(R * 0.62, quad_segs=8)

def sample(g, n):
    x0, y0, x1, y1 = g.bounds
    out = []
    while len(out) < n:
        P = rng.uniform([x0, y0], [x1, y1], size=(n, 2))
        out += [p for p in P if g.contains(Point(p))]
    return np.array(out[:n])

def cells_for(k):
    g, n = G[k], SEATS[k]
    if n == 1:
        return [g]
    pts = sample(g, 4000)
    best = None
    for seed in range(4):
        cent, lab = kmeans2(pts, n, minit='++', seed=seed * 7 + 1, iter=60)
        if len(set(lab)) == n:
            inertia = ((pts - cent[lab]) ** 2).sum()
            if best is None or inertia < best[0]: best = (inertia, cent)
    cent = best[1]
    vd = voronoi_diagram(MultiPoint([tuple(c) for c in cent]), envelope=box(*g.buffer(50).bounds))
    out = []
    for c in cent:
        cell = next(v for v in vd.geoms if v.contains(Point(c)))
        out.append(cell.intersection(g))
    return out

def largest(g):
    return max(g.geoms, key=lambda p: p.area) if g.geom_type == 'MultiPolygon' else g

def ring(g, n=NRING):
    """n points evenly spaced along the exterior of the largest part, clockwise (y down), from the top."""
    p = largest(g).exterior
    coords = np.array(p.coords)
    # screen clockwise (y grows downwards) == mathematically counter-clockwise in y-up
    area = 0.5 * np.sum(coords[:-1, 0] * coords[1:, 1] - coords[1:, 0] * coords[:-1, 1])
    if area < 0: p = type(p)(coords[::-1])
    L = p.length
    pts = np.array([p.interpolate(L * i / n).coords[0] for i in range(n)])
    c = np.array(largest(g).centroid.coords[0])
    # start at the point closest to "straight up" from the centroid
    ang = np.arctan2(pts[:, 0] - c[0], -(pts[:, 1] - c[1]))
    i0 = int(np.argmin(np.abs(ang)))
    return np.roll(pts, -i0, axis=0)

def path(g):
    parts = list(g.geoms) if g.geom_type == 'MultiPolygon' else [g]
    d = ''
    for p in parts:
        if p.is_empty or p.geom_type != 'Polygon': continue
        for r in [p.exterior, *p.interiors]:
            cs = np.array(r.coords)[:-1]
            d += 'M' + 'L'.join(f'{x:.0f},{y:.0f}' for x, y in cs) + 'Z'
    return d

def norm(P, ref):
    P = np.asarray(P, float); m = ref.mean(0); s = np.sqrt(((ref - m) ** 2).sum(1).mean()) or 1
    return (P - m) / s

cells_out = [None] * len(HEX)
for k in polys:
    cs = cells_for(k)
    hidx = [i for i, h in enumerate(HEX) if h['id'] == k]
    assert len(hidx) == len(cs) == SEATS[k], (k, len(hidx), len(cs))
    hp = np.array([[HEX[i]['x'], HEX[i]['y']] for i in hidx])
    gc = np.array([c.centroid.coords[0] for c in cs])
    cost = ((norm(hp, hp)[:, None, :] - norm(gc, gc)[None, :, :]) ** 2).sum(-1)
    ri, ci = linear_sum_assignment(cost)
    for a, b in zip(ri, ci):
        c = cs[b]
        cells_out[hidx[a]] = {'d': path(c), 'ring': [[round(x), round(y)] for x, y in ring(c)],
                              'c': [round(v, 1) for v in largest(c).centroid.coords[0]]}

prov = {k: path(G[k]) for k in G}
cas = {}
for k in G: cas.setdefault(CA[k], []).append(G[k].buffer(0.3, join_style=2))
ca = ''.join(path(unary_union(v).buffer(-0.3, join_style=2).simplify(1.4)) for v in cas.values())
allg = unary_union(list(G.values()))
x0, y0, x1, y1 = allg.bounds
json.dump({'cells': cells_out, 'prov': prov, 'ca': ca, 'box': [round(x0), round(y0), round(x1), round(y1)], 'canBox': [round(v) for v in (tx + s * bx0 - 14, ty + s * by0 - 14, tx + s * bx1 + 14, ty + s * by1 + 14)], 'n': NRING},
          open(os.path.join(D, 'vor.json'), 'w'), separators=(',', ':'))
print('ok', sum(1 for c in cells_out if c), 'cells; box', [round(v) for v in (x0, y0, x1, y1)],
      'kB', os.path.getsize(os.path.join(D, 'vor.json')) // 1024)
