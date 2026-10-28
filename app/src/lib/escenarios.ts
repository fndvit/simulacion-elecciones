// Escenarios: concrete «what if» questions, each one a set of adjustments to the poll projection.
// Newest first on the page: add a new one anywhere in the list, the date sorts it.
//  · title and body are HTML (title takes <strong> for the bold half, as the section headings)
//  · st: only what the scenario moves; the rest stays as in the projection (same shape as the simulator)
import type { Scenario } from './types';
import { blank } from './model';

export interface Escenario {
  slug: string;          // anchor (#slug) and key
  date: string;          // YYYY-MM-DD, publication date
  title: string;
  body: string;
  st: Partial<Scenario>;
}

const LIST: Escenario[] = [
  {
    // PLACEHOLDER: layout test, to be replaced by the first real scenario
    slug: 'borrador',
    date: '2026-10-28',
    title: 'Título del escenario, <strong>en negrita la parte que importa</strong>',
    body: 'Párrafo de presentación: la pregunta, de dónde salen los supuestos y qué conviene mirar en el resultado. Texto provisional para probar la maqueta.',
    st: { nat: { PSOE: 1.5, PP: -1.5 }, turnNat: 2 }
  }
];

export const ESCENARIOS = [...LIST].sort((a, b) => b.date.localeCompare(a.date));
export const scenarioOf = (e: Escenario): Scenario => ({ ...blank(), ...JSON.parse(JSON.stringify(e.st)) });
