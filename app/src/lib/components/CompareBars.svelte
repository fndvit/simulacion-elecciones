<script lang="ts">
  // Two answers to the same scenario, one above the other and mirrored: thin bar 2023, fat bar the first
  // source's scenario, fat bar the second's, thin bar 2023; between each thin and fat bar, the ribbons from 2023
  // seats to the scenario's, as in the seat bar. Below, what each one changes against the projection, in two
  // columns, and how far PP + Vox are from the majority.
  import { isTouch, dismiss, tipStyle } from '$lib/touch';
  import { PARTY, BLOC } from '$lib/parties';
  import { BASE, seats2023, sumSeats } from '$lib/model';
  import { sgnInt } from '$lib/format';
  import type { RunResult, PartyKey } from '$lib/types';

  // part: the mirrored bars (full width) or the changes of each (in the text well)
  let { a, b, part = 'bars' }: { a: { name: string; cur: RunResult }; b: { name: string; cur: RunResult }; part?: 'bars' | 'changes' } = $props();
  let W = $state(800);
  const N = 350, BAND = 34;
  const s23 = seats2023('ES');
  const n23 = Object.values(s23).reduce((x, y) => x + y, 0) || 1;
  /** «Según el CIS», «Según 40dB» */
  const segun = (v: { name: string }) => 'Según ' + v.name;

  function segsOf(cur: RunResult) {
    let accF = 0, accS = 0;
    return BLOC.filter((P) => (s23[P] || 0) + (cur.seats[P] || 0) > 0).map((P) => {
      const f = (cur.seats[P] || 0) / N, s = (s23[P] || 0) / n23;
      accF += f; accS += s;
      return { P, f, s, f0: accF - f, s0: accS - s, d23: (cur.seats[P] || 0) - (s23[P] || 0) };
    });
  }
  /** the ribbons; down: 2023 below the scenario (the mirrored half) */
  function bandOf(segs: ReturnType<typeof segsOf>, down: boolean) {
    let last = -1e9;
    return segs.map((x) => {
      const a0 = x.s0 * W, a1 = (x.s0 + x.s) * W, b0 = x.f0 * W, b1 = (x.f0 + x.f) * W;
      const lx = x.f ? (b0 + b1) / 2 : (a0 + a1) / 2;
      const show = x.d23 !== 0 && lx - last > 26;
      if (show) last = lx;
      const [ya, yb] = down ? [BAND, 0] : [0, BAND];
      return { P: x.P, pts: `${a0},${ya} ${a1},${ya} ${b1},${yb} ${b0},${yb}`, lx, show, d: x.d23 };
    });
  }
  const segA = $derived(segsOf(a.cur)), segB = $derived(segsOf(b.cur));
  const bandA = $derived(bandOf(segA, false)), bandB = $derived(bandOf(segB, true));

  /** what each one changes against the projection, in bloc order */
  const changes = (cur: RunResult) => BLOC.map((P) => [P, (cur.seats[P] || 0) - (BASE.seats[P] || 0)] as [PartyKey, number]).filter(([, d]) => d);
  const cols = $derived([a, b].map((v) => ({ v, ch: changes(v.cur), right: sumSeats(v.cur.seats, ['PP', 'VOX']) })));
  const right0 = sumSeats(BASE.seats, ['PP', 'VOX']);

  // hover: the party stands out in all four bars, with its seats in each
  let hov = $state<PartyKey | null>(null);
  let tip = $state({ x: 0, y: 0, h: 0 });
  let barsEl = $state<HTMLDivElement>();
  function over(e: PointerEvent, P: PartyKey) { const r = barsEl!.getBoundingClientRect(); hov = P; tip = { x: e.clientX - r.left, y: e.clientY - r.top, h: r.height }; }
</script>

{#if part === 'bars'}
<div class="cmp" bind:clientWidth={W}>
  <div class="cap"><b>Congreso</b> · 350 escaños · mayoría absoluta, 176</div>
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="bars" class:hovering={hov} bind:this={barsEl} onpointerleave={(e) => { if (!isTouch(e)) hov = null; }} use:dismiss={() => (hov = null)}>
    <span class="blab top" aria-hidden="true">23J</span>
    <div class="bar slim" role="img" aria-label="Escaños en 2023">
      {#each segA as s (s.P)}{#if s.s}<span class:on={hov === s.P} style="width:{s.s * 100}%;background:{PARTY[s.P].c}" onpointermove={(e) => over(e, s.P)} onpointerdown={(e) => over(e, s.P)}></span>{/if}{/each}
    </div>
    <svg class="band" width={W} height={BAND} viewBox="0 0 {W} {BAND}" aria-label="De los escaños de 2023 a los de este escenario, {segun(a)}">
      {#each bandA as x (x.P)}<polygon points={x.pts} fill={PARTY[x.P].c} opacity={hov ? (hov === x.P ? 0.6 : 0.12) : 0.28} onpointermove={(e) => over(e, x.P)} onpointerdown={(e) => over(e, x.P)} />{/each}
      {#each bandA as x (x.P)}{#if x.show}<text x={x.lx} y={BAND - 7} text-anchor="middle" class:up={x.d > 0} class:down={x.d < 0}>{sgnInt(x.d)}</text>{/if}{/each}
    </svg>
    <div class="bar fat" role="img" aria-label="Escaños en este escenario, {segun(a)}">
      {#each segA as s (s.P)}{#if s.f}<span class:on={hov === s.P} style="width:{s.f * 100}%;background:{PARTY[s.P].c}" onpointermove={(e) => over(e, s.P)} onpointerdown={(e) => over(e, s.P)}></span>{/if}{/each}
      <b class="blab in" aria-hidden="true">{segun(a)}</b>
    </div>
    <div class="gap"></div>
    <div class="bar fat" role="img" aria-label="Escaños en este escenario, {segun(b)}">
      {#each segB as s (s.P)}{#if s.f}<span class:on={hov === s.P} style="width:{s.f * 100}%;background:{PARTY[s.P].c}" onpointermove={(e) => over(e, s.P)} onpointerdown={(e) => over(e, s.P)}></span>{/if}{/each}
      <b class="blab in low" aria-hidden="true">{segun(b)}</b>
    </div>
    <svg class="band" width={W} height={BAND} viewBox="0 0 {W} {BAND}" aria-label="De los escaños de 2023 a los de este escenario, {segun(b)}">
      {#each bandB as x (x.P)}<polygon points={x.pts} fill={PARTY[x.P].c} opacity={hov ? (hov === x.P ? 0.6 : 0.12) : 0.28} onpointermove={(e) => over(e, x.P)} onpointerdown={(e) => over(e, x.P)} />{/each}
      {#each bandB as x (x.P)}{#if x.show}<text x={x.lx} y={19} text-anchor="middle" class:up={x.d > 0} class:down={x.d < 0}>{sgnInt(x.d)}</text>{/if}{/each}
    </svg>
    <div class="bar slim" role="img" aria-label="Escaños en 2023">
      {#each segB as s (s.P)}{#if s.s}<span class:on={hov === s.P} style="width:{s.s * 100}%;background:{PARTY[s.P].c}" onpointermove={(e) => over(e, s.P)} onpointerdown={(e) => over(e, s.P)}></span>{/if}{/each}
    </div>
    <span class="blab bottom" aria-hidden="true">23J</span>
    <div class="maj" aria-hidden="true"></div>
    {#if hov}
      <div class="tip" style={tipStyle(tip.x, tip.y, W, tip.h * 2)}>
        <h4><span class="sw" style="background:{PARTY[hov].c}"></span>{PARTY[hov].n}</h4>
        <div>{segun(a)}: <b>{a.cur.seats[hov] || 0}</b>{#if (a.cur.seats[hov] || 0) - (BASE.seats[hov] || 0)} ({sgnInt((a.cur.seats[hov] || 0) - (BASE.seats[hov] || 0))}){/if}</div>
        <div>{segun(b)}: <b>{b.cur.seats[hov] || 0}</b>{#if (b.cur.seats[hov] || 0) - (BASE.seats[hov] || 0)} ({sgnInt((b.cur.seats[hov] || 0) - (BASE.seats[hov] || 0))}){/if}</div>
        <div>Proyección: <b>{BASE.seats[hov] || 0}</b> · en 2023: <b>{s23[hov] || 0}</b></div>
      </div>
    {/if}
  </div>
  <div class="note">Barras finas: escaños de 2023; entre las barras, el cambio desde entonces · barras gruesas: este escenario según {a.name} (arriba) y según {b.name} (abajo). En 2023, Frente Amplio es Sumar.</div>

</div>
{:else}
  <div class="cols">
    {#each cols as c (c.v.name)}
      <div class="col">
        <div class="dhead">Cambios según {c.v.name}</div>
        <div class="items">
          {#each c.ch as [P, d] (P)}
            <div class="ditem">
              <div class="dparty"><i style="background:{PARTY[P].c}"></i>{PARTY[P].n}</div>
              <div class="dnum" class:up={d > 0} class:down={d < 0}>{sgnInt(d)}</div>
            </div>
          {:else}<div class="none">No cambia ningún escaño.</div>{/each}
        </div>
        <div class="sums">PP + Vox <b>{c.right}</b> {#if c.right !== right0}<span class="was">({sgnInt(c.right - right0)})</span>{/if} {#if c.right >= 176}<span class="ok">mayoría absoluta</span>{:else}· a {176 - c.right} de la mayoría absoluta{/if}</div>
      </div>
    {/each}
  </div>
{/if}

<style>
  .cmp { display: flex; flex-direction: column; gap: 7px; }
  .cap { font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; }
  .cap b { color: var(--fg); }
  .bars { position: relative; display: flex; flex-direction: column; margin: 16px 0 18px; }
  .band { display: block; overflow: visible; }
  .band text { font-family: var(--font-ui); font-size: 11px; font-weight: 700; fill: var(--muted); paint-order: stroke; stroke: var(--bg); stroke-width: 3px; font-variant-numeric: tabular-nums; }
  .band text.up { fill: var(--up); } .band text.down { fill: var(--down); }
  .bar { display: flex; width: 100%; overflow: hidden; border-radius: 6px; background: var(--panel); }
  .bar span { height: 100%; display: block; cursor: pointer; transition: opacity 0.15s ease, width 0.35s ease; }
  .bar span + span { box-shadow: -1px 0 0 var(--bg); }
  .band polygon { cursor: pointer; transition: opacity 0.15s ease; }
  .hovering .bar span:not(.on) { opacity: 0.35; }
  .bar.slim { height: 12px; opacity: 0.72; }
  .bar.fat { height: 56px; position: relative; }
  .gap { height: 6px; }
  .blab { font-family: var(--font-ui); font-size: 11px; line-height: 1; pointer-events: none; }
  .blab.top { position: absolute; left: 0; top: -16px; color: var(--muted); font-weight: 400; }
  .blab.bottom { position: absolute; left: 0; bottom: -16px; color: var(--muted); font-weight: 400; }
  .blab.in { position: absolute; left: 8px; top: 7px; color: #fff; font-weight: 700; text-shadow: 0 0 3px rgb(0 0 0 / 0.35); }
  .blab.in.low { top: auto; bottom: 7px; }
  .maj { position: absolute; left: 50%; top: -6px; bottom: -6px; border-left: 2px dashed var(--stroke); }
  .maj::after { content: '176'; position: absolute; top: -18px; left: -12px; font-family: var(--font-ui); font-size: 11px; font-weight: 700; color: var(--ink); }
  .tip .sw { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; vertical-align: -1px; }

  /* the changes, one column per source */
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 20px 32px; }
  .col { display: flex; flex-direction: column; gap: 10px; }
  .dhead { font-family: var(--font-ui); font-weight: 700; font-size: 14px; line-height: 20px; color: var(--fg); }
  .items { display: flex; flex-wrap: wrap; gap: 8px 16px; }
  .ditem { display: flex; flex-direction: column; align-items: flex-start; }
  .dparty { font-family: var(--font-ui); font-size: 13px; line-height: 20px; white-space: nowrap; color: var(--muted); font-weight: 400; display: flex; align-items: center; gap: 5px; }
  .dparty i { width: 8px; height: 8px; border-radius: 2px; }
  .dnum { font-family: var(--font-ui); font-weight: 700; font-size: 30px; line-height: 1; font-variant-numeric: tabular-nums; }
  .dnum.up { color: var(--up); } .dnum.down { color: var(--down); }
  .none { font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; }
  .sums { font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; }
  .sums b { color: var(--ink); font-size: 18px; font-variant-numeric: tabular-nums; }
  .sums .was { font-weight: 700; color: var(--muted); }
  .sums .ok { color: var(--up); font-weight: 700; }
  @media (max-width: 820px) { .dnum { font-size: 26px; } }
  @media (max-width: 560px) { .cols { grid-template-columns: 1fr; } }
</style>
