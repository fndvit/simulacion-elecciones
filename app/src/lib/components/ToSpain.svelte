<script lang="ts">
  // «Ver toda España»: a small black pill that clears the province selection, shown wherever a section
  // follows the selected province (bar, map, last seat, transfers, simulator controls).
  let { scope = $bindable() }: { scope: string } = $props();
</script>

{#if scope !== 'ES'}
  <button type="button" class="tospain" onclick={(e) => { e.stopPropagation(); scope = 'ES'; }}>
    <svg class="flipx" xmlns="http://www.w3.org/2000/svg" height="16" viewBox="0 -960 960 960" width="16" fill="currentColor" aria-hidden="true"><path d="M480-160q-134 0-227-93t-93-227q0-134 93-227t227-93q69 0 132 28.5T720-690v-110h80v280H520v-80h168q-32-56-87.5-88T480-720q-100 0-170 70t-70 170q0 100 70 170t170 70q77 0 139-44t87-116h84q-28 106-114 173t-196 67Z"/></svg>
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
  /* «Restablecer»'s icon, mirrored */
  .flipx { transform: scaleX(-1); }
  .tospain:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
</style>
