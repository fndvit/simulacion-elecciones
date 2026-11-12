<script lang="ts">
  // One scenario, as the projection page below the hero: headline, date, presentation, the adjustments it
  // makes (each with the seats it moves on its own; the whole set opens in the simulator), the seat bar
  // against the projection, the map and the closest seats.
  import SeatBar from './SeatBar.svelte';
  import HexMap from './HexMap.svelte';
  import LastSeat from './LastSeat.svelte';
  import CompareBars from './CompareBars.svelte';
  import AgeBars from './AgeBars.svelte';
  import { run, historyEntries, blank } from '$lib/model';
  import { PARTY } from '$lib/parties';
  import { longDate, sgnInt } from '$lib/format';
  import { encodeScenario } from '$lib/share';
  import { href } from '$lib/nav';
  import { scenarioOf, SUPUESTOS, CAMBIOS, DATOS, type Escenario, type Ctx } from '$lib/escenarios';
  import { BASE } from '$lib/model';
  import { DATA } from '$lib/data';
  import type { PartyKey } from '$lib/types';

  let { e }: { e: Escenario } = $props();
  const st = $derived(scenarioOf(e));
  const cur = $derived(run(st));
  const entries = $derived(historyEntries(st));
  // the texts may be written from the data
  // a scenario answered with two sources: each with its adjustments, result and step-by-step
  const vs = $derived((e.versions || []).map((v) => {
    const s = { ...blank(), ...JSON.parse(JSON.stringify(v.st())) };
    return { ...v, st: s, cur: run(s), entries: historyEntries(s) };
  }));
  const ctx = $derived<Ctx>({ st, cur, base: BASE, today: DATA.today, vs: Object.fromEntries(vs.map((v) => [v.key, v.cur])) });
  const title = $derived(typeof e.title === 'function' ? e.title(ctx) : e.title);
  const paras = $derived.by(() => { const b = typeof e.body === 'function' ? e.body(ctx) : e.body; return Array.isArray(b) ? b : [b]; });
  // the simulator with these adjustments as its starting point (?e=… travels before the #/… of the hash router)
  const simOf = (x: typeof st) => {
    const h = href('/simula'), q = '?e=' + encodeScenario(x);
    return h.startsWith('#') ? q + h : h + q;
  };
  const simHref = $derived(simOf(st));
  let allV = $state<Record<string, boolean>>({});
  let scope = $state('ES');
  let focusParty = $state('PP');
  // the adjustments: beyond three, only the first two until asked
  const FOLD = 3, SHOW = 2;
  let allSup = $state(false);
  // Material Symbols Outlined fork_chart, as the Escenarios tab
  const FORK = 'M120-160v-310q-26-7-43-28t-17-50v-192q0-8 6-14t14-6q8 0 14 6t6 14v140h30v-140q0-8 6-14t14-6q8 0 14 6t6 14v140h30v-140q0-8 6-14t14-6q8 0 14 6t6 14v192q0 29-17 50t-43 28v310h-60Zm480 1q-134 0-227.5-93.5T279-480q0-133 93.5-226.5T600-800q133 0 226.5 93.5T920-480q0 134-93.5 227.5T600-159Zm203-482L642-480l161 162q26-34 41.5-75t15.5-87q0-46-15.5-87T803-641Zm-173-97v186l131-131q-28-22-61-36t-70-19Zm-30 519q46 0 87-15.5t74-41.5L570-467v-271q-98 11-164.5 84.5T339-480q0 109 76 185t185 76Z';
  const nm = (k: string) => PARTY[k as PartyKey].n;
</script>

{#snippet sups()}
  {#if !vs.length}
    <div class="w">{@render supBox('Los supuestos', simHref, entries, allSup, () => (allSup = !allSup))}</div>
  {:else}
    <!-- the adjustments of each source, one under the other -->
    <div class="w vstack">
      {#each vs as v (v.key)}{@render supBox('Los supuestos según ' + v.name, simOf(v.st), v.entries, !!allV[v.key], () => (allV[v.key] = !allV[v.key]), true)}{/each}
    </div>
  {/if}
{/snippet}

<!-- compact: folded, only the start of the first adjustment, in two lines (the boxes of a scenario with two sources) -->
{#snippet supBox(head: string, href: string, list: typeof entries, open: boolean, toggle: () => void, compact = false)}
  <div class="supuestos" class:compact>
    <div class="shead">{head}</div>
    <a class="tosim" {href} aria-label="Abrir en el simulador"><svg viewBox="0 -960 960 960" aria-hidden="true"><path d={FORK} /></svg><span class="lbl">Abrir en el simulador</span></a>
    {#if compact && !open && list.length > 1}
      <div class="stext sclamp">{@html list[0].html}</div>
    {:else}
    <ol class="slist">
      {#each list.length > FOLD && !open ? list.slice(0, SHOW) : list as x (x.key)}
        <li>
          <div class="stext">{@html x.html}</div>
          <div class="simpact">
            {#each x.impact as [k, d]}<span class:up={d > 0} class:down={d < 0}>{sgnInt(d)} {nm(k)}</span>{:else}<span class="zero">sin cambio de escaños por sí solo</span>{/each}
          </div>
        </li>
      {/each}
    </ol>
    {/if}
    {#if list.length > FOLD || (compact && list.length > 1)}
      <button type="button" class="more-sup" aria-expanded={open} onclick={toggle}>
        {open ? 'Ver menos' : `Ver los ${list.length} supuestos`}
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" class:flip={open}><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
      </button>
    {/if}
  </div>
{/snippet}

<article class="sec esc" id={e.slug}>
  <section class="sec">
    <h2 class="etitle w6">{@html title}</h2>
    <p class="updated w">Publicado el <time datetime={e.date}>{longDate(e.date)}</time></p>
      {#each paras as p}
        {#if p === SUPUESTOS}{@render sups()}
        {:else if p === CAMBIOS}{#if vs.length}<div class="w"><CompareBars a={vs[0]} b={vs[1]} part="changes" /></div>{/if}
        {:else if p === DATOS}{#if vs.length}<div class="w"><AgeBars charts={vs.map((v) => v.chart!).filter(Boolean)} sources={vs.map((v) => v.source)} /></div>{/if}
        {:else}<p class="lede w">{@html p}</p>{/if}
      {/each}
      {#if !paras.includes(SUPUESTOS)}{@render sups()}{/if}
      {#if !vs.length}
        <div class="f"><SeatBar {cur} bind:scope who="este" /></div>
      {:else}
        <!-- two sources: the seats each one moves and the data behind each go where the text places them
             (or here, if it does not); the mirrored seat bars close the scenario -->
        {#if !paras.includes(CAMBIOS)}<div class="w"><CompareBars a={vs[0]} b={vs[1]} part="changes" /></div>{/if}
        {#if !paras.includes(DATOS)}<div class="w"><AgeBars charts={vs.map((v) => v.chart!).filter(Boolean)} sources={vs.map((v) => v.source)} /></div>{/if}
        <div class="f mirror"><CompareBars a={vs[0]} b={vs[1]} /></div>
      {/if}
  </section>

  {#if !vs.length}
  <section class="sec">
    <h3 class="hd w">Así quedaría <strong>el reparto por provincias</strong> en este escenario.</h3>
    <HexMap {cur} bind:scope bind:focusParty who="este" />
  </section>
  <section class="sec"><div class="w stack"><LastSeat {cur} bind:scope who="este" /></div></section>
  {/if}
</article>

<style>
  .esc { row-gap: var(--s3); padding-top: var(--s4); border-top: 1px solid var(--line); }
  /* the headline, as the heads of the other pages (Metodología, Quiénes somos) */
  .etitle { font-family: var(--font-ui); font-weight: 200; font-size: 44px; line-height: 1.1; color: var(--ink); margin: 0; }
  .etitle :global(strong) { font-weight: 700; }
  @media (max-width: 900px) { .etitle { font-size: 34px; } }
  .esc :global(.updated) { margin: -8px 0 0; font-family: var(--font-ui); font-size: 14px; font-weight: 700; color: #c4314b; }
  /* the adjustments, as the simulator's step-by-step panel */
  .supuestos { position: relative; display: flex; flex-direction: column; gap: 12px; padding: 16px 18px; border-radius: 10px; background: var(--panel); }
  .shead { font-family: var(--font-ui); font-weight: 700; font-size: 14px; color: var(--muted); }
  .slist { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
  .slist li { padding: 10px 0; border-bottom: 1px solid var(--line); display: flex; flex-direction: column; gap: 5px; }
  .slist li:first-child { padding-top: 0; }
  .slist li:last-child { padding-bottom: 0; border-bottom: 0; }
  /* see all the adjustments: the site's button */
  .more-sup { align-self: flex-start; display: inline-flex; align-items: center; gap: 4px; font-family: var(--font-ui); font-weight: 400; font-size: 14px; line-height: 18px; cursor: pointer;
    border: 0; border-radius: 999px; background: var(--ink); color: var(--bg); padding: 7px 12px 7px 16px; }
  .more-sup:hover { opacity: 0.85; }
  .more-sup svg { transition: transform 0.3s ease; }
  .more-sup svg.flip { transform: rotate(180deg); }
  .stext { font-family: var(--font-ui); font-size: 14px; line-height: 1.45; color: var(--muted); font-weight: 400; }
  .stext :global(strong) { font-weight: 700; color: var(--ink); }
  .simpact { display: flex; flex-wrap: wrap; gap: 4px; }
  .simpact span { font-family: var(--font-ui); font-weight: 700; font-size: 12px; font-variant-numeric: tabular-nums; padding: 2px 7px; border-radius: 4px; }
  .simpact .up { background: var(--up-bg); } .simpact .down { background: var(--down-bg); }
  .simpact .zero { color: var(--muted); background: var(--bg); font-weight: 400; }
  /* open in the simulator: the site's button, folded to its icon at the top right of the box; on hover
     (or keyboard focus) it unfolds to the left into the full button with its name */
  .tosim { position: absolute; top: 10px; right: 10px; display: inline-flex; align-items: center; height: 32px; padding: 0 7px; border-radius: 999px;
    background: var(--ink); color: var(--bg); text-decoration: none; font-family: var(--font-ui); font-weight: 400; font-size: 14px; line-height: 18px; white-space: nowrap; }
  .tosim svg { flex: none; width: 18px; height: 18px; fill: currentColor; }
  .tosim .lbl { max-width: 0; overflow: hidden; opacity: 0; transition: max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.2s ease, margin 0.3s ease; }
  .tosim:hover, .tosim:focus-visible { padding: 0 16px 0 12px; }
  .tosim:hover .lbl, .tosim:focus-visible .lbl { max-width: 200px; opacity: 1; margin-left: 7px; }
  .tosim { transition: padding 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
  .stack { display: flex; flex-direction: column; gap: 14px; }
  /* the adjustments of each source, side by side */
  .vstack { display: flex; flex-direction: column; gap: 10px; }
  .supuestos.compact { gap: 8px; padding: 12px 16px; }
  .supuestos.compact .tosim { top: 8px; right: 8px; }
  .sclamp { display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; padding-right: 36px; }
  .supuestos.compact .more-sup { padding: 5px 10px 5px 14px; }
  .mirror { margin-top: var(--s2); }
</style>
