import json, os, math
import numpy as np
from shapely.geometry import shape, Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from scipy.optimize import linear_sum_assignment
D = os.path.join(os.path.dirname(__file__), '..', 'datos')
polys = json.load(open(os.path.join(D, 'proj_polys.json')))
app = json.load(open(os.path.join(D, 'app_data.json')))
SEATS = {p['id']: p['seats'] for p in app['prov']}
CA = {p['id']: p['ca'] for p in app['prov']}
OFF = {'07', '35', '38', '51', '52'}
geom = {k: MultiPolygon([Polygon(p[0], p[1:]) for p in v]).buffer(0) for k, v in polys.items()}
MAIN = [k for k in geom if k not in OFF]
land = unary_union([geom[k] for k in MAIN]).buffer(0)
N = sum(SEATS[k] for k in MAIN)
SQ3 = math.sqrt(3)
def grid(r, x0=-200, x1=1200, y0=-200, y1=1200):
    cells = []
    for row in range(int((y1 - y0) / (1.5 * r)) + 1):
        y = y0 + row * 1.5 * r
        for col in range(int((x1 - x0) / (SQ3 * r)) + 1):
            x = x0 + col * SQ3 * r + (row % 2) * SQ3 * r / 2
            cells.append((row, col, x, y))
    return cells
def inside(r):
    return [c for c in grid(r) if land.contains(Point(c[2], c[3]))]
lo, hi = 5.0, 60.0
for _ in range(40):
    mid = (lo + hi) / 2
    if len(inside(mid)) > N: lo = mid
    else: hi = mid
R = lo
cells = inside(R)
allc = grid(R)
inset = set((c[0], c[1]) for c in cells)
# adjust count to exactly N
if len(cells) > N:
    cells.sort(key=lambda c: -land.exterior.distance(Point(c[2], c[3])) if land.geom_type == 'Polygon' else -land.boundary.distance(Point(c[2], c[3])))
    cells = cells[:N]
elif len(cells) < N:
    extra = sorted([c for c in allc if (c[0], c[1]) not in inset], key=lambda c: land.distance(Point(c[2], c[3])))
    cells += extra[:N - len(cells)]
print('R', round(R, 2), 'cells', len(cells), 'N', N)
pts = np.array([[c[2], c[3]] for c in cells])
geo_c = {k: np.array(geom[k].centroid.coords[0]) for k in MAIN}
sites = dict(geo_c)
slots = [k for k in MAIN for _ in range(SEATS[k])]
import sys
ALPHA = float(sys.argv[1]) if len(sys.argv) > 1 else 0.6
for it in range(40):
    S = np.array([sites[k] for k in slots])
    cost = ((pts[:, None, :] - S[None, :, :]) ** 2).sum(-1)
    ri, ci = linear_sum_assignment(cost)
    owner = {int(i): slots[j] for i, j in zip(ri, ci)}
    for k in MAIN:
        m = pts[[i for i, o in owner.items() if o == k]].mean(0)
        sites[k] = ALPHA * geo_c[k] + (1 - ALPHA) * m
# contiguity check
idx = {(c[0], c[1]): i for i, c in enumerate(cells)}
def nbrs(row, col):
    if row % 2 == 0: d = [(0,-1),(0,1),(-1,-1),(-1,0),(1,-1),(1,0)]
    else: d = [(0,-1),(0,1),(-1,0),(-1,1),(1,0),(1,1)]
    return [(row + a, col + b) for a, b in d]
def components(k):
    mine = {i for i, o in owner.items() if o == k}
    seen, comps = set(), 0
    for s in mine:
        if s in seen: continue
        comps += 1; st = [s]; seen.add(s)
        while st:
            i = st.pop(); c = cells[i]
            for n in nbrs(c[0], c[1]):
                j = idx.get(n)
                if j is not None and j in mine and j not in seen: seen.add(j); st.append(j)
    return comps
def comps_of(k):
    mine = {i for i, o in owner.items() if o == k}; seen = set(); out = []
    for s0 in mine:
        if s0 in seen: continue
        comp = {s0}; st = [s0]; seen.add(s0)
        while st:
            i = st.pop(); c = cells[i]
            for n in nbrs(c[0], c[1]):
                j = idx.get(n)
                if j is not None and j in mine and j not in seen: seen.add(j); comp.add(j); st.append(j)
        out.append(comp)
    return sorted(out, key=len, reverse=True)
for rep in range(200):
    changed = False
    for k in MAIN:
        cs = comps_of(k)
        if len(cs) < 2: continue
        main = cs[0]
        for comp in cs[1:]:
            for i in comp:
                # give stray cell i to a neighbouring province q; take from q a cell adjacent to k's main body
                qs = [owner[idx[n]] for n in nbrs(*cells[i][:2]) if idx.get(n) is not None and owner[idx[n]] != k]
                done = False
                for q in qs:
                    cand = [idx[n] for m in main for n in nbrs(*cells[m][:2]) if idx.get(n) is not None and owner[idx[n]] == q]
                    cand.sort(key=lambda j: ((pts[j] - pts[i]) ** 2).sum())
                    for j in cand:
                        owner[i], owner[j] = q, k
                        if len(comps_of(q)) <= 1 and len(comps_of(k)) < len(cs): done = True; break
                        owner[i], owner[j] = k, q
                    if done: break
                if done: changed = True; break
            if changed: break
    if not changed: break
bad = {k: components(k) for k in MAIN if components(k) > 1}
print('non-contiguous', bad)
# off-mainland
taken = {(c[0], c[1]) for c in cells}
def nearest_free(pt, n, avoid_adj=True):
    cand = sorted([c for c in allc if (c[0], c[1]) not in taken], key=lambda c: (c[2] - pt[0]) ** 2 + (c[3] - pt[1]) ** 2)
    out = []
    for c in cand:
        if len(out) == n: break
        if avoid_adj and any(nb in taken and nb not in {(o[0], o[1]) for o in out} for nb in nbrs(c[0], c[1])): continue
        out.append(c)
    for c in out: taken.add((c[0], c[1]))
    return out
offc = {}
bal = np.array(geom['07'].centroid.coords[0]); offc['07'] = nearest_free(bal, SEATS['07'])
def body(k): return pts[[i for i, o in owner.items() if o == k]]
cz = body('11'); offc['51'] = nearest_free(np.array([cz[:, 0].mean() + R, cz[:, 1].max() + 2.4 * R]), 1)
al = body('04'); offc['52'] = nearest_free(np.array([al[:, 0].mean(), al[:, 1].max() + 2.4 * R]), 1)
xs = pts[:, 0]; ys = pts[:, 1]
base = np.array([xs.min() - 1 * R, ys.max() + 8 * R])
offc['38'] = nearest_free(base + np.array([1.0 * SQ3 * R, 0]), SEATS['38'], avoid_adj=False)
offc['35'] = nearest_free(base + np.array([4.2 * SQ3 * R, 0]), SEATS['35'], avoid_adj=False)
hexes = [dict(id=owner[i], x=round(c[2], 2), y=round(c[3], 2), r=c[0], c=c[1]) for i, c in enumerate(cells)]
for k, cs in offc.items():
    for c in cs: hexes.append(dict(id=k, x=round(c[2], 2), y=round(c[3], 2), r=c[0], c=c[1]))
from collections import Counter
cnt = Counter(h['id'] for h in hexes); assert all(cnt[k] == SEATS[k] for k in SEATS), [(k, cnt[k], SEATS[k]) for k in SEATS if cnt[k] != SEATS[k]]
json.dump(dict(R=R, hexes=hexes), open(os.path.join(D, 'hex.json'), 'w'))
print(len(hexes))
