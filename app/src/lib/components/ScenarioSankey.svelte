<script lang="ts">
  import * as Plot from '@observablehq/plot';
  // Atlas ScenarioSankey (Observable Plot): from the 2023 vote to the scenario, nationally or in one
  // constituency. The constituency picker is shared with the map, the controls and the last seat.
  import LibDrop from './LibDrop.svelte';
  import { PROV } from '$lib/data';
  import { partyColor, partyLabel } from '$lib/parties';
  import { transfers } from '$lib/model';
  import { sortEs } from '$lib/format';
  import type { RunResult } from '$lib/types';

  let { cur, scope = $bindable() }: { cur: RunResult; scope: string } = $props();
  const flows = $derived(transfers(cur, scope));
  const opts = [{ value: 'ES', label: 'toda España' }, ...[...PROV].sort((a, b) => sortEs(a.n, b.n)).map((p) => ({ value: p.id, label: p.n }))];

  const GREY = '#a59c92';
  const ORDER = ['PSOE', 'SUMAR', 'FA', 'COMP', 'PODEMOS', 'ERC', 'BILDU', 'BNG', 'AA', 'PNV', 'JUNTS', 'CC', 'UPN', 'AC', 'SALF', 'VOX', 'PP', 'OTROS', 'ABST'];
  const rank = (k: string) => { const i = ORDER.indexOf(k); return i < 0 ? 99 : i; };
  const nodeLabel = (n: string) => (n === 'SUMAR' ? 'Sumar' : partyLabel(n));
  const nodeColor = (n: string) => (n === 'ABST' ? GREY : n === 'SUMAR' ? partyColor('FA') : partyColor(n));
  const fmtK = (v: number) => (v >= 1e6 ? (v / 1e6).toFixed(1).replace('.', ',') + ' M' : v >= 1e4 ? Math.round(v / 1e3) + ' mil' : v >= 1e3 ? (v / 1e3).toFixed(1).replace('.', ',') + ' mil' : String(Math.round(v)));

  const model = $derived.by(() => {
    if (!flows.length) return null;
    const total = flows.reduce((a, f) => a + f.votes, 0) || 1;
    const min = total * 0.004;
    const links = flows.filter((f) => f.votes >= min);
    if (!links.length) return null;

    const outTot = new Map<string, number>(), inTot = new Map<string, number>();
    for (const f of links) { outTot.set(f.from, (outTot.get(f.from) ?? 0) + f.votes); inTot.set(f.to, (inTot.get(f.to) ?? 0) + f.votes); }
    const srcOrder = [...outTot.keys()].sort((a, b) => rank(a) - rank(b));
    const tgtOrder = [...inTot.keys()].sort((a, b) => rank(a) - rank(b));

    // layout in PIXELS: both columns get a GAP between their parties. The taller
    // column sets the height; the shorter one is centred against it.
    const BASE = 660, GAP = 12;
    const pxPerVote = BASE / total;
    const colHeight = (order: string[], tot: Map<string, number>) =>
      order.reduce((a, k) => a + tot.get(k)! * pxPerVote, 0) + GAP * Math.max(0, order.length - 1);
    const srcH = colHeight(srcOrder, outTot), tgtH = colHeight(tgtOrder, inTot);
    const height = Math.max(BASE, srcH, tgtH);
    const layout = (order: string[], tot: Map<string, number>, h: number) => {
      const m = new Map<string, { y0: number; y1: number }>();
      let acc = (height - h) / 2;
      for (const k of order) { const v = tot.get(k)! * pxPerVote; m.set(k, { y0: acc, y1: acc + v }); acc += v + GAP; }
      return m;
    };
    const sSpan = layout(srcOrder, outTot, srcH);
    const tSpan = layout(tgtOrder, inTot, tgtH);

    const sCur = new Map(srcOrder.map((k) => [k, sSpan.get(k)!.y0]));
    const tCur = new Map(tgtOrder.map((k) => [k, tSpan.get(k)!.y0]));
    const ordered = [...links].sort((a, b) => srcOrder.indexOf(a.from) - srcOrder.indexOf(b.from) || tgtOrder.indexOf(a.to) - tgtOrder.indexOf(b.to));
    const rows: any[] = [];
    const grads: { id: string; s: string; t: string }[] = [];
    ordered.forEach((f, k) => {
      const dv = f.votes * pxPerVote;
      const s0 = sCur.get(f.from)!; sCur.set(f.from, s0 + dv);
      const t0 = tCur.get(f.to)!; tCur.set(f.to, t0 + dv);
      const id = `sk-${k}`;
      rows.push({ id, x: 0, y1: s0, y2: s0 + dv });
      rows.push({ id, x: 1, y1: t0, y2: t0 + dv });
      grads.push({ id, s: nodeColor(f.from), t: nodeColor(f.to) });
    });
    const nodes = [
      ...srcOrder.map((k) => ({ side: 'source', label: `${nodeLabel(k)} ${fmtK(outTot.get(k)!)}`, y: (sSpan.get(k)!.y0 + sSpan.get(k)!.y1) / 2 })),
      ...tgtOrder.map((k) => ({ side: 'target', label: `${nodeLabel(k)} ${fmtK(inTot.get(k)!)}`, y: (tSpan.get(k)!.y0 + tSpan.get(k)!.y1) / 2 }))
    ];
    // keep labels at least 17 px apart on each side (small parties sit close together)
    for (const side of ['source', 'target']) {
      const L = nodes.filter((n) => n.side === side).sort((p, q) => p.y - q.y);
      for (let i = 1; i < L.length; i++) if (L[i].y - L[i - 1].y < 17) L[i].y = L[i - 1].y + 17;
      const over = L.length ? L[L.length - 1].y - (height - 4) : 0;
      if (over > 0) for (let i = L.length - 1; i >= 0; i--) { L[i].y -= over; if (i && L[i].y - L[i - 1].y >= 17) break; }
    }
    return { rows, grads, nodes, height };
  });

  let host = $state<HTMLDivElement>();
  let figW = $state(560);
  const NS = 'http://www.w3.org/2000/svg';

  $effect(() => {
    if (!host) return;
    if (!model) { host.replaceChildren(); return; }
    // match the city-page Sankey (VoteTransfers): 50px side margins, labels
    // reading inward with a page-bg halo, full-opacity ribbons over 0.8 gradients.
    const W = figW || 560, H = model.height + 14;
    const fig = Plot.plot({
      width: W, height: H, marginLeft: W < 600 ? 50 : 156, marginRight: W < 600 ? 50 : 156, marginTop: 8, marginBottom: 6,
      x: { domain: [0, 1], axis: null },
      y: { axis: null, reverse: true, domain: [0, model.height] },
      marks: [
        Plot.areaY(model.rows, { x: 'x', y1: 'y1', y2: 'y2', z: 'id', fill: (d: any) => `url(#${d.id})`, fillOpacity: 1, curve: 'bump-x' }),
        Plot.text(model.nodes.filter((n) => n.side === 'source'), { x: 0, y: 'y', text: 'label', textAnchor: 'start', dx: W < 600 ? -44 : -150, fontSize: 14, fill: 'currentColor', strokeWidth: 5 }),
        Plot.text(model.nodes.filter((n) => n.side === 'target'), { x: 1, y: 'y', text: 'label', textAnchor: 'end', dx: W < 600 ? 44 : 150, fontSize: 14, fill: 'currentColor', strokeWidth: 5 })
      ]
    });
    const svg = (fig.tagName.toLowerCase() === 'svg' ? fig : fig.querySelector('svg')) as SVGSVGElement;
    const defs = document.createElementNS(NS, 'defs');
    for (const g of model.grads) {
      const lg = document.createElementNS(NS, 'linearGradient');
      lg.setAttribute('id', g.id);
      for (const [off, col] of [['0%', g.s], ['100%', g.t]] as const) {
        const st = document.createElementNS(NS, 'stop');
        st.setAttribute('offset', off); st.setAttribute('stop-color', col); st.setAttribute('stop-opacity', '0.8');
        lg.appendChild(st);
      }
      defs.appendChild(lg);
    }
    svg.insertBefore(defs, svg.firstChild);
    host.replaceChildren(fig);
    return () => fig.remove();
  });
</script>

<h2 class="hd w">Transferencia de voto <strong>de 2023 a la proyección</strong> en <span class="sel"><LibDrop bind:value={scope} options={opts} label="Ámbito de la transferencia" filter /></span></h2>
<p class="sub w">Izquierda: el voto de las generales de 2023 (con la abstención sobre el censo de 2026). Derecha: la proyección. Cada partido conserva todo el voto que puede y lo que pierde va a quien crece; Sumar pasa a Frente Amplio, Compromís y Podemos. Es la estimación de mínimo trasvase, calculada provincia a provincia: los movimientos reales son mayores.</p>
<div class="sankey c7">
  <div class="fig" bind:this={host} bind:clientWidth={figW}
    role="img" aria-label="Transferencias de voto de 2023 a la proyección"></div>
  {#if !model}
    <p class="empty">No hay datos para este ámbito.</p>
  {/if}
</div>

<style>
  .sankey { min-width: 0; }
  .fig { min-width: 0; color: var(--muted); }
  .sel { display: inline-flex; vertical-align: baseline; }
  .sel :global(.word) { font-size: 24px; line-height: 30px; padding: 0 10px; font-weight: 200; }
  .sel :global(.opts) { max-height: 320px; overflow-y: auto; }
  .sel :global(.opt) { font-size: 16px; line-height: 24px; }
  .fig :global(text) { stroke: var(--halo); paint-order: stroke; stroke-linejoin: round; font-family: var(--font-ui); }
  .empty { font-family: var(--font-ui); font-weight: 400; font-size: 14px; color: var(--muted); margin: 0; }
</style>
