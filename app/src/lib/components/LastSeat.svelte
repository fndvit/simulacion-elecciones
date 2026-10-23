<script lang="ts">
  // The last seat in the selected constituency (or the tightest one nationwide) + the 10 tightest seats.
  import SeatDiagram from './SeatDiagram.svelte';
  import LibDrop from './LibDrop.svelte';
  import { sortEs } from '$lib/format';
  import { PROV, BYID } from '$lib/data';
  import { PARTY } from '$lib/parties';
  import { fmtN, pct } from '$lib/format';
  import type { RunResult, PartyKey } from '$lib/types';

  let { cur, scope = $bindable() }: { cur: RunResult; scope: string } = $props();
  const nm = (k: string) => PARTY[k as PartyKey].n, col = (k: string) => PARTY[k as PartyKey].c;

  const list = $derived(
    PROV.map((p) => ({ p, r: cur.prov[p.id] })).filter((x) => x.r.chal && x.r.last).sort((a, b) => a.r.chal!.need / a.r.valid - b.r.chal!.need / b.r.valid)
  );
  const focus = $derived(scope !== 'ES' ? { p: BYID[scope], r: cur.prov[scope] } : list[0]);
  // the province picker is shared with the map, the controls and the transfers
  const provOpts = [...PROV].sort((a, b) => sortEs(a.n, b.n)).map((p) => ({ value: p.id, label: p.n }));
</script>

<h2 class="hd">
  En <span class="sel"><LibDrop bind:value={() => focus.p.id, (v) => (scope = v)} options={provOpts} label="Provincia" filter /></span>{#if focus.r.last && focus.r.chal}, el último escaño se disputa entre <strong>{nm(focus.r.last.k)}</strong> y <strong>{nm(focus.r.chal.k)}</strong>{/if}
</h2>
{#if scope === 'ES'}<p class="note">Sin provincia elegida se muestra la más ajustada de tu escenario.</p>{/if}
<p class="sub">
  {#if focus.r.chal}{nm(focus.r.chal.k)} necesita <b>{fmtN(focus.r.chal.need)} votos</b> más para quitárselo (un {pct(focus.r.chal.need / focus.r.valid, 2)} del voto válido de la provincia).{/if}
  Cada columna es un partido y cada fila un divisor D'Hondt; el recuadro marca el escaño más frágil y el siguiente en la cola.
</p>
<SeatDiagram r={focus.r} />

<h3 class="hd" style="margin-top:12px">Los <strong>escaños más ajustados</strong> de tu escenario</h3>
<p class="sub">Votos que le faltan al aspirante para arrebatar el último escaño, en proporción al voto válido de cada circunscripción. Pulsa una fila para ir a esa provincia.</p>
<div class="tight">
  {#each list.slice(0, 10) as x (x.p.id)}
    <button class="trow" onclick={() => (scope = x.p.id)}>
      <span class="pv">{x.p.n}</span>
      <span class="vs"><span class="chip first"><i style="background:{col(x.r.last!.k)}"></i>{nm(x.r.last!.k)}</span> tiene el último; <span class="chip"><i style="background:{col(x.r.chal!.k)}"></i>{nm(x.r.chal!.k)}</span>, el más próximo</span>
      <span class="gap">{fmtN(x.r.chal!.need)}</span>
    </button>
  {/each}
</div>

<style>
  .tight { display: flex; flex-direction: column; }
  .sel { display: inline-flex; vertical-align: baseline; }
  .sel :global(.word) { font-size: 24px; line-height: 30px; padding: 0 10px; font-weight: 200; }
  .sel :global(.opts) { max-height: 320px; overflow-y: auto; }
  .sel :global(.opt) { font-size: 16px; line-height: 24px; }
  .trow { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2.2fr) 70px; gap: 10px; align-items: center; padding: 8px 0; border: 0; border-bottom: 1px solid var(--line); font-family: var(--font-ui); font-size: 14px; color: var(--ink); cursor: pointer; background: none; text-align: left; font-weight: 400; }
  .trow:hover { background: var(--panel); }
  .pv { font-weight: 700; }
  .vs { color: var(--muted); line-height: 1.9; }
  .vs .chip.first { margin-right: 3px; }
  .gap { text-align: right; font-variant-numeric: tabular-nums; font-weight: 700; }
  @media (max-width: 820px) {
    .trow { grid-template-columns: minmax(0, 1fr) 84px; }
    .vs { grid-column: 1 / -1; grid-row: 2; }
  }
</style>
