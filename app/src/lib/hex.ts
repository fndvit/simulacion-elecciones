/**
 * Hex cartogram (one pointy-top hexagon per seat), after El Confidencial's 350-seat map.
 * The layout itself is precomputed by modelo/hexmap.py (capacity-constrained assignment over
 * the mainland outline, contiguous provinces; Baleares, Canarias, Ceuta and Melilla placed apart).
 */
import { DATA, BYID } from './data';
import vor from './data/vor.json';
import { BASE } from './model';
import { ORDER } from './parties';
import type { RunResult } from './types';

export interface Hex { id: string; x: number; y: number; r: number; c: number; i: number }

const R = DATA.hex.R;
const H: Hex[] = DATA.hex.hexes.map((h, i) => ({ ...h, i }));
const at = new Map(H.map((h) => [h.r + ',' + h.c, h]));
const pt = (x: number, y: number, r: number, deg: number) => [x + r * Math.cos((deg * Math.PI) / 180), y + r * Math.sin((deg * Math.PI) / 180)];
// neighbour offsets for directions 0°, 60°, …, 300° (y grows downwards; odd rows shifted right)
function nb(h: Hex, k: number) {
  const even = h.r % 2 === 0;
  const d = [[0, 1], even ? [1, 0] : [1, 1], even ? [1, -1] : [1, 0], [0, -1], even ? [-1, -1] : [-1, 0], even ? [-1, 0] : [-1, 1]][k];
  return at.get(h.r + d[0] + ',' + (h.c + d[1]));
}
export const poly = (h: Hex, r: number) => [-90, -30, 30, 90, 150, 210].map((d) => pt(h.x, h.y, r, d).map((v) => v.toFixed(1)).join(',')).join(' ');

/** shared edges: between provinces of the same community (pv) and between communities (ca); per-province outline */
const lines = { pv: '', ca: '' };
const outline: Record<string, string> = {};
for (const h of H)
  [0, 60, 120, 180, 240, 300].forEach((deg, k) => {
    const n = nb(h, k);
    if (n && n.id === h.id) return;
    const [ax, ay] = pt(h.x, h.y, R, deg - 30), [bx, by] = pt(h.x, h.y, R, deg + 30);
    const seg = `M${ax.toFixed(1)},${ay.toFixed(1)}L${bx.toFixed(1)},${by.toFixed(1)}`;
    outline[h.id] = (outline[h.id] || '') + seg;
    if (n && h.i < n.i) lines[BYID[h.id].ca === BYID[n.id].ca ? 'pv' : 'ca'] += seg;
  });

/** hexes of each province, ordered clockwise from north so each party's seats sit together */
const byProv: Record<string, Hex[]> = {};
for (const h of H) (byProv[h.id] ||= []).push(h);
for (const id in byProv) {
  const L = byProv[id], cx = L.reduce((a, h) => a + h.x, 0) / L.length, cy = L.reduce((a, h) => a + h.y, 0) / L.length;
  const ang = (h: Hex) => (Math.atan2(h.y - cy, h.x - cx) + 2.5 * Math.PI) % (2 * Math.PI);
  L.sort((p, q) => ang(p) - ang(q));
}

const xs = H.map((h) => h.x), ys = H.map((h) => h.y), pad = R * 1.4;
const viewBox = [Math.min(...xs) - pad, Math.min(...ys) - pad, Math.max(...xs) - Math.min(...xs) + 2 * pad, Math.max(...ys) - Math.min(...ys) + 2 * pad].map((v) => Math.round(v)).join(' ');
const can = H.filter((h) => h.id === '35' || h.id === '38');
const canBox = [Math.min(...can.map((h) => h.x)) - R * 1.5, Math.min(...can.map((h) => h.y)) - R * 1.6, Math.max(...can.map((h) => h.x)) + R * 1.5, Math.max(...can.map((h) => h.y)) + R * 1.6];

export const HEX = { R, H, byProv, lines, outline, viewBox, canBox };

/* ---------- geographic seat map (Voronoi cells, precomputed by modelo/voronoi.py) ---------- */
type Pt = [number, number];
const NR: number = vor.n;
/** one cell per hexagon (same index as HEX.H): SVG path, morph ring (NR points, clockwise from the top), centroid */
export const GEO = {
  cells: vor.cells as { d: string; ring: Pt[]; c: Pt }[],
  prov: vor.prov as Record<string, string>,
  ca: vor.ca as string,
  canBox: vor.canBox as number[]
};
/** the same NR-point ring for every hexagon: NR/6 points per side, clockwise from the top vertex */
const HEXRING: Pt[][] = H.map((h) => {
  const v = [-90, -30, 30, 90, 150, 210].map((d) => pt(h.x, h.y, R, d));
  const per = NR / 6, out: Pt[] = [];
  for (let k = 0; k < 6; k++) {
    const a = v[k], b = v[(k + 1) % 6];
    for (let j = 0; j < per; j++) out.push([a[0] + ((b[0] - a[0]) * j) / per, a[1] + ((b[1] - a[1]) * j) / per]);
  }
  return out;
});
/** cell i at morph progress t (0 = geographic, 1 = hexagon) */
export function morphPath(i: number, t: number) {
  const g = GEO.cells[i].ring, h = HEXRING[i];
  let d = 'M';
  for (let k = 0; k < NR; k++) d += (k ? 'L' : '') + (g[k][0] + (h[k][0] - g[k][0]) * t).toFixed(1) + ',' + (g[k][1] + (h[k][1] - g[k][1]) * t).toFixed(1);
  return d + 'Z';
}
/** a viewBox that holds both maps, so the morph never rescales */
const [vx, vy, vw, vh] = viewBox.split(' ').map(Number), [gx0, gy0, gx1, gy1] = vor.box as number[];
const ux0 = Math.min(vx, gx0 - 8), uy0 = Math.min(vy, gy0 - 8), ux1 = Math.max(vx + vw, gx1 + 8), uy1 = Math.max(vy + vh, gy1 + 8);
export const VIEWBOX = [ux0, uy0, ux1 - ux0, uy1 - uy0].map(Math.round).join(' ');

const seatOrder = (seats: Record<string, number>) =>
  Object.entries(seats).filter(([, n]) => n > 0).sort((a, b) => b[1] - a[1] || ORDER.indexOf(a[0] as never) - ORDER.indexOf(b[0] as never));

/** reference party for every hex: the poll projection, or the 2023 result. Madrid has one more hex than
 *  its 2023 seats (left empty = a new seat) and Cádiz one fewer (its smallest 2023 seat drops).
 *  With a clear winner, the winner takes the middle of the province (the cells nearest its most central
 *  cell, on the geographic map) and the other parties follow round the edge, clockwise from the north,
 *  each in one run. Without one (a tie at the top), all parties go clockwise from the north. */
const dist = (a: Pt, b: Pt) => Math.hypot(a[0] - b[0], a[1] - b[1]);
function refArray(seats: Record<string, number>, id: string) {
  const L = byProv[id], n = L.length, order = seatOrder(seats);
  const flat: string[] = [];
  for (const [k, c] of order) for (let i = 0; i < c; i++) flat.push(k);
  while (flat.length < n) flat.push('');
  flat.length = n;
  const clear = order.length > 1 && order[0][1] > order[1][1] && n > 2;
  if (!clear) return flat;
  const P = L.map((h) => GEO.cells[h.i].c as Pt);
  // the most central cell: the one closest, in total, to all the others
  let mid = 0, best = Infinity;
  P.forEach((p, i) => { const s = P.reduce((a, q) => a + dist(p, q), 0); if (s < best) { best = s; mid = i; } });
  const [W, w] = order[0];
  const byNear = P.map((_, i) => i).sort((a, b) => dist(P[a], P[mid]) - dist(P[b], P[mid]));
  const inner = new Set(byNear.slice(0, w));
  const ang = (i: number) => (Math.atan2(P[i][1] - P[mid][1], P[i][0] - P[mid][0]) + 2.5 * Math.PI) % (2 * Math.PI);
  const outer = P.map((_, i) => i).filter((i) => !inner.has(i)).sort((a, b) => ang(a) - ang(b));
  const arr: string[] = new Array(n).fill('');
  for (const i of inner) arr[i] = W;
  flat.slice(w).forEach((k, j) => (arr[outer[j]] = k));
  return arr;
}
export const BASE_HEX: Record<string, string[]> = {};
export const HEX_2023: Record<string, string[]> = {};
for (const id in byProv) {
  BASE_HEX[id] = refArray(BASE.prov[id].seats, id);
  HEX_2023[id] = refArray(BYID[id].r23.s as Record<string, number>, id);
}
/** scenario party per hex, laid out on the reference: a hex keeps its reference party while that party
 *  still has seats, so only real changes move */
export function hexParties(cur: RunResult, id: string, ref: Record<string, string[]> = BASE_HEX): string[] {
  const base = ref[id], quota = { ...cur.prov[id].seats }, out: (string | null)[] = base.map(() => null);
  base.forEach((k, i) => { if (k && quota[k] > 0) { out[i] = k; quota[k]--; } });
  const rest: string[] = [];
  for (const [k, n] of seatOrder(quota)) for (let i = 0; i < n; i++) rest.push(k);
  return out.map((k) => k || rest.shift() || '');
}

/** hexes that changed hands since 2023, on the fixed (projection-anchored) layout: for each party that
 *  has more seats than in 2023, mark that many of its hexes, preferring the ones it took from the
 *  projection. Only the highlight depends on the comparison; colours never move. */
export function changedSince2023(parts: string[], id: string): boolean[] {
  const s23 = BYID[id].r23.s as Record<string, number>, base = BASE_HEX[id];
  const out = parts.map(() => false), have: Record<string, number> = {};
  for (const k of parts) if (k) have[k] = (have[k] || 0) + 1;
  for (const k in have) {
    let gain = have[k] - (s23[k] || 0);
    const idx = parts.map((p, i) => i).filter((i) => parts[i] === k);
    idx.sort((a, b) => Number(base[b] !== k) - Number(base[a] !== k) || b - a);
    for (const i of idx) { if (gain-- <= 0) break; out[i] = true; }
  }
  return out;
}
