<script lang="ts">
  // Site footer, after the atlas's: «Un proyecto de» ViT · contact · sections · share. No gradient: the
  // intro's black, light grey headers.
  import { href } from '$lib/nav';
  const SITE = 'https://trescincuenta.es';
  const TEXT = 'TresCincuenta.es · la proyección de los 350 escaños del Congreso para el 29N';
  const share = {
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(SITE)}`,
    bluesky: `https://bsky.app/intent/compose?text=${encodeURIComponent(`${TEXT} ${SITE}`)}`
  };
  const GITHUB = 'https://github.com/fndvit';
</script>

<footer class="site-foot">
  <div class="foot">
    <div class="brand">
      <div class="proj">Un proyecto de</div>
      <a class="logo" href="https://fundaciovit.org" target="_blank" rel="noopener" aria-label="Fundació ViT">
        <svg viewBox="48 37 151 88" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path opacity="0.9" d="M136.822 62.271H127.724V71.1645H136.822V62.271Z" fill="currentColor" />
          <path opacity="0.9" d="M51.7383 40.3589H62.8039L89.0518 121.077H79.8716L51.7383 40.3589Z" fill="currentColor" />
          <path opacity="0.45" d="M119.161 40.3589H108.952L82.6956 121.077H91.0195L119.161 40.3589Z" fill="currentColor" />
          <path opacity="0.45" d="M168.52 40.3589H158.525V121.069H168.52V40.3589Z" fill="currentColor" />
          <path opacity="0.9" d="M105.971 49.4999H195.361V40.3589H108.952L105.971 49.4999Z" fill="currentColor" />
          <path opacity="0.7" d="M136.822 77.0713H127.724V121.077H136.822V77.0713Z" fill="currentColor" />
        </svg>
      </a>
    </div>

    <div class="col">
      <div class="col-title">Contacto</div>
      <div>Karma Peiró</div>
      <a href="mailto:karma@fundaciovit.org">karma@fundaciovit.org</a>
    </div>

    <nav class="col links" aria-label="Mapa web">
      <div class="col-title">Secciones</div>
      <a href={href('/')}>Proyección</a>
      <a href={href('/simula')}>Simula</a>
      <a href={href('/escenarios')}>Escenarios</a>
      <a href={href('/metodologia')}>Metodología</a>
      <a href={href('/quienes-somos')}>Quiénes somos</a>
    </nav>

    <div class="col">
      <div class="col-title">Comparte</div>
      <div class="social">
        <a href={share.linkedin} target="_blank" rel="noopener" aria-label="Compartir en LinkedIn">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.07 2.07 0 1 1 0-4.13 2.07 2.07 0 0 1 0 4.13zm1.78 13.02H3.55V9h3.57v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45C23.2 24 24 23.23 24 22.27V1.73C24 .77 23.2 0 22.22 0z" /></svg>
        </a>
        <a href={share.bluesky} target="_blank" rel="noopener" aria-label="Compartir en Bluesky">
          <svg viewBox="0 0 41 36" aria-hidden="true"><path d="M9.2742 2.99067C13.8181 6.38153 18.7056 13.2568 20.5 16.9464C22.2946 13.2571 27.1818 6.38147 31.7258 2.99067C35.0044 0.543964 40.3167 -1.34916 40.3167 4.67486C40.3167 5.87794 39.6227 14.7814 39.2157 16.2268C37.801 21.2521 32.6459 22.5339 28.0603 21.7581C36.0758 23.1141 38.1149 27.6058 33.7113 32.0976C25.348 40.6282 21.6908 29.9572 20.7532 27.2229C20.5815 26.7216 20.5011 26.4871 20.4999 26.6865C20.4987 26.4871 20.4183 26.7216 20.2465 27.2229C19.3094 29.9572 15.6523 40.6285 7.28848 32.0976C2.8848 27.6058 4.9238 23.1139 12.9394 21.7581C8.35372 22.5339 3.19852 21.2521 1.78402 16.2268C1.37701 14.7812 0.683102 5.87781 0.683102 4.67486C0.683102 -1.34916 5.99547 0.543964 9.27397 2.99067H9.2742Z" /></svg>
        </a>
        <a href={GITHUB} target="_blank" rel="noopener" aria-label="Fundació ViT en GitHub">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" /></svg>
        </a>
      </div>
    </div>
  </div>
</footer>

<style>
  .site-foot { margin-top: var(--s4); background: #16181d; color: #d6d1d3; font-family: var(--font-ui); font-weight: 400; }
  .foot { max-width: 1262px; margin: 0 auto; padding: var(--s4) 16px var(--s3); box-sizing: content-box;
    display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; row-gap: var(--s3); align-items: start; }
  .brand { grid-column: 1 / 4; }
  .foot > :nth-child(2) { grid-column: 4 / 7; }
  .foot > :nth-child(3) { grid-column: 7 / 10; }
  .foot > :nth-child(4) { grid-column: 10 / 13; }
  .proj { color: #a9a3a5; font-weight: 700; font-size: 20px; margin-bottom: 12px; }
  .logo { display: inline-block; color: #f7f4ef; }
  .logo svg { height: 80px; width: auto; display: block; }
  .col { display: flex; flex-direction: column; gap: 5px; font-size: 16px; line-height: 1.5; }
  .col-title { color: #a9a3a5; font-weight: 700; font-size: 16px; margin-bottom: 8px; }
  .col a { color: inherit; text-decoration: none; }
  .col a:hover { color: #fff; text-decoration: underline; }
  .social { display: flex; align-items: center; gap: 24px; margin-top: 2px; }
  .social a { display: inline-flex; color: #f7f4ef; }
  .social a:hover { color: #fff; text-decoration: none; opacity: 0.8; }
  .social svg { height: 30px; width: auto; display: block; fill: currentColor; }
  @media (max-width: 760px) {
    .foot > * { grid-column: 1 / -1 !important; }
    .proj { font-size: 16px; }
    .logo svg { height: auto; width: 64px; }
    .col, .col-title { font-size: 14px; line-height: 1.35; }
  }
</style>
