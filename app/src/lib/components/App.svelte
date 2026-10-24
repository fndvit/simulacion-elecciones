<script lang="ts">
  // TresCincuenta.es — two views of the same page.
  //  · Proyección: the poll projection itself, on the atlas's 12-column grid, no rails.
  //  · Simulación: the rails slide in (controls on the left, step-by-step on the right) and the sections
  //    that only explain the projection (transfers, la base, method) fade out.
  //  · Escenarios: coming soon.
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { resolve as res } from '$app/paths';
  // with the hash router keep only the #/… part, so links work in the single-file build (file://, artifact)
  const resolve = (p: '/' | '/simula' | '/escenarios') => { const r = res(p); const i = r.indexOf('#'); return i >= 0 ? r.slice(i) : r; };
  import { fade } from 'svelte/transition';
  import DialRail from './DialRail.svelte';
  import SeatBar from './SeatBar.svelte';
  import HexMap from './HexMap.svelte';
  import ScenarioTable from './ScenarioTable.svelte';
  import LastSeat from './LastSeat.svelte';
  import ScenarioSankey from './ScenarioSankey.svelte';
  import PollSection from './PollSection.svelte';
  import HistoryRail from './HistoryRail.svelte';
  import VitLogo from './VitLogo.svelte';
  import ShareButton from './ShareButton.svelte';
  import { blank, run, historyEntries, BASE } from '$lib/model';
  import { DATA } from '$lib/data';
  import { longDate } from '$lib/format';
  import { scenarioFromUrl } from '$lib/share';
  import type { Scenario } from '$lib/types';

  let st = $state<Scenario>(blank());
  let scope = $state('ES');
  let focusParty = $state('PP');
  let ready = $state(false);
  // each view is its own URL (/, /simula, /escenarios); this shell lives in the layout, so it persists
  // between them and the rails can slide in and out instead of the page reloading
  const tab = $derived<'proj' | 'sim' | 'esc'>(page.route.id === '/simula' ? 'sim' : page.route.id === '/escenarios' ? 'esc' : 'proj');
  const sim = $derived(tab === 'sim');
  // Material Symbols Outlined (weight 400): dashboard, modeling, fork_chart
  const ICON = {
    proj: 'M510-570v-270h330v270H510ZM120-450v-390h330v390H120Zm390 330v-390h330v390H510Zm-390 0v-270h330v270H120Zm60-390h210v-270H180v270Zm390 330h210v-270H570v270Zm0-450h210v-150H570v150ZM180-180h210v-150H180v150Zm210-330Zm180-120Zm0 180ZM390-330Z',
    sim: 'M718-145 569-295l149-150 42 43-76 77 196 1v60l-196-1 76 77-42 43Zm-578-15q-24 0-42-18t-18-42v-147q0-24 18-42t42-18h269q24 0 42 18t18 42v147q0 24-18 42t-42 18H140Zm0-60h269v-147H140v147Zm102-297-42-42 76-78H80v-60h196l-76-77 42-42 149 149-149 150Zm309-16q-24 0-42-18t-18-42v-147q0-24 18-42t42-18h269q24 0 42 18t18 42v147q0 24-18 42t-42 18H551Zm0-60h269v-147H551v147ZM409-220v-147 147Zm142-373v-147 147Z',
    esc: 'M120-160v-310q-26-7-43-28t-17-50v-192q0-8 6-14t14-6q8 0 14 6t6 14v140h30v-140q0-8 6-14t14-6q8 0 14 6t6 14v140h30v-140q0-8 6-14t14-6q8 0 14 6t6 14v192q0 29-17 50t-43 28v310h-60Zm480 1q-134 0-227.5-93.5T279-480q0-133 93.5-226.5T600-800q133 0 226.5 93.5T920-480q0 134-93.5 227.5T600-159Zm203-482L642-480l161 162q26-34 41.5-75t15.5-87q0-46-15.5-87T803-641Zm-173-97v186l131-131q-28-22-61-36t-70-19Zm-30 519q46 0 87-15.5t74-41.5L570-467v-271q-98 11-164.5 84.5T339-480q0 109 76 185t185 76Z'
  };

  const scen = $derived(run(st));
  // the projection tab always shows the poll projection; the simulation, the user's scenario
  const cur = $derived(sim ? scen : BASE);
  // in-page jump without touching the hash (the router lives there)
  function toBase(e: MouseEvent) { e.preventDefault(); document.getElementById('la-base')?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
  const entries = $derived(historyEntries(st));

  // a shared link (?e=…) opens that scenario in the simulation; otherwise the one saved in this browser, if any
  onMount(() => {
    const linked = scenarioFromUrl(blank);
    if (linked) { st = linked; if (!sim) goto(resolve('/simula') + location.search); }
    else try { const s = JSON.parse(localStorage.getItem('sim29n') || 'null'); if (s && s.nat) st = Object.assign(blank(), s); } catch {}
    ready = true;
  });
  $effect(() => {
    const snap = JSON.stringify(st);
    if (!ready) return;
    try { localStorage.setItem('sim29n', snap); } catch {}
  });
</script>

{#snippet icon(d: string)}<svg class="ti" viewBox="0 -960 960 960" aria-hidden="true"><path {d} /></svg>{/snippet}
<header class="mast" class:sim>
  <div class="brand"><VitLogo height={26} /><h1 class="brand-title">TresCincuenta.es</h1></div>
  <nav class="tabs" aria-label="Secciones">
    <a href={resolve('/')} class:on={tab === 'proj'} aria-current={tab === 'proj' ? 'page' : undefined}>{@render icon(ICON.proj)}Proyección</a>
    <a href={resolve('/simula')} class:on={tab === 'sim'} aria-current={tab === 'sim' ? 'page' : undefined}>{@render icon(ICON.sim)}Simula</a>
    <a href={resolve('/escenarios')} class="soon" class:on={tab === 'esc'} aria-current={tab === 'esc' ? 'page' : undefined}>{@render icon(ICON.esc)}<em>Cocinando</em> Escenarios</a>
  </nav>
  {#if sim}<div class="share-top" transition:fade={{ duration: 200 }}><ShareButton {entries} {st} cur={scen} /></div>{/if}
</header>

<div class="scn" class:sim>
  <aside class="rail left" aria-label="Controles del escenario" aria-hidden={!sim} inert={!sim}>
    <div class="rin"><DialRail bind:scope bind:st cur={scen} bind:focusParty /></div>
  </aside>

  <main class="center">
    {#if tab === 'esc'}
      <section class="sec" in:fade={{ duration: 300 }}>
        <h2 class="hd w">Cocinando <strong>escenarios</strong></h2>
        <p class="lede w">Pronto podrás explorar escenarios ya preparados para el 29 de noviembre. Mientras tanto, mira la <a href={resolve('/')}>proyección</a> o <a href={resolve('/simula')}>simula</a> el tuyo.</p>
      </section>
    {:else}
    <section class="sec">
      {#if sim}
        <p class="lede deck w6">Personaliza <strong>la proyección de nuestro modelo</strong>: cambia el voto de cada partido y la participación, en toda España o provincia a provincia, mira cómo se mueven los 350 escaños y <strong>comparte tu escenario</strong>.</p>
      {:else}
  <p class="lede deck w6">Nuestro modelo <strong>proyecta el reparto de los 350 escaños</strong> del Congreso para las elecciones generales del <strong>29 de noviembre</strong> a partir de una <a class="jump" href="#la-base" onclick={(e) => { if (tab !== 'proj') { e.preventDefault(); goto(resolve('/')).then(() => setTimeout(() => toBase(e), 450)); } else toBase(e); }}><strong>media de encuestas</strong></a> nacionales.</p>
      {/if}
      <p class="updated w6">Datos actualizados a {longDate(DATA.today)}</p>
    </section>
    <section class="sec">
      <h2 class="hd w">{#if sim}Así quedaría <strong>el Congreso</strong> con tus cambios.{:else}Esto dicen <strong>las encuestas</strong> a día de hoy.{/if}</h2>
      <div class="f"><SeatBar {cur} bind:scope projection={!sim} /></div>
    </section>
    <section class="sec">
      <h2 class="hd w">{#if sim}Así quedaría <strong>el reparto por provincias</strong> en tu escenario.{:else}Así quedaría <strong>el reparto por provincias</strong> según dónde ha sido más fuerte o más débil cada partido en las tres últimas generales.{/if}</h2>
      <HexMap {cur} bind:scope bind:focusParty projection={!sim} />
    </section>
    <section class="sec"><div class="w"><ScenarioTable {cur} {scope} projection={!sim} /></div></section>
    <section class="sec"><div class="w stack"><LastSeat {cur} bind:scope projection={!sim} /></div></section>
    {#if !sim}
      <section class="sec" transition:fade={{ duration: 300 }}><ScenarioSankey {cur} bind:scope /></section>
      <section class="sec" transition:fade={{ duration: 300 }}><PollSection /></section>
    {:else}
      <section class="sec notes" transition:fade={{ duration: 300 }}>
        <h2 class="hd w">Notas sobre <strong>la simulación</strong></h2>
        <div class="w prose">
          <p><b>Tus controles.</b> Los deslizadores mueven votos, no escaños. Un cambio nacional se reparte entre provincias de forma proporcional al voto que el partido ya tiene en cada una y el resto de partidos cede votos en proporción a su tamaño. Un cambio provincial solo afecta a esa provincia. La participación añade o quita votantes, que se reparten como el resto salvo que cambies el reparto. Después, D'Hondt asigna los escaños en cada circunscripción.</p>
          <p><b>Punto de partida.</b> Cada simulación parte de la proyección de las encuestas. La participación de partida es la de 2023 en cada provincia.</p>
          <p>Es una calculadora de supuestos, no un pronóstico: no estima incertidumbre ni probabilidades.</p>
        </div>
      </section>
    {/if}
    {/if}
  </main>

  <aside class="rail right" aria-label="Historial del escenario" aria-hidden={!sim} inert={!sim}>
    <div class="rin">
      <div class="share-rail"><ShareButton {entries} {st} cur={scen} /></div>
      <HistoryRail {entries} bind:st cur={scen} />
    </div>
  </aside>
</div>

<style>
  :global(:root) { --nav-h: 60px; }
  /* sticky title bar, as in trees.fndvit.org: the page fades out under it (gradient + slight blur, masked) */
  .mast { position: sticky; top: 0; z-index: 30; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 24px; padding-block: 8px; padding-inline: max(16px, calc((100% - 1262px) / 2)); transition: padding 0.55s cubic-bezier(0.4, 0, 0.2, 1); }
  /* aligned with the content: the 1262 px grid in the projection, the 1440 px page with rails in the simulation */
  .mast.sim { padding-inline: max(16px, calc((100% - 1440px) / 2 + 16px)); }
  .mast::before { content: ''; position: absolute; inset: 0 0 -40px; z-index: -1; pointer-events: none;
    background: linear-gradient(var(--bg), color-mix(in srgb, var(--bg) 20%, transparent));
    -webkit-backdrop-filter: blur(1px); backdrop-filter: blur(1px);
    -webkit-mask-image: linear-gradient(#000 40%, transparent); mask-image: linear-gradient(#000 40%, transparent); }
  /* the name is as tall as the logo: Bodoni Moda's capitals are 0.75 em high, so font-size = logo height / 0.75,
     and the baseline sits on the logo's bottom edge (a flex item with no text aligns by its bottom) */
  .brand { --logo-h: 26px; display: inline-flex; align-items: baseline; gap: 12px; min-width: 0; }
  .brand :global(.vitlogo svg) { height: var(--logo-h); }
  .brand-title { font-family: var(--font-display); font-weight: 500; font-variation-settings: 'opsz' 18; font-size: calc(var(--logo-h) / 0.75); line-height: 1.2; color: var(--ink); margin: 0; white-space: nowrap; letter-spacing: 0; overflow: hidden; text-overflow: ellipsis; }

  /* tabs */
  /* tabs: right-aligned, ending on the grid's last column (the title bar shares the grid's edges) */
  .tabs { flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 26px; min-width: 0; }
  .tabs a { text-decoration: none; }
  .tabs a, .soon { display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-ui); font-size: 13px; font-weight: 700; letter-spacing: 0.01em; text-transform: uppercase; line-height: 1; white-space: nowrap;
    background: none; border: 0; padding: 10px 0 8px; border-bottom: 2px solid transparent; color: var(--muted); }
  .tabs a { cursor: pointer; }
  .tabs a:hover { color: var(--ink); }
  .tabs a.on { color: var(--ink); border-bottom-color: var(--ink); }
  .ti { width: 18px; height: 18px; fill: currentColor; flex: none; }
  .soon em { margin-right: -2px; }
  .soon:not(.on) { opacity: 0.55; }
  .soon em { font-style: normal; font-weight: 400; text-transform: none; letter-spacing: 0; font-size: 12px; }
  .share-top { display: none; }

  /* page grid: rail · gap · centre · gutter · rail. In the projection the rail tracks are 0 and the
     rails are invisible; entering the simulation animates the tracks open and slides the rails in. */
  .scn { max-width: 1440px; margin: 0 auto; padding-block: var(--s2) var(--s4); padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
    display: grid; grid-template-columns: 0px 0px minmax(0, 1fr) 0px 0px; align-items: start; transition: grid-template-columns 0.55s cubic-bezier(0.4, 0, 0.2, 1); }
  .scn.sim { grid-template-columns: 300px 48px minmax(0, 1fr) 24px 200px; }
  .rail { position: sticky; top: calc(var(--nav-h) + 8px); align-self: start; max-height: calc(100vh - var(--nav-h) - 16px); overflow: hidden; overscroll-behavior: contain;
    opacity: 0; pointer-events: none; transition: opacity 0.35s ease, transform 0.55s cubic-bezier(0.4, 0, 0.2, 1); }
  .rail.left { grid-column: 1; grid-row: 1; transform: translateX(-32px); }
  .rail.right { grid-column: 5; grid-row: 1; transform: translateX(32px); padding-top: 14px; }
  .left .rin { width: 300px; padding-right: 6px; }
  .right .rin { width: 200px; }
  .sim .rail { opacity: 1; transform: none; pointer-events: auto; overflow-y: auto; transition-delay: 0.15s, 0s; }
  .share-rail { margin-bottom: var(--s2); }
  .share-rail :global(.share) { width: 100%; justify-content: center; padding-inline: 10px; }

  /* centre: the atlas 12-column grid (1262 px) */
  .center { grid-column: 3; grid-row: 1; display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; row-gap: var(--s4);
    width: 100%; max-width: 1262px; justify-self: center; min-width: 0; padding-top: 14px; }
  .sim .center { max-width: none; }
  /* in the simulation the centre is narrower: text well widens to 9 columns, wide charts to all 12 */
  .sim .center :global(.sec > .w) { grid-column: 1 / 10; }
  .sim .center :global(.sec > .c7), .sim .center :global(.sec > .c7w) { grid-column: 1 / -1; }
  /* the deck runs over cols 2–7 in the projection (all 12 → 1–9 in the simulation) */
  .center :global(.sec > .w6) { grid-column: 2 / 8; }
  .sim .center :global(.sec > .w6) { grid-column: 1 / 10; }
  .notes { border-top: 1px solid var(--line); padding-top: var(--s2); }
  .prose { font-family: var(--font-body); font-size: 16px; line-height: 1.72; color: var(--fg); display: flex; flex-direction: column; gap: 12px; }
  .prose p { margin: 0; }
  .stack { display: flex; flex-direction: column; gap: 14px; }

  /* the deck: same size as the h2s, light sans */
  .deck { font-family: var(--font-ui); font-weight: 200; font-size: 24px; line-height: 32px; color: var(--ink); margin: 0; }
  .deck strong { font-weight: 700; }
  /* same size as the seat bar caption; date of the last good data (the page is only rebuilt with good data) */
  .updated { margin: -8px 0 0; font-family: var(--font-ui); font-size: 14px; font-weight: 700; color: #c4314b; }
  @media (prefers-color-scheme: dark) { :global(:root:not([data-theme='light'])) .updated { color: #f2847a; } }
  :global(:root[data-theme='dark']) .updated { color: #f2847a; }
  .jump { color: inherit; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 4px; }
  .jump:hover { text-decoration-thickness: 2px; }
  :global(#la-base) { scroll-margin-top: calc(var(--nav-h) + 16px); }

  /* tabs drop to their own row under the name */
  @media (max-width: 1100px) {
    :global(:root) { --nav-h: 92px; }
    .tabs { order: 3; flex-basis: 100%; justify-content: flex-start; gap: 22px; overflow-x: auto; scrollbar-width: none; }
    .share-top { margin-left: auto; }
  }
  /* medium screens: the history rail moves under the centre and sharing goes to the title bar */
  @media (max-width: 1380px) {
    .scn.sim { grid-template-columns: 280px 32px minmax(0, 1fr) 0px 0px; }
    .sim .rail.right { grid-column: 1 / -1; grid-row: 2; position: static; max-height: none; overflow: visible; padding-top: var(--s3); }
    .sim .right .rin { width: auto; max-width: 560px; }
    .share-top { display: block; }
    .share-rail { display: none; }
  }
  /* small screens: one column, as the atlas below 900 px */
  @media (max-width: 900px) {
    .scn, .scn.sim { grid-template-columns: 0px 0px minmax(0, 1fr) 0px 0px; transition: none; }
    .rail { display: none; }
    .sim .rail { display: block; grid-column: 1 / -1; position: static; max-height: none; overflow: visible; }
    .sim .rail.left { grid-row: 1; }
    .sim .center { grid-row: 2; padding-top: var(--s3); }
    .sim .rail.right { grid-row: 3; }
    .left .rin, .right .rin { width: auto; padding-right: 0; }
    .center { grid-template-columns: minmax(0, 1fr); }
    .center :global(.sec > .w6), .sim .center :global(.sec > .w), .sim .center :global(.sec > .w6), .sim .center :global(.sec > .c7), .sim .center :global(.sec > .c7w) { grid-column: 1 / -1; }
  }
  @media (max-width: 480px) { .brand { --logo-h: 20px; } .tabs a { font-size: 12px; } .ti { width: 16px; height: 16px; } }
</style>
