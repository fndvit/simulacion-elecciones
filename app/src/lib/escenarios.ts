// Escenarios: concrete «what if» questions, each one a set of adjustments to the poll projection.
// Newest first on the page: add a new one anywhere in the list, the date sorts it.
//  · title and body are HTML (title takes <strong> for the bold half, as the section headings)
//  · st: only what the scenario moves; the rest stays as in the projection (same shape as the simulator)
import type { Scenario, RunResult, PartyKey } from './types';
import { blank, run, BASE, provTurnShift } from './model';
import { PROV, BYID, DATA } from './data';
import { PARTY } from './parties';
import { longDate } from './format';

/** what a scenario's texts can draw on: the adjustments, the result, the projection and the data date */
export interface Ctx { st: Scenario; cur: RunResult; base: RunResult; today: string }
type Text = string | string[];

export interface Escenario {
  slug: string;          // anchor (#slug) and key
  date: string;          // YYYY-MM-DD, publication date
  /** HTML; or a function of the result, so the text follows the data */
  title: string | ((c: Ctx) => string);
  /** HTML, one string per paragraph; or a function of the result */
  body: Text | ((c: Ctx) => Text);
  /** the adjustments, or a function that works them out from the day's projection (so the scenario
   *  keeps its meaning when the polls move) */
  st: Partial<Scenario> | (() => Partial<Scenario>);
}

/** Party P gives up, in each province where D'Hondt hands it the last seat, the fewest votes (to the tenth of a
 *  point, as the simulator's controls) for that seat to go to someone else, as long as that takes no more than
 *  `max` points (a loss within a poll's margin of error). The votes it loses go to the other parties in
 *  proportion to their size, as any province adjustment in the simulator. */
function sinUltimoEscano(P: string, max = 3): Partial<Scenario> {
  const prov: Scenario['prov'] = {};
  for (const p of PROV) {
    const b = BASE.prov[p.id];
    if (b.last?.k !== P) continue;
    const loses = (d: number) => (run({ ...blank(), prov: { [p.id]: { [P]: -d } } }).prov[p.id].seats[P] || 0) < (b.seats[P] || 0);
    let lo = 0, hi = 100 * (b.votes[P] || 0) / b.valid;
    if (!loses(hi)) continue;
    for (let i = 0; i < 24; i++) { const m = (lo + hi) / 2; if (loses(m)) hi = m; else lo = m; }
    let d = Math.ceil(hi * 10) / 10;
    while (!loses(d)) d = Math.round(d * 10 + 1) / 10;
    if (d > max) continue;
    prov[p.id] = { [P]: -d };
  }
  return { prov };
}

const LIST: Escenario[] = [
  {
    slug: 'vox-sin-ultimo-escano',
    date: '2026-10-28',
    title: '¿Y si Vox no se llevase <strong>el último escaño</strong> allá donde está más en disputa?',
    body: (c) => {
      const P = 'VOX';
      const ids = Object.keys(c.st.prov).filter((id) => c.st.prov[id][P]);
      const lost = (c.base.seats[P] || 0) - (c.cur.seats[P] || 0);
      const gain = gains(c, P);
      const top = gain.filter(([, n]) => n === gain[0]?.[1]).map(([k]) => k);
      // seats that change hands for fewer than a thousand votes
      const close = ids.filter((id) => votesFor(c, id, P) < 1000).sort((a, b) => votesFor(c, a, P) - votesFor(c, b, P));
      const out = [
        `${top.length > 1 ? 'Se reparten el botín ' + listEs(top.map(art)) : 'Se lleva el botín ' + art(top[0])}. En este escenario, con los datos de las encuestas actualizados a ${longDate(c.today)}, Vox pierde ${lost} ${lost === 1 ? 'escaño' : 'escaños'} a favor ${listEs(gain.map(([k]) => de(k)))}.`
      ];
      if (close.length)
        out.push(`${close.length > 1 ? 'Algunos de los escaños, en' : 'El escaño de'} ${listEs(close.map((id) => BYID[id].n))}, se decidirán por apenas unos centenares de votos, muy por debajo del típico margen de error de ±3 puntos porcentuales de cualquier encuesta. Ese margen de error explica, en jerga estadística, que si una encuesta dice que el 25% apoya una opción, el apoyo real estaría entre el 22% y el 28%.`);
      // only while most of these seats are in small constituencies (5 seats or fewer)
      if (ids.filter((id) => BYID[id].seats <= 5).length > ids.length / 2)
        out.push(`La mayoría se mueve en circunscripciones pequeñas, lo que sumado al método D'Hondt, eleva el listón a la hora de repartir escaños.`);
      return out;
    },
    st: () => sinUltimoEscano('VOX', 3)
  },
  {
    slug: 'vivienda',
    date: '2026-10-28',
    // TEXT PENDING (Xaquín): headline and paragraphs
    title: '¿Y si la vivienda moviera <strong>el voto joven</strong>?',
    body: '[Texto pendiente]',
    st: () => vivienda(75)
  },
  {
    // PLACEHOLDER: older scenario, to test the compact layout
    slug: 'borrador-2',
    date: '2026-10-21',
    title: 'Un escenario anterior, <strong>empujado hacia abajo</strong>',
    body: 'Texto provisional para probar cómo se ven los escenarios antiguos.',
    st: { nat: { VOX: 2, PP: -2 } }
  },
  {
    // PLACEHOLDER: older scenario, to test the compact layout
    slug: 'borrador-3',
    date: '2026-10-14',
    title: 'Otro escenario más antiguo, <strong>con la participación a la baja</strong>',
    body: 'Texto provisional para probar cómo se ven los escenarios antiguos.',
    st: { turnNat: -4, nat: { FA: 1 } }
  }
];

export const ESCENARIOS = [...LIST].sort((a, b) => b.date.localeCompare(a.date));
/** Housing. Provinces where housing is a hot issue: rent of 13.5 €/m² a month or more, or a sale price of
 *  2,900 €/m² or more; and, a step below, rent of 11.8 €/m² or more with a sale price of 2,000 €/m² or more
 *  (Alicante, Sevilla, Álava, Cantabria; not Segovia, cheap to buy), in Idealista's September 2026 reports (datos/vivienda_idealista_2026-09.csv; the INE
 *  housing price index rises between 9.5 % and 15.2 % a year in every region, so it is the price level that
 *  tells them apart). There:
 *   · young voters turn out more: YOUTH_EXTRA more points of turnout in the province (18–34 year olds are
 *     about a fifth of the census: as if their turnout rose some 25 points);
 *   · half of those young newcomers vote for the lists that carry Frente Amplio and Podemos (in Catalonia, the
 *     comuns' list; in the Valencian Community, with Compromís; in the Canaries, Unidad del Pueblo Canario);
 *     the other half, and everyone else who turns out, vote as newcomers usually do there.
 *  And overall turnout rises to 75 %, voting as newcomers usually do. */
export const VIVIENDA_HOT = ['28', '07', '29', '08', '20', '48', '38', '35', '46', '17', '03', '41', '01', '39'];
const YOUTH_EXTRA = 5;
const LEFT_LISTS = ['FA', 'PODEMOS', 'COMP', 'UPC'];
function vivienda(turnoutTo = 75): Partial<Scenario> {
  const turnNat = Math.round((turnoutTo - 100 * BASE.turnout) * 10) / 10;
  const extra = YOUTH_EXTRA;
  const turnProv: Scenario['turnProv'] = {}, distProv: Scenario['distProv'] = {};
  for (const id of VIVIENDA_HOT) {
    const p = BYID[id], row = p.s as Record<string, number>, prof = DATA.tp?.[id]?.up || {};
    const L = LEFT_LISTS.filter((k) => (row[k] || 0) > 0);
    // how newcomers vote here by default: share of the left lists (tau) and of everyone else
    let A = 0, B = p.bl * (prof.BL ?? 1);
    for (const k in row) { const w = row[k] * (prof[k] ?? 1); if (L.includes(k)) A += w; else B += w; }
    const tau = A / (A + B), young = extra, general = provTurnShift(p, turnNat);
    // share of ALL newcomers in the province the left lists must get: half of the young ones, the usual share of the rest
    const T = (0.5 * young + tau * general) / (young + general);
    const f = Math.round(((T * B) / (A * (1 - T))) * 100) / 100;
    turnProv[id] = Math.round(extra * 10) / 10;
    distProv[id] = Object.fromEntries(L.map((k) => [k, f]));
  }
  return { turnNat, turnProv, distProv };
}

// ── helpers for the texts ───────────────────────────────────────────────────────────────────────
/** parties that take an article in running text */
const ART: Partial<Record<PartyKey, string>> = { PP: 'el PP', PSOE: 'el PSOE', PNV: 'el PNV', BNG: 'el BNG' };
export const art = (k: string) => ART[k as PartyKey] || PARTY[k as PartyKey].n;
/** «de» + party, with «del» where it takes an article */
export const de = (k: string) => (ART[k as PartyKey] ? 'del ' + ART[k as PartyKey]!.slice(3) : 'de ' + PARTY[k as PartyKey].n);
/** «A, B y C» */
export const listEs = (xs: string[]) => (xs.length < 2 ? xs.join('') : xs.slice(0, -1).join(', ') + ' y ' + xs[xs.length - 1]);
/** parties (other than P) that gain seats against the projection, most first */
export const gains = (c: Ctx, P: string) =>
  Object.keys(c.cur.seats).map((k) => [k, (c.cur.seats[k] || 0) - (c.base.seats[k] || 0)] as [string, number]).filter(([k, n]) => k !== P && n > 0).sort((a, b) => b[1] - a[1]);
/** votes a province adjustment of party P moves (points of the projection's valid vote) */
export const votesFor = (c: Ctx, id: string, P: string) => Math.abs(c.st.prov[id]?.[P] || 0) / 100 * c.base.prov[id].valid;

const cache = new Map<string, Scenario>();
export const scenarioOf = (e: Escenario): Scenario => {
  if (!cache.has(e.slug)) cache.set(e.slug, { ...blank(), ...JSON.parse(JSON.stringify(typeof e.st === 'function' ? e.st() : e.st)) });
  return JSON.parse(JSON.stringify(cache.get(e.slug)));
};
