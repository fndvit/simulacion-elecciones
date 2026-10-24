<script lang="ts">
  // Metodología: the whole method, step by step, with the live numbers the model uses today
  // (pollster ratings, house effects, weights). After the atlas's «De dónde vienen los datos».
  import PageHead from '$lib/components/PageHead.svelte';
  import { DATA } from '$lib/data';
  import { PARTY } from '$lib/parties';
  import { fmtN, dec, longDate } from '$lib/format';
  import { href } from '$lib/nav';

  const nPolls = DATA.polls.length;
  const firms = new Set(DATA.polls.map((p) => p.f)).size;

  // ── weights of one poll ───────────────────────────────────────────────
  const weights = [
    { k: 'Recencia', f: `0,5 ^ (días / ${dec(DATA.halfLife, 0)})`, d: `El peso se reduce a la mitad cada ${dec(DATA.halfLife, 0)} días desde el último día de campo.` },
    { k: 'Muestra', f: '√(min(n, 3.000) ÷ 1.000)', d: 'Más entrevistas, más peso, con tope en 3.000. Si la muestra no se publica se supone n = 800.' },
    { k: 'Valoración', f: '0,6 – 1,4', d: 'Multiplicador según el acierto de la empresa en las generales de 2023 (tabla abajo). Sin historial: 0,85.' },
    { k: 'Frecuencia', f: '1 ÷ √k', d: 'k = encuestas de la misma empresa en los últimos 30 días: quien publica mucho reparte su peso.' }
  ];

  // ── pollster ratings (2023) ───────────────────────────────────────────
  // re-estimates of CIS microdata count as unrated, whatever their 2023 record
  const ratings = Object.entries(DATA.ratings)
    .filter(([f]) => !f.startsWith('CIS ('))
    .map(([f, [mae, w]]) => ({ f, mae, w }))
    .sort((a, b) => b.w - a.w || a.mae - b.mae);

  // ── house effects of the firms with more polls ────────────────────────
  const HE_P = ['PP', 'PSOE', 'VOX', 'SUMAR'] as const;
  const heLab: Record<string, string> = { PP: 'PP', PSOE: 'PSOE', VOX: 'Vox', SUMAR: 'Sumar/FA' };
  const houses = Object.entries(DATA.he)
    .map(([f, v]) => ({ f, v, n: DATA.heN[f] ?? 0 }))
    .filter((h) => h.n >= 5)
    .sort((a, b) => b.n - a.n);
  const sgn = (x: number | undefined) => { if (x == null) return '–'; const r = Math.round(x * 10) / 10; return (r > 0 ? '+' : r < 0 ? '−' : '') + dec(Math.abs(r)); };

  // ── today's national average (after correcting house effects) ─────────
  const ORDERED = Object.entries(DATA.S).filter(([k]) => k !== 'OTROS').sort((a, b) => b[1] - a[1]);
  const name = (k: string) => PARTY[k as keyof typeof PARTY]?.n ?? k;

  // ── election weights for the provincial profile ───────────────────────
  const ELEC: Record<string, string> = { g2023: 'Generales de julio de 2023', g2019n: 'Generales de noviembre de 2019', g2019a: 'Generales de abril de 2019' };

  // ── party lineages ────────────────────────────────────────────────────
  const lineage = [
    { k: 'Frente Amplio', e23: 'Sumar (en la Comunidad Valenciana, la mitad del voto de Sumar-Compromís)', e19: 'Unidas Podemos + Más País' },
    { k: 'Compromís', e23: 'la otra mitad de Sumar-Compromís', e19: 'Compromís (Més Compromís)' },
    { k: 'Podemos', e23: '— (iba dentro de Sumar)', e19: 'Unidas Podemos' },
    { k: 'PP', e23: 'PP', e19: 'PP (en Navarra no cuenta: fue con Navarra Suma)' },
    { k: 'UPN', e23: 'UPN', e19: '— (dentro de Navarra Suma)' },
    { k: 'SALF', e23: '—', e19: '—', note: 'Sin historial: mitad perfil uniforme, mitad el de Vox' },
    { k: 'Aliança Catalana', e23: '—', e19: '—', note: 'Sin historial: uniforme en las cuatro provincias catalanas' },
    { k: 'Adelante Andalucía', e23: 'Adelante Andalucía', e19: '—', note: 'Perfil supuesto, más fuerte en Cádiz y Sevilla' }
  ];

  // ── sources ───────────────────────────────────────────────────────────
  const sources = [
    { q: 'Encuestas', s: 'Recopilación de sondeos publicados de Wikipedia en español (empresas demoscópicas, medios y CIS)', u: 'https://es.wikipedia.org/wiki/Encuestas_de_opini%C3%B3n_para_las_elecciones_generales_de_Espa%C3%B1a_de_2026', d: 'Cada día' },
    { q: 'Resultados electorales', s: 'Ministerio del Interior, infoelectoral: generales de abril y noviembre de 2019 y julio de 2023, por circunscripción', u: 'https://infoelectoral.interior.gob.es', d: 'Fijo' },
    { q: 'Censo y escaños del 29N', s: 'Real decreto de convocatoria y censo electoral (incluidos los residentes en el extranjero)', u: '', d: 'Fijo' },
    { q: 'Valoración de las empresas', s: 'Último sondeo publicado por cada empresa antes del 23J de 2023, frente al resultado', u: '', d: 'Fijo' },
    { q: 'Límites provinciales', s: 'es-atlas (Instituto Geográfico Nacional)', u: 'https://github.com/martgnz/es-atlas', d: 'Fijo' },
    { q: 'Cartograma de hexágonos', s: 'A partir del de El Confidencial', u: '', d: 'Fijo' }
  ];

  const REPO = 'https://github.com/fndvit/simulacion-elecciones';
  const bibtex = `@misc{trescincuenta_29n,
  title        = {TresCincuenta.es: proyección del reparto de escaños del Congreso para las elecciones generales del 29 de noviembre de 2026},
  author       = {{Fundació ViT, Visualització per a la Transparència}},
  year         = {2026},
  howpublished = {\\url{https://trescincuenta.es}},
  note         = {Modelo, datos y aplicación web}
}`;
  let copied = $state(false);
  async function copyBib() {
    try { await navigator.clipboard.writeText(bibtex); copied = true; setTimeout(() => (copied = false), 1600); } catch { /* no clipboard */ }
  }

  // the pipeline, top to bottom
  const steps = [
    { t: 'Encuestas', d: 'Wikipedia, cada mañana', c: '#d1366b' },
    { t: 'Validación', d: 'o se mantiene el último día bueno', c: '#db4540' },
    { t: 'Media ponderada', d: 'recencia · muestra · acierto · frecuencia', c: '#edc747' },
    { t: 'Sesgo de cada empresa', d: 'se resta antes de promediar', c: '#759ac6' },
    { t: 'Reparto por provincias', d: 'perfil de 2019–2023 + ajuste iterativo', c: '#275aa3' },
    { t: 'Escaños', d: "D'Hondt con barrera del 3 %", c: '#5db9ae' },
    { t: 'Web', d: 'proyección, simulador y mapa', c: '#7bba56' }
  ];
</script>

<svelte:head>
  <title>Metodología · TresCincuenta.es</title>
  <meta name="description" content="Cómo se calcula la proyección de TresCincuenta.es: de qué encuestas sale la media, cómo se pondera cada una, cómo se corrige el sesgo de cada empresa, cómo se reparte el voto por provincias y cómo se asignan los 350 escaños." />
</svelte:head>

<PageHead
  kicker="Metodología"
  title="Cómo se calcula <strong>la proyección</strong>"
  lede="De qué encuestas sale la media, cuánto pesa cada una, cómo se corrige el sesgo de cada empresa, cómo se reparte el voto entre las 52 circunscripciones y cómo se asignan los <strong>350 escaños</strong>. Todo el código es abierto y cada número se puede rastrear hasta su fuente." />

<section class="page">
  <div class="prose well">
    <p>
      TresCincuenta.es <strong>no es un pronóstico</strong>. Es una <strong>proyección</strong>: traduce a escaños lo que dicen hoy las
      encuestas publicadas, con un método explícito y reproducible. No estima la incertidumbre, no asigna probabilidades ni
      intenta anticipar cómo cambiará la intención de voto hasta el 29 de noviembre. El simulador, por su parte, es una
      <strong>calculadora de supuestos</strong>: parte de la proyección y deja que cada cual mueva votos y vea qué pasa con los escaños.
    </p>
    <p>
      El método sigue la escuela de FiveThirtyEight —el sitio que popularizó Nate Silver en Estados Unidos—, adaptada al sistema
      español: una <strong>media ponderada</strong> que da más peso a las encuestas recientes, grandes y de empresas demoscópicas que
      acertaron en 2023; una <strong>corrección del sesgo</strong> sistemático de cada empresa; un <strong>reparto por provincias</strong>
      según dónde ha sido más fuerte o más débil cada partido en las tres últimas generales, y el <strong>D'Hondt</strong> de cada
      circunscripción. Hoy la media usa <strong>{nPolls} encuestas</strong> de <strong>{firms} empresas o medios</strong>, publicadas desde
      octubre de 2025; los datos son del {longDate(DATA.today)}.
    </p>
  </div>

  <figure class="fig">
    <ol class="pipe">
      {#each steps as s, i}
        <li style="--c:{s.c}"><span class="n">{i + 1}</span><b>{s.t}</b><span class="d">{s.d}</span></li>
      {/each}
    </ol>
    <figcaption>El recorrido del dato, cada mañana: de la recopilación de encuestas a la web. Los resultados de 2019 y 2023 entran en el paso 5; el censo y los escaños del 29N, en el 6.</figcaption>
  </figure>

  <!-- ── polls ─────────────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>1. Las <strong>encuestas</strong></h2>
    <p>
      La materia prima es la tabla de sondeos publicados que mantiene la comunidad de Wikipedia en español para estas elecciones.
      Cada mañana se descarga con la API de Wikipedia (con tres intentos), se lee fila a fila y se normaliza: empresa y medio,
      fechas de campo, tamaño de la muestra y estimación de voto de cada partido, en porcentaje del voto válido. Cuenta el
      <strong>último día de campo</strong>, no la fecha de publicación.
    </p>
    <p>
      Se incluyen la estimación del <strong>CIS</strong> y las <strong>reestimaciones de sus microdatos</strong> que publican otras
      empresas («CIS (Target Point)», «CIS (Ateneo del Dato)»…). Como todas salen de la misma encuesta, comparten un único presupuesto
      de peso por frecuencia, y las reestimaciones no tienen valoración propia (cuentan como empresa sin historial).
    </p>
    <h3>Sumar, Frente Amplio y Compromís</h3>
    <p>
      La mayoría de los sondeos todavía publica una sola cifra para el espacio de Sumar. Las encuestas que dan Compromís por
      separado fijan su peso dentro de ese espacio: de media, el <strong>{dec(DATA.compSplit * 100, 0)} %</strong>. Con esa proporción
      se divide la cifra conjunta entre Frente Amplio y Compromís en todas las encuestas.
    </p>
  </div>

  <!-- ── weighted average ──────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>2. La <strong>media ponderada</strong></h2>
    <p>
      Cada encuesta pesa el producto de cuatro factores. Ninguno descarta encuestas: las viejas, pequeñas o de empresas que fallaron
      cuentan menos, pero cuentan.
    </p>
    <table class="tbl">
      <caption>Peso de una encuesta = recencia × muestra × valoración × frecuencia</caption>
      <thead><tr><th>Factor</th><th>Fórmula</th><th>Qué hace</th></tr></thead>
      <tbody>
        {#each weights as w}<tr><td class="k">{w.k}</td><td class="mono nowrap">{w.f}</td><td>{w.d}</td></tr>{/each}
      </tbody>
    </table>
    <p>
      Para cada partido, la media es el promedio de sus estimaciones con esos pesos, ya corregidas del sesgo de cada empresa (paso 3).
      La línea del gráfico de la proyección repite el cálculo semana a semana con lo que se sabía en cada fecha. La tabla de
      encuestas de la página principal muestra el peso que tiene hoy cada una.
    </p>

    <h3>La valoración de las empresas demoscópicas</h3>
    <p>
      Para cada empresa se toma su <strong>último sondeo publicado antes del 23J de 2023</strong> y se calcula su error medio absoluto
      en PP, PSOE, Vox y Sumar. El multiplicador es <code>(error medio de todas ÷ error de la empresa)²</code>, acotado entre 0,6 y 1,4:
      las que más acertaron pesan hasta un 40 % más; las que más fallaron, un 40 % menos.
    </p>
    <table class="tbl">
      <caption>Valoración · error en las generales de 2023 y multiplicador</caption>
      <thead><tr><th>Empresa</th><th class="r">Error medio (puntos)</th><th class="r">Multiplicador</th></tr></thead>
      <tbody>
        {#each ratings as r}<tr><td>{r.f}</td><td class="r num">{dec(r.mae)}</td><td class="r num"><span class="bar" style="width:{Math.round(r.w * 40)}px"></span>{dec(r.w)}</td></tr>{/each}
        <tr><td class="muted">Sin historial en 2023</td><td class="r num muted">–</td><td class="r num"><span class="bar" style="width:34px"></span>0,85</td></tr>
      </tbody>
    </table>
  </div>

  <!-- ── house effects ─────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>3. El <strong>sesgo</strong> de cada empresa</h2>
    <p>
      Algunas empresas dan sistemáticamente más (o menos) a un partido que el resto. Para medirlo, cada encuesta se compara con la
      media de las <strong>demás empresas</strong> en una ventana de ±21 días (ponderada por cercanía en el tiempo y tamaño de muestra).
      La desviación media de cada empresa con cada partido es su <strong>efecto de la casa</strong>.
    </p>
    <p>
      Con pocas encuestas esa desviación es ruidosa, así que se <strong>encoge hacia cero</strong>: se multiplica por <code>k ÷ (k + 4)</code>,
      donde <code>k</code> es el número de encuestas de la empresa. Con 4 encuestas se aplica la mitad; con 36, el 90 %. El efecto se
      resta a cada estimación antes de promediar.
    </p>
    <table class="tbl">
      <caption>Efecto de la casa hoy · puntos por encima (+) o por debajo (−) del resto · empresas con 5 encuestas o más</caption>
      <thead><tr><th>Empresa</th><th class="r">Encuestas</th>{#each HE_P as p}<th class="r">{heLab[p]}</th>{/each}</tr></thead>
      <tbody>
        {#each houses as h}
          <tr><td>{h.f}</td><td class="r num muted">{h.n}</td>{#each HE_P as p}<td class="r num" class:pos={(h.v[p] ?? 0) >= 0.5} class:neg={(h.v[p] ?? 0) <= -0.5}>{sgn(h.v[p])}</td>{/each}</tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- ── national average today ────────────────────────────────────────── -->
  <div class="prose well">
    <h3>La media de hoy</h3>
    <p>El resultado de los pasos 1 a 3 es una estimación nacional por partido, en porcentaje del voto válido:</p>
    <div class="avg">
      {#each ORDERED as [k, v]}
        <div class="row"><span class="nm"><i style="background:{PARTY[k as keyof typeof PARTY]?.c}"></i>{name(k)}</span><span class="track"><span style="width:{(v / ORDERED[0][1]) * 100}%;background:{PARTY[k as keyof typeof PARTY]?.c}"></span></span><span class="num">{dec(v)} %</span></div>
      {/each}
    </div>
  </div>

  <!-- ── provinces ─────────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>4. De España a las <strong>provincias</strong></h2>
    <p>
      Las encuestas son nacionales, pero los escaños se reparten en 52 circunscripciones. Para bajar la media a cada provincia se usa
      el <strong>perfil territorial</strong> de cada partido: su fuerza relativa en cada circunscripción, es decir, su porcentaje allí
      dividido por su porcentaje en toda España. Un partido con índice 1,5 en una provincia saca allí un 50 % más que su media nacional.
    </p>
    <table class="tbl">
      <caption>Elecciones que forman el perfil territorial</caption>
      <thead><tr><th>Elección</th><th class="r">Peso</th></tr></thead>
      <tbody>
        {#each Object.entries(DATA.wElec) as [e, w]}<tr><td>{ELEC[e] ?? e}</td><td class="r num">{dec(w, 2)}</td></tr>{/each}
      </tbody>
    </table>
    <p>
      El índice final es el promedio ponderado de los tres. Si un partido no se presentó en una provincia en una de esas elecciones,
      ese año no cuenta para esa provincia (no se toma como apoyo cero): por ejemplo, Vox en Santa Cruz de Tenerife en 2023.
    </p>
    <h3>Las familias de partidos</h3>
    <p>Entre 2019 y 2026 el espacio a la izquierda del PSOE se ha recompuesto. Cada partido de hoy hereda el perfil de sus antecesores:</p>
    <table class="tbl">
      <caption>Continuidad de los partidos</caption>
      <thead><tr><th>Partido en 2026</th><th>En 2023</th><th>En 2019</th></tr></thead>
      <tbody>
        {#each lineage as l}<tr><td class="k">{l.k}</td><td>{l.e23}</td><td>{l.e19}{#if l.note}<div class="muted small">{l.note}</div>{/if}</td></tr>{/each}
      </tbody>
    </table>
    <h3>El ajuste</h3>
    <p>
      Multiplicar la media nacional por el índice de cada provincia no basta: las provincias no suman exactamente la media nacional
      y cada provincia tiene que sumar el 100 % de su voto válido. Se resuelve con un <strong>ajuste proporcional iterativo</strong>
      (<em>raking</em>): se escala cada partido hasta que la suma de provincias reproduce su media nacional, después se escala cada
      provincia hasta que suma su voto válido menos el blanco, y se repite hasta que las dos condiciones se cumplen a la vez. El voto a
      otras candidaturas y en blanco de cada provincia parte del de 2023.
    </p>
  </div>

  <!-- ── census, turnout, seats ────────────────────────────────────────── -->
  <div class="prose well">
    <h2>5. Censo, participación y <strong>escaños</strong></h2>
    <p>
      El censo del 29N es de <strong>{fmtN(DATA.census)} electores</strong>, incluidos los residentes en el extranjero, repartido entre
      provincias en proporción al de 2023. La participación, el voto nulo y el voto en blanco de cada provincia son los de las generales
      de 2023; el simulador permite cambiar la participación.
    </p>
    <p>
      Los escaños son los de la convocatoria: respecto a 2023, <strong>Madrid pasa de 37 a 38 y Cádiz de 9 a 8</strong>. En cada
      circunscripción se aplica la <strong>regla D'Hondt</strong> con la barrera legal del <strong>3 % del voto válido</strong> (el blanco
      cuenta como válido), como fija la LOREG. Ceuta y Melilla eligen un diputado cada una. Como comprobación, el mismo código reproduce
      los repartos oficiales de abril de 2019, noviembre de 2019 y julio de 2023 en las 52 circunscripciones.
    </p>
    <h3>El último escaño</h3>
    <p>
      Para cada circunscripción se identifica el escaño asignado con el cociente más bajo —el más frágil— y el partido que más cerca está
      de quitárselo: los votos que le faltan para superar ese cociente o, si está por debajo, para cruzar el 3 %. Es lo que muestran «el
      escaño más volátil» y la tabla de escaños más ajustados.
    </p>
  </div>

  <!-- ── simulator ─────────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>6. El <strong>simulador</strong></h2>
    <p>Los controles mueven <strong>votos</strong>, nunca escaños. Después de cada cambio se recalcula el D'Hondt de las 52 circunscripciones.</p>
    <ul>
      <li><strong>Un partido en toda España.</strong> Su nuevo porcentaje nacional se reparte entre provincias en proporción a los votos que ya tiene en cada una, con el mismo ajuste iterativo del paso 4. El resto de partidos cede (o gana) votos en proporción a su tamaño, provincia a provincia.</li>
      <li><strong>Un partido en una provincia.</strong> El cambio solo afecta a esa provincia; los demás partidos de esa provincia lo absorben en proporción a su tamaño.</li>
      <li><strong>La participación.</strong> Añade o quita votantes en cada provincia (nacional y, además, por provincia), entre el 20 % y el 98 % del censo.</li>
      <li><strong>Los que se suman.</strong> Por defecto, los nuevos votantes votan como el resto (×1). Cada partido puede captar entre nada (×0) y cuatro veces su parte (×4) de esos votantes. Sin cambio de participación, este control no tiene efecto.</li>
    </ul>
    <p>
      El escenario se guarda en el navegador y se puede compartir: el enlace lleva codificados todos los cambios. Es una calculadora de
      supuestos: no dice qué es probable, solo qué pasaría si.
    </p>
  </div>

  <!-- ── transfers & map ───────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>7. Transferencias de voto y <strong>mapa</strong></h2>
    <p>
      El diagrama de transferencias compara, en cada circunscripción, el voto de 2023 (con la abstención sobre el censo de 2026) con la
      proyección. Cada opción conserva todo el voto que puede —Sumar pasa a Frente Amplio, Compromís y Podemos— y lo que pierde se
      reparte entre las que crecen, en proporción a lo que crecen; la abstención cierra la cuenta. Es el <strong>trasvase mínimo</strong>
      compatible con los dos resultados, no una medición: los movimientos reales de votantes son mayores, porque hay flujos que se
      compensan. Las provincias se suman para el total de España.
    </p>
    <p>
      En el mapa <strong>cada celda es un escaño</strong>. Dentro de cada provincia, el territorio se divide en tantas celdas como
      diputados elige (un diagrama de Voronoi con puntos repartidos sobre la provincia), y cada celda toma el color del partido que gana
      ese escaño. Los límites provinciales y autonómicos vienen de es-atlas (IGN). La vista de hexágonos es un cartograma con un hexágono
      por escaño, a partir del de El Confidencial. «Escaños que cambian de manos» compara con 2023 en la proyección; en el simulador se puede comparar con la
      proyección o con 2023.
    </p>
  </div>

  <!-- ── daily update ──────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>8. Actualización diaria y <strong>respaldo</strong></h2>
    <p>
      Todo el proceso corre solo cada mañana (a las 07:17 UTC, las 08:17 en Madrid en invierno) en GitHub Actions: descarga, validación,
      media, proyección, comprobación y publicación. La web solo se reconstruye con datos que superan todas las comprobaciones:
    </p>
    <ul>
      <li>al menos 50 encuestas, y no más de un 10 % menos que el último fichero bueno;</li>
      <li>la encuesta más reciente no puede ser anterior a la del día previo, y no puede haber fechas futuras;</li>
      <li>PP y PSOE entre el 5 % y el 60 % en cada encuesta, y ninguna encuesta puede sumar más del 115 %;</li>
      <li>el resultado final tiene 52 circunscripciones, reparte exactamente 350 escaños y sus porcentajes suman el 100 %.</li>
    </ul>
    <p>
      Si algo falla, la web sigue con el <strong>último día bueno</strong> (la fecha de «Datos actualizados» es la de esos datos) y se abre
      un aviso para revisarlo a mano. Cada versión anterior de las encuestas se guarda con su fecha: se conservan las 30 últimas.
    </p>
  </div>

  <!-- ── limits ────────────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>Límites</h2>
    <ul>
      <li><strong>Las encuestas pueden fallar todas a la vez.</strong> La media corrige el sesgo de cada empresa respecto a las demás, no el de todas respecto al resultado.</li>
      <li><strong>El perfil territorial es el del pasado.</strong> Si un partido crece o cae de forma desigual entre provincias, la proyección no lo ve hasta que lo vean las encuestas autonómicas, que no se usan.</li>
      <li><strong>Los partidos nuevos tienen perfiles supuestos.</strong> SALF, Aliança Catalana y, en parte, Adelante Andalucía no tienen historial en generales.</li>
      <li><strong>La participación es la de 2023.</strong> Un cambio grande de participación cambia los escaños más ajustados.</li>
      <li><strong>El último escaño se decide por pocos votos.</strong> Diferencias de unos cientos o miles de votos están muy por debajo del error de cualquier encuesta.</li>
    </ul>
  </div>

  <!-- ── sources ───────────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>Fuentes</h2>
    <table class="tbl">
      <thead><tr><th>Dato</th><th>Fuente</th><th>Actualización</th></tr></thead>
      <tbody>
        {#each sources as s}<tr><td class="k">{s.q}</td><td>{#if s.u}<a href={s.u} target="_blank" rel="noopener">{s.s}</a>{:else}{s.s}{/if}</td><td class="muted nowrap">{s.d}</td></tr>{/each}
      </tbody>
    </table>
  </div>

  <!-- ── cite ──────────────────────────────────────────────────────────── -->
  <div class="prose well">
    <h2>Cómo <strong>citar</strong></h2>
    <p>El código, los datos de cada día y las transformaciones son públicos y reproducibles. Si reutilizas la proyección, cítala así:</p>
    <p class="cite-apa">Fundació ViT, Visualització per a la Transparència. (2026). <em>TresCincuenta.es: proyección del reparto de escaños del Congreso para las elecciones generales del 29 de noviembre de 2026</em> [modelo, datos y aplicación web]. https://trescincuenta.es</p>
    <div class="code">
      <div class="code-head"><span>BibTeX</span><button class="copy" type="button" onclick={copyBib}>{copied ? '✓ Copiado' : 'Copiar'}</button></div>
      <pre>{bibtex}</pre>
    </div>
    <a class="repo" href={REPO} target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" /></svg>
      <span><strong>El código en GitHub</strong> — descarga, media, proyección, comprobaciones y web, abiertos</span>
    </a>
    <p class="back"><a href={href('/')}>← Volver a la proyección</a></p>
  </div>
</section>

<style>
  .page { max-width: 1262px; margin: 0 auto; padding: 0 16px var(--s3); box-sizing: content-box; display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; }
  .well { grid-column: 2 / 8; min-width: 0; }
  .fig { grid-column: 1 / 13; min-width: 0; margin: var(--s2) 0 var(--s1); }
  @media (max-width: 900px) {
    .page { grid-template-columns: minmax(0, 1fr); }
    .well, .fig { grid-column: 1; }
  }
  .prose h2 { font-family: var(--font-ui); font-weight: 200; font-size: 24px; line-height: 32px; color: var(--ink); margin: var(--s3) 0 var(--s1); }
  .prose h2 :global(strong) { font-weight: 700; }
  .prose h3 { font-family: var(--font-ui); font-weight: 700; font-size: 16px; color: var(--ink); margin: var(--s2) 0 6px; }
  .prose p, .prose li { font-family: var(--font-body); font-weight: 300; font-size: 16px; line-height: 1.72; color: var(--fg); }
  .prose p { margin: 0 0 1em; }
  .prose ul { margin: 0 0 1em; padding-left: 1.1em; }
  .prose li { margin-bottom: 0.45em; }
  .prose a { color: inherit; text-decoration: underline; text-decoration-color: var(--muted); text-underline-offset: 3px; }
  .prose a:hover { text-decoration-color: var(--fg); }
  .prose code, .mono { font-family: 'SFMono-Regular', ui-monospace, Menlo, monospace; font-size: 0.86em; }
  .prose code { background: var(--panel); padding: 1px 5px; border-radius: 4px; }
  .nowrap { white-space: nowrap; }
  .small { font-size: 12px; margin-top: 2px; }

  .pipe { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 10px; counter-reset: s; }
  .pipe li { position: relative; display: flex; flex-direction: column; gap: 4px; padding: 14px 12px 14px; border-top: 4px solid var(--c); background: var(--panel); border-radius: 0 0 var(--radius) var(--radius); font-family: var(--font-ui); }
  .pipe li:not(:last-child)::after { content: '→'; position: absolute; right: -10px; top: 14px; transform: translateX(50%); font-size: 14px; color: var(--muted); z-index: 1; }
  .pipe .n { font-size: 12px; font-weight: 700; color: var(--muted); }
  .pipe b { font-size: 15px; line-height: 1.25; color: var(--ink); }
  .pipe .d { font-size: 12px; line-height: 1.4; color: var(--muted); }
  @media (max-width: 900px) { .pipe { grid-template-columns: minmax(0, 1fr); } .pipe li:not(:last-child)::after { content: '↓'; right: auto; left: 50%; top: auto; bottom: -12px; transform: translate(-50%, 0); } }
  .fig figcaption { font-family: var(--font-ui); font-weight: 400; font-size: 13px; line-height: 1.5; color: var(--muted); margin-top: 14px; max-width: 720px; }

  .tbl { width: 100%; border-collapse: collapse; margin: var(--s1) 0 var(--s2); font-family: var(--font-ui); font-weight: 400; font-size: 14px; }
  .tbl caption { text-align: left; font-weight: 700; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); padding-bottom: 10px; line-height: 1.4; }
  .tbl th { text-align: left; font-weight: 700; font-size: 11px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); padding: 8px 14px 8px 0; border-bottom: 1px solid var(--line); }
  .tbl td { padding: 9px 14px 9px 0; border-bottom: 1px solid var(--line); vertical-align: top; color: var(--fg); line-height: 1.5; }
  .tbl td.k { font-weight: 700; color: var(--ink); white-space: nowrap; }
  .tbl .r { text-align: right; }
  .tbl th.r { text-align: right; }
  .tbl .num { font-variant-numeric: tabular-nums; white-space: nowrap; }
  .tbl .muted { color: var(--muted); }
  .tbl td.pos { color: #1a7f37; font-weight: 700; }
  .tbl td.neg { color: #b3261e; font-weight: 700; }
  .tbl a { color: var(--fg); }
  .bar { display: inline-block; height: 8px; margin-right: 8px; border-radius: 2px; background: var(--fg); opacity: 0.55; vertical-align: middle; }
  @media (max-width: 600px) { .tbl { display: block; overflow-x: auto; } }

  .avg { display: flex; flex-direction: column; gap: 6px; margin: var(--s1) 0 var(--s2); font-family: var(--font-ui); font-size: 14px; }
  .avg .row { display: grid; grid-template-columns: 130px minmax(0, 1fr) 64px; align-items: center; gap: 10px; }
  .avg .nm { display: inline-flex; align-items: center; gap: 6px; color: var(--ink); font-weight: 700; white-space: nowrap; }
  .avg .nm i { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
  .avg .track { height: 10px; background: var(--panel); border-radius: 2px; overflow: hidden; }
  .avg .track span { display: block; height: 100%; }
  .avg .num { text-align: right; font-variant-numeric: tabular-nums; color: var(--fg); }

  .cite-apa { padding-left: 16px; border-left: 2px solid var(--muted); }
  .code { margin: var(--s2) 0; border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
  .code-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 8px 12px; background: var(--panel); border-bottom: 1px solid var(--line);
    font-family: var(--font-ui); font-weight: 700; font-size: 12px; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); }
  .copy { font-family: var(--font-ui); font-weight: 700; font-size: 12px; color: var(--fg); background: var(--bg); border: 1px solid var(--line); border-radius: 6px; padding: 4px 12px; cursor: pointer; }
  .copy:hover { border-color: var(--fg); }
  .code pre { margin: 0; padding: 14px 16px; overflow-x: auto; background: var(--bg); font-family: 'SFMono-Regular', ui-monospace, Menlo, monospace; font-size: 12.5px; line-height: 1.6; color: var(--fg); }
  .repo { display: flex; align-items: center; gap: 12px; margin-top: var(--s1); padding: 14px 18px; border: 1px solid var(--line); border-radius: var(--radius); text-decoration: none !important;
    color: var(--fg); font-family: var(--font-ui); font-size: 15px; font-weight: 400; }
  .repo:hover { border-color: var(--fg); background: var(--panel); }
  .repo svg { width: 22px; height: 22px; fill: var(--fg); flex: none; }
  .back { margin-top: var(--s3) !important; font-family: var(--font-ui) !important; font-size: 14px !important; }
</style>
