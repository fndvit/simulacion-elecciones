<script lang="ts">
  // A horizontally scrolling box (wide tables, the D'Hondt grid) that shows there is more to the right: a
  // fade over the cut edge and a small chevron, both gone once the reader reaches the end. The chevron also
  // scrolls the box when tapped. The chevron sits at the top, by the column headers, so it shows even on a long table.
  import type { Snippet } from 'svelte';
  let { children, cls = '' }: { children: Snippet; cls?: string } = $props();
  let el: HTMLDivElement;
  let more = $state(false);
  function update() { if (el) more = el.scrollLeft + el.clientWidth < el.scrollWidth - 4; }
  $effect(() => {
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    if (el.firstElementChild) ro.observe(el.firstElementChild);
    return () => ro.disconnect();
  });
  function nudge() { el.scrollBy({ left: el.clientWidth * 0.7, behavior: 'smooth' }); }
</script>

<div class="sx {cls}">
  <div class="sxin" bind:this={el} onscroll={update}>{@render children()}</div>
  <div class="fade" class:on={more} aria-hidden="true"></div>
  <button type="button" class="chev" class:on={more} tabindex="-1" aria-label="Ver más columnas" onclick={nudge}>
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M9 5l7 7-7 7" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" /></svg>
  </button>
</div>

<style>
  .sx { position: relative; min-width: 0; }
  .sxin { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .fade, .chev { opacity: 0; transition: opacity 0.2s ease; pointer-events: none; }
  .fade { position: absolute; top: 0; right: 0; bottom: 0; width: 56px; background: linear-gradient(to right, transparent, var(--bg) 85%); }
  .chev { position: absolute; right: 2px; top: 6px; display: grid; place-items: center; width: 28px; height: 28px; padding: 0; border: 0; border-radius: 50%; background: var(--ink); color: var(--bg); cursor: pointer; box-shadow: var(--shadow); }
  .fade.on, .chev.on { opacity: 1; }
  .chev.on { pointer-events: auto; }
</style>
