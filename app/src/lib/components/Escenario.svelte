<script lang="ts">
  // One scenario, as the projection page below the hero: headline, date, presentation, the adjustments it
  // makes (each with the seats it moves on its own; the whole set opens in the simulator), the seat bar
  // against the projection and, behind «Leer más», the map and the closest seats.
  import { slide } from 'svelte/transition';
  import SeatBar from './SeatBar.svelte';
  import HexMap from './HexMap.svelte';
  import LastSeat from './LastSeat.svelte';
  import { run, historyEntries } from '$lib/model';
  import { PARTY } from '$lib/parties';
  import { longDate, sgnInt } from '$lib/format';
  import { encodeScenario } from '$lib/share';
  import { href } from '$lib/nav';
  import { scenarioOf, type Escenario } from '$lib/escenarios';
  import type { PartyKey } from '$lib/types';

  let { e }: { e: Escenario } = $props();
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
  const nm = (k: string) => PARTY[k as PartyKey].n;
</script>

<article class="sec esc" id={e.slug}>
  <section class="sec">
    <h2 class="hd w">{@html e.title}</h2>
    <p class="updated w"><time datetime={e.date}>{longDate(e.date)}</time></p>
    <p class="lede w">{@html e.body}</p>
    <div class="w supuestos">
      <div class="shead">Los supuestos</div>
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
      <a class="tosim" href={simHref}>Abre este escenario en el simulador</a>
    </div>
    <div class="f"><SeatBar {cur} bind:scope who="este" /></div>
  </section>

  {#if open}
    <section class="sec" transition:slide={{ duration: 350 }}>
      <h3 class="hd w">Así quedaría <strong>el reparto por provincias</strong> en este escenario.</h3>
      <HexMap {cur} bind:scope bind:focusParty who="este" />
    </section>
    <section class="sec" transition:slide={{ duration: 350 }}><div class="w stack"><LastSeat {cur} bind:scope who="este" /></div></section>
  {/if}
  <div class="w more">
    <button type="button" aria-expanded={open} aria-controls={e.slug} onclick={() => (open = !open)}>
      {open ? 'Leer menos' : 'Leer más'}
      <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" class:up={open}><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
    </button>
  </div>
</article>

<style>
  .esc { row-gap: var(--s3); padding-top: var(--s4); border-top: 1px solid var(--line); }
  :global(.esc:first-child) { padding-top: 0; border-top: 0; }
  .esc :global(.updated) { margin: -8px 0 0; font-family: var(--font-ui); font-size: 14px; font-weight: 700; color: #c4314b; }
  /* the adjustments, as the simulator's step-by-step panel */
  .supuestos { display: flex; flex-direction: column; gap: 12px; padding: 16px 18px; border-radius: 10px; background: var(--panel); }
  .shead { font-family: var(--font-ui); font-weight: 700; font-size: 14px; color: var(--muted); }
  .slist { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
  .slist li { padding: 10px 0; border-bottom: 1px solid var(--line); display: flex; flex-direction: column; gap: 5px; }
  .slist li:first-child { padding-top: 0; }
  .stext { font-family: var(--font-ui); font-size: 14px; line-height: 1.45; color: var(--muted); }
  .stext :global(strong) { font-weight: 700; color: var(--ink); }
  .simpact { display: flex; flex-wrap: wrap; gap: 4px; }
  .simpact span { font-family: var(--font-ui); font-weight: 700; font-size: 12px; font-variant-numeric: tabular-nums; padding: 2px 7px; border-radius: 4px; }
  .simpact .up { background: var(--up-bg); } .simpact .down { background: var(--down-bg); }
  .simpact .zero { color: var(--muted); background: var(--bg); font-weight: 400; }
  .tosim { align-self: flex-start; display: inline-flex; align-items: center; font-family: var(--font-ui); font-size: 14px; line-height: 18px; text-decoration: none;
    border-radius: 999px; background: var(--ink); color: var(--bg); padding: 7px 16px; }
  .tosim:hover { opacity: 0.85; }
  .more button { display: inline-flex; align-items: center; gap: 4px; padding: 0 0 2px; border: 0; border-bottom: 2px solid currentColor; background: none; cursor: pointer;
    font-family: var(--font-ui); font-weight: 700; font-size: 15px; color: var(--ink); }
  .more button:hover { color: #d1366b; }
  .more svg { transition: transform 0.3s ease; }
  .more svg.up { transform: rotate(180deg); }
  .stack { display: flex; flex-direction: column; gap: 14px; }
</style>
