<script lang="ts">
  // Head of the content pages (Metodología, Quiénes somos), after the atlas's PageHead, on the page
  // background: grey kicker, big light/bold title, lede. Cols 2–7 of the grid.
  let { kicker = '', title = '', lede = '' }: { kicker?: string; title?: string; lede?: string } = $props();
</script>

<header class="page-head">
  <div class="in">
    {#if kicker}<div class="kicker">{kicker}</div>{/if}
    <h1 class="title">{@html title}</h1>
    {#if lede}<p class="lede-big">{@html lede}</p>{/if}
  </div>
</header>

<style>
  .page-head { padding-inline: 16px; }
  .in { max-width: 1262px; margin: 0 auto; padding: var(--s3) 0 var(--s2); display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; }
  .in > * { grid-column: 2 / 8; }
  .kicker { color: #8a8486; font-family: var(--font-ui); font-weight: 700; font-size: 13px; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 14px; }
  .title { font-family: var(--font-ui); font-weight: 200; font-size: 44px; line-height: 1.1; color: var(--ink); margin: 0; }
  .title :global(strong) { font-weight: 700; }
  .lede-big { font-family: var(--font-ui); font-weight: 200; font-size: 24px; line-height: 32px; color: var(--ink); margin: 20px 0 0; }
  .lede-big :global(strong) { font-weight: 700; }
  @media (max-width: 900px) {
    .in { grid-template-columns: minmax(0, 1fr); padding-top: var(--s2); }
    .in > * { grid-column: 1; }
    .title { font-size: 34px; }
    .lede-big { font-size: 20px; line-height: 28px; }
  }
</style>
