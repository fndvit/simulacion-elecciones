// Escenarios: concrete «what if» questions, each one a set of adjustments to the poll projection.
// Newest first on the page: add a new one anywhere in the list, the date sorts it.
//  · title and body are HTML (title takes <strong> for the bold half, as the section headings)
//  · st: only what the scenario moves; the rest stays as in the projection (same shape as the simulator)
import type { Scenario } from './types';
import { blank, run, BASE } from './model';
import { PROV } from './data';

export interface Escenario {
  slug: string;          // anchor (#slug) and key
  date: string;          // YYYY-MM-DD, publication date
  title: string;
  body: string;
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
    // TEXT PENDING (Xaquín): headline and paragraph
    title: '¿Y si Vox no se llevara <strong>el último escaño</strong>?',
    body: '[Texto pendiente]',
    st: () => sinUltimoEscano('VOX', 3)
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
const cache = new Map<string, Scenario>();
export const scenarioOf = (e: Escenario): Scenario => {
  if (!cache.has(e.slug)) cache.set(e.slug, { ...blank(), ...JSON.parse(JSON.stringify(typeof e.st === 'function' ? e.st() : e.st)) });
  return JSON.parse(JSON.stringify(cache.get(e.slug)));
};
