// Escenarios: concrete «what if» questions, each one a set of adjustments to the poll projection.
// Newest first on the page: the date sorts them; on the same date, the order of this list.
//  · title and body are HTML (title takes <strong> for the bold half, as the section headings)
//  · st: only what the scenario moves; the rest stays as in the projection (same shape as the simulator)
import type { Scenario, RunResult, PartyKey } from './types';
import { blank, run, BASE, provTurnShift, INVEST } from './model';
import { PROV, BYID, DATA } from './data';
import { PARTY, BLOC } from './parties';
import { longDate } from './format';

/** in a body, a paragraph that is only this marker places the adjustments («los supuestos») there */
export const SUPUESTOS = '{{supuestos}}';
/** in a scenario with versions: the seats each one moves (CAMBIOS) and the data behind each (DATOS) */
export const CAMBIOS = '{{cambios}}', DATOS = '{{datos}}';
/** what a scenario's texts can draw on: the adjustments, the result, the projection and the data date */
export interface Ctx { st: Scenario; cur: RunResult; base: RunResult; today: string;
  /** a scenario with versions: each one's result, by key */
  vs?: Record<string, RunResult> }
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
  /** the same question answered with two sources that disagree: the page shows both side by side (seat bars
   *  mirrored, the changes, the data behind each, the adjustments of each) instead of the map; st is the first */
  versions?: Version[];
}
/** one answer to a scenario's question, from one source */
export interface Version {
  key: string;
  /** the source as it reads after «según» / «con»: «el CIS», «40dB» */
  name: string;
  /** HTML link to the source */
  source: string;
  st: () => Partial<Scenario>;
  /** a small bar chart of the data behind it: label, colour key, share among everyone, share in the group (null: not given) */
  chart?: { title: string; group: string; rows: [string, PartyKey, number, number | null][]; note: string };
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
    slug: 'mayores',
    date: '2026-11-09',
    // TEXT PENDING (Xaquín)
    title: '¿Y si <strong>los mayores de 65 años</strong> no salen a votar?',
    body: (c) => {
      const A = c.vs!.cis, B = c.vs!['40db'];
      const cis = '<a href="https://www.cis.es/documents/d/guest/es3582mar_a-pdf" target="_blank" rel="noopener">barómetro de octubre del CIS</a>';
      const db = '<a href="https://ep00.epimg.net/infografias/encuestas40db/2026/10-barometro/2026_10_informe_voto.pdf" target="_blank" rel="noopener">encuesta de 40dB para El País</a>';
      // the turnout drop, and the three provinces where it is largest
      const drop = 100 * (c.base.turnout - A.turnout);
      const most = PROV.map((p) => [p.id, c.base.prov[p.id].turnout - A.prov[p.id].turnout] as [string, number]).sort((x, y) => y[1] - x[1]).slice(0, 3).map(([id]) => BYID[id].n);
      // Vox's gains, province by province, grouped by whom they come from
      const voxFrom = (R: RunResult) => {
        const by: [string, string[]][] = [];
        for (const p of PROV) {
          const d = (k: string) => (R.prov[p.id].seats[k] || 0) - (c.base.prov[p.id].seats[k] || 0);
          if (d('VOX') <= 0) continue;
          const from = Object.keys({ ...R.prov[p.id].seats, ...c.base.prov[p.id].seats }).find((k) => k !== 'VOX' && d(k) < 0) || '';
          const g = by.find(([k]) => k === from);
          if (g) g[1].push(p.n); else by.push([from, [p.n]]);
        }
        // most seats first; on a tie, from the right of the bar (PP before PSOE)
        return by.sort((x, y) => y[1].length - x[1].length || BLOC.indexOf(y[0] as PartyKey) - BLOC.indexOf(x[0] as PartyKey));
      };
      const vA = voxFrom(A), vB = voxFrom(B), dv = (R: RunResult) => (R.seats.VOX || 0) - (c.base.seats.VOX || 0);
      const voxTxt = (R: RunResult, g: typeof vA) => `${dv(R) >= 0 ? 'Sumaría' : 'Perdería'} ${Math.abs(dv(R))} ${Math.abs(dv(R)) === 1 ? 'escaño' : 'escaños'}: ` +
        (g.length === 2 ? (x: string[]) => x.join(', y ') : listEs)(g.map(([k, ps]) => `en ${listEs(ps)}${k ? ', a costa ' + de(k) : ''}`)) + '.';
      const same = JSON.stringify(vA) === JSON.stringify(vB) && dv(A) === dv(B);
      // PSOE and PP, with each source
      const d = (R: RunResult, k: string) => (R.seats[k] || 0) - (c.base.seats[k] || 0);
      const n = (x: number) => `${Math.abs(x)} ${Math.abs(x) === 1 ? 'escaño' : 'escaños'}`;
      const mv = (x: number, pl: boolean, unit = true) => (x > 0 ? (pl ? 'ganarían ' : 'ganaría ') : x < 0 ? (pl ? 'perderían ' : 'perdería ') : '') + (x ? (unit ? n(x) : Math.abs(x)) : (pl ? 'se quedarían igual' : 'se quedaría igual'));
      const [pA, ppA, pB, ppB] = [d(A, 'PSOE'), d(A, 'PP'), d(B, 'PSOE'), d(B, 'PP')];
      const bTxt = pB < 0 && ppB < 0 ? `y ambos perderían: el PSOE ${n(pB)} y el PP ${Math.abs(ppB)}` : `: el PSOE ${mv(pB, false)} y el PP ${mv(ppB, false, false)}`;
      const r0 = (c.base.seats.PP || 0) + (c.base.seats.VOX || 0), rs = [A, B].map((R) => (R.seats.PP || 0) + (R.seats.VOX || 0));
      const lo = Math.min(...rs), hi = Math.max(...rs);
      return [
        `Son mayoría —3 de cada 10 votantes— y son quienes más votan —el 93% vs. el 87% de los jóvenes en el 23J—, según el ${cis}.`,
        `En este escenario suponemos que uno de cada cinco se queda en casa el 29N. La participación bajaría ${aprox(drop)}, más en las provincias más envejecidas como ${listEs(most)}.`,
        SUPUESTOS,
        '¿Y a quién le sale mejor?',
        'A Vox, que tiene un electorado más joven y mucho menos apoyo entre los mayores de 65.',
        '¿Cuánto mejor?',
        'Em ... pues depende de a quién se pregunte.',
        CAMBIOS,
        same ? voxTxt(A, vA) : `Según el CIS, ${voxTxt(A, vA).replace(/^S/, 's').replace(/^P/, 'p')} Según 40dB, ${voxTxt(B, vB).replace(/^S/, 's').replace(/^P/, 'p')}`,
        `Según el CIS, los mayores votan mucho más al PSOE que el resto —el 51 % de los que dicen a quién votarían, frente al 34 % del total—: los socialistas ${mv(pA, true)} y el PP ${mv(ppA, false, false)}. ` +
          `Según la ${db}, en cambio, PSOE y PP empatan entre los mayores, con un 28,2 % cada uno, ${bTxt}.`,
        DATOS,
        `Con una encuesta o con la otra, PP y Vox pasarían de ${r0} a ${lo === hi ? lo : `entre ${lo} y ${hi}`} escaños` +
          (lo >= MAJORITY ? (r0 >= MAJORITY ? ', y ampliarían su mayoría absoluta.' : ', y lograrían la mayoría absoluta.') : '.')
      ];
    },
    st: () => mayores(0.2, OLD_RATIO),
    versions: [
      { key: 'cis', name: 'el CIS', source: '<a href="https://www.cis.es/documents/d/guest/es3582mar_a-pdf" target="_blank" rel="noopener">CIS, barómetro de octubre de 2026</a>',
        st: () => mayores(0.2, OLD_RATIO),
        chart: { title: 'Según el CIS', group: 'Mayores de 65', note: 'Voto más simpatía, sobre quienes dicen un partido o votarían en blanco. Microdatos del estudio 3582, ponderados.',
          rows: [['PSOE', 'PSOE', 34.0, 51.2], ['PP', 'PP', 20.2, 21.5], ['Vox', 'VOX', 14.5, 6.5], ['Sumar', 'FA', 7.1, 3.1], ['Podemos', 'PODEMOS', 2.8, 2.1], ['SALF', 'SALF', 1.5, 0.1]] } },
      { key: '40db', name: '40dB', source: '<a href="https://ep00.epimg.net/infografias/encuestas40db/2026/10-barometro/2026_10_informe_voto.pdf" target="_blank" rel="noopener">40dB para El País, barómetro de octubre de 2026</a>',
        st: () => mayores(0.2, OLD_RATIO_40DB),
        chart: { title: 'Según 40dB', group: 'Mayores de 65', note: 'Intención directa de voto, sobre toda la población (indecisos incluidos). Solo publica las cifras de más del 2 %.',
          rows: [['PSOE', 'PSOE', 22.4, 28.2], ['PP', 'PP', 19.6, 28.2], ['Vox', 'VOX', 19.1, 12.1], ['Sumar', 'FA', 4.4, 3.8], ['Podemos', 'PODEMOS', 2.6, 2.5], ['SALF', 'SALF', 2.2, null]] } }
    ]
  },
  {
    slug: 'vivienda',
    date: '2026-11-10',
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
        '<a href="https://elpais.com/espana/madrid/2026-09-23/maricarmen-se-queda-un-centenar-de-activistas-espera-junto-a-la-anciana-a-la-comision-judicial.html" target="_blank" rel="noopener">El desahucio de Maricarmen</a> fue la chispa. Enseguida llegaron las protestas, la reacción legislativa del gobierno —que tumbó el Congreso—, y la convocatoria electoral.',
        'La vivienda, poder comprar o alquilar, es una de las <a href="https://www.cis.es/documents/d/guest/es3582mar_a-pdf" target="_blank" rel="noopener">mayores preocupaciones</a> de la sociedad española. Es una carga que <a href="https://www.bde.es/f/webbe/SES/Secciones/Publicaciones/PublicacionesAnuales/InformesAnuales/25/Fich/IIPP-2026-06-18-lopez-salido-es-or.pdf" target="_blank" rel="noopener">no se veía desde la burbuja de 2007</a> y es <a href="https://www.cje.org/download/313/ano-2025/23618/2025-balance-general.pdf" target="_blank" rel="noopener">la juventud</a> la clase más afectada —los y las y les menores de 35 años—.',
        `En ${provs} la vivienda está disparada, según datos del ${ine} y los informes de precios en ${ide} de Idealista. Aquí es donde objetivamente podría ser un factor decisivo.`,
        'Si la izquierda —el espacio que en el 23J llevó en sus <a href="https://movimientosumar.es/wp-content/uploads/2023/07/Un-Programa-para-ti.pdf" target="_blank" rel="noopener">manifiestos</a> <a href="https://www.psoe.es/media-content/2023/07/PROGRAMA_ELECTORAL-GENERALES-2023.pdf" target="_blank" rel="noopener">políticos</a> <a href="https://static.esquerra.cat/uploads/20230705/e2023-programa.pdf" target="_blank" rel="noopener">más</a> <a href="https://www.bng.gal/media/bnggaliza/files/2023/07/05/23_bng_xerais_programa.pdf" target="_blank" rel="noopener">propuestas</a> <a href="https://ehbildu.eus/dokumentuak/23J-COMPROMISO-DE-EUSKAL-HERRIA-BILDU.pdf" target="_blank" rel="noopener">concretas</a> para atajar la problemática— fuese capaz de movilizar a los más afectados, el panorama sería muy distinto al que han venido pintando las encuestas. ' +
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
    date: '2026-11-10',
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
        `${top.length > 1 ? 'Se reparten el botín ' + listEs(top.map(art)) : 'Se lleva el botín ' + art(top[0])}. En este escenario, con los datos de las encuestas a ${longDate(c.today)}, Vox pierde ${lost} ${lost === 1 ? 'escaño' : 'escaños'} a favor ${listEs(gain.map(([k]) => de(k)))}.`
      ];
      if (close.length)
        out.push(`${close.length > 1 ? `Algunos de los escaños, en ${listEs(close.map((id) => BYID[id].n))}, se decidirán` : `El escaño de ${BYID[close[0]].n} se decidirá`} por apenas unos centenares de votos, muy por debajo del típico <a href="https://www.aimc.es/a1mc-c0nt3nt/uploads/2016/10/2016_09rev_aedemo_los_margenes_de_error_en_las_encuestas_electorales.pdf" target="_blank" rel="noopener">margen de error</a> de <a href="https://www.cuadernosdeperiodistas.com/encuestas-y-margen-de-error-una-guia-practica/" target="_blank" rel="noopener">±3 puntos porcentuales</a> de cualquier encuesta. Ese margen de error explica, en jerga estadística, que si una encuesta dice que el 25% apoya una opción, el apoyo real estaría entre el 22% y el 28%.`);
      // only while most of these seats are in small constituencies (5 seats or fewer)
      const small = ids.filter((id) => BYID[id].seats <= 5);
      if (small.length > ids.length / 2) {
        const ts = small.map((id) => Math.round(100 * effThreshold(c.base, id)));
        const lo = Math.min(...ts), hi = Math.max(...ts);
        const range = lo === hi ? `en torno al ${lo} %` : `entre el ${lo} % y el ${hi} %, según la provincia`;
        out.push(`La mayoría de esos escaños están en provincias pequeñas —con cinco escaños o menos—. Con tan pocos en juego, el método D'Hondt exige mucho voto para conseguir uno —<a href="https://preprints.apsanet.org/engage/api-gateway/apsa/assets/orp/resource/item/6a958e3fd1922e37d5d26525/original/estimating-effective-electoral-thresholds-a-logical-model.pdf" target="_blank" rel="noopener">${range}</a>— y Vox los gana por poco. Un pequeño cambio y ... zas, cambia de manos.`);
      }
      return out;
    },
    st: () => sinUltimoEscano('VOX', 3)
  },
  {
    slug: 'periferia',
    date: '2026-11-10',
    title: '¿Y si <strong>el nacionalismo de izquierdas</strong> en Galicia, Cataluña, País Vasco y Navarra galvaniza la resistencia contra la ultraderecha?',
    body: (c) => {
      const P = PERIFERIA;
      const inBase = (k: string, ids: string[]) => ids.reduce((a, id) => a + (c.base.prov[id].votes[k] || 0), 0);
      const inCur = (k: string, ids: string[]) => ids.reduce((a, id) => a + (c.cur.prov[id].votes[k] || 0), 0);
      const ercPct = ((100 * (c.base.votes.ERC || 0)) / c.base.valid).toFixed(1).replace('.', ',');
      const bng = seatMoves(c, 'BNG', P.GAL), erc = seatMoves(c, 'ERC', P.CAT), bildu = seatMoves(c, 'BILDU', P.EUS_NAV);
      const right = (k: 'base' | 'cur') => (c[k].seats.PP || 0) + (c[k].seats.VOX || 0);
      const r0 = right('base'), r1 = right('cur'), over = r1 - MAJORITY;
      const n = (x: number) => (x === 1 ? 'escaño' : 'escaños');
      // «El BNG ganaría 2 escaños, en A Coruña y Lugo, arrebatados a Vox y al PP.»
      const gainTxt = (k: string, m: SeatMoves, first: boolean) =>
        m.won
          ? `${cap(art(k))} ${first ? `ganaría ${m.won} ${n(m.won)}` : `sumaría otros ${m.won}`}, en ${listEs(m.provs.map((id) => BYID[id].n))}, ${first ? 'arrebatados ' + listEs(m.from.map(al)) : 'a costa ' + listEs(m.from.map(de))}.`
          : `${cap(art(k))} no ganaría ningún escaño.`;
      return [
        'Tenemos un <a href="https://www.congreso.es/webpublica/estudios/Parlamento_fragmentado_y_forma_Gobierno.pdf" target="_blank" rel="noopener">parlamento fragmentado</a> —desde hace varias legislaturas— y una izquierda más fragmentada aún.',
        `Podría darse que la izquierda <a href="https://www.cepc.gob.es/sites/default/files/2026-07/41172rep21205leon-saez-de-ybarrayleon-ranero.pdf" target="_blank" rel="noopener"><em>periférica</em></a> fuese la que más se movilizase ante la posibilidad de que Vox entrase en el gobierno. Este escenario supone que ERC pesca parte del electorado de los <a href="https://www.ara.cat/politica/eleccions-generals/batalles-amaga-29-n-catalunya_1_5900233.html" target="_blank" rel="noopener">Comuns</a> y la <a href="https://en.ara.cat/politics/the-psc-would-win-the-spanish-and-catalan-elections-with-erc-and-alianca-disputing-second-place_1_5878621.html" target="_blank" rel="noopener">CUP</a>, EH Bildu supera los ${thousands(P.BILDU_TARGET)} votos entre Euskadi y Navarra, y el BNG llega a los ${thousands(P.BNG_TARGET)} en Galicia.`,
        `Sí, sería un salto enorme para el BNG, que pasaría de ${thousands(inBase('BNG', P.GAL))} votos en nuestra proyección a ${thousands(P.BNG_TARGET)}, pero los gallegos <a href="https://www.eldiario.es/galicia/ana-ponton-lleva-bng-techo-historico-25-diputados-queda-lejos-presidencia_1_10935676.html" target="_blank" rel="noopener">rompieron su techo</a> en las autonómicas de 2024 con 470 mil votos. Nuestro escenario plantea que mantengan menos de dos tercios de esos votantes.`,
        `Las demás organizaciones subirían más modestamente: EH Bildu sumaría ${thousands(inCur('BILDU', P.EUS_NAV) - inBase('BILDU', P.EUS_NAV))} más, y ERC ya ronda el ${ercPct}% en nuestra proyección.`,
        'A pesar de todo, el resultado mueve poco el dial. ' + gainTxt('BNG', bng, true) + ' ' + (erc.won ? gainTxt('ERC', erc, false) : 'ERC no ganaría ningún escaño.') + ' ' +
          (bildu.won
            ? gainTxt('BILDU', bildu, false)
            : `EH Bildu, pese a crecer, se quedaría con los mismos ${c.cur.seats.BILDU || 0} ${n(c.cur.seats.BILDU || 0)}: el voto de más no le basta para el siguiente escaño en ninguna de sus provincias.`),
        `PP y Vox ${r1 < r0 ? 'bajarían' : r1 > r0 ? 'subirían' : 'se quedarían'} ${r1 === r0 ? 'en ' + r1 : 'de ' + r0 + ' a ' + r1} escaños y ` +
          (over > 0 ? `seguirían ${over} por encima de la mayoría absoluta.` : over === 0 ? 'se quedarían justo en la mayoría absoluta.' : `se quedarían ${-over} por debajo de la mayoría absoluta.`)
      ];
    },
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

/** Voters over 65 stay home.
 *  · Where they are: INE, Estadística Continua de Población, 1 July 2026 (table 59591), Spanish nationals, share of
 *    adults aged 65 and over per province (OLD_ADULTS; datos/ine/edades_prov_2026-07.csv). Nationally 27.9 %.
 *  · How much more they vote: CIS 3582 (October 2026 barometer, microdata, weighted with PESO), 2023 vote recall:
 *    93.2 % of those 65 and over say they voted against 86.5 % of those younger (OLD_TURNOUT = 1.077). Surveys
 *    overstate turnout, but both groups are measured the same way, so we only use the ratio. (The same barometer
 *    gives 18–34 vs older 79.0 / 90.5 = 0.87, as CIS 3493 P0A2 does: 72.7 / 83.0 = 0.88.) With 27.9 % of adults,
 *    that makes them 29.4 % of voters (3582 itself: 29.6 %).
 *  · How they vote: CIS 3582, vote + sympathy among those who name a party or blank: their weight per party
 *    relative to all voters (OLD_RATIO; e.g. PSOE 51.2 % of those over 65 vs 34.0 % of all = ×1.50); 980
 *    respondents over 65. Sumar for FA and Compromís, «Coalición de izquierdas» for UPC, «Otro partido» for OTROS;
 *    CC as everyone (no respondents over 65).
 *  A fraction `drop` of the voters over 65 in each province do not vote: that province's turnout falls
 *  drop × (their share of its voters) × its turnout, and those who stay home are, party by party, as much more or
 *  less likely as those over 65 are to vote for it.
 *  The polls already carry their own turnout: this is «that many fewer voters over 65 than the polls expect». */
const OLD_ADULTS: Record<string, number> = { '01': 0.309, '02': 0.279, '03': 0.267, '04': 0.236, '05': 0.351, '06': 0.275, '07': 0.235, '08': 0.280, '09': 0.336, '10': 0.317, '11': 0.248, '12': 0.285, '13': 0.289, '14': 0.276, '15': 0.325, '16': 0.325, '17': 0.276, '18': 0.262, '19': 0.240, '20': 0.317, '21': 0.253, '22': 0.323, '23': 0.275, '24': 0.362, '25': 0.302, '26': 0.311, '27': 0.375, '28': 0.265, '29': 0.243, '30': 0.237, '31': 0.289, '32': 0.392, '33': 0.350, '34': 0.356, '35': 0.221, '36': 0.306, '37': 0.355, '38': 0.238, '39': 0.314, '40': 0.323, '41': 0.240, '42': 0.350, '43': 0.284, '44': 0.335, '45': 0.261, '46': 0.276, '47': 0.322, '48': 0.322, '49': 0.394, '50': 0.305, '51': 0.188, '52': 0.185 };
const OLD_TURNOUT = 93.2 / 86.5;
const OLD_RATIO: Record<string, number> = { PSOE: 1.5, PP: 1.06, VOX: 0.45, FA: 0.44, COMP: 0.44, PODEMOS: 0.74, ERC: 0.79,
  SALF: 0.05, JUNTS: 1.59, BILDU: 1.0, BNG: 0.63, AA: 0.37, PNV: 1.68, UPC: 0.89, OTROS: 0.86 };
/** The same, as 40dB has it (barometer for El País, October 2026, direct vote intention among the whole
 *  population: share among those 65 and over ÷ share among all). Parties it does not break down (or gives
 *  under 2 % for those over 65) vote as everyone (×1). */
const OLD_RATIO_40DB: Record<string, number> = { PSOE: 28.2 / 22.4, PP: 28.2 / 19.6, VOX: 12.1 / 19.1, FA: 3.8 / 4.4, COMP: 3.8 / 4.4, PODEMOS: 2.5 / 2.6 };
function mayores(drop = 0.2, ratio: Record<string, number> = OLD_RATIO): Partial<Scenario> {
  const turnProv: Record<string, number> = {};
  for (const [id, c] of Object.entries(OLD_ADULTS)) {
    const v = (c * OLD_TURNOUT) / (c * OLD_TURNOUT + 1 - c);              // over-65 share of that province's voters
    turnProv[id] = -Math.round(drop * v * BASE.prov[id].turnout * 1000) / 10;
  }
  return { turnProv, distNat: { ...ratio } };
}

// ── helpers for the texts ───────────────────────────────────────────────────────────────────────
const MAJORITY = 176;
/** 3,9 → «casi cuatro puntos»; 4,0 → «cuatro puntos»; 4,2 → «algo más de cuatro puntos» */
const WORDS = ['cero', 'un', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez'];
function aprox(x: number): string {
  const r = Math.round(x), w = r === 1 ? 'un punto' : `${WORDS[r] ?? r} puntos`;
  return Math.abs(x - r) < 0.05 ? w : x < r ? 'casi ' + w : 'algo más de ' + w;
}
const cap = (t: string) => t.charAt(0).toUpperCase() + t.slice(1);
/** 240000 → «240.000», to the thousand */
const thousands = (x: number) => String(Math.round(x / 1000) * 1000).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
/** «al» + party, with «a» where it takes no article */
const al = (k: string) => (ART[k as PartyKey] ? 'al ' + ART[k as PartyKey]!.slice(3) : 'a ' + PARTY[k as PartyKey].n);
interface SeatMoves { won: number; provs: string[]; from: string[] }
/** seats party P wins against the projection in provinces ids, where, and from whom (parties that lose seats there) */
function seatMoves(c: Ctx, P: string, ids: string[]): SeatMoves {
  const provs: string[] = [], from: string[] = [];
  let won = 0;
  for (const id of ids) {
    const d = (k: string) => (c.cur.prov[id].seats[k] || 0) - (c.base.prov[id].seats[k] || 0);
    if (d(P) <= 0) continue;
    won += d(P); provs.push(id);
    for (const k of Object.keys({ ...c.cur.prov[id].seats, ...c.base.prov[id].seats })) if (k !== P && d(k) < 0 && !from.includes(k)) from.push(k);
  }
  return { won, provs, from };
}
/** Effective threshold of a province: the vote share at which a party has an even chance of its first seat.
 *  Bailey (2026), «Estimating Effective Electoral Thresholds: A Logical Model», eq. 8:
 *  t = (1 − θ)·min(tR, tX) + θ·tX, with tR = 1/(m·n), tX = 1/(m+1), θ = 1 − (1 − 1/n)^m,
 *  m = seats, n = effective number of parties by votes (Laakso–Taagepera, 1/Σv², on the projection; «otros» as one). */
function effThreshold(R: RunResult, id: string): number {
  const v = Object.values(R.prov[id].votes), T = v.reduce((a, x) => a + x, 0);
  const n = 1 / v.reduce((a, x) => a + (x / T) ** 2, 0), m = BYID[id].seats;
  const tR = 1 / (m * n), tX = 1 / (m + 1), th = 1 - (1 - 1 / n) ** m;
  return (1 - th) * Math.min(tR, tX) + th * tX;
}
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
