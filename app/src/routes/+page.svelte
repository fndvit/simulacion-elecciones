<script lang="ts">
  // Escenarios 29N — same layout as the atlas /escenarios page: sticky left rail (controls) ·
  // centre (seats, map, table, last seat, transfers, polls) · sticky right rail (history).
  import { onMount } from 'svelte';
  import DialRail from '$lib/components/DialRail.svelte';
  import SeatBar from '$lib/components/SeatBar.svelte';
  import HexMap from '$lib/components/HexMap.svelte';
  import ScenarioTable from '$lib/components/ScenarioTable.svelte';
  import LastSeat from '$lib/components/LastSeat.svelte';
  import ScenarioSankey from '$lib/components/ScenarioSankey.svelte';
  import PollSection from '$lib/components/PollSection.svelte';
  import HistoryRail from '$lib/components/HistoryRail.svelte';
  import VitLogo from '$lib/components/VitLogo.svelte';
  import ShareButton from '$lib/components/ShareButton.svelte';
  import { blank, run, historyEntries } from '$lib/model';
  import { DATA } from '$lib/data';
  import { longDate } from '$lib/format';
  import { scenarioFromUrl } from '$lib/share';
  import type { Scenario } from '$lib/types';

  let st = $state<Scenario>(blank());
  let scope = $state('ES');
  let focusParty = $state('PP');
  let ready = $state(false);

  const cur = $derived(run(st));
  // in-page jump without touching the hash (the router lives there)
  function toBase(e: MouseEvent) { e.preventDefault(); document.getElementById('la-base')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  const entries = $derived(historyEntries(st));

  // a shared link (?e=…) opens that scenario; otherwise the one saved in this browser, if any
  onMount(() => {
    const linked = scenarioFromUrl(blank);
    if (linked) st = linked;
    else try { const s = JSON.parse(localStorage.getItem('sim29n') || 'null'); if (s && s.nat) st = Object.assign(blank(), s); } catch {}
    ready = true;
  });
  $effect(() => {
    const snap = JSON.stringify(st);
    if (!ready) return;
    try { localStorage.setItem('sim29n', snap); } catch {}
  });
</script>

<header class="mast">
  <div class="brand"><VitLogo height={26} /><h1 class="brand-title">Proyección elecciones 29N</h1></div>
  <div class="share-top"><ShareButton {entries} {st} {cur} /></div>
</header>

<div class="scn">
  <aside class="rail left" aria-label="Controles del escenario">
    <DialRail bind:scope bind:st {cur} bind:focusParty />
  </aside>

  <main class="center">
    <section class="block intro">
      <p class="lede">Este simulador <strong>proyecta el reparto de los 350 escaños</strong> del Congreso para las elecciones generales del <strong>29 de noviembre</strong> a partir de una <a class="jump" href="#la-base" onclick={toBase}><strong>media ponderada de encuestas</strong></a> nacionales, repartida por provincias según dónde ha sido más fuerte o más débil cada partido en las tres últimas generales.</p>
      <p class="updated">Datos actualizados a {longDate(DATA.today)}</p>
    </section>
    <section class="block"><SeatBar {cur} {scope} /></section>
    <section class="block"><HexMap {cur} bind:scope bind:focusParty /></section>
    <section class="block narrow"><ScenarioTable {cur} {scope} /></section>
    <section class="block narrow"><LastSeat {cur} bind:scope /></section>
    <section class="block"><ScenarioSankey {cur} bind:scope /></section>
    <section class="block"><PollSection /></section>
  </main>

  <aside class="rail right" aria-label="Historial del escenario">
    <div class="share-rail"><ShareButton {entries} {st} {cur} /></div>
    <HistoryRail {entries} bind:st {cur} />
  </aside>
</div>

<style>
  /* sticky title bar, as in trees.fndvit.org: the page fades out under it (gradient + slight blur, masked) */
  .mast { position: sticky; top: 0; z-index: 30; display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-block: 12px; padding-inline: max(16px, calc((100% - 1440px) / 2 + 16px)); }

  /* atlas grid: rail · gap · centre · gutter · history */
  .scn { max-width: 1440px; margin: 0 auto; padding-block: var(--s2) var(--s4); padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
    display: grid; grid-template-columns: 310px 64px minmax(0, 1fr) 24px 200px; row-gap: var(--s3); align-items: start; }
  .mast::before { content: ''; position: absolute; inset: 0 0 -40px; z-index: -1; pointer-events: none;
    background: linear-gradient(var(--bg), color-mix(in srgb, var(--bg) 20%, transparent));
    -webkit-backdrop-filter: blur(1px); backdrop-filter: blur(1px);
    -webkit-mask-image: linear-gradient(#000 40%, transparent); mask-image: linear-gradient(#000 40%, transparent); }
  .share-top { display: none; }
  .share-rail { margin-bottom: var(--s2); }
  .share-rail :global(.share) { width: 100%; justify-content: center; padding-inline: 10px; }
  .rail { position: sticky; top: calc(var(--nav-h) + 8px); align-self: start; max-height: calc(100vh - var(--nav-h) - 16px); overflow-y: auto; overscroll-behavior: contain; }
  .rail.left { grid-column: 1; padding-right: 6px; }
  .rail.right { grid-column: 5; padding-top: 14px; }
  .center { grid-column: 3; display: flex; flex-direction: column; gap: var(--s4); min-width: 0; padding-top: 14px; }
  .block { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
  .narrow { max-width: 560px; }
  .brand { display: inline-flex; align-items: center; gap: 12px; min-width: 0; }
  .brand-title { font-family: var(--font-display); font-weight: 500; font-variation-settings: 'opsz' 18; font-size: 21px; line-height: 1.3; color: var(--fg); margin: 0; white-space: nowrap; letter-spacing: 0; overflow: hidden; text-overflow: ellipsis; }
  @media (max-width: 480px) { .brand-title { font-size: 17px; } }
  .intro { margin-bottom: calc(var(--s2) - var(--s4)); }
  /* the deck: same size as the h2s of the centre column, light sans */
  .intro .lede { max-width: 40em; font-family: var(--font-ui); font-weight: 200; font-size: 24px; line-height: 32px; color: var(--ink); }
  .intro .lede strong { font-weight: 700; }
  /* same size as the seat bar caption; date of the last good data (the page is only rebuilt with good data) */
  .updated { margin: -6px 0 0; font-family: var(--font-ui); font-size: 14px; font-weight: 400; color: #c4314b; }
  @media (prefers-color-scheme: dark) { :global(:root:not([data-theme='light'])) .updated { color: #f2847a; } }
  :global(:root[data-theme='dark']) .updated { color: #f2847a; }
  .jump { color: inherit; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 4px; }
  .jump:hover { text-decoration-thickness: 2px; }
  :global(#la-base) { scroll-margin-top: calc(var(--nav-h) + 16px); }
  :global(:root) { --nav-h: 50px; }

  @media (max-width: 1380px) {
    .scn { grid-template-columns: 290px 40px minmax(0, 1fr); }
    .rail.right { grid-column: 1 / -1; position: static; max-height: none; }
    .share-top { display: block; }
    .share-rail { display: none; }
  }
  @media (max-width: 820px) {
    .scn { grid-template-columns: minmax(0, 1fr); row-gap: var(--s2); }
    .rail.left, .center, .rail.right { grid-column: 1; }
    .rail.left { position: static; max-height: none; overflow: visible; padding-right: 0; }
  }
</style>
