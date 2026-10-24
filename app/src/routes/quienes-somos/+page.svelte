<script lang="ts">
  // Quiénes somos — after the atlas's «equipo» page. Names and bios marked TK are placeholders.
  import PageHead from '$lib/components/PageHead.svelte';
  const team = [
    { nombre: 'Xaquín G.V.', rol: 'Dirección del proyecto', bio: 'TK TK' },
    { nombre: 'Karma Peiró', rol: 'Dirección editorial', bio: 'TK TK' },
    { nombre: 'TK TK', rol: 'TK TK', bio: 'TK TK' }
  ];
</script>

<svelte:head>
  <title>Quiénes somos · TresCincuenta.es</title>
  <meta name="description" content="TresCincuenta.es es un proyecto del Centre de Recerca de la Fundació ViT. Conoce al equipo." />
</svelte:head>

<PageHead
  kicker="El equipo"
  color="#5db9ae"
  title="Quiénes <strong>somos</strong>"
  lede="TresCincuenta.es es un proyecto del Centre de Recerca de la <a href='https://fundaciovit.org' target='_blank' rel='noopener'>Fundació ViT</a>, Visualització per a la Transparència." />

<section class="page">
  {#each team as p}
    <article class="member">
      <div class="bio">
        <h2 class="name">{p.nombre}</h2>
        <div class="role">{p.rol}</div>
        <p class="txt">{p.bio}</p>
      </div>
      <div class="portrait" aria-hidden="true"></div>
    </article>
  {/each}
</section>

<style>
  .page { max-width: 1262px; margin: 0 auto; padding: 0 16px var(--s3); box-sizing: content-box; }
  .member { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; align-items: start; padding: var(--s3) 0; border-top: 1px solid var(--line); }
  .member:first-child { border-top: 0; padding-top: var(--s1); }
  .bio { grid-column: 2 / 7; min-width: 0; }
  .portrait { grid-column: 8 / 11; aspect-ratio: 1 / 1; background: var(--panel); border-radius: var(--radius); }
  .name { font-family: var(--font-ui); font-weight: 200; font-size: 26px; line-height: 1.1; color: var(--ink); margin: 0; }
  .role { font-family: var(--font-ui); font-weight: 700; font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); margin: 8px 0 14px; }
  .txt { font-family: var(--font-body); font-weight: 300; font-size: 16px; line-height: 1.72; color: var(--fg); margin: 0; }
  :global(.lede-big a) { color: inherit; }
  @media (max-width: 900px) {
    .member { grid-template-columns: minmax(0, 1fr); }
    .bio, .portrait { grid-column: 1; }
    .portrait { margin-top: 16px; max-width: 280px; width: 100%; }
  }
</style>
