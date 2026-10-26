<script lang="ts">
  // «Ver toda España»: a small black pill that clears the province selection, shown wherever a section
  // follows the selected province (bar, map, last seat, transfers, simulator controls).
  let { scope = $bindable() }: { scope: string } = $props();
</script>

{#if scope !== 'ES'}
  <button type="button" class="tospain" onclick={(e) => { e.stopPropagation(); scope = 'ES'; }}>
    <svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path d="M12 5V2L7.5 6.5 12 11V7.5a5.5 5.5 0 1 1-5.5 5.5H4a8 8 0 1 0 8-8z" fill="currentColor" /></svg>
    Ver toda España
  </button>
{/if}

<style>
  .tospain {
    display: inline-flex; align-items: center; gap: 6px; flex: none; vertical-align: middle;
    padding: 4px 12px 4px 9px; border: 0; border-radius: 999px; cursor: pointer;
    background: var(--ink); color: var(--bg);
    font-family: var(--font-ui); font-weight: 700; font-size: 13px; line-height: 18px; letter-spacing: 0; white-space: nowrap;
  }
  .tospain:hover { opacity: 0.85; }
  .tospain:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
</style>
