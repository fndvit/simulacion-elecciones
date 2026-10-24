<script lang="ts">
  // The baseline: 538-style weighted poll average (trend + recent polls with today's weight) and the method.
  import { DATA } from '$lib/data';
  import { PARTY } from '$lib/parties';
  import { fmtN, dec, longDate } from '$lib/format';
  import { href } from '$lib/nav';

  const KEYS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS', 'SALF'] as const;
  const col = (k: string) => (k === 'SUMAR' ? PARTY.FA.c : PARTY[k as keyof typeof PARTY].c);
  const lab = (k: string) => (k === 'SUMAR' ? 'Sumar / FA + Compromís' : PARTY[k as keyof typeof PARTY].n);

  // the chart spans the full 12 columns: drawn at its real pixel width so text and marks keep their size
  let cw = $state(760);
  const W = $derived(Math.max(560, Math.round(cw))), H = 340, m = { l: 34, r: 196, t: 12, b: 26 };
  const SER = DATA.series;
  const t0 = new Date(SER[0].d).getTime(), t1 = new Date(DATA.today).getTime();
  const X = $derived((d: string) => m.l + ((new Date(d).getTime() - t0) / (t1 - t0)) * (W - m.l - m.r));
  const Y = (v: number) => m.t + (1 - v / 40) * (H - m.t - m.b);
  const MONTHS = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  const months = $derived.by(() => {
    const out: { x: number; t: string }[] = [];
    for (let d = new Date(2025, 10, 1); d <= new Date(DATA.today); d.setMonth(d.getMonth() + 1))
      out.push({ x: X(d.toISOString().slice(0, 10)), t: MONTHS[d.getMonth()] + (d.getMonth() === 0 ? ' 26' : '') });
    return out;
  });
  const dots = $derived(DATA.polls.filter((p) => new Date(p.end).getTime() >= t0).flatMap((p) => KEYS.filter((k) => p.v[k] != null).map((k) => ({ x: X(p.end), y: Y(p.v[k]), c: col(k), k, p }))));
  const lines = $derived(KEYS.map((k) => ({ k, d: SER.map((s, i) => (i ? 'L' : 'M') + X(s.d).toFixed(1) + ',' + Y(s[k]).toFixed(1)).join('') })));
  const last = SER[SER.length - 1];
  const labels = KEYS.map((k) => ({ k, y: Y(last[k]), v: last[k] })).sort((a, b) => a.y - b.y);
  for (let i = 1; i < labels.length; i++) if (labels[i].y - labels[i - 1].y < 15) labels[i].y = labels[i - 1].y + 15;

  // tooltip: a poll when the pointer is on (or very near) a dot, otherwise the average on that date
  let svgEl: SVGSVGElement;
  type Dot = { x: number; y: number; c: string; k: (typeof KEYS)[number]; p: (typeof DATA.polls)[number] };
  let hov = $state<{ kind: 'poll'; d: Dot } | { kind: 'avg'; i: number } | null>(null);
  let hpos = $state({ x: 0, y: 0, left: true });
  function hover(e: PointerEvent) {
    const m = svgEl.getScreenCTM(); if (!m) return;
    const pt = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
    let best: Dot | null = null, bd = 49; // within 7 px (chart units)
    for (const d of dots) { const q = (d.x - pt.x) ** 2 + (d.y - pt.y) ** 2; if (q < bd) { bd = q; best = d; } }
    if (best) hov = { kind: 'poll', d: best };
    else if (pt.x >= X(SER[0].d) && pt.x <= X(last.d) + 4) {
      let i = 0, bx = 1e9;
      SER.forEach((s, k) => { const dx = Math.abs(X(s.d) - pt.x); if (dx < bx) { bx = dx; i = k; } });
      hov = { kind: 'avg', i };
    } else hov = null;
    const r = svgEl.getBoundingClientRect();
    hpos = { x: e.clientX - r.left, y: Math.min(Math.max(e.clientY - r.top, 95), r.height - 60), left: e.clientX - r.left < r.width * 0.6 };
  }
  const recent = DATA.polls.slice(0, 30);
  const maxW = Math.max(...recent.map((p) => p.w));
  const cell = (p: (typeof recent)[number], k: string) => (p.v[k] != null ? dec(p.v[k]) : '–');
</script>

<h2 class="hd w" id="la-base">La base: <strong>media ponderada de encuestas</strong></h2>
<p class="lede w">La proyección sigue la metodología de FiveThirtyEight, el modelo que popularizó Nate Silver en Estados Unidos, adaptada a las encuestas españolas: una media ponderada que premia las encuestas recientes, grandes y de empresas demoscópicas que acertaron en 2023, corrige el sesgo de cada empresa y reparte el resultado por provincias según dónde ha sido más fuerte o más débil cada partido en las tres últimas generales. Después, D'Hondt reparte los escaños. Las encuestas se recogen cada día, de forma automática, de la recopilación de sondeos publicados que mantiene Wikipedia.</p>
<div class="cwrap c9" bind:clientWidth={cw}><div class="scrollx">
  <svg bind:this={svgEl} onpointermove={hover} onpointerleave={() => (hov = null)} class="chart" viewBox="0 0 {W} {H}" width={W} height={H} role="img" aria-label="Evolución de la media de encuestas">
    {#each [0, 10, 20, 30, 40] as v}<line class="grid" x1={m.l} x2={W - m.r} y1={Y(v)} y2={Y(v)} /><text x={m.l - 6} y={Y(v) + 4} text-anchor="end">{v}</text>{/each}
    {#each months as mo}<text x={mo.x} y={H - 6} text-anchor="middle">{mo.t}</text>{/each}
    {#each dots as d}<circle cx={d.x} cy={d.y} r="2" fill={d.c} opacity="0.28" />{/each}
    {#each lines as l}<path d={l.d} fill="none" stroke={col(l.k)} stroke-width="2.4" stroke-linejoin="round" />{/each}
    {#each KEYS as k}<circle cx={X(last.d)} cy={Y(last[k])} r="4" fill={col(k)} />{/each}
    {#each labels as L}<text class="lbl" x={W - m.r + 10} y={L.y + 4} fill={col(L.k)}>{dec(L.v)} {lab(L.k)}</text>{/each}
    {#if hov?.kind === 'avg'}
      {@const s = SER[hov.i]}
      <line class="rule" x1={X(s.d)} x2={X(s.d)} y1={m.t} y2={H - m.b} />
      {#each KEYS as k}<circle cx={X(s.d)} cy={Y(s[k])} r="3.5" fill={col(k)} stroke="var(--bg)" stroke-width="1.5" />{/each}
    {:else if hov?.kind === 'poll'}
      <circle cx={hov.d.x} cy={hov.d.y} r="4.5" fill={hov.d.c} stroke="var(--ink)" stroke-width="1.5" />
    {/if}
  </svg>
  </div>
  {#if hov}
    <div class="tip" style="left:{hpos.x}px;top:{hpos.y}px;transform:translate({hpos.left ? '14px' : 'calc(-100% - 14px)'}, -50%)">
      {#if hov.kind === 'avg'}
        {@const s = SER[hov.i]}
        <h4>Media a {longDate(s.d)}</h4>
        {#each KEYS.map((k) => [k, s[k]] as const).sort((a, b) => b[1] - a[1]) as [k, v]}<div><span class="sw" style="background:{col(k)}"></span>{lab(k)}: <b>{dec(v)} %</b></div>{/each}
      {:else}
        {@const p = hov.d.p}{@const dk = hov.d.k}
        <h4>{p.p}</h4>
        <div>Campo: {p.fw}{p.n ? ` · ${fmtN(p.n)} entrevistas` : ''}</div>
        <div><span class="sw" style="background:{hov.d.c}"></span>{lab(hov.d.k)}: <b>{dec(p.v[hov.d.k])} %</b></div>
        <div class="tm">{KEYS.filter((k) => k !== dk && p.v[k] != null).map((k) => `${lab(k)} ${dec(p.v[k])}`).join(' · ')}</div>
      {/if}
    </div>
  {/if}
</div>
<p class="method w">Líneas: media ajustada semana a semana con los datos disponibles en cada fecha. Puntos: cada encuesta publicada, sin ajustar. % de voto válido.</p>

<div class="scrollx c7">
  <table class="ptable">
    <thead><tr><th>Empresa demoscópica / medio</th><th>Campo</th><th>Muestra</th><th>PP</th><th>PSOE</th><th>Vox</th><th>Sumar/FA</th><th>Podemos</th><th>SALF</th><th style="text-align:left">Peso hoy</th></tr></thead>
    <tbody>
      {#each recent as p}
        <tr>
          <td>{p.p}</td><td class="fw">{p.fw}</td><td>{p.n ? fmtN(p.n) : '¿?'}</td>
          {#each KEYS as k}<td>{cell(p, k)}</td>{/each}
          <td class="wcell"><span class="wn">{Math.round((p.w / maxW) * 100)}</span><span class="wbar" style="width:{Math.round((p.w / maxW) * 46)}px"></span></td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>

<section class="meth w">
  <h3 class="hd">Cómo se calcula <strong>la proyección</strong></h3>
  <div class="prose">
    <p>Una media de las {DATA.polls.length} encuestas publicadas desde octubre de 2025 que pesa más las recientes, las de más entrevistas y las de empresas demoscópicas que acertaron en 2023, y que corrige el sesgo de cada empresa. La media se reparte por provincias según dónde ha sido más fuerte o más débil cada partido en las generales de 2019 y 2023, y los escaños se asignan con D'Hondt y la barrera del 3 % en cada circunscripción. No es un pronóstico: refleja lo que dicen hoy las encuestas y no estima incertidumbre ni probabilidades.</p>
    <p class="more"><a href={href('/metodologia')}>Lee la metodología completa →</a></p>
    <p class="src"><b>Fuentes.</b> Encuestas: <a href="https://es.wikipedia.org/wiki/Encuestas_de_opini%C3%B3n_para_las_elecciones_generales_de_Espa%C3%B1a_de_2026" target="_blank" rel="noopener">recopilación de Wikipedia</a>, descargada cada día (última actualización: {longDate(DATA.today)}). Resultados de 2019 y 2023: <a href="https://infoelectoral.interior.gob.es" target="_blank" rel="noopener">Ministerio del Interior</a>.</p>
  </div>
</section>

<style>
  .chart { display: block; touch-action: pan-y; }
  .cwrap { position: relative; }
  .chart .rule { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 3 3; }
  .tip .sw { display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin-right: 5px; }
  .tip .tm { color: var(--muted); margin-top: 3px; }
  .chart text { font-family: var(--font-ui); font-size: 13px; fill: var(--muted); }
  .chart .grid { stroke: var(--line); stroke-width: 1; }
  .chart .lbl { font-weight: 700; font-size: 12px; paint-order: stroke; stroke: var(--halo); stroke-width: 3px; }
  .ptable { width: 100%; border-collapse: collapse; font-family: var(--font-ui); font-size: 13px; color: var(--ink); font-weight: 400; }
  .ptable th { text-align: right; font-size: 12px; color: var(--muted); padding: 4px 5px; border-bottom: 1px solid var(--line); white-space: nowrap; }
  .ptable th:first-child, .ptable td:first-child { text-align: left; }
  .ptable td { padding: 5px 5px; border-bottom: 1px solid var(--line); text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .ptable td.fw { color: var(--muted); }
  .ptable td.wcell { text-align: left; width: 90px; }
  .wn { display: inline-block; width: 3ch; text-align: right; margin-right: 6px; }
  .wbar { display: inline-block; height: 8px; border-radius: 2px; background: var(--fg); vertical-align: middle; opacity: 0.7; }
  .meth { margin-top: var(--s3); display: flex; flex-direction: column; gap: 4px; }
  .prose { font-family: var(--font-body); font-size: 16px; line-height: 1.72; color: var(--fg); max-width: 64ch; display: flex; flex-direction: column; gap: 12px; margin-top: 12px; }
  .prose p { margin: 0; }
  .prose a { color: inherit; }
  .prose .src { font-size: 13px; line-height: 1.6; color: var(--muted); }
  .more a { font-family: var(--font-ui); font-weight: 700; font-size: 15px; text-decoration: none; color: var(--ink); border-bottom: 2px solid currentColor; }
  .more a:hover { color: #d1366b; }
</style>
