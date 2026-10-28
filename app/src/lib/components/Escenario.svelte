<script lang="ts">
  // One scenario, as the projection page below the hero: headline, date, presentation, the adjustments it
  // makes (each with the seats it moves on its own; the whole set opens in the simulator), the seat bar
  // against the projection and, behind «Leer más», the map and the closest seats.
  import { slide } from 'svelte/transition';
  import SeatBar from './SeatBar.svelte';
  import HexMap from './HexMap.svelte';
  import LastSeat from './LastSeat.svelte';
  import { run, historyEntries } from '$lib/model';
  import { PARTY, BLOC } from '$lib/parties';
  import { longDate, sgnInt } from '$lib/format';
  import { encodeScenario } from '$lib/share';
  import { href } from '$lib/nav';
  import { scenarioOf, type Escenario } from '$lib/escenarios';
  import type { PartyKey } from '$lib/types';

  let { e, latest = true }: { e: Escenario; latest?: boolean } = $props();
  const st = $derived(scenarioOf(e));
  const cur = $derived(run(st));
  const entries = $derived(historyEntries(st));
  // the simulator with these adjustments as its starting point (?e=… travels before the #/… of the hash router)
  const simHref = $derived.by(() => {
    const h = href('/simula'), q = '?e=' + encodeScenario(st);
    return h.startsWith('#') ? q + h : h + q;
  });
  let scope = $state('ES');
  let focusParty = $state('PP');
  let open = $state(false);
  // older scenarios, pushed down by newer ones, show only the headline, the date and a mini seat bar;
  // «Leer más» unfolds the whole scenario
  let full = $state(false);
  const compact = $derived(!latest && !full);
  const toggle = () => { if (latest) open = !open; else { full = !full; open = full; } };
  const expanded = $derived(latest ? open : full);
  const mini = $derived(BLOC.filter((P) => cur.seats[P]).map((P) => ({ P, f: cur.seats[P] / 350 })));
  // Material Symbols Outlined fork_chart, as the Escenarios tab
  const FORK = 'M120-160v-310q-26-7-43-28t-17-50v-192q0-8 6-14t14-6q8 0 14 6t6 14v140h30v-140q0-8 6-14t14-6q8 0 14 6t6 14v140h30v-140q0-8 6-14t14-6q8 0 14 6t6 14v192q0 29-17 50t-43 28v310h-60Zm480 1q-134 0-227.5-93.5T279-480q0-133 93.5-226.5T600-800q133 0 226.5 93.5T920-480q0 134-93.5 227.5T600-159Zm203-482L642-480l161 162q26-34 41.5-75t15.5-87q0-46-15.5-87T803-641Zm-173-97v186l131-131q-28-22-61-36t-70-19Zm-30 519q46 0 87-15.5t74-41.5L570-467v-271q-98 11-164.5 84.5T339-480q0 109 76 185t185 76Z';
  const nm = (k: string) => PARTY[k as PartyKey].n;
</script>

<article class="sec esc" class:compact id={e.slug}>
  <section class="sec">
    <h2 class="hd w">{@html e.title}</h2>
    <p class="updated w"><time datetime={e.date}>{longDate(e.date)}</time></p>
    {#if compact}
      <div class="w minibar" role="img" aria-label="Escaños en este escenario">
        {#each mini as s (s.P)}<span style="width:{s.f * 100}%;background:{PARTY[s.P].c}"></span>{/each}
        <i class="maj" aria-hidden="true"></i>
      </div>
    {:else}
      <p class="lede w">{@html e.body}</p>
      <div class="w supuestos">
        <div class="shead">Los supuestos</div>
        <a class="tosim" href={simHref} aria-label="Abrir en el simulador"><svg viewBox="0 -960 960 960" aria-hidden="true"><path d={FORK} /></svg><span class="tip">Abrir en el simulador</span></a>
        <ol class="slist">
          {#each entries as x (x.key)}
            <li>
              <div class="stext">{@html x.html}</div>
              <div class="simpact">
                {#each x.impact as [k, d]}<span class:up={d > 0} class:down={d < 0}>{sgnInt(d)} {nm(k)}</span>{:else}<span class="zero">sin cambio de escaños por sí solo</span>{/each}
              </div>
            </li>
          {/each}
        </ol>
      </div>
      <div class="f"><SeatBar {cur} bind:scope who="este" /></div>
    {/if}
  </section>

  {#if open}
    <section class="sec" transition:slide={{ duration: 350 }}>
      <h3 class="hd w">Así quedaría <strong>el reparto por provincias</strong> en este escenario.</h3>
      <HexMap {cur} bind:scope bind:focusParty who="este" />
    </section>
    <section class="sec" transition:slide={{ duration: 350 }}><div class="w stack"><LastSeat {cur} bind:scope who="este" /></div></section>
  {/if}
  <div class="w more">
    <button type="button" aria-expanded={expanded} aria-controls={e.slug} onclick={toggle}>
      {expanded ? 'Leer menos' : 'Leer más'}
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" class:flip={expanded}><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
    </button>
  </div>
</article>

<style>
  .esc { row-gap: var(--s3); padding-top: var(--s4); border-top: 1px solid var(--line); }
  :global(.esc:first-child) { padding-top: 0; border-top: 0; }
  .esc :global(.updated) { margin: -8px 0 0; font-family: var(--font-ui); font-size: 14px; font-weight: 700; color: #c4314b; }
  /* the adjustments, as the simulator's step-by-step panel */
  .supuestos { position: relative; display: flex; flex-direction: column; gap: 12px; padding: 16px 18px; border-radius: 10px; background: var(--panel); }
  .compact { row-gap: var(--s2); }
  /* older scenarios: the scenario's seats as a slim bar, with the 176 line */
  .minibar { position: relative; display: flex; height: 14px; border-radius: 3px; overflow: hidden; max-width: 520px; }
  .minibar span { display: block; height: 100%; }
  .minibar span + span { box-shadow: inset 1px 0 0 var(--bg); }
  .minibar .maj { position: absolute; left: calc(176 / 350 * 100%); top: -3px; bottom: -3px; border-left: 2px dashed var(--ink); }
  .shead { font-family: var(--font-ui); font-weight: 700; font-size: 14px; color: var(--muted); }
  .slist { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
  .slist li { padding: 10px 0; border-bottom: 1px solid var(--line); display: flex; flex-direction: column; gap: 5px; }
  .slist li:first-child { padding-top: 0; }
  .slist li:last-child { padding-bottom: 0; border-bottom: 0; }
  .stext { font-family: var(--font-ui); font-size: 14px; line-height: 1.45; color: var(--muted); }
  .stext :global(strong) { font-weight: 700; color: var(--ink); }
  .simpact { display: flex; flex-wrap: wrap; gap: 4px; }
  .simpact span { font-family: var(--font-ui); font-weight: 700; font-size: 12px; font-variant-numeric: tabular-nums; padding: 2px 7px; border-radius: 4px; }
  .simpact .up { background: var(--up-bg); } .simpact .down { background: var(--down-bg); }
  .simpact .zero { color: var(--muted); background: var(--bg); font-weight: 400; }
  /* open in the simulator: icon-only button floating top right of the box, its name on hover */
  .tosim { position: absolute; top: 10px; right: 10px; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 999px; background: var(--ink); color: var(--bg); }
  .tosim:hover { opacity: 0.85; }
  .tosim svg { width: 20px; height: 20px; fill: currentColor; }
  .tosim .tip { position: absolute; right: calc(100% + 8px); top: 50%; transform: translateY(-50%); white-space: nowrap; pointer-events: none; opacity: 0; transition: opacity 0.15s ease;
    font-family: var(--font-ui); font-size: 13px; line-height: 18px; padding: 4px 10px; border-radius: 6px; color: var(--ink);
    background: color-mix(in srgb, var(--bg) 78%, transparent); -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px); box-shadow: var(--shadow); }
  .tosim:hover .tip, .tosim:focus-visible .tip { opacity: 1; }
  .more button { display: inline-flex; align-items: center; gap: 4px; font-family: var(--font-ui); font-weight: 400; font-size: 14px; line-height: 18px; cursor: pointer;
    border: 0; border-radius: 999px; background: var(--ink); color: var(--bg); padding: 7px 12px 7px 16px; }
  .more button:hover { opacity: 0.85; }
  .more svg { transition: transform 0.3s ease; }
  .more svg.flip { transform: rotate(180deg); }
  .stack { display: flex; flex-direction: column; gap: 14px; }
</style>
