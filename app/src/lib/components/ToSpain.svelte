<script lang="ts">
  // «Ver toda España»: a small black pill that clears the province selection, shown wherever a section
  // follows the selected province (bar, map, last seat, transfers, simulator controls).
  let { scope = $bindable() }: { scope: string } = $props();
</script>

{#if scope !== 'ES'}
  <button type="button" class="tospain" onclick={(e) => { e.stopPropagation(); scope = 'ES'; }}>
    <svg xmlns="http://www.w3.org/2000/svg" height="16" viewBox="0 -960 960 960" width="16" fill="currentColor" aria-hidden="true"><path d="M440-122q-121-15-200.5-105.5T160-440q0-66 26-126.5T260-672l57 57q-38 34-57.5 79T240-440q0 88 56 155.5T440-202v80Zm80 0v-80q87-16 143.5-83T720-440q0-100-70-170t-170-70h-3l44 44-56 56-140-140 140-140 56 56-44 44h3q134 0 227 93t93 227q0 121-79.5 211.5T520-122Z"/></svg>
    Ver toda España
  </button>
{/if}

<style>
  .tospain {
    /* the same ink pill as «Restablecer» and «Compartir mi escenario» */
    display: inline-flex; align-items: center; gap: 7px; flex: none; align-self: flex-start; vertical-align: middle;
    padding: 7px 16px 7px 12px; border: 0; border-radius: 999px; cursor: pointer;
    background: var(--ink); color: var(--bg);
    font-family: var(--font-ui); font-weight: 400; font-size: 14px; line-height: 18px; letter-spacing: 0; white-space: nowrap;
  }
  .tospain:hover { opacity: 0.85; }
  .tospain:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
</style>
