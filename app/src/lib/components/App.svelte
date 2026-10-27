<script lang="ts">
  // TresCincuenta.es — two views of the same page.
  //  · Proyección: the poll projection itself, on the atlas's 12-column grid, no rails.
  //  · Simulación: the rails slide in (controls on the left, step-by-step on the right) and the sections
  //    that only explain the projection (transfers, la base, method) fade out.
  //  · Escenarios: coming soon.
  import { onMount, tick } from 'svelte';
  import { page } from '$app/state';
  import { goto, beforeNavigate, afterNavigate } from '$app/navigation';
  import { href as resolve } from '$lib/nav';
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
  // the TresCincuenta.es mark, inlined (works in the single-file build too); also the favicon, on a square canvas
  import logo350 from '$lib/assets/logo-350.svg?raw';
  import cocina from '$lib/assets/cocina.webp?inline';
  const favicon = 'data:image/svg+xml,' + encodeURIComponent(logo350.replace(/viewBox="[^"]*"/, 'viewBox="0 -170.475 799.31 799.31"'));
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
  // /metodologia and /quienes-somos are pages of their own: the bar stays, the projection shell does not
  const tab = $derived<'proj' | 'sim' | 'esc' | 'page'>(page.route.id === '/simula' ? 'sim' : page.route.id === '/escenarios' ? 'esc' : page.route.id === '/' ? 'proj' : 'page');
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
  // phones: the controls live in a bottom sheet (a quarter of the screen, or expanded to almost all of it)
  // with two tabs, controls and history
  let sheetBig = $state(false);
  let sheetTab = $state<'ctl' | 'hist'>('ctl');

  // ── hero (Proyección only) ───────────────────────────────────────────────────────────────────────
  // A dark intro with the big 350 lockup, the deck and the tabs. As in the atlas homepage, the title bar
  // compacts once the lockup reaches it: the 350 mark shrinks into its place in the bar, the stacked
  // name gives way to the one-line one and the tabs travel from the hero to the right of the bar.
  const heroOn = $derived(tab === 'proj');
  let pastLogo = $state(false);
  let pastTabs = $state(false);
  let overDark = $state(false); // the bar still sits over the dark hero
  const compact = $derived(!heroOn || pastLogo);
  const tabsUp = $derived(!heroOn || pastTabs);
  let mastEl = $state<HTMLElement>(), heroEl = $state<HTMLElement>(), lockEl = $state<HTMLElement>();
  let hero350 = $state<HTMLElement>(), heroTabs = $state<HTMLElement>(), head350 = $state<HTMLElement>(), headTabs = $state<HTMLElement>();
  const reduce = () => typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
  // FLIP: animate `to` from where `from` was, scaling to match widths
  function fly(to: HTMLElement | undefined, a: DOMRect | undefined) {
    if (!to || !a || reduce() || instant) return;
    const b = to.getBoundingClientRect(); if (!b.width) return;
    const s = a.width / b.width;
    to.animate([{ transformOrigin: '0 0', transform: `translate(${a.left - b.left}px, ${a.top - b.top}px) scale(${s})` }, { transformOrigin: '0 0', transform: 'none' }],
      { duration: 480, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' });
  }
  // each piece moves into the bar when it reaches it: first the 350 lockup, then (further down) the tabs
  async function setPast(v: boolean) {
    if (v === pastLogo) return;
    const from = (v ? hero350 : head350)?.getBoundingClientRect(); // where it is now, before the swap
    pastLogo = v;
    await tick();
    fly(v ? head350 : hero350, from);
  }
  // the tabs ride up with the intro until they are level with their place in the bar; there they stick
  // and slide sideways into position (scaling from the intro's larger size, centred vertically)
  // the links' own extent (the bar's nav is wider than its right-aligned links)
  function extent(el: HTMLElement) {
    const rs = [...el.children].map((c) => c.getBoundingClientRect()).filter((r) => r.width);
    const l = Math.min(...rs.map((r) => r.left)), r = Math.max(...rs.map((r) => r.right)), t = Math.min(...rs.map((r) => r.top)), bt = Math.max(...rs.map((r) => r.bottom));
    return { left: l, width: r - l, mid: (t + bt) / 2 };
  }
  function slide(to: HTMLElement | undefined, a: ReturnType<typeof extent> | undefined) {
    if (!to || !a || reduce() || instant) return;
    const box = to.getBoundingClientRect(), b = extent(to); if (!b.width) return;
    const s = a.width / b.width, ox = b.left - box.left;
    to.animate([{ transformOrigin: `${ox}px 50%`, transform: `translate(${a.left - b.left}px, ${a.mid - b.mid}px) scale(${s})` }, { transformOrigin: `${ox}px 50%`, transform: 'none' }],
      { duration: 520, easing: 'cubic-bezier(0.4, 0, 0.2, 1)' });
  }
  async function setTabs(v: boolean) {
    if (v === pastTabs) return;
    const src = v ? heroTabs : headTabs; const from = src ? extent(src) : undefined;
    pastTabs = v;
    await tick();
    slide(v ? headTabs : heroTabs, from);
  }
  function onScroll() {
    if (!heroOn || !lockEl || !mastEl) { overDark = false; return; }
    const h = mastEl.getBoundingClientRect().height;
    setPast(lockEl.getBoundingClientRect().top <= h);
    if (heroTabs && headTabs) setTabs(extent(heroTabs).mid <= extent(headTabs).mid);
    // switch once what is left of the dark intro fits under the opaque top of the light layer
    overDark = !!heroEl && heroEl.getBoundingClientRect().bottom > Math.min(20, h * 0.35);
  }
  onMount(() => {
    let raf = 0;
    const on = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(onScroll); };
    window.addEventListener('scroll', on, { passive: true }); window.addEventListener('resize', on);
    onScroll();
    return () => { window.removeEventListener('scroll', on); window.removeEventListener('resize', on); };
  });
  // arriving at or leaving the projection (the only view with the intro), the bar swaps state at once:
  // no transitions, so the logo and tabs don't visibly travel back
  let instant = $state(false);
  beforeNavigate((nav) => { if ((nav.to?.route.id === '/') !== (page.route.id === '/')) instant = true; });
  // held a little past the swap: the intro's state settles over a couple of frames after the route changes
  afterNavigate(() => { if (instant) setTimeout(() => (instant = false), 500); });
  // entering the projection from another tab: start from the top state without animating
  $effect(() => { if (heroOn) tick().then(() => { pastLogo = false; pastTabs = false; onScroll(); }); else { pastLogo = false; pastTabs = false; overDark = false; } });

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

<svelte:head><link rel="icon" type="image/svg+xml" href={favicon} /></svelte:head>
{#snippet icon(d: string)}<svg class="ti" viewBox="0 -960 960 960" aria-hidden="true"><path {d} /></svg>{/snippet}
{#snippet tablinks()}
  <a href={resolve('/')} class:on={tab === 'proj'} aria-current={tab === 'proj' ? 'page' : undefined}>{@render icon(ICON.proj)}Proyección</a>
  <a href={resolve('/simula')} class:on={tab === 'sim'} aria-current={tab === 'sim' ? 'page' : undefined}>{@render icon(ICON.sim)}Simula</a>
  <a href={resolve('/escenarios')} class="soon" class:on={tab === 'esc'} aria-current={tab === 'esc' ? 'page' : undefined}>{@render icon(ICON.esc)}<em>Cocinando</em> Escenarios</a>
{/snippet}
<header class="mast" class:instant class:sim class:hero={heroOn && !compact} class:notabs={!tabsUp} class:dark={heroOn && overDark} bind:this={mastEl}>
  <div class="brand"><VitLogo height={26} /><a class="l350" href={resolve('/')} aria-label="TresCincuenta.es · inicio" bind:this={head350}>{@html logo350}</a><h1 class="brand-title">TresCincuenta.es</h1></div>
  <nav class="tabs" aria-label="Secciones" bind:this={headTabs} inert={!tabsUp}>{@render tablinks()}</nav>
</header>

{#if heroOn}
  <section class="intro" class:past={pastLogo} class:tabsup={pastTabs} bind:this={heroEl} out:fade={{ duration: 200 }}>
    <div class="hero-in">
      <div class="lockup" bind:this={lockEl}>
        <span class="h350" bind:this={hero350} aria-hidden="true">{@html logo350}</span>
        <p class="h-title" aria-hidden="true">Tres<br />Cincuenta<br />.es</p>
      </div>
      <p class="h-deck">Nuestro modelo <strong>proyecta el reparto de los 350 escaños</strong> del Congreso para las elecciones generales del <strong>29 de noviembre</strong> a partir de una <a class="jump" href="#la-base" onclick={toBase}><strong>media de encuestas</strong></a> nacionales.</p>
      <p class="h-updated">Datos actualizados a {longDate(DATA.today)}</p>
      <nav class="h-tabs" aria-label="Secciones" bind:this={heroTabs} inert={tabsUp}>{@render tablinks()}</nav>
    </div>
  </section>
{/if}

{#if tab !== 'page'}
<div class="scn" class:sim>
  <aside class="rail left" class:big={sheetBig} aria-label="Controles del escenario" aria-hidden={!sim} inert={!sim}>
    <!-- phones only: the sheet's handle and tabs -->
    <div class="sheet-head">
      <button type="button" class="sheet-fold" aria-expanded={sheetBig} aria-label={sheetBig ? 'Reducir los controles' : 'Ampliar los controles'} onclick={() => (sheetBig = !sheetBig)}>
        <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M6 15l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
      </button>
      <div class="sheet-tabs" role="tablist">
        <button type="button" role="tab" aria-selected={sheetTab === 'ctl'} class:on={sheetTab === 'ctl'} onclick={() => (sheetTab = 'ctl')}>Ajustes</button>
        <button type="button" role="tab" aria-selected={sheetTab === 'hist'} class:on={sheetTab === 'hist'} onclick={() => (sheetTab = 'hist')}>Paso a paso{#if entries.length} <span class="sheet-n">{entries.length}</span>{/if}</button>
      </div>
    </div>
    <div class="rin sheet-body" class:off={sheetTab !== 'ctl'}><DialRail bind:scope bind:st cur={scen} bind:focusParty /></div>
    <div class="rin sheet-body sheet-hist" class:off={sheetTab !== 'hist'}>
      <div class="sheet-share"><ShareButton {entries} {st} cur={scen} /></div>
      <HistoryRail {entries} bind:st cur={scen} />
    </div>
  </aside>

  <main class="center">
    {#if tab === 'esc'}
      <section class="sec" in:fade={{ duration: 300 }}>
        <h2 class="hd w">Cocinando <strong>escenarios</strong></h2>
        <p class="lede w">Estamos cocinando escenarios para el 29N. Preguntas concretas convertidas en cambios de voto y de participación, con los supuestos a la vista. ¿Qué pasaría si votan los barrios más jóvenes, esos donde hoy más gente se queda en casa? ¿Y si la vivienda mueve el voto donde el alquiler más aprieta? ¿Y si las encuestas se equivocan con Vox, como cuando en 2016 anunciaron un <em>sorpasso</em> que nunca cuajó, o al revés?</p>
        <p class="lede w">Ninguno de estos escenarios es una predicción. Son preguntas del tipo «¿qué pasaría si…?», y cada una muestra cuánto se reordenaría el hemiciclo y en qué provincias se decidiría. Y, de paso, sirven de trampolín para tus propios escenarios.</p>
        <p class="lede w">Mientras tanto, mira la <a href={resolve('/')}>proyección</a> o <a href={resolve('/simula')}>simula tu escenario</a>.</p>
        <figure class="cocina"><img src={cocina} width="1400" height="1278" alt="Ilustración del equipo de TresCincuenta.es en una cocina, preparando gráficos como si fueran platos" /><figcaption class="note">Ilustración @oyematias</figcaption></figure>
      </section>
    {:else}
    {#if sim}
    <section class="sec simintro">
        <p class="lede deck w6">Personaliza <strong>la proyección de nuestro modelo</strong>: cambia el voto de cada partido y la participación, en toda España o provincia a provincia, mira cómo se mueven los 350 escaños y <strong>comparte tu escenario</strong>.</p>
      <p class="updated w6">Datos actualizados a {longDate(DATA.today)}</p>
    </section>
    {/if}
    <section class="sec">
      <h2 class="hd w">{#if sim}Así quedaría <strong>el Congreso</strong> con tus cambios.{:else}Esto dicen <strong>las encuestas</strong> hoy.{/if}</h2>
      <div class="f"><SeatBar {cur} bind:scope projection={!sim} /></div>
    </section>
    <section class="sec">
      <h2 class="hd w">{#if sim}Así quedaría <strong>el reparto por provincias</strong> en tu escenario.{:else}Así quedaría <strong>el reparto por provincias</strong> según los resultados de cada partido en las tres últimas generales.{/if}</h2>
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
          <p>Los controles mueven votos, no escaños: un cambio nacional se reparte entre provincias según dónde tiene ya votos cada partido, uno provincial solo afecta a esa provincia, y la participación añade o quita votantes que, por defecto, salen de donde hay más margen y votan como sus vecinos de mesa electoral. Después, D'Hondt asigna los escaños en las 52 circunscripciones. Cada simulación parte de la proyección de las encuestas. Es una calculadora de supuestos, no un pronóstico.</p>
          <p class="more"><a href={resolve('/metodologia')}>Lee la metodología completa</a></p>
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
{/if}

<style>
  :global(:root) { --nav-h: 60px; }
  /* sticky title bar, as in trees.fndvit.org: the page fades out under it (gradient + slight blur, masked) */
  .mast { position: sticky; top: 0; z-index: 30; display: flex; flex-wrap: wrap; align-items: center; gap: 8px 24px; padding-block: 8px; padding-inline: max(16px, calc((100% - 1262px) / 2)); transition: padding 0.55s cubic-bezier(0.4, 0, 0.2, 1); }
  /* aligned with the content: the 1262 px grid in the projection, the 1440 px page with rails in the simulation */
  .mast::before { content: ''; position: absolute; inset: 0 0 -40px; z-index: -1; pointer-events: none;
    background: linear-gradient(var(--bg), color-mix(in srgb, var(--bg) 20%, transparent));
    -webkit-backdrop-filter: blur(1px); backdrop-filter: blur(1px);
    -webkit-mask-image: linear-gradient(#000 40%, transparent); mask-image: linear-gradient(#000 40%, transparent); }
  /* the name is as tall as the logo: Bodoni Moda's capitals are 0.75 em high, so font-size = logo height / 0.75,
     and the baseline sits on the logo's bottom edge (a flex item with no text aligns by its bottom) */
  .brand { --logo-h: 26px; display: inline-flex; align-items: baseline; gap: 12px; min-width: 0; }
  .brand :global(.vitlogo svg) { height: var(--logo-h); }
  /* as in the atlas nav: ViT logo · project mark · title, all the same height */
  .l350 { display: inline-flex; line-height: 0; align-self: baseline; }
  .l350 :global(svg) { height: var(--logo-h); width: auto; display: block; }
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

  /* page grid: rail · gap · centre · gutter · rail. In the projection the rail tracks are 0 and the
     rails are invisible; entering the simulation animates the tracks open and slides the rails in. */
  /* page grid: the atlas 12 columns (1262 px). Five tracks: left rail · gap · centre · gutter · right rail.
     In the projection only the centre has width (all 12 columns). In the simulation, on the same columns:
     left rail 1–3, half a column empty, centre from 4½ to the end of column 10 (text keeps the 5-column
     well width), right rail on columns 11–12. The tracks animate between both. */
  .scn { --gw: min(1262px, calc(100vw - 32px)); --g: 10px; --c: calc((var(--gw) - 11 * var(--g)) / 12);
    max-width: calc(1262px + 32px); margin: 0 auto; padding-block: var(--s2) var(--s4); padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
    display: grid; grid-template-columns: 0px 0px minmax(0, 1fr) 0px 0px; align-items: start; transition: grid-template-columns 0.55s cubic-bezier(0.4, 0, 0.2, 1); }
  .scn.sim { grid-template-columns: calc(3 * var(--c) + 2 * var(--g)) calc(var(--c) / 2 + var(--g)) minmax(0, 1fr) var(--g) calc(2 * var(--c) + var(--g)); }
  .rail { position: sticky; top: calc(var(--nav-h) + 8px); align-self: start; max-height: calc(100vh - var(--nav-h) - 16px); overflow: hidden; overscroll-behavior: contain;
    opacity: 0; pointer-events: none; transition: opacity 0.35s ease, transform 0.55s cubic-bezier(0.4, 0, 0.2, 1); }
  .rail.left { grid-column: 1; grid-row: 1; transform: translateX(-32px); }
  .rail.right { grid-column: 5; grid-row: 1; transform: translateX(32px); padding-top: 14px; }
  .left .rin { width: calc(3 * var(--c) + 2 * var(--g)); }
  .right .rin { width: calc(2 * var(--c) + var(--g)); }
  .sim .rail { opacity: 1; transform: none; pointer-events: auto; overflow-y: auto; transition-delay: 0.15s, 0s; }
  .share-rail { margin-bottom: var(--s2); }
  /* the sheet's handle, tabs and history copy only exist on phones */
  .sheet-head, .sheet-hist { display: none; }
  .share-rail :global(.share) { width: 100%; justify-content: center; padding-inline: 10px; white-space: normal; text-align: center; line-height: 1.25; }

  /* centre: the atlas 12-column grid (1262 px) */
  .center { grid-column: 3; grid-row: 1; display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; row-gap: var(--s4);
    width: 100%; max-width: 1262px; justify-self: center; min-width: 0; padding-top: 14px; }
  .sim .center { max-width: none; }
  /* in the simulation the centre is narrower: text well widens to 9 columns, wide charts to all 12 */
  .sim .center :global(.sec > *) { grid-column: 1 / -1; }
  /* text and well-sized pieces keep the projection's well width: 5 columns */
  .sim .center :global(.sec > .w), .sim .center :global(.sec > .w6) { max-width: calc(5 * var(--c) + 4 * var(--g)); }
  /* the deck runs over cols 2–7 in the projection (all 12 → 1–9 in the simulation) */
  .center :global(.sec > .w6) { grid-column: 2 / 8; }
  .sim .center :global(.sec > .w6) { grid-column: 1 / -1; }
  .notes { border-top: 1px solid var(--line); padding-top: var(--s2); }
  .prose { font-family: var(--font-body); font-size: 16px; line-height: 1.72; color: var(--fg); display: flex; flex-direction: column; gap: 12px; }
  .prose p { margin: 0; }
  .more a { font-family: var(--font-ui); font-weight: 700; font-size: 15px; text-decoration: none; color: var(--ink); border-bottom: 2px solid currentColor; }
  .more a:hover { color: #d1366b; }
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

  .mast.instant, .mast.instant :global(*), .mast.instant::before, .mast.instant::after { transition: none !important; }
  /* ── hero ─────────────────────────────────────────────────────────────────────────────────────── */
  /* the bar over the hero: transparent, only the (larger, light) ViT mark; name, 350 and tabs wait */
  /* two layers crossfade: the dark one while the bar sits over the intro, the light gradient + blur after */
  .mast::before { transition: opacity 0.45s ease; }
  .mast::after { content: ''; position: absolute; inset: 0 0 -40px; z-index: -1; pointer-events: none; opacity: 0; transition: opacity 0.45s ease;
    background: linear-gradient(#16181d, color-mix(in srgb, #16181d 20%, transparent));
    -webkit-mask-image: linear-gradient(#000 40%, transparent); mask-image: linear-gradient(#000 40%, transparent); }
  .mast.hero::before, .mast.dark::before { opacity: 0; }
  .mast.dark:not(.hero)::after { opacity: 1; }
  .brand-title { transition: opacity 0.35s ease, color 0.45s ease; }
  .tabs a { transition: color 0.45s ease, border-color 0.45s ease; }
  .brand :global(.vitlogo) { transform-origin: 0 0; transition: transform 0.45s cubic-bezier(0.4, 0, 0.2, 1), color 0.35s ease; }
  .mast.hero .brand :global(.vitlogo) { transform: translate(106px, 18px) scale(1.385); }
  @media (max-width: 900px) { .mast.hero .brand :global(.vitlogo) { transform: translateY(14px) scale(1.385); } }
  .mast.dark .brand :global(.vitlogo) { color: #f7f4ef; }
  .l350, .brand-title, .mast .tabs { transition: opacity 0.35s ease; }
  .mast.hero .l350, .mast.notabs .tabs { opacity: 0; visibility: hidden; transition: none; }
  .mast.hero .brand-title { opacity: 0; }
  .mast.dark .brand-title { color: #fff; }
  .mast.dark .tabs a { color: rgba(214, 209, 211, 0.75); }
  .mast.dark .tabs a:hover, .mast.dark .tabs a.on { color: #fff; border-bottom-color: #fff; }

  /* the hero runs under the bar (which is sticky, so it already takes its height) */
  .intro { margin-top: calc(-1 * var(--nav-h)); background: #16181d; color: #fff; }
  .hero-in { max-width: 1262px; margin: 0 auto; padding: 208px 16px 60px; box-sizing: content-box;
    display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; }
  .hero-in > * { grid-column: 2 / 8; }
  .lockup { display: flex; align-items: flex-start; gap: 27px; }
  .h350 { display: block; line-height: 0; }
  .h350 :global(svg) { height: 130px; width: auto; display: block; }
  .h-title { margin: -4px 0 0; font-family: var(--font-display); font-weight: 500; font-variation-settings: 'opsz' 48; font-size: 48px; line-height: 45px; color: #fff; transition: opacity 0.35s ease; }
  .past .h350, .tabsup .h-tabs { visibility: hidden; }
  .past .h-title { opacity: 0; }
  .h-deck { margin: 28px 0 0; font-family: var(--font-ui); font-weight: 200; font-size: 24px; line-height: 32px; color: #fff; max-width: 620px; }
  .h-deck strong { font-weight: 700; }
  .h-updated { margin: 6px 0 0; font-family: var(--font-ui); font-size: 14px; font-weight: 700; line-height: 21px; color: #ffefad; }
  .h-tabs { margin-top: 27px; display: flex; flex-wrap: wrap; gap: 27px; }
  .h-tabs a { display: inline-flex; align-items: center; gap: 6px; padding: 10px 0 8px; border-bottom: 2px solid transparent; text-decoration: none;
    font-family: var(--font-ui); font-size: 13px; font-weight: 700; letter-spacing: 0.01em; text-transform: uppercase; line-height: 1; white-space: nowrap; color: rgba(214, 209, 211, 0.6); }
  .h-tabs a:hover { color: #fff; }
  .h-tabs a.on { color: #fff; border-bottom-color: #fff; }
  .h-tabs .soon:not(.on) { color: rgba(214, 209, 211, 0.4); opacity: 1; }
  .h-tabs .ti { width: 36px; height: 36px; }
  .h-tabs em { font-style: normal; font-weight: 300; text-transform: none; letter-spacing: 0; font-size: 13px; }
  .intro .jump { color: inherit; }

  /* tabs drop to their own row under the name */
  @media (max-width: 1100px) {
    :global(:root) { --nav-h: 92px; }
    .tabs { order: 3; flex-basis: 100%; justify-content: flex-start; gap: 22px; overflow-x: auto; scrollbar-width: none; }
  }
  /* small screens: one column, as the atlas below 900 px */
  @media (max-width: 900px) {
    .share-rail { display: none; }
    .sim .center :global(.sec > .w), .sim .center :global(.sec > .w6) { max-width: none; }
    .scn, .scn.sim { grid-template-columns: 0px 0px minmax(0, 1fr) 0px 0px; transition: none; }
    .rail { display: none; }
    /* the controls: a sheet fixed to the bottom third of the screen, with its own scroll; folded, only its
       handle shows. The page above scrolls on its own, so every change is seen at once. The history (the
       right rail on desktop) is the sheet's second tab; sharing stays in the title bar. */
    .sim .rail.left { display: flex; flex-direction: column; position: fixed; left: 0; right: 0; bottom: 0; top: auto; z-index: 35;
      height: 25dvh; max-height: none; overflow: hidden; background: var(--bg); border-radius: 16px 16px 0 0;
      box-shadow: 0 -8px 28px rgba(0, 0, 0, 0.18); transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .sim .rail.left.big { height: calc(100dvh - 56px); }
    .sim .rail.right { display: none; }
    .sim .center { grid-row: 1; }
    /* room under the page (footer included) so nothing stays hidden behind the sheet */
    :global(body:has(.scn.sim)) { padding-bottom: 25dvh; }
    .sheet-head { display: flex; align-items: center; gap: 10px; flex: none; height: 48px; padding: 0 12px; border-bottom: 1px solid var(--line); }
    .sheet-fold { display: grid; place-items: center; width: 34px; height: 34px; padding: 0; border: 0; border-radius: 50%; background: var(--panel); color: var(--ink); cursor: pointer; }
    .sheet-fold svg { transition: transform 0.3s ease; }
    .big .sheet-fold svg { transform: rotate(180deg); }
    .sheet-tabs { display: flex; gap: 4px; padding: 2px; border-radius: var(--radius); background: var(--panel); }
    .sheet-tabs button { font-family: var(--font-ui); font-size: 14px; line-height: 22px; font-weight: 400; padding: 2px 12px; border: 0; border-radius: 5px; background: transparent; color: var(--muted); cursor: pointer; }
    .sheet-tabs button.on { background: var(--highlight); color: var(--hl-ink); box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2); }
    .sheet-n { margin-left: 4px; display: inline-block; min-width: 18px; padding: 0 5px; border-radius: 9px; background: var(--ink); color: var(--bg); font-size: 11px; line-height: 18px; font-weight: 700; text-align: center; }
    .rail.left .sheet-body { flex: 1; min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding: 12px 16px calc(16px + env(safe-area-inset-bottom, 0px)); }
    .sheet-hist { display: block; }
    .sim .center :global(.sec.simintro) { display: none; }
    .sheet-body.off { display: none; }
    .sheet-share { margin-bottom: 16px; }
    .sheet-share :global(.share) { width: 100%; justify-content: center; padding: 10px 14px; }
    .sheet-share :global(.lbl) { display: inline; }
    .left .rin, .right .rin { width: auto; padding-right: 0; }
    .center { grid-template-columns: minmax(0, 1fr); }
    .center :global(.sec > .w6), .sim .center :global(.sec > .w), .sim .center :global(.sec > .w6), .sim .center :global(.sec > .c7), .sim .center :global(.sec > .c7w) { grid-column: 1 / -1; }
  }
  @media (max-width: 900px) {
    .hero-in { padding-top: calc(var(--nav-h) + 56px); padding-bottom: 40px; grid-template-columns: minmax(0, 1fr); }
    .hero-in > * { grid-column: 1; }
    .h350 :global(svg) { height: 88px; }
    .lockup { gap: 18px; }
    .h-title { font-size: 34px; line-height: 31px; margin-top: -3px; }
    .h-deck { font-size: 22px; line-height: 30px; margin-top: 24px; }
    .h-tabs { gap: 20px; }
    .h-tabs .ti { width: 28px; height: 28px; }
  }
  @media (max-width: 480px) { .brand { --logo-h: 20px; } .tabs a { font-size: 12px; } .ti { width: 16px; height: 16px; }
    .mast.hero .brand :global(.vitlogo) { transform: translateY(10px) scale(1.3); }
    .h350 :global(svg) { height: 72px; } .h-title { font-size: 28px; line-height: 26px; } .h-tabs a { font-size: 12px; } .h-tabs .ti { width: 24px; height: 24px; } }
  .cocina { margin: 24px auto 0; max-width: 1200px; }
  .cocina img { display: block; width: 100%; height: auto; border-radius: 12px; }
  .cocina figcaption { margin-top: 8px; text-align: right; }
</style>
