// Escenarios: concrete «what if» questions, each one a set of adjustments to the poll projection.
// Newest first on the page: the date sorts them; on the same date, the order of this list.
//  · title and body are HTML (title takes <strong> for the bold half, as the section headings)
//  · st: only what the scenario moves; the rest stays as in the projection (same shape as the simulator)
import type { Scenario, RunResult, PartyKey } from './types';
import { blank, run, BASE, provTurnShift, INVEST } from './model';
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
  /** kept ready but not on the page yet */
  hidden?: boolean;
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
    slug: 'jovenes',
    date: '2026-11-09',
    // TEXT PENDING (Xaquín)
    title: '¿Qué pasa si <strong>los jóvenes</strong> no acuden a las urnas?',
    body: '[Texto pendiente]',
    st: () => jovenes(0.2)
  },
  {
    slug: 'vivienda',
    date: '2026-10-28',
    title: '¿Y si es <strong>la crisis de la vivienda</strong> —que desató la convocatoria electoral— lo que decide?',
    body: (c) => {
      const provs = listEs(VIVIENDA_HOT.map((id) => BYID[id].n));
      // the 2023 investiture parties against a PP + Vox pact, as under the seat bar
      const right = (c.cur.seats.PP || 0) + (c.cur.seats.VOX || 0);
      const inv = INVEST.reduce((a, k) => a + (c.cur.seats[k] || 0), 0);
      const gap = right - inv;
      const ine = '<a href="https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736152838&menu=ultiDatos&idp=1254735976607" target="_blank" rel="noopener">Índice de precios de vivienda del INE</a>';
      const ide = '<a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/report/" target="_blank" rel="noopener">alquiler</a> y <a href="https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/venta/report/" target="_blank" rel="noopener">venta</a>';
      return [
        '<a href="https://elpais.com/espana/madrid/2026-09-23/maricarmen-se-queda-un-centenar-de-activistas-espera-junto-a-la-anciana-a-la-comision-judicial.html" target="_blank" rel="noopener">El desahucio de Maricarmen</a> fue la chispa. Enseguida llegaron las protestas; la reacción legislativa del gobierno, que tumbó el Congreso; y la convocatoria electoral.',
        'La vivienda, poder comprar o alquilar, es una de las <a href="https://www.cis.es/documents/d/guest/es3582mar_a-pdf" target="_blank" rel="noopener">mayores preocupaciones</a> de la sociedad española. Es una carga que <a href="https://www.bde.es/f/webbe/SES/Secciones/Publicaciones/PublicacionesAnuales/InformesAnuales/25/Fich/IIPP-2026-06-18-lopez-salido-es-or.pdf" target="_blank" rel="noopener">no se veía desde la burbuja de 2007</a> y es <a href="https://www.cje.org/download/313/ano-2025/23618/2025-balance-general.pdf" target="_blank" rel="noopener">la juventud</a> la clase más afectada —los y las y les menores de 35 años—.',
        `En ${provs} la vivienda está disparada, según datos del ${ine} y los informes de precios en ${ide} de Idealista. Aquí es donde objetivamente podría ser un factor decisivo.`,
        'Si la izquierda —el espacio que lleva en sus <a href="https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf" target="_blank" rel="noopener">manifiestos</a> <a href="https://www.psoe.es/media-content/2023/07/PROGRAMA_ELECTORAL-GENERALES-2023.pdf" target="_blank" rel="noopener">políticos</a> <a href="https://static.esquerra.cat/uploads/20230705/e2023-programa.pdf" target="_blank" rel="noopener">más</a> <a href="https://www.bng.gal/media/bnggaliza/files/2023/07/05/23_bng_xerais_programa.pdf" target="_blank" rel="noopener">propuestas</a> <a href="https://ehbildu.eus/dokumentuak/23J-COMPROMISO-DE-EUSKAL-HERRIA-BILDU.pdf" target="_blank" rel="noopener">concretas</a> para atajar la problemática— fuese capaz de movilizar a ese electorado, que tiende a quedarse más en casa que sus progenitores cuando se llama a las urnas, el panorama sería muy distinto al que han venido pintando las encuestas. ' +
          (gap > 0
            ? `Aunque no sería suficiente para darle la vuelta al marcador, estarían aún a ${gap} ${gap === 1 ? 'escaño' : 'escaños'} de un pacto PP + Vox.`
            : gap === 0
              ? 'Empatarían en escaños con un pacto PP + Vox.'
              : `Le darían la vuelta al marcador: superarían en ${-gap} ${gap === -1 ? 'escaño' : 'escaños'} a un pacto PP + Vox.`)
      ];
    },
    st: () => vivienda(75)
  },
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
        out.push(`${close.length > 1 ? `Algunos de los escaños, en ${listEs(close.map((id) => BYID[id].n))}, se decidirán` : `El escaño de ${BYID[close[0]].n} se decidirá`} por apenas unos centenares de votos, muy por debajo del típico margen de error de ±3 puntos porcentuales de cualquier encuesta. Ese margen de error explica, en jerga estadística, que si una encuesta dice que el 25% apoya una opción, el apoyo real estaría entre el 22% y el 28%.`);
      // only while most of these seats are in small constituencies (5 seats or fewer)
      if (ids.filter((id) => BYID[id].seats <= 5).length > ids.length / 2)
        out.push(`La mayoría se mueve en circunscripciones pequeñas, lo que sumado al método D'Hondt, eleva el listón a la hora de repartir escaños.`);
      return out;
    },
    st: () => sinUltimoEscano('VOX', 3)
  },
  {
    slug: 'periferia',
    date: '2026-10-28',
    hidden: true,   // maybe next week
    // TEXT PENDING (Xaquín): headline and paragraphs
    title: '¿Y si <strong>el nacionalismo de izquierdas</strong> en Galicia, Cataluña, País Vasco y Navarra galvaniza la resistencia contra la ultraderecha?',
    body: '[Texto pendiente]',
    st: () => periferia()
  }
];

export const ESCENARIOS = LIST.filter((e) => !e.hidden).sort((a, b) => b.date.localeCompare(a.date));
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
/** the young vote's quarters: a quarter each to the PSOE, Frente Amplio and Podemos everywhere; Catalonia and
 *  the Valencian Community swap Podemos for ERC and Compromís; in the Canaries, half to Unidad del Pueblo Canario */
const Q = 0.25;
function quarters(): Pick<Scenario, 'shareNat' | 'shareProv'> {
  const shareProv: Scenario['shareProv'] = {};
  for (const id of CAT) shareProv[id] = { PSOE: Q, FA: Q, ERC: Q };
  for (const id of VAL) shareProv[id] = { PSOE: Q, FA: Q, COMP: Q };
  for (const id of CAN) shareProv[id] = { PSOE: Q, UPC: 2 * Q };
  return { shareNat: { PSOE: Q, FA: Q, PODEMOS: Q }, shareProv };
}
function vivienda(turnoutTo = 75): Partial<Scenario> {
  const turnProv: Scenario['turnProv'] = Object.fromEntries(VIVIENDA_HOT.map((id) => [id, YOUTH_EXTRA]));
  // the national rise that, with the hot provinces' extra points, takes turnout to the target
  let lo = -20, hi = 30;
  for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (run({ ...blank(), turnNat: m, turnProv }).turnout * 100 < turnoutTo) lo = m; else hi = m; }
  return { turnNat: Math.round(hi * 10) / 10, turnProv, ...quarters() };
}

/** The periphery. Three adjustments, by province, worked out on the day's projection:
 *   · ERC reaches ERC_TARGET % of the valid vote in Spain, taking the same share of the voters of the comuns'
 *     list (Frente Amplio) and of the small parties («otros», where the CUP is) in each Catalan province;
 *   · EH Bildu passes BILDU_TARGET votes between the Basque Country and Navarre;
 *   · the BNG reaches BNG_TARGET votes in Galicia.
 *  Bildu and BNG grow by the same proportion in each of their provinces, taking votes from all the other
 *  parties in proportion to their size, as any province adjustment in the simulator. Points to the tenth. */
const ERC_TARGET = 2.5, BILDU_TARGET = 400000, BNG_TARGET = 300000;
const PERI = { CAT: ['08', '17', '25', '43'], EUS_NAV: ['01', '20', '48', '31'], GAL: ['15', '27', '32', '36'] };
const shareOf = (id: string, k: string) => (100 * (BASE.prov[id].votes[k] || 0)) / BASE.prov[id].valid;
const r1 = (x: number) => Math.round(x * 10) / 10;
/** ERC takes a fraction phi of FA's and the small parties' voters in each Catalan province */
function ercFrom(phi: number): Scenario['prov'] {
  return Object.fromEntries(PERI.CAT.map((id) => {
    const fa = shareOf(id, 'FA'), ot = shareOf(id, 'OTROS');
    return [id, { ERC: r1(phi * (fa + ot)), FA: -r1(phi * fa), OTROS: -r1(phi * ot) }];
  }));
}
/** party k grows by the same proportion in the provinces ids until it has `votes` votes there */
function growTo(ids: string[], k: string, votes: number): Scenario['prov'] {
  const at = (f: number) => Object.fromEntries(ids.map((id) => [id, { [k]: Math.ceil(shareOf(id, k) * (f - 1) * 10) / 10 }]));
  const got = (f: number) => { const R = run({ ...blank(), prov: at(f) }); return ids.reduce((a, id) => a + (R.prov[id].votes[k] || 0), 0); };
  let lo = 1, hi = 4;
  for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; if (got(m) >= votes) hi = m; else lo = m; }
  return at(hi);
}
export const PERIFERIA = { ERC_TARGET, BILDU_TARGET, BNG_TARGET, ...PERI };
function periferia(): Partial<Scenario> {
  let lo = 0, hi = 1;
  for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; const R = run({ ...blank(), prov: ercFrom(m) }); if ((100 * R.votes.ERC) / R.valid >= ERC_TARGET) hi = m; else lo = m; }
  return { prov: { ...ercFrom(hi), ...growTo(PERI.EUS_NAV, 'BILDU', BILDU_TARGET), ...growTo(PERI.GAL, 'BNG', BNG_TARGET) } };
}

/** Young voters stay home.
 *  · Where the young are: INE, Estadística Continua de Población, 1 July 2026 (table 59591), Spanish nationals,
 *    share of adults aged 18–34 per province (YOUNG_ADULTS; 18–19 taken as 2/5 of the 15–19 group;
 *    datos/ine/jovenes_18_34_prov_2026-07.csv). Nationally 20.8 %.
 *  · How much less they vote: CIS 3493, P0A2 (2023 vote recall by age, «No votó» column): 72.7 % of those aged 18–34
 *    say they voted against 83.0 % of those older (YOUNG_TURNOUT = 0.876). Surveys overstate turnout, but both
 *    groups are measured the same way, so we only use the ratio. With 20.8 % of adults, that makes the young 18.7 %
 *    of voters (3493 itself: 18.1 %).
 *  · How they vote: CIS 3582 (October 2026 barometer, microdata, weighted with PESO), vote + sympathy among those
 *    who name a party or blank: their weight per party relative to all voters (YOUTH_RATIO; e.g. Vox 20.6 % of the
 *    young vs 14.5 % of all = ×1.41). 3582 rather than 3493 because the projection is 2026 intention and 3582 has
 *    852 young respondents; in 3493 the regional parties have 2–12 each.
 *  A fraction `drop` of the young voters in each province do not vote: that province's turnout falls
 *  drop × (young share of its voters) × its turnout, and those who stay home are, party by party, as much more or
 *  less likely as the young are to vote for it.
 *  The polls already carry their own turnout: this is «that many fewer young voters than the polls expect». */
const YOUNG_ADULTS: Record<string, number> = { '01': 0.183, '02': 0.207, '03': 0.213, '04': 0.234, '05': 0.166, '06': 0.208, '07': 0.237, '08': 0.216, '09': 0.173, '10': 0.184, '11': 0.218, '12': 0.206, '13': 0.205, '14': 0.213, '15': 0.169, '16': 0.188, '17': 0.220, '18': 0.222, '19': 0.215, '20': 0.195, '21': 0.217, '22': 0.186, '23': 0.217, '24': 0.155, '25': 0.206, '26': 0.191, '27': 0.143, '28': 0.221, '29': 0.221, '30': 0.238, '31': 0.212, '32': 0.147, '33': 0.152, '34': 0.159, '35': 0.228, '36': 0.179, '37': 0.171, '38': 0.221, '39': 0.176, '40': 0.185, '41': 0.227, '42': 0.173, '43': 0.211, '44': 0.185, '45': 0.214, '46': 0.209, '47': 0.178, '48': 0.181, '49': 0.145, '50': 0.197, '51': 0.302, '52': 0.326 };
const YOUNG_TURNOUT = 72.7 / 83.0;
const YOUTH_RATIO: Record<string, number> = { PSOE: 0.66, PP: 0.82, VOX: 1.41, FA: 1.48, COMP: 1.48, PODEMOS: 0.88, ERC: 1.48,
  SALF: 1.7, JUNTS: 0.89, BILDU: 1.09, BNG: 2.08, AA: 1.64, PNV: 0.75, UPC: 1.29, OTROS: 1.19 };   // CC: as everyone (×1.03)
function jovenes(drop = 0.2): Partial<Scenario> {
  const turnProv: Record<string, number> = {};
  for (const [id, c] of Object.entries(YOUNG_ADULTS)) {
    const v = (c * YOUNG_TURNOUT) / (c * YOUNG_TURNOUT + 1 - c);           // young share of that province's voters
    turnProv[id] = -Math.round(drop * v * BASE.prov[id].turnout * 1000) / 10;
  }
  return { turnProv, distNat: { ...YOUTH_RATIO } };
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
