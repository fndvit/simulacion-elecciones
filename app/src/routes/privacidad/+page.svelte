<script lang="ts">
  // Política de privacidad: what happens with visitors' data (almost nothing), in plain language.
  import PageHead from '$lib/components/PageHead.svelte';
  const MAIL = 'karma@fundaciovit.org';
</script>

<svelte:head>
  <title>Política de privacidad · TresCincuenta.es</title>
  <meta name="description" content="Qué pasa con tus datos cuando visitas TresCincuenta.es: sin cookies, sin rastreadores y solo estadísticas agregadas de visitas." />
</svelte:head>

<PageHead
  kicker="Privacidad"
  title="Política de <strong>privacidad</strong>"
  lede="Igual que publicamos cómo calculamos la proyección, contamos aquí qué pasa con tus datos cuando visitas la web. La respuesta corta: <strong>casi nada, y nada que te identifique</strong>." />

<section class="page">
  <div class="prose well">
    <h3>Quién es responsable</h3>
    <p>
      TresCincuenta.es es un proyecto de la <a href="https://fundaciovit.org" target="_blank" rel="noopener">Fundació VIT, Visualització
      per a la Transparència</a>, inscrita como fundación cultural con el
      <a href="https://justicia.gencat.cat/ca/serveis/guia_d_entitats/index.html?idEntitat=108636#" target="_blank" rel="noopener">número 3185
      del Registro de Fundaciones de la Generalitat de Catalunya</a>, con sede en Carrer Marfà 14, 17006 Girona. Puedes escribirnos a
      <a href="mailto:{MAIL}">{MAIL}</a> para cualquier pregunta sobre esta política o sobre tus datos.
    </p>

    <h3>Lo que no hacemos</h3>
    <p>
      No usamos cookies. No tenemos cuentas de usuario, formularios ni boletines. No mostramos publicidad, no vendemos ni cedemos
      datos, no creamos perfiles y no usamos rastreadores de redes sociales ni de terceros. Las tipografías y el resto de archivos de
      la web se sirven desde nuestro propio dominio, de modo que tu navegador no se conecta a servicios de terceros como Google Fonts.
      Los botones para compartir son enlaces normales: no cargan nada de LinkedIn ni de Bluesky hasta que haces clic.
    </p>

    <h3>Estadísticas de visitas</h3>
    <p>
      Para saber cuánta gente usa la web y qué secciones le interesan, usamos
      <a href="https://vercel.com/docs/analytics/privacy-policy" target="_blank" rel="noopener">Vercel Web Analytics</a>, una herramienta
      sin cookies que solo produce estadísticas agregadas. Por cada página vista registra la dirección de la página, la web de la que
      vienes, el país y la región aproximados, el tipo de dispositivo, el sistema operativo y el navegador. No guarda tu dirección IP.
      Para contar visitantes únicos genera un identificador cifrado a partir de la petición, y lo borra a las 24 horas, así que no
      puede seguirte de un día a otro ni entre webs. Antes de enviar cada visita quitamos de la dirección el escenario que hayas creado
      en el simulador: lo que simulas no forma parte de nuestras estadísticas.
    </p>
    <p>Base legal: nuestro interés legítimo en conocer el uso agregado de un servicio público y gratuito (art. 6.1.f del RGPD).</p>

    <h3>Alojamiento</h3>
    <p>
      La web está alojada en Vercel Inc. Como cualquier servidor, Vercel procesa datos técnicos de cada conexión, como la dirección
      IP, para servir las páginas y protegerlas frente a abusos, y actúa como encargado del tratamiento. Vercel Inc. está adherida y
      certificada en el Marco de Privacidad de Datos UE-EE. UU. (EU-U.S. Data Privacy Framework), además de utilizar cláusulas
      contractuales tipo (CCT) como mecanismo complementario para las transferencias internacionales de datos de usuarios del Espacio
      Económico Europeo (EEE).
    </p>

    <h3>Lo que se queda en tu navegador</h3>
    <p>
      El simulador guarda tu último escenario en el almacenamiento local de tu navegador, para que no lo pierdas si recargas la página.
      Ese dato no sale de tu dispositivo y no lo vemos. Puedes borrarlo limpiando los datos del sitio en tu navegador.
    </p>

    <h3>Escenarios compartidos</h3>
    <p>Cuando compartes un escenario, los cambios que hiciste van codificados en el propio enlace. No guardamos esos enlaces en ningún sitio.</p>

    <h3>Tus derechos</h3>
    <p>
      Como no guardamos datos que te identifiquen, normalmente no tendremos nada tuyo. Aun así, puedes ejercer tus derechos de acceso,
      rectificación, supresión, oposición, limitación y portabilidad escribiendo a <a href="mailto:{MAIL}">{MAIL}</a>. Si crees que no
      los hemos respetado, puedes reclamar ante la <a href="https://www.aepd.es" target="_blank" rel="noopener">Agencia Española de
      Protección de Datos</a>.
    </p>

    <h3>Cambios</h3>
    <p>Si cambiamos algo, actualizaremos esta página con la fecha. Última actualización: 26 de octubre de 2026.</p>
  </div>
</section>

<style>
  .page { max-width: 1262px; margin: 0 auto; padding: 0 16px var(--s3); box-sizing: content-box; display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; }
  .well { grid-column: 2 / 8; min-width: 0; }
  .prose h3 { font-family: var(--font-ui); font-weight: 700; font-size: 16px; color: var(--ink); margin: var(--s2) 0 6px; }
  .prose h3:first-child { margin-top: 0; }
  .prose p { font-family: var(--font-body); font-weight: 300; font-size: 16px; line-height: 1.72; color: var(--fg); margin: 0 0 1em; }
  .prose a { color: inherit; text-decoration: underline; text-decoration-color: var(--muted); text-underline-offset: 3px; }
  @media (max-width: 900px) { .page { grid-template-columns: minmax(0, 1fr); } .well { grid-column: 1; } }
</style>
