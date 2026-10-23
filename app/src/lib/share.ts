/** Scenario <-> shareable link. The scenario travels in the query string (?e=…), compact JSON in
 *  base64url; the hash stays free for the router. A link always wins over what the browser saved. */
import type { Scenario } from './types';

const clean = (o: Record<string, unknown>): Record<string, unknown> => {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(o)) {
    if (v && typeof v === 'object') { const c = clean(v as Record<string, unknown>); if (Object.keys(c).length) out[k] = c; }
    else if (typeof v === 'number' && v !== 0) out[k] = Math.round(v * 1000) / 1000;
  }
  return out;
};
const b64 = (s: string) => btoa(unescape(encodeURIComponent(s))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const unb64 = (s: string) => decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/'))));

export function encodeScenario(st: Scenario) {
  const c = clean({ ...st, turnNat: st.turnNat } as unknown as Record<string, unknown>);
  return Object.keys(c).length ? b64(JSON.stringify(c)) : '';
}
export function decodeScenario(code: string, blank: () => Scenario): Scenario | null {
  try { const o = JSON.parse(unb64(code)); return o && typeof o === 'object' ? Object.assign(blank(), o) : null; } catch { return null; }
}
export function scenarioFromUrl(blank: () => Scenario) {
  try { const e = new URLSearchParams(location.search).get('e'); return e ? decodeScenario(e, blank) : null; } catch { return null; }
}
export function shareUrl(st: Scenario) {
  const u = new URL(location.href), e = encodeScenario(st);
  if (e) u.searchParams.set('e', e); else u.searchParams.delete('e');
  return u.toString();
}
