<script lang="ts">
  // The data behind each answer, side by side, as bullet graphs: for each party, a thick bar in its colour for
  // its share in the group the scenario is about, and inside it a thin bar in a darker shade for its share among
  // everyone (the whole). One column per source, on the same scale.
  import { PARTY } from '$lib/parties';
  import type { PartyKey } from '$lib/types';

  type Chart = { title: string; group: string; rows: [string, PartyKey, number, number | null][]; note: string };
  let { charts, sources }: { charts: Chart[]; sources: string[] } = $props();
  const max = $derived(Math.max(...charts.flatMap((c) => c.rows.flatMap(([, , a, g]) => [a, g ?? 0]))));
  // bars up to half the column, so the values fit to their right
  const w = (x: number) => `${(50 * x) / max}%`;
  const num = (x: number) => x.toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %';
  const far = (all: number, grp: number | null) => w(Math.max(all, grp ?? 0));
</script>

<div class="ages">
  {#each charts as c, i (c.title)}
    <figure class="col">
      <figcaption class="dhead">{c.title}</figcaption>
      <div class="legend"><span><i class="grp"></i>{c.group}</span><span><i class="all"></i>Conjunto</span></div>
      {#each c.rows as [label, P, all, grp] (label)}
        <div class="row">
          <div class="nm"><i style="background:{PARTY[P].c}"></i>{label}</div>
          <div class="bullet" style="--c:{PARTY[P].c}">
            <div class="track" style="width:{far(all, grp)}">
              <span class="grp" style="width:{grp == null ? 0 : (100 * grp) / Math.max(all, grp)}%"></span>
              <span class="all" style="width:{(100 * all) / Math.max(all, grp ?? 0)}%"></span>
            </div>
            <em><b>{grp == null ? '< 2 %' : num(grp)}</b> / {num(all)}</em>
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
  .legend .grp { height: 12px; background: var(--muted); }
  .legend .all { height: 4px; background: var(--ink); }
  .row { display: grid; grid-template-columns: 78px minmax(0, 1fr); gap: 8px; align-items: center; }
  .nm { display: flex; align-items: center; gap: 5px; font-family: var(--font-ui); font-size: 13px; color: var(--ink); font-weight: 400; white-space: nowrap; }
  .nm i { width: 8px; height: 8px; border-radius: 2px; flex: none; }
  .bullet { display: flex; align-items: center; gap: 8px; }
  .track { position: relative; height: 16px; flex: none; min-width: 2px; }
  .track span { position: absolute; left: 0; display: block; border-radius: 2px; }
  .track .grp { top: 0; height: 16px; background: var(--c); }
  /* the whole: a darker shade of the party's colour */
  .track .all { top: 6px; height: 4px; background: color-mix(in srgb, var(--c) 55%, #000); }
  .bullet em { font-style: normal; font-family: var(--font-ui); font-size: 11px; color: var(--muted); font-weight: 400; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .bullet em b { color: var(--ink); font-weight: 700; }
  /* sources: links as in running text */
  .note :global(a) { color: inherit; text-decoration: underline; text-decoration-color: var(--muted); text-underline-offset: 3px; }
  .note :global(a:hover) { text-decoration-color: var(--fg); }
  @media (max-width: 760px) { .ages { grid-template-columns: 1fr; } }
</style>
