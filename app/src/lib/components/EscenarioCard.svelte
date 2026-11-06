<script lang="ts">
  // A scenario in the list at the top of the page, as the short version: headline, date, the scenario's seats in
  // a slim bar with the 176 line and, below, the seats it moves against the projection.
  // Clicking it opens the scenario, whole, below the list.
  import { run, BASE } from '$lib/model';
  import { PARTY, BLOC } from '$lib/parties';
  import { longDate, sgnInt } from '$lib/format';
  import { scenarioOf, type Escenario, type Ctx } from '$lib/escenarios';
  import { DATA } from '$lib/data';
  import type { PartyKey } from '$lib/types';

  let { e, selected = false, onselect }: { e: Escenario; selected?: boolean; onselect: () => void } = $props();
  const st = $derived(scenarioOf(e));
  const cur = $derived(run(st));
  const ctx = $derived<Ctx>({ st, cur, base: BASE, today: DATA.today });
  const title = $derived(typeof e.title === 'function' ? e.title(ctx) : e.title);
  const delta = (P: string) => (cur.seats[P] || 0) - (BASE.seats[P] || 0);
  const segs = $derived(BLOC.filter((P) => cur.seats[P]).map((P) => ({ P, f: cur.seats[P] / 350 })));
  const changes = $derived(BLOC.map((P) => ({ P, d: delta(P) })).filter((x) => x.d).sort((a, b) => b.d - a.d));
  const nm = (k: string) => PARTY[k as PartyKey].n;
</script>

<button type="button" class="item w" class:on={selected} aria-pressed={selected} onclick={onselect}>
  <span class="hd t">{@html title}</span>
  <span class="date"><time datetime={e.date}>{longDate(e.date)}</time></span>
  <span class="minibar" role="img" aria-label="Escaños en este escenario">
    {#each segs as s (s.P)}<span style="width:{s.f * 100}%;background:{PARTY[s.P].c}"></span>{/each}
    <i class="maj" aria-hidden="true"></i>
  </span>
  <span class="chg">
    {#each changes as c (c.P)}<span class:up={c.d > 0} class:down={c.d < 0}>{sgnInt(c.d)} {nm(c.P)}</span>{:else}<span class="zero">sin cambio de escaños</span>{/each}
  </span>
</button>

<style>
  .item { display: flex; flex-direction: column; gap: 10px; text-align: left; cursor: pointer; padding: 0; border: 0; background: none; color: var(--ink); font: inherit; }
  .t { display: block; font-family: var(--font-ui); }   /* .hd sets size and weight; the button would give it the body font */
  .item:hover .t, .item:focus-visible .t { text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 5px; }
  /* the one open below: its headline underlined */
  .item.on .t { text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 5px; }
  .date { font-family: var(--font-ui); font-size: 14px; font-weight: 700; color: #c4314b; margin-top: -4px; }
  /* the scenario's seats as a slim bar, with the 176 line */
  .minibar { position: relative; display: flex; height: 14px; border-radius: 3px; overflow: hidden; width: 100%; max-width: 520px; }
  .minibar span { display: block; height: 100%; }
  .minibar span + span { box-shadow: inset 1px 0 0 var(--bg); }
  .minibar .maj { position: absolute; left: calc(176 / 350 * 100%); top: 0; bottom: 0; border-left: 2px dashed var(--ink); }
  .chg { display: flex; flex-wrap: wrap; gap: 4px; }
  .chg span { font-family: var(--font-ui); font-weight: 700; font-size: 12px; font-variant-numeric: tabular-nums; padding: 2px 7px; border-radius: 4px; }
  .chg .up { background: var(--up-bg); } .chg .down { background: var(--down-bg); }
  .chg .zero { color: var(--muted); background: var(--panel); font-weight: 400; }
</style>
