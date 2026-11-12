<script lang="ts">
  // The data behind each answer, side by side: for each party, its share among everyone (light bar) and in the
  // group the scenario is about (bar in the party's colour), one column per source, on the same scale.
  import { PARTY } from '$lib/parties';
  import type { PartyKey } from '$lib/types';

  type Chart = { title: string; group: string; rows: [string, PartyKey, number, number | null][]; note: string };
  let { charts, sources }: { charts: Chart[]; sources: string[] } = $props();
  const max = $derived(Math.max(...charts.flatMap((c) => c.rows.flatMap(([, , a, g]) => [a, g ?? 0]))));
  // bars up to 78 % of the width, so the largest value's label still fits
  const w = (x: number) => `${(78 * x) / max}%`;
  const num = (x: number) => x.toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %';
</script>

<div class="ages">
  {#each charts as c, i (c.title)}
    <figure class="col">
      <figcaption class="dhead">{c.title}</figcaption>
      <div class="legend"><span><i class="all"></i>Todos</span><span><i class="grp"></i>{c.group}</span></div>
      {#each c.rows as [label, P, all, grp] (label)}
        <div class="row">
          <div class="nm"><i style="background:{PARTY[P].c}"></i>{label}</div>
          <div class="pair">
            <div class="b"><span class="all" style="width:{w(all)}"></span><em>{num(all)}</em></div>
            <div class="b"><span style="width:{w(grp ?? 0)};background:{PARTY[P].c}"></span><em>{grp == null ? 'menos del 2 %' : num(grp)}</em></div>
          </div>
        </div>
      {/each}
      <p class="note">{c.note} Fuente: {@html sources[i]}.</p>
    </figure>
  {/each}
</div>

<style>
  .ages { display: grid; grid-template-columns: 1fr 1fr; gap: 24px 32px; }
  .col { margin: 0; display: flex; flex-direction: column; gap: 8px; min-width: 0; }
  .dhead { font-family: var(--font-ui); font-weight: 700; font-size: 14px; line-height: 20px; color: var(--fg); }
  .legend { display: flex; gap: 14px; font-family: var(--font-ui); font-size: 12px; color: var(--muted); font-weight: 400; }
  .legend span { display: inline-flex; align-items: center; gap: 5px; }
  .legend i { width: 14px; height: 8px; border-radius: 2px; }
  .legend .all { background: var(--line); }
  .legend .grp { background: var(--ink); }
  .row { display: grid; grid-template-columns: 78px minmax(0, 1fr); gap: 8px; align-items: center; }
  .nm { display: flex; align-items: center; gap: 5px; font-family: var(--font-ui); font-size: 13px; color: var(--ink); font-weight: 400; white-space: nowrap; }
  .nm i { width: 8px; height: 8px; border-radius: 2px; flex: none; }
  .pair { display: flex; flex-direction: column; gap: 2px; }
  .b { display: flex; align-items: center; gap: 6px; height: 12px; }
  .b span { display: block; height: 100%; border-radius: 2px; flex: none; }
  .b span.all { background: var(--line); }
  .b em { font-style: normal; font-family: var(--font-ui); font-size: 11px; color: var(--muted); font-weight: 400; font-variant-numeric: tabular-nums; white-space: nowrap; }
  /* sources: links as in running text */
  .note :global(a) { color: inherit; text-decoration: underline; text-decoration-color: var(--muted); text-underline-offset: 3px; }
  .note :global(a:hover) { text-decoration-color: var(--fg); }
  @media (max-width: 560px) { .ages { grid-template-columns: 1fr; } }
</style>
