<script lang="ts">
  // Atlas HistoryRail: every adjustment, with the seats it moves on its own vs the projection.
  import { PARTY } from '$lib/parties';
  import type { HistoryEntry } from '$lib/model';
  import { sgnInt } from '$lib/format';
  import type { RunResult, Scenario, PartyKey } from '$lib/types';

  let { entries, st = $bindable(), cur }: { entries: HistoryEntry[]; st: Scenario; cur: RunResult } = $props();
  const nm = (k: string) => PARTY[k as PartyKey].n;
</script>

<div class="history">
  <div class="hhead">Tu escenario, paso a paso</div>
  {#if entries.length}
    <ol class="hlist">
      {#each entries as e (e.key)}
        <li class="hentry">
          <div class="htext">{@html e.html}</div>
          <div class="himpact">
            {#each e.impact as [k, d]}<span class:up={d > 0} class:down={d < 0}>{sgnInt(d)} {nm(k)}</span>{:else}<span class="zero">sin cambio de escaños por sí solo</span>{/each}
          </div>
          <button class="hx" onclick={() => e.undo(st)}>Quitar</button>
        </li>
      {/each}
    </ol>
  {:else}
    <p class="hempty">Mueve los controles de la izquierda: cada ajuste aparecerá aquí con los escaños que mueve por sí solo, frente a la proyección.</p>
  {/if}
</div>

<style>
  .history { display: flex; flex-direction: column; gap: 16px; }
  .hhead { font-family: var(--font-ui); font-weight: 700; font-size: 14px; color: var(--muted); }
  .hlist { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
  .hentry { padding: 12px 0; border-bottom: 1px solid var(--line); display: flex; flex-direction: column; gap: 5px; }
  .hentry:first-child { padding-top: 0; }
  .htext { font-family: var(--font-ui); font-size: 14px; line-height: 1.45; color: var(--muted); font-weight: 400; }
  .htext :global(strong) { font-weight: 700; color: var(--ink); }
  .himpact { display: flex; flex-wrap: wrap; gap: 4px; }
  .himpact span { font-family: var(--font-ui); font-weight: 700; font-size: 12px; font-variant-numeric: tabular-nums; padding: 2px 7px; border-radius: 4px; }
  .himpact .up { background: var(--up-bg); } .himpact .down { background: var(--down-bg); }
  .himpact .zero { color: var(--muted); background: var(--panel); font-weight: 400; }
  .hx { align-self: flex-start; background: none; border: 0; padding: 0; font-family: var(--font-ui); font-size: 12px; color: var(--muted); cursor: pointer; text-decoration: underline; }
  .hempty { font-family: var(--font-ui); font-size: 14px; line-height: 1.5; color: var(--muted); margin: 0; font-weight: 400; }
</style>
