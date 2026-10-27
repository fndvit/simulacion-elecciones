<script lang="ts">
  // Quiénes somos — the team, bios and photos from the atlas's «equipo» page. The photos are inlined
  // (small 480 px webp) so they also show in the single-file build.
  import PageHead from '$lib/components/PageHead.svelte';
  import karma from '$lib/assets/team/karma.webp?inline';
  import xaquin from '$lib/assets/team/xaquin.webp?inline';
  import aleix from '$lib/assets/team/aleix.webp?inline';
  import laia from '$lib/assets/team/laia.webp?inline';
  import judit from '$lib/assets/team/judit.webp?inline';
  import pol from '$lib/assets/team/pol.webp?inline';

  // bios carry <em> for outlet names
  type Member = { nombre: string; rol: string; bio: string[]; email?: string; photo?: string };
  const team: Member[] = [
    {
      nombre: 'Karma Peiró',
      rol: 'Dirección editorial',
      bio: [
        'Es cofundadora y directora de la Fundació ViT. Periodista especializada en tecnología desde 1995. Ha trabajado para <em>en.red.ando</em>, <em>La Vanguardia</em>, <em>Catalunya Ràdio</em>, <em>TV3</em> y <em>Nació Digital</em>, entre otros medios. Actualmente, también es profesora asociada a la UdG y la URL-Blanquerna.',
        'Activista de datos: en las últimas dos décadas ha impulsado actividades para el conocimiento, análisis y concienciación del uso de los datos abiertos. El objetivo siempre ha sido el mismo: que la ciudadanía ejerza su derecho de acceso a la información pública.'
      ],
      email: 'karma@fundaciovit.org',
      photo: karma
    },
    {
      nombre: 'Xaquín G.V.',
      rol: 'Dirección del proyecto',
      bio: [
        'Periodista visual y de datos gallego. Trabajó en <em>The New York Times</em> y en <em>National Geographic</em>, y lideró el equipo de Visuals de <em>The Guardian</em>. Actualmente es mentor del equipo visual de <em>The Straits Times</em> y profesor asociado en la Universidad de Girona.',
        'Ha visualizado elecciones locales, autonómicas, nacionales, presidenciales, primarias, referéndums. Con mapas y cartogramas. Hexágonos, gradientes, pictogramas. Sparklines y bolitas. En papel y en digital. En tres continentes. Durante el pasado cuarto de siglo.'
      ],
      email: 'xaquin@fundaciovit.org',
      photo: xaquin
    },
    {
      nombre: 'Aleix Álvarez',
      rol: 'Full-stack',
      bio: ['Ingeniero informático graduado por la Universitat de Girona, con experiencia en desarrollo de software, administración de redes y gestión de bases de datos.'],
      email: 'aleix@fundaciovit.org',
      photo: aleix
    },
    {
      nombre: 'Laia Verdaguer',
      rol: 'Diseño y front-end',
      bio: ['Diseñadora y desarrolladora graduada en Desarrollo de Videojuegos por la Universitat de Girona, especializada en interfaces y visualización de datos.'],
      email: 'laia@fundaciovit.org',
      photo: laia
    },
    {
      nombre: 'Judit Quintana',
      rol: 'Full-stack',
      bio: ['Ingeniera informática con un máster en Data Science, especializada en visualización de datos.'],
      email: 'judit@fundaciovit.org',
      photo: judit
    },
    {
      nombre: 'Pol Darder',
      rol: 'Full-stack',
      bio: ['Ingeniero con un máster en Data Science y un grado en Desarrollo de Videojuegos, con experiencia como desarrollador backend.'],
      email: 'pol@fundaciovit.org',
      photo: pol
    }
  ];
</script>

<svelte:head>
  <title>Quiénes somos · TresCincuenta.es</title>
  <meta name="description" content="TresCincuenta.es es un proyecto del Centre de Recerca de la Fundació ViT. Conoce al equipo." />
</svelte:head>

<PageHead
  kicker="El equipo"
  title="Quiénes <strong>somos</strong>"
  lede="TresCincuenta.es es un proyecto del <strong>Centre de Recerca de la <a href='https://fundaciovit.org/' target='_blank' rel='noopener'>Fundació ViT</a></strong>" />

<section class="page">
  {#each team as p}
    <article class="member">
      <div class="bio">
        <h2 class="name">{p.nombre}</h2>
        <div class="role">{p.rol}</div>
        {#each p.bio as para}<p class="txt">{@html para}</p>{/each}
        {#if p.email}<div class="contact"><a href="mailto:{p.email}">{p.email}</a></div>{/if}
      </div>
      <div class="portrait">{#if p.photo}<img src={p.photo} alt={p.nombre} />{/if}</div>
    </article>
  {/each}
</section>

<style>
  .page { max-width: 1262px; margin: 0 auto; padding: 0 16px var(--s3); box-sizing: content-box; }
  .member { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; align-items: start; padding: var(--s3) 0; }
  .member:first-child { padding-top: var(--s1); }
  .bio { grid-column: 2 / 7; min-width: 0; }
  .portrait { grid-column: 8 / 11; aspect-ratio: 1 / 1; background: var(--panel); border-radius: var(--radius); overflow: hidden; }
  .portrait img { width: 100%; height: 100%; object-fit: cover; display: block; }
  .txt + .txt { margin-top: 12px; }
  .contact { display: flex; flex-wrap: wrap; gap: 4px 14px; margin-top: 12px; }
  .contact a { font-family: var(--font-ui); font-weight: 400; font-size: 14px; color: var(--muted); text-decoration: none; }
  .contact a:hover { color: var(--fg); text-decoration: underline; }
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
