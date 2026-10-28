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
 *   · young voters turn out more there: YOUTH_EXTRA more points of turnout in the province (18–34 year olds
 *     are about a fifth of the census: as if their turnout rose some 25 points);
 *  and overall turnout reaches 75 %: whatever is missing after those extra points comes in every province, as
 *  any national rise does. All the newcomers, everywhere, are young voters who split in quarters: a quarter to
 *  the PSOE, a quarter to Frente Amplio's space, a quarter to the space of Podemos, ERC or Compromís (by region)
 *  and the last quarter to the rest of the parties, as newcomers usually vote there. In the Canaries both spaces
 *  go together in Unidad del Pueblo Canario (half); in Catalonia, where Podemos does not run, its quarter goes to
 *  ERC; in the Valencian Community, to Compromís. Where a space has no list, its quarter goes to the rest.
 *  So the young vote moves to the left everywhere, and more where housing is a hotter issue. */
export const VIVIENDA_HOT = ['28', '07', '29', '08', '20', '48', '38', '35', '46', '17', '03', '41', '01', '39'];
const YOUTH_EXTRA = 5;
const CAT = ['08', '17', '25', '43'], VAL = ['03', '12', '46'], CAN = ['35', '38'];
/** the young vote's quarters in a province: each group of lists gets a quarter (the rest, the last quarter) */
function youthGroups(id: string): string[][] {
  if (CAN.includes(id)) return [['PSOE'], ['UPC'], ['UPC']];
  return [['PSOE'], ['FA'], CAT.includes(id) ? ['ERC'] : VAL.includes(id) ? ['COMP'] : ['PODEMOS']];
}
/** newcomer multipliers that give each targeted list its quarter of the newcomers; the rest keep their usual proportions */
function quarters(id: string): Record<string, number> {
  const p = BYID[id], row = p.s as Record<string, number>, prof = DATA.tp?.[id]?.up || {};
  const youth: Record<string, number> = {};
  for (const g of youthGroups(id)) { const ok = g.filter((k) => (row[k] || 0) > 0); for (const k of ok) youth[k] = (youth[k] || 0) + 0.25 / ok.length; }
  const qRest = 1 - Object.values(youth).reduce((a, b) => a + b, 0);
  let W = p.bl * (prof.BL ?? 1), rest = W;
  const w: Record<string, number> = {};
  for (const k in row) { w[k] = row[k] * (prof[k] ?? 1); W += w[k]; if (!(k in youth)) rest += w[k]; }
  return Object.fromEntries(Object.entries(youth).map(([k, q]) => [k, Math.round(((q / (w[k] / W)) / (qRest / (rest / W))) * 100) / 100]));
}
function vivienda(turnoutTo = 75): Partial<Scenario> {
  const turnProv: Scenario['turnProv'] = Object.fromEntries(VIVIENDA_HOT.map((id) => [id, YOUTH_EXTRA]));
  // the national rise that, with the hot provinces' extra points, takes turnout to the target
  let lo = -20, hi = 30;
  for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (run({ ...blank(), turnNat: m, turnProv }).turnout * 100 < turnoutTo) lo = m; else hi = m; }
  const turnNat = Math.round(hi * 10) / 10;
  const distProv: Scenario['distProv'] = Object.fromEntries(PROV.map((p) => [p.id, quarters(p.id)]));
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
