/**
 * The 29N scenario engine — an ASSUMPTION CALCULATOR, not a forecast.
 *
 * Baseline: the poll-average projection per constituency (see modelo/ in the repo).
 * The user moves VOTES, never seats:
 *  · national party swing  → iterative proportional fitting: the touched party hits its new national
 *    share, spread across provinces in proportion to where it already has votes; every other party
 *    gives up votes in proportion to its size, province by province.
 *  · province party swing  → +Δ points in that province only; the rest absorb it proportionally.
 *  · turnout (national + per-province extra) → voters added to / removed from each province. A national
 *    rise lands where there is abstention to draw on (∝ 1 − t), a fall where turnout is middling or low
 *    (∝ t·(1 − t)), so no province passes its ceiling. Inside each province they vote like the polling
 *    stations they come from (DATA.tp, 2023 by mesa), times the user's newcomer multipliers.
 * Then D'Hondt with the 3 % threshold over valid votes (blank included) in each of the 52 constituencies.
 */
import { PROV, BYID, DATA } from './data';
import { ORDER, PARTY, INVEST23 } from './parties';
import type { Scenario, RunResult, DhondtResult, ProvResult } from './types';

export const THR = 0.03;

export const blank = (): Scenario => ({ nat: {}, prov: {}, turnNat: 0, turnProv: {}, distNat: {}, distProv: {} });

/** baseline valid votes per province (2023 turnout and null rate on the 2026 census) */
export const V0: Record<string, number> = Object.fromEntries(PROV.map((p) => [p.id, p.census * p.t0 * (1 - p.nr)]));
export const VNAT = Object.values(V0).reduce((a, b) => a + b, 0);
export const CENSUS = PROV.reduce((a, p) => a + p.census, 0);
// how a national turnout change is shared between provinces: by room to rise (1 − t) or to fall (t·(1 − t)),
// scaled so the national change in voters matches the slider
const UP_W = CENSUS / PROV.reduce((a, p) => a + p.census * (1 - p.t0), 0);
const DN_W = CENSUS / PROV.reduce((a, p) => a + p.census * p.t0 * (1 - p.t0), 0);
export const provTurnShift = (p: { t0: number }, dNat: number) => (dNat >= 0 ? dNat * (1 - p.t0) * UP_W : dNat * p.t0 * (1 - p.t0) * DN_W);

/** D'Hondt + the last seat and its cheapest challenger (votes needed to beat the last quotient or cross 3 %) */
export function dhondt(votes: Record<string, number>, n: number, valid: number): DhondtResult {
  const elig = Object.entries(votes).filter(([k, v]) => k !== 'OTROS' && v > 0 && v / valid >= THR);
  const q: { k: string; q: number; v: number }[] = [];
  for (const [k, v] of elig) for (let d = 1; d <= n + 1; d++) q.push({ k, q: v / d, v });
  q.sort((a, b) => b.q - a.q || b.v - a.v);
  const seats: Record<string, number> = {};
  for (const x of q.slice(0, n)) seats[x.k] = (seats[x.k] || 0) + 1;
  const last = q[n - 1] || null;
  let chal: DhondtResult['chal'] = null;
  for (const [k, v] of Object.entries(votes)) {
    if (k === 'OTROS' || !(v > 0) || !last || k === last.k) continue;
    const s = seats[k] || 0;
    let need = Math.floor(last.q * (s + 1)) - v + 1;
    if (v / valid < THR) need = Math.max(need, Math.ceil(THR * valid) - v);
    if (need > 0 && (!chal || need < chal.need)) chal = { k, need };
  }
  return { seats, last, chal };
}

export function run(st: Scenario): RunResult {
  // 1) national swings (IPF)
  const S: Record<string, Record<string, number>> = {};
  for (const p of PROV) S[p.id] = { ...(p.s as Record<string, number>) };
  const changed = Object.entries(st.nat).filter(([, d]) => d);
  if (changed.length) {
    const share = (P: string) => PROV.reduce((a, p) => a + (S[p.id][P] || 0) * V0[p.id], 0) / VNAT;
    const target: Record<string, number> = {};
    for (const [P, d] of changed) target[P] = Math.max(0, share(P) + d / 100);
    for (let it = 0; it < 40; it++) {
      for (const P in target) {
        const cur = share(P);
        const f = cur > 0 ? target[P] / cur : 0;
        for (const p of PROV) if (S[p.id][P]) S[p.id][P] *= f;
      }
      for (const p of PROV) {
        const row = S[p.id], tgt = 1 - p.bl;
        let tot = 0;
        for (const k in row) tot += row[k];
        for (const k in row) row[k] *= tgt / tot;
      }
    }
  }
  // 2) province swings
  for (const id in st.prov) {
    const deltas = Object.entries(st.prov[id] || {}).filter(([, d]) => d);
    if (!deltas.length) continue;
    const row = S[id], tgt = 1 - BYID[id].bl, touched = new Set<string>();
    for (const [P, d] of deltas) { if (row[P] == null) continue; row[P] = Math.max(0, row[P] + d / 100); touched.add(P); }
    let fixed = 0, rest = 0;
    for (const k in row) (touched.has(k) ? (fixed += row[k]) : (rest += row[k]));
    if (fixed > tgt) { for (const k of touched) row[k] *= tgt / fixed; fixed = tgt; }
    const f = rest > 0 ? (tgt - fixed) / rest : 0;
    for (const k in row) if (!touched.has(k)) row[k] *= f;
  }
  // 3) turnout + newcomer distribution, then D'Hondt
  const out: Record<string, ProvResult> = {};
  const natVotes: Record<string, number> = {}, natSeats: Record<string, number> = {};
  let natValid = 0, natVotantes = 0;
  for (const p of PROV) {
    const row = S[p.id];
    const votes: Record<string, number> = {};
    for (const k in row) votes[k] = row[k] * V0[p.id];
    let blankV = p.bl * V0[p.id];
    const dt = provTurnShift(p, st.turnNat || 0) + (st.turnProv[p.id] || 0);
    const t = Math.min(0.98, Math.max(0.2, p.t0 + dt / 100));
    const dVal = p.census * (t - p.t0) * (1 - p.nr);
    if (dVal) {
      const mult = st.distProv[p.id] || st.distNat || {};
      const prof = DATA.tp?.[p.id]?.[dVal > 0 ? 'up' : 'down'] || {};
      const w: Record<string, number> = {};
      const wb = p.bl * (prof.BL ?? 1);
      let W = wb;
      for (const k in row) { w[k] = row[k] * (prof[k] ?? 1) * (mult[k] != null ? mult[k] : 1); W += w[k]; }
      for (const k in row) votes[k] = Math.max(0, votes[k] + (dVal * w[k]) / W);
      blankV = Math.max(0, blankV + (dVal * wb) / W);
    }
    let valid = blankV;
    for (const k in votes) valid += votes[k];
    const dh = dhondt(votes, p.seats, valid);
    out[p.id] = { votes, blank: blankV, valid, turnout: t, ...dh };
    natValid += valid; natVotantes += valid / (1 - p.nr);
    for (const k in votes) natVotes[k] = (natVotes[k] || 0) + votes[k];
    for (const k in dh.seats) natSeats[k] = (natSeats[k] || 0) + dh.seats[k];
  }
  return { prov: out, votes: natVotes, seats: natSeats, valid: natValid, turnout: natVotantes / CENSUS };
}

export const BASE = run(blank());

// ── scope helpers ──────────────────────────────────────────────────────────
export const scopeVotes = (R: RunResult, id: string) => (id === 'ES' ? R.votes : R.prov[id].votes);
export const scopeSeats = (R: RunResult, id: string) => (id === 'ES' ? R.seats : R.prov[id].seats);
export const scopeValid = (R: RunResult, id: string) => (id === 'ES' ? R.valid : R.prov[id].valid);
export function partiesIn(id: string) {
  const s = id === 'ES' ? BASE.votes : (BYID[id].s as Record<string, number>);
  return ORDER.filter((P) => (s[P] || 0) > (id === 'ES' ? 1 : 0.0005));
}
/** 2023 seats for a scope (FA = Sumar in 2023) */
export function seats2023(id: string): Record<string, number> {
  if (id !== 'ES') return { ...(BYID[id].r23.s as Record<string, number>) };
  const s: Record<string, number> = {};
  for (const p of PROV) for (const k in p.r23.s) s[k] = (s[k] || 0) + (p.r23.s as Record<string, number>)[k];
  return s;
}
export const sumSeats = (seats: Record<string, number>, ks: string[]) => ks.reduce((a, k) => a + (seats[k] || 0), 0);
export const INVEST = INVEST23 as string[];

/** newcomer slider (−1…1) ↔ multiplier (0…4); centre = ×1 */
/** what the voters who join (or, if `down`, stay home) vote, as shares of them, in Spain or one province:
 *  each province's polling-station profile × the user's multipliers, provinces weighted by how many they add */
export function newcomerShares(st: Scenario, cur: RunResult, scope: string, down: boolean) {
  const acc: Record<string, number> = {};
  let tot = 0;
  for (const p of PROV) {
    if (scope !== 'ES' && p.id !== scope) continue;
    const r = cur.prov[p.id], prof = DATA.tp?.[p.id]?.[down ? 'down' : 'up'] || {}, mult = st.distProv[p.id] || st.distNat || {};
    const om = scope !== 'ES' ? 1 : p.census * (down ? p.t0 * (1 - p.t0) : 1 - p.t0);
    const w: Record<string, number> = {};
    let W = (r.blank / r.valid) * (prof.BL ?? 1);
    for (const k in r.votes) { w[k] = (r.votes[k] / r.valid) * (prof[k] ?? 1) * (mult[k] != null ? mult[k] : 1); W += w[k]; }
    if (W <= 0) continue;
    for (const k in w) acc[k] = (acc[k] || 0) + (om * w[k]) / W;
    tot += om;
  }
  for (const k in acc) acc[k] /= tot || 1;
  return acc;
}

export const s2m = (v: number) => (v >= 0 ? 1 + 3 * v : 1 + v);
export const m2s = (m: number) => (m >= 1 ? (m - 1) / 3 : m - 1);

export function hasScopeChanges(st: Scenario, scope: string) {
  if (scope === 'ES') return Object.values(st.nat).some(Boolean) || !!st.turnNat || Object.values(st.distNat).some((v) => v !== 1);
  return Object.values(st.prov[scope] || {}).some(Boolean) || !!st.turnProv[scope] || !!st.distProv[scope];
}

/**
 * Vote transfers 2023 → projection for Spain or one province. Precomputed in modelo/transfers.py: the latest CIS
 * barometer's 2023 recall × current intention, as a pattern, fitted (IPF) to each province's real 2023 result and
 * its projection. Spain is the sum of the 52 provinces. Only for the projection (not the user's scenario).
 */
export function transfers(_cur: RunResult, scope: string) {
  const F: Record<string, number> = {};
  for (const p of PROV) {
    if (scope !== 'ES' && p.id !== scope) continue;
    for (const [a, b, v] of DATA.tr[p.id] || []) { const k = a + '>' + b; F[k] = (F[k] || 0) + v; }
  }
  return Object.entries(F).map(([k, votes]) => { const [from, to] = k.split('>'); return { from, to, votes }; });
}

// ── history: each adjustment on its own, with the seats it moves vs the projection ──
export interface HistoryEntry { key: string; html: string; impact: [string, number][]; undo: (st: Scenario) => void }
const nm = (P: string) => PARTY[P as keyof typeof PARTY]?.n ?? P;
const d1 = (v: number) => Math.abs(v).toFixed(1).replace('.', ',');
const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!);
function impactOf(st: Scenario): [string, number][] {
  const r = run(st), d: [string, number][] = [];
  for (const k of new Set([...Object.keys(r.seats), ...Object.keys(BASE.seats)])) { const x = (r.seats[k] || 0) - (BASE.seats[k] || 0); if (x) d.push([k, x]); }
  return d.sort((a, b) => b[1] - a[1]);
}
export function historyEntries(st: Scenario): HistoryEntry[] {
  const out: HistoryEntry[] = [];
  const distTxt = (d?: Record<string, number>) => {
    const e = Object.entries(d || {}).filter(([, m]) => m !== 1);
    return e.length ? '; los nuevos votantes ' + e.map(([P, m]) => `${m > 1 ? 'favorecen' : 'castigan'} a ${nm(P)} (×${m.toFixed(1).replace('.', ',')})`).join(', ') : '';
  };
  for (const [P, v] of Object.entries(st.nat)) if (v)
    out.push({ key: 'n' + P, html: `<strong>${nm(P)}</strong> ${v > 0 ? 'gana' : 'pierde'} ${d1(v)} puntos en toda España`, impact: impactOf({ ...blank(), nat: { [P]: v } }), undo: (s) => { delete s.nat[P]; } });
  for (const [id, o] of Object.entries(st.prov)) for (const [P, v] of Object.entries(o || {})) if (v)
    out.push({ key: 'p' + id + P, html: `<strong>${nm(P)}</strong> ${v > 0 ? 'gana' : 'pierde'} ${d1(v)} puntos en ${esc(BYID[id].n)}`, impact: impactOf({ ...blank(), prov: { [id]: { [P]: v } } }), undo: (s) => { delete s.prov[id][P]; } });
  if (st.turnNat)
    out.push({ key: 'tn', html: `La participación ${st.turnNat > 0 ? 'sube' : 'baja'} ${d1(st.turnNat)} puntos en toda España${distTxt(st.distNat)}`, impact: impactOf({ ...blank(), turnNat: st.turnNat, distNat: { ...st.distNat } }), undo: (s) => { s.turnNat = 0; } });
  for (const [id, v] of Object.entries(st.turnProv)) if (v)
    out.push({ key: 't' + id, html: `La participación ${v > 0 ? 'sube' : 'baja'} ${d1(v)} puntos en ${esc(BYID[id].n)}${distTxt(st.distProv[id] || st.distNat)}`, impact: impactOf({ ...blank(), turnProv: { [id]: v }, distNat: { ...st.distNat }, distProv: JSON.parse(JSON.stringify(st.distProv)) }), undo: (s) => { delete s.turnProv[id]; } });
  return out;
}
