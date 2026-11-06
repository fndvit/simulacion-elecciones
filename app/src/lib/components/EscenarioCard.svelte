<script lang="ts">
  // A scenario in the list at the top of the page: headline, date and a mini seat bar of the scenario where
  // only the parties whose seats change against the projection keep their colour, with those changes below.
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
  const segs = $derived(BLOC.filter((P) => cur.seats[P]).map((P) => ({ P, f: cur.seats[P] / 350, d: delta(P) })));
  const changes = $derived(BLOC.map((P) => ({ P, d: delta(P) })).filter((x) => x.d).sort((a, b) => b.d - a.d));
  const nm = (k: string) => PARTY[k as PartyKey].n;
</script>

<button type="button" class="card" class:on={selected} aria-pressed={selected} onclick={onselect}>
  <span class="t">{@html title}</span>
  <span class="date"><time datetime={e.date}>{longDate(e.date)}</time></span>
  <span class="mini" role="img" aria-label="Escaños en este escenario; en color, los partidos que ganan o pierden escaños frente a la proyección">
    {#each segs as s (s.P)}<span class:still={!s.d} style="width:{s.f * 100}%;background:{PARTY[s.P].c}"></span>{/each}
    <i class="maj" aria-hidden="true"></i>
  </span>
  <span class="chg">
    {#each changes as c (c.P)}<span class:up={c.d > 0} class:down={c.d < 0}>{sgnInt(c.d)} {nm(c.P)}</span>{:else}<span class="zero">sin cambio de escaños</span>{/each}
  </span>
</button>

<style>
  .card { display: flex; flex-direction: column; gap: 10px; width: 100%; height: 100%; text-align: left; cursor: pointer; padding: 16px 18px 18px;
    border: 1px solid var(--line); border-radius: 10px; background: var(--bg); color: var(--ink); font: inherit; transition: background 0.2s ease, border-color 0.2s ease; }
  .card:hover { background: var(--panel); }
  .card.on { background: var(--panel); border-color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
  .t { font-family: var(--font-ui); font-weight: 200; font-size: 19px; line-height: 25px; }
  .t :global(strong) { font-weight: 700; }
  .date { font-family: var(--font-ui); font-size: 13px; font-weight: 700; color: #c4314b; margin-top: -4px; }
  /* the scenario's seats; the parties that do not move, faded */
  .mini { position: relative; display: flex; height: 14px; border-radius: 3px; overflow: hidden; margin-top: auto; }
  .mini span { display: block; height: 100%; }
  .mini span + span { box-shadow: inset 1px 0 0 var(--bg); }
  .mini span.still { opacity: 0.18; }
  .mini .maj { position: absolute; left: calc(176 / 350 * 100%); top: 0; bottom: 0; border-left: 2px dashed var(--ink); }
  .chg { display: flex; flex-wrap: wrap; gap: 4px; }
  .chg span { font-family: var(--font-ui); font-weight: 700; font-size: 12px; font-variant-numeric: tabular-nums; padding: 2px 7px; border-radius: 4px; }
  .chg .up { background: var(--up-bg); } .chg .down { background: var(--down-bg); }
  .chg .zero { color: var(--muted); background: var(--panel); font-weight: 400; }
</style>
