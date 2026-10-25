<script lang="ts">
  // Two views of the 350 seats that morph into each other: a geographic map (each constituency split
  // into one Voronoi cell per seat, the default) and the hexagon cartogram. One cell/hexagon per seat. Escaños: each hex takes the colour of the party that wins it; hexes whose
  // party differs from the poll projection get a black stroke. Voto a un partido: every hex of a
  // constituency is shaded by that party's vote share there. Province and community limits are
  // gaps in the page colour (thin / wide). Click a constituency to tune it.
  import LibDrop from './LibDrop.svelte';
  import { BYID } from '$lib/data';
  import { PARTY, BLOC, ORDER } from '$lib/parties';
  import { HEX, GEO, VIEWBOX, BASE_HEX, hexParties, changedSince2023, poly, morphPath } from '$lib/hex';
  import { Tween } from 'svelte/motion';
  import { cubicInOut } from 'svelte/easing';
  import { BASE } from '$lib/model';
  import { pct, fmtN } from '$lib/format';
  import type { RunResult } from '$lib/types';

  let { cur, scope = $bindable(), focusParty = $bindable(), projection = false }: { cur: RunResult; scope: string; focusParty: string; projection?: boolean } = $props();

  let mode = $state<'seats' | 'party'>('seats');
  let compareSel = $state<'scenario' | '2023'>('scenario');
  // the projection has no scenario of its own: changes are always counted from 2023
  const compare = $derived(projection ? '2023' : compareSel);
  let view = $state<'geo' | 'hex'>('geo');
  // 0 = geographic map, 1 = hexagons; in between, every cell morphs into its hexagon
  const T = new Tween(0, { duration: 1100, easing: cubicInOut });
  function setView(v: 'geo' | 'hex') { view = v; T.target = v === 'hex' ? 1 : 0; tip = null; }
  const t = $derived(T.current);
  const moving = $derived(t > 0 && t < 1);
  const shapes = $derived(moving ? HEX.H.map((h) => morphPath(h.i, t)) : null);
  const fadeGeo = $derived(Math.max(0, 1 - t * 4)), fadeHex = $derived(Math.max(0, t * 4 - 3));
  const lerp = (a: number, b: number) => a + (b - a) * t;
  let tip = $state<{ id: string; x: number; y: number } | null>(null);
  let wrapEl: HTMLDivElement;

  const den = $derived.by(() => {
    let m = 0;
    for (const id in HEX.byProv) { const r = cur.prov[id]; m = Math.max(m, (r.votes[focusParty] || 0) / r.valid); }
    return Math.max(0.05, Math.ceil(m / 0.05) * 0.05);
  });
  const mixFill = (c: string, t: number) => `color-mix(in srgb, ${c} ${Math.round(Math.min(1, t) * 100)}%, var(--map-empty))`;

  const cells = $derived.by(() => {
    const out: { key: string; id: string; gi: number; pts: string; inner: string; fill: string; chg: boolean }[] = [];
    for (const id in HEX.byProv) {
      // the layout is always anchored to the poll projection, so the toggle only moves the highlight
      const parts = hexParties(cur, id, BASE_HEX), r = cur.prov[id];
      const since = compare === '2023' ? changedSince2023(parts, id) : null;
      const share = (r.votes[focusParty] || 0) / r.valid;
      HEX.byProv[id].forEach((h, i) => {
        const k = parts[i], chg = since ? since[i] : k !== BASE_HEX[id][i];
        const fill = mode === 'seats' ? (k ? PARTY[k as keyof typeof PARTY].c : 'var(--map-empty)') : share > 0 ? mixFill(PARTY[focusParty as keyof typeof PARTY].c, share / den) : 'var(--map-empty)';
        out.push({ key: id + ':' + i, id, gi: h.i, pts: poly(h, HEX.R), inner: poly(h, HEX.R * 0.86), fill, chg });
      });
    }
    return out;
  });
  const nChg = $derived(cells.filter((c) => c.chg).length);
  const hb = HEX.canBox, gb = GEO.canBox;
  const cb = $derived([0, 1, 2, 3].map((k) => lerp(gb[k], hb[k])));
  const hovId = $derived(tip && !moving ? tip.id : null);
  // other provinces fade towards the page colour (a mixed fill, not opacity, so cells don't show seams)
  const dimmed = (c: { id: string; fill: string }) => (hovId && c.id !== hovId ? `color-mix(in srgb, ${c.fill} 42%, var(--bg))` : c.fill);
  const ce = $derived(lbl('51')), me = $derived(lbl('52'));

  // community names: over the map for the peninsula (non-interactive, blended), outside it for the islands and cities
  const CA_N: Record<string, string[]> = {
    '01': ['Andalucía'], '02': ['Aragón'], '03': ['Asturias'], '04': ['Illes Balears'], '05': ['Canarias'], '06': ['Cantabria'],
    '07': ['Castilla-', 'La Mancha'], '08': ['Castilla', 'y León'], '09': ['Cataluña'], '10': ['Extremadura'], '11': ['Galicia'],
    '12': ['Madrid'], '13': ['Navarra'], '14': ['País', 'Vasco'], '15': ['Murcia'], '16': ['La Rioja'], '17': ['Comunitat', 'Valenciana']
  };
  const ringArea = (r: number[][]) => { let a = 0, x = 0, y = 0; for (let k = 0; k < r.length; k++) { const p = r[k], q = r[(k + 1) % r.length], f = p[0] * q[1] - q[0] * p[1]; a += f; x += (p[0] + q[0]) * f; y += (p[1] + q[1]) * f; } return { a: a / 2, x: x / (3 * a), y: y / (3 * a) }; };
  const CA_POS = Object.keys(CA_N).map((ca) => {
    const hs = HEX.H.filter((h) => BYID[h.id].ca === ca);
    let A = 0, gx = 0, gy = 0;
    for (const h of hs) { const r = ringArea(GEO.cells[h.i].ring); A += Math.abs(r.a); gx += r.x * Math.abs(r.a); gy += r.y * Math.abs(r.a); }
    const hx = hs.reduce((a, h) => a + h.x, 0) / hs.length, hy = hs.reduce((a, h) => a + h.y, 0) / hs.length;
    // Baleares: above the islands in both maps
    const top = ca === '04' ? [Math.min(...hs.map((h) => GEO.cells[h.i].ring.reduce((m, p) => Math.min(m, p[1]), 1e9))), Math.min(...hs.map((h) => h.y))] : null;
    return { ca, lines: CA_N[ca], out: ca === '04', g: top ? [gx / A, top[0] - 14] : [gx / A, gy / A], h: top ? [hx, top[1] - HEX.R - 10] : [hx, hy] };
  }).filter((c) => c.ca !== '05');
  // how to read the map: A Coruña drawn larger under the Balearic Islands, split into its seats
  const KEY = '15';
  const [VX, VY, VW, VH] = VIEWBOX.split(' ').map(Number);
  const keyHex = HEX.byProv[KEY];
  const bboxOf = (pts: number[][]) => [Math.min(...pts.map((p) => p[0])), Math.min(...pts.map((p) => p[1])), Math.max(...pts.map((p) => p[0])), Math.max(...pts.map((p) => p[1]))];
  const keyGeoBox = bboxOf(keyHex.flatMap((h) => GEO.cells[h.i].ring));
  const keyHexBox = bboxOf(keyHex.flatMap((h) => [[h.x - HEX.R, h.y - HEX.R], [h.x + HEX.R, h.y + HEX.R]]));
  const keyBox = $derived([0, 1, 2, 3].map((k) => lerp(keyGeoBox[k], keyHexBox[k])));
  const keyCells = $derived(cells.filter((c) => c.id === KEY));
  // anchor: just under the Balearic Islands (both maps), as a share of the map box
  const bal = HEX.H.filter((h) => BYID[h.id].ca === '04');
  const balGeo = bboxOf(bal.flatMap((h) => GEO.cells[h.i].ring)), balHex = bboxOf(bal.map((h) => [h.x, h.y + HEX.R]));
  const keyTop = $derived((lerp(balGeo[3], balHex[3]) + 46 - VY) / VH * 100);
  // pointer over the sea, a gap or the inset box: no province is hovered any more
  function offCell(e: MouseEvent) { if (tip && !(e.target as Element).classList?.contains('hx')) tip = null; }
  function clear(e: MouseEvent) { if (!(e.target as Element).classList?.contains('hx')) { scope = 'ES'; tip = null; } }
  function lbl(id: string) { const h = HEX.byProv[id][0], g = GEO.cells[h.i].c; return { x: lerp(g[0], h.x), y: lerp(g[1], h.y) }; }

  function pick(id: string) { scope = scope === id ? 'ES' : id; tip = null; }
  function move(e: MouseEvent, id: string) {
    const b = wrapEl.getBoundingClientRect();
    tip = { id, x: Math.min(e.clientX - b.left, b.width - 270), y: e.clientY - b.top };
  }
  const tipData = $derived.by(() => {
    if (!tip) return null;
    const p = BYID[tip.id], r = cur.prov[tip.id], b = BASE.prov[tip.id];
    const seats = ORDER.filter((P) => r.seats[P]).sort((a, c) => r.seats[c] - r.seats[a]);
    const top = Object.entries(r.votes).filter(([k]) => k !== 'OTROS').sort((a, c) => c[1] - a[1]).slice(0, 4);
    return { p, r, b, seats, top };
  });
</script>

<div class="c8w stickyui mapui">
<div class="map-top">
  <div class="toggle" role="group" aria-label="Cómo colorear el mapa">
    <button class:on={mode === 'seats'} aria-pressed={mode === 'seats'} onclick={() => (mode = 'seats')}>Escaños</button>
    <button class:on={mode === 'party'} aria-pressed={mode === 'party'} onclick={() => (mode = 'party')}>Voto a un partido</button>
  </div>
  {#if mode === 'party'}
    <span class="pdrop"><LibDrop bind:value={focusParty} options={ORDER.map((P) => ({ value: P as string, label: PARTY[P].n }))} label="Partido del mapa" /></span>
  {/if}
  <div class="toggle viewt" role="group" aria-label="Tipo de mapa">
    <button class:on={view === 'geo'} aria-pressed={view === 'geo'} onclick={() => setView('geo')}>Mapa</button>
    <button class:on={view === 'hex'} aria-pressed={view === 'hex'} onclick={() => setView('hex')}>Hexágonos</button>
  </div>
</div>
<div class="chg-row">
  <span class="map-heading">
    <svg width="16" height="16" viewBox="-10 -10 20 20" aria-hidden="true"><polygon points="0,-8 6.9,-4 6.9,4 0,8 -6.9,4 -6.9,-4" fill="none" stroke="currentColor" stroke-width="3" /></svg>
    Escaños que cambian de manos{#if nChg}&nbsp;({nChg}){/if}
  </span>
  {#if projection}<span class="since">desde 2023</span>{:else}
  <div class="toggle small" role="group" aria-label="Escaños que cambian de manos: respecto a">
    <button class:on={compare === 'scenario'} aria-pressed={compare === 'scenario'} onclick={() => (compareSel = 'scenario')}>en tu escenario</button>
    <button class:on={compare === '2023'} aria-pressed={compare === '2023'} onclick={() => (compareSel = '2023')}>desde 2023</button>
  </div>{/if}
</div>
</div>


<div class="legend c8w">
  {#if mode === 'seats'}
    <span>Líneas finas: provincias; gruesas: comunidades autónomas.</span>
    {#each BLOC.filter((P) => cur.seats[P]) as P}<span><i style="background:{PARTY[P].c}"></i>{PARTY[P].n} {cur.seats[P]}</span>{/each}
  {:else}
    <span>Voto a {PARTY[focusParty as keyof typeof PARTY].n} en cada circunscripción</span>
    <span>0 %<span class="ramp" style="background:linear-gradient(90deg, var(--map-empty), {PARTY[focusParty as keyof typeof PARTY].c})"></span>{Math.round(den * 100)} %</span>
  {/if}
</div>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<div class="mapwrap c8" bind:this={wrapEl} role="presentation" onmouseleave={() => (tip = null)} onmousemove={offCell} onclick={clear}>
  <svg class="map" viewBox={VIEWBOX} role="img" aria-label="Mapa de los 350 escaños por circunscripción">
    <defs>{#each GEO.cells as g, i}<clipPath id="vc{i}"><path d={g.d} /></clipPath>{/each}</defs>
    <path class="canbox" d="M{cb[0]},{cb[1]}H{cb[2]}V{cb[3]}" />
    {#each cells as c (c.key)}
      <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
      {#if t === 1}<polygon class="hx" points={c.pts} style="fill:{dimmed(c)};stroke:{dimmed(c)}" onclick={() => pick(c.id)} onmousemove={(e) => move(e, c.id)} />
      {:else}<path class="hx" d={shapes ? shapes[c.gi] : GEO.cells[c.gi].d} style="fill:{dimmed(c)};stroke:{dimmed(c)}" onclick={() => pick(c.id)} onmousemove={(e) => move(e, c.id)} />{/if}
    {/each}
    {#if fadeGeo > 0}
      <g style="opacity:{fadeGeo}" class="lines">{#each Object.values(GEO.prov) as d}<path class="pvl geo" {d} />{/each}<path class="cal geo" d={GEO.ca} /></g>
    {/if}
    {#if fadeHex > 0}<g style="opacity:{fadeHex}" class="lines"><path class="pvl" d={HEX.lines.pv} /><path class="cal" d={HEX.lines.ca} /></g>{/if}
    {#if !moving}
      {#each cells as c (c.key)}
        {#if c.chg}
          <!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
          {#if t === 1}<polygon class="hx chg" points={c.inner} style="fill:{dimmed(c)}" onclick={() => pick(c.id)} onmousemove={(e) => move(e, c.id)} />
          {:else}<path class="hx chg geo" d={GEO.cells[c.gi].d} clip-path="url(#vc{c.gi})" style="fill:{dimmed(c)}" onclick={() => pick(c.id)} onmousemove={(e) => move(e, c.id)} />{/if}
        {/if}
      {/each}
      {#if tip && tip.id !== scope}<path class="hov" d={t === 1 ? HEX.outline[tip.id] : GEO.prov[tip.id]} />{/if}
      {#if scope !== 'ES'}<path class="selo" d={t === 1 ? HEX.outline[scope] : GEO.prov[scope]} />{/if}
    {/if}
    {#each CA_POS as c (c.ca)}
      {@const n = c.lines.length}
      <text class="ca" class:over={!c.out} x={lerp(c.g[0], c.h[0])} y={lerp(c.g[1], c.h[1]) - (n - 1) * 10 + 7} text-anchor="middle">{#each c.lines as l, k}<tspan x={lerp(c.g[0], c.h[0])} dy={k ? 20 : 0}>{l}</tspan>{/each}</text>
    {/each}
    <text class="ca" x={ce.x - HEX.R * 1.2} y={ce.y + 7} text-anchor="end">Ceuta</text>
    <text class="ca" x={me.x + HEX.R * 1.2} y={me.y + 7}>Melilla</text>
    <text class="ca" x={cb[0] + 2} y={cb[1] - 10}>Canarias</text>
  </svg>

  <div class="key" style="--top:{keyTop}%">
    <span class="kname">{BYID[KEY].n} · {BYID[KEY].seats} escaños</span>
    <svg viewBox="{keyBox[0] - 2} {keyBox[1] - 2} {keyBox[2] - keyBox[0] + 4} {keyBox[3] - keyBox[1] + 4}" aria-hidden="true">
      {#each keyCells as c (c.key)}
        {#if t === 1}<polygon points={c.pts} style="fill:{c.fill}" />{:else}<path d={shapes ? shapes[c.gi] : GEO.cells[c.gi].d} style="fill:{c.fill}" />{/if}
      {/each}
    </svg>
    <p>
      <b>Cómo leer el mapa</b>
      {#if view === 'hex'}Cada provincia tiene tantos hexágonos como escaños reparte{:else}Cada provincia se divide en tantas partes como escaños reparte{/if}{#if mode === 'seats'}, y cada una toma el color del partido que gana ese escaño, con el primero en el centro.{:else}, todas con el tono del voto del partido en la provincia.{/if}
      {#if view === 'geo'}Las partes no siguen los municipios: no muestran dónde se vota a cada partido.{/if}
    </p>
  </div>

  {#if tipData && tip}
    <div class="tip" style="left:{tip.x}px;top:{tip.y}px">
      <h4>{tipData.p.n} · {tipData.p.seats} {tipData.p.seats === 1 ? 'escaño' : 'escaños'}</h4>
      <div class="chips">{#each tipData.seats as P}<span class="chip"><i style="background:{PARTY[P].c}"></i>{PARTY[P].n} {tipData.r.seats[P]}</span>{/each}</div>
      {#each tipData.top as [k, v]}
        {@const bs = (tipData.b.votes[k] || 0) / tipData.b.valid}
        <div>{PARTY[k as keyof typeof PARTY].n}: <b>{pct(v / tipData.r.valid)}</b>{#if Math.abs(v / tipData.r.valid - bs) > 0.0005} ({pct(bs)} en la proyección){/if}</div>
      {/each}
      <div>Participación: <b>{pct(tipData.r.turnout)}</b></div>
      {#if tipData.r.last && tipData.r.chal}<div>Último escaño: <b>{PARTY[tipData.r.last.k as keyof typeof PARTY].n}</b>; {PARTY[tipData.r.chal.k as keyof typeof PARTY].n} lo gana con {fmtN(tipData.r.chal.need)} votos más.</div>{/if}
    </div>
  {/if}
</div>

<p class="sub w">
  {#if compare === 'scenario'}El trazo negro marca los escaños que tu escenario cambia de manos respecto a la proyección de las encuestas.{:else}El trazo negro marca los escaños que cambian de manos respecto a las generales de 2023 (en Madrid cuenta también el escaño nuevo).{/if}
  Pulsa una provincia para seleccionarla en toda la página.
</p>

<style>
  .viewt { margin-left: auto; }
  .map-top { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px; }
  .toggle { display: inline-flex; padding: 2px; border-radius: var(--radius); background: var(--panel); }
  .toggle button { font-family: var(--font-ui); font-weight: 300; font-size: 17px; line-height: 26px; cursor: pointer; border: 0; border-radius: 5px; padding: 2px 12px; background: transparent; color: var(--muted); }
  .toggle button.on { background: var(--highlight); color: var(--hl-ink); box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2); }
  .mapui { display: flex; flex-direction: column; gap: 10px; }
  .since { font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; margin-left: -4px; }
  .chg-row { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; margin-top: -4px; }
  .toggle.small { border-radius: 999px; }
  .toggle.small button { font-size: 14px; line-height: 20px; padding: 2px 12px; border-radius: 999px; }
  .pdrop :global(.word) { font-size: 17px; line-height: 26px; padding: 2px 10px; }
  .pdrop :global(.opt) { font-size: 16px; }
  .map-heading { display: inline-flex; align-items: center; gap: 8px; font-family: var(--font-ui); font-weight: 700; font-size: 14px; color: var(--fg); }
  .mapwrap { position: relative; }
  .map { width: 100%; height: auto; display: block; }
  /* in the simulation the centre is narrower; keep the map from growing past 820 px there */
  :global(.sim) .map { max-width: 820px; }
  /* each hex is stroked in its own fill colour so neighbours fuse without anti-aliasing seams */
  .hx { cursor: pointer; transition: fill 0.3s ease, stroke 0.3s ease; stroke-width: 1.5; stroke-linejoin: round; }
  .hx { transition: fill 0.3s ease, stroke 0.3s ease, opacity 0.15s ease; }
  .hov { fill: none; stroke: var(--ink); stroke-width: 2.5; stroke-linejoin: round; pointer-events: none; opacity: 0.85; }
  .hx.chg { stroke: var(--stroke); stroke-width: 5; stroke-linejoin: round; }
  .hx.chg.geo { stroke-width: 7; }
  .lines { pointer-events: none; }
  .pvl.geo { stroke-width: 1.2; stroke-linejoin: round; }
  .cal.geo { stroke-width: 5; stroke-linejoin: round; }
  .pvl { fill: none; stroke: var(--bg); stroke-width: 1.8; stroke-linecap: round; pointer-events: none; }
  .cal { fill: none; stroke: var(--bg); stroke-width: 7; stroke-linecap: round; pointer-events: none; }
  .selo { fill: none; stroke: var(--fg); stroke-width: 3.5; stroke-linecap: round; pointer-events: none; }
  .canbox { fill: none; stroke: var(--muted); stroke-width: 1.2; }
  .map text { font-family: var(--font-ui); font-size: 13px; fill: var(--muted); paint-order: stroke; stroke: var(--halo); stroke-width: 3px; pointer-events: none; }
  .map text.ca { font-size: 19px; font-weight: 700; fill: var(--fg); letter-spacing: 0.01em; }
  /* over the map: solid text with a wide halo in the page colour, so it reads on any party colour */
  .map text.ca.over { fill: var(--ink); stroke: var(--halo); stroke-width: 5px; stroke-linejoin: round; }
  .key { position: absolute; right: 0; top: var(--top); width: 26%; display: flex; flex-direction: column; gap: 8px; pointer-events: none; }
  .key svg { width: 46%; height: auto; display: block; }
  .key svg :global(path), .key svg :global(polygon) { stroke: var(--bg); stroke-width: 1.6; stroke-linejoin: round; }
  .key p { margin: 0; font-family: var(--font-ui); font-weight: 400; font-size: 12px; line-height: 1.45; color: var(--muted); }
  .kname { font-family: var(--font-ui); font-weight: 700; font-size: 12px; color: var(--fg); margin-bottom: -4px; }
  .key b { display: block; color: var(--fg); font-weight: 700; margin-bottom: 2px; }
  @media (max-width: 700px) {
    .key { position: static; width: auto; display: grid; grid-template-columns: 84px 1fr; align-items: start; gap: 4px 12px; margin-top: 12px; }
    .kname { grid-column: 1 / 3; margin: 0; }
    .key svg { width: 84px; flex: none; }
  }
  .mapwrap { cursor: default; }
  .legend { margin-bottom: -6px; display: flex; flex-wrap: wrap; gap: 6px 14px; font-family: var(--font-ui); font-size: 12px; color: var(--muted); font-weight: 400; }
  .legend i { display: inline-block; width: 11px; height: 11px; border-radius: 2px; vertical-align: -1px; margin-right: 5px; }
  .ramp { display: inline-block; width: 120px; height: 10px; border-radius: 2px; vertical-align: middle; margin: 0 6px; }
</style>
