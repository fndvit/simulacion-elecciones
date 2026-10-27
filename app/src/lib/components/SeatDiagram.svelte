<script lang="ts">
  import ScrollX from './ScrollX.svelte';
  // Atlas SeatDiagram: D'Hondt quotient grid for one constituency, with the last (most fragile)
  // seat and the next in the queue outlined.
  import { PARTY, ORDER } from '$lib/parties';
  import { fmtN } from '$lib/format';
  import type { ProvResult } from '$lib/types';

  let { r }: { r: ProvResult } = $props();

  const grid = $derived.by(() => {
    const cols = ORDER.filter((P) => r.seats[P] || P === r.chal?.k).sort((a, b) => (r.votes[b] || 0) - (r.votes[a] || 0)).slice(0, 7);
    const maxS = Math.max(1, ...cols.map((P) => r.seats[P] || 0));
    return { cols, rows: Array.from({ length: Math.min(maxS + 1, 14) }, (_, i) => i + 1) };
  });
</script>

<div class="diagram">
  <ScrollX>
  <div class="dgrid" style="grid-template-columns: 30px repeat({grid.cols.length}, minmax(54px, 1fr))">
    <div></div>
    {#each grid.cols as P}<div class="chead" style="color:{PARTY[P].c}">{PARTY[P].n}</div>{/each}
    {#each grid.rows as d}
      <div class="rowlab">÷{d}</div>
      {#each grid.cols as P}
        {@const won = d <= (r.seats[P] || 0)}
        <div class="cell" class:won class:last={won && r.last?.k === P && d === r.seats[P]} class:next={!won && r.chal?.k === P && d === (r.seats[P] || 0) + 1}
          style={won ? `background:${PARTY[P].c}` : ''}>{fmtN((r.votes[P] || 0) / d)}</div>
      {/each}
    {/each}
  </div>
  </ScrollX>
  <p class="legend">
    <span class="c" style="background:var(--muted)"></span> escaño asignado ·
    <span class="c last"></span> último escaño ·
    <span class="c next"></span> siguiente en la cola
  </p>
</div>

<style>
  .diagram { display: flex; flex-direction: column; gap: 12px; }
  .dgrid { display: grid; gap: 4px; }
  .chead { font-family: var(--font-ui); font-weight: 700; font-size: 12px; text-align: center; padding-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .rowlab { font-family: var(--font-ui); font-size: 12px; color: var(--muted); display: flex; align-items: center; justify-content: flex-end; padding-right: 4px; }
  .cell { font-family: var(--font-ui); font-size: 12px; font-variant-numeric: tabular-nums; text-align: center; padding: 6px 2px; border-radius: 4px; color: var(--muted); background: var(--panel); font-weight: 400; }
  .cell.won { font-weight: 700; color: #fff; }
  .cell.last { outline: 2px solid var(--stroke); outline-offset: -2px; }
  .cell.next { outline: 2px dashed var(--fg); outline-offset: -2px; color: var(--ink); font-weight: 700; }
  .legend { font-family: var(--font-ui); font-size: 12px; color: var(--muted); display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin: 0; font-weight: 400; }
  .c { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
  .c.last { outline: 2px solid var(--stroke); outline-offset: -2px; }
  .c.next { outline: 2px dashed var(--fg); outline-offset: -2px; }
</style>
