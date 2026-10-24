<script lang="ts">
  // Atlas SeatBar: slim bar = 2023 result, fat bar = scenario, both ordered by bloc (PSOE far left … PP far
  // right) with the 176 majority line. Between them, a small Sankey links each party's 2023 seats to its
  // scenario seats, with the change since 2023 in small type. Under the fat bar, in big type, what YOUR
  // adjustments change against the poll projection (labels pushed sideways, then into rows, if they collide).
  import { BYID } from '$lib/data';
  import { PARTY, BLOC } from '$lib/parties';
  import { BASE, scopeSeats, seats2023, sumSeats, INVEST } from '$lib/model';
  import { sgnInt } from '$lib/format';
  import type { RunResult } from '$lib/types';

  let { cur, scope, projection = false }: { cur: RunResult; scope: string; projection?: boolean } = $props();
  let W = $state(800);

  const isES = $derived(scope === 'ES');
  const n = $derived(isES ? 350 : BYID[scope].seats);
  const sC = $derived(scopeSeats(cur, scope));
  const s23 = $derived(seats2023(scope));
  const n23 = $derived(Object.values(s23).reduce((a, b) => a + b, 0) || 1);
  const sB = $derived(scopeSeats(BASE, scope));

  const segs = $derived.by(() => {
    let accF = 0, accS = 0;
    return BLOC.filter((P) => (s23[P] || 0) + (sC[P] || 0) + (sB[P] || 0) > 0).map((P) => {
      const f = (sC[P] || 0) / n, s = (s23[P] || 0) / n23;
      const c = sC[P] ? accF + f / 2 : accS + s / 2;
      accF += f; accS += s;
      return { P, f, s, c, s0: accS - s, f0: accF - f, d: (sC[P] || 0) - (sB[P] || 0), d23: (sC[P] || 0) - (s23[P] || 0) };
    });
  });
  // 2023 → scenario ribbons + small labels (skipped when they would collide)
  const BAND = 34;
  const band = $derived.by(() => {
    let last = -1e9;
    return segs.map((x) => {
      const a0 = x.s0 * W, a1 = (x.s0 + x.s) * W, b0 = x.f0 * W, b1 = (x.f0 + x.f) * W;
      const lx = x.f ? (b0 + b1) / 2 : (a0 + a1) / 2;
      const show = x.d23 !== 0 && lx - last > 26;
      if (show) last = lx;
      return { P: x.P, pts: `${a0},0 ${a1},0 ${b1},${BAND} ${b0},${BAND}`, lx, show, d: x.d23 };
    });
  });

  const stack = $derived(W < 600);
  const layout = $derived.by(() => {
    const lo = stack ? 4 : Math.min(0.4 * W, 110), hi = W - 4;
    const items = segs.filter((x) => x.d).map((x) => ({ ...x, w: Math.max(PARTY[x.P].n.length * 7 + 22, 22 + String(Math.abs(x.d)).length * 21), x: 0, row: 0 }));
    const layRow = (row: typeof items) => {
      let prev = lo;
      for (const it of row) { it.x = Math.max(it.c * W, prev + it.w / 2); prev = it.x + it.w / 2 + 10; }
      let next = hi;
      for (let i = row.length - 1; i >= 0; i--) { const it = row[i]; it.x = Math.min(it.x, next - it.w / 2); next = it.x - it.w / 2 - 10; }
      return row.length === 0 || row[0].x - row[0].w / 2 >= lo - 1;
    };
    let rows = [items];
    for (let k = 2; !rows.every(layRow) && k <= items.length; k++) rows = Array.from({ length: k }, (_, r) => items.filter((_, i) => i % k === r));
    rows.forEach((row, r) => row.forEach((it) => (it.row = r)));
    return { items, rows: Math.max(1, rows.length) };
  });

  const right = $derived(sumSeats(sC, ['PP', 'VOX']));
  const inv = $derived(sumSeats(sC, INVEST));
</script>

<div class="seatbar" bind:clientWidth={W}>
  <div class="cap"><b>{isES ? 'Congreso' : BYID[scope].n}</b> · {n} {n === 1 ? 'escaño' : 'escaños'}{isES ? ' · mayoría absoluta, 176' : ''}</div>
  <div class="bars">
    <div class="bar slim" role="img" aria-label="Escaños en 2023">
      {#each segs as s (s.P)}{#if s.s}<span style="width:{s.s * 100}%;background:{PARTY[s.P].c}" title="{PARTY[s.P].n}: {s23[s.P] || 0} en 2023"></span>{/if}{/each}
    </div>
    <svg class="band" width={W} height={BAND} viewBox="0 0 {W} {BAND}" aria-label={projection ? "De los escaños de 2023 a los de la proyección" : "De los escaños de 2023 a los de tu escenario"}>
      {#each band as b (b.P)}<polygon points={b.pts} fill={PARTY[b.P].c} opacity="0.28" />{/each}
      {#each band as b (b.P)}{#if b.show}<text x={b.lx} y={BAND - 7} text-anchor="middle" class:up={b.d > 0} class:down={b.d < 0}>{sgnInt(b.d)}</text>{/if}{/each}
    </svg>
    <div class="bar fat" role="img" aria-label={projection ? "Escaños en la proyección" : "Escaños en tu escenario"}>
      {#each segs as s (s.P)}{#if s.f}<span style="width:{s.f * 100}%;background:{PARTY[s.P].c}" title="{PARTY[s.P].n}: {sC[s.P] || 0}"></span>{/if}{/each}
    </div>
    {#if isES}<div class="maj" aria-hidden="true"></div>{/if}
  </div>
  <div class="note">Barra fina: escaños de 2023{!isES && n23 !== n ? ` (${n23})` : ''}; entre las barras, el cambio desde entonces · barra gruesa: {projection ? 'la proyección' : 'tu escenario'}. En 2023, Frente Amplio es Sumar.</div>

  {#if !projection}
  <div class="deltas" class:stack style="min-height:{Math.max(64, layout.rows * 62) + (stack ? 26 : 0)}px">
    <div class="dhead">Cambios en tu escenario</div>
    {#if layout.items.length}
      {#each layout.items as it (it.P)}
        <div class="ditem" style="left:{it.x}px;top:{it.row * 62}px">
          <div class="dparty"><i style="background:{PARTY[it.P].c}"></i>{PARTY[it.P].n}</div>
          <div class="dnum" class:up={it.d > 0} class:down={it.d < 0}>{sgnInt(it.d)}</div>
        </div>
      {/each}
    {:else}
      <div class="none">Mueve los controles: aquí verás los escaños que tus cambios mueven respecto a la proyección de las encuestas.</div>
    {/if}
  </div>
  {/if}

  {#if isES}
    <div class="sums">
      <span>PP + Vox <b>{right}</b> {#if right >= 176}<span class="ok">mayoría</span>{:else}· a {176 - right} de la mayoría{/if}</span>
      <span>Partidos de la investidura de 2023 <b>{inv}</b> {#if inv >= 176}<span class="ok">mayoría</span>{:else}· a {176 - inv}{/if}</span>
    </div>
  {/if}
</div>

<style>
  .seatbar { display: flex; flex-direction: column; gap: 7px; }
  .cap { font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; }
  .cap b { color: var(--fg); }
  .bars { position: relative; display: flex; flex-direction: column; gap: 0; margin-top: 16px; }
  .band { display: block; overflow: visible; }
  .band text { font-family: var(--font-ui); font-size: 11px; font-weight: 700; fill: var(--muted); paint-order: stroke; stroke: var(--bg); stroke-width: 3px; font-variant-numeric: tabular-nums; }
  .band text.up { fill: var(--up); } .band text.down { fill: var(--down); }
  .bar { display: flex; width: 100%; overflow: hidden; border-radius: 6px; background: var(--panel); }
  .bar span { height: 100%; display: block; transition: width 0.35s ease; }
  .bar span + span { box-shadow: -1px 0 0 var(--bg); }
  .bar.slim { height: 12px; opacity: 0.72; }
  .bar.fat { height: 56px; }
  .maj { position: absolute; left: 50%; top: -6px; bottom: -6px; border-left: 2px dashed var(--stroke); }
  .maj::after { content: '176'; position: absolute; top: -18px; left: -12px; font-family: var(--font-ui); font-size: 11px; font-weight: 700; color: var(--ink); }
  .deltas { position: relative; margin-top: 6px; }
  .dhead { position: absolute; left: 0; top: 0; width: 88px; font-family: var(--font-ui); font-weight: 700; font-size: 14px; line-height: 20px; color: var(--fg); }
  .ditem { position: absolute; top: 0; transform: translateX(-50%); display: flex; flex-direction: column; align-items: center; transition: left 0.35s ease; }
  .dparty { font-family: var(--font-ui); font-size: 13px; line-height: 20px; white-space: nowrap; color: var(--muted); font-weight: 400; display: flex; align-items: center; gap: 5px; }
  .dparty i { width: 8px; height: 8px; border-radius: 2px; }
  .dnum { font-family: var(--font-ui); font-weight: 700; font-size: 34px; line-height: 1; font-variant-numeric: tabular-nums; }
  .none { position: absolute; left: 96px; top: 0; max-width: 440px; font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; }
  .stack .dhead, .stack .none { position: static; width: auto; }
  .stack .ditem { margin-top: 26px; }
  .sums { display: flex; flex-wrap: wrap; gap: 8px 20px; font-family: var(--font-ui); font-size: 14px; color: var(--muted); font-weight: 400; }
  .sums b { color: var(--ink); font-size: 18px; font-variant-numeric: tabular-nums; }
  .sums .ok { color: var(--up); font-weight: 700; }
  @media (max-width: 820px) { .dnum { font-size: 26px; } }
</style>
