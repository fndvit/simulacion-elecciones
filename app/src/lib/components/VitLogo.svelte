<script lang="ts">
  // ViT · elecciones logo: the atlas's one-colour mark (static/vit-elecciones-logo-white.svg, same shapes and
  // opacities, 26px high as in its top nav), printed in grey instead of white.
  let { height = 26 }: { height?: number } = $props();
</script>

<a class="vitlogo" href="https://fundaciovit.org" target="_blank" rel="noopener" aria-label="ViT · elecciones">
  <svg class="mark" viewBox="0 0 72 40" height={height} fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <g clip-path="url(#vlw-clip)">
      <mask id="vlw-m0" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="38" y="10" width="5" height="6"><path d="M42.6489 10.8573H38.0918V15.2662H42.6489V10.8573Z" fill="white" /></mask>
      <g mask="url(#vlw-m0)"><path d="M42.6489 10.8573H38.0918V15.2662H42.6489V10.8573Z" fill="currentColor" opacity="0.9" /></g>
      <path d="M0 0H5.54623L18.7078 40H14.1002L0 0Z" fill="currentColor" opacity="0.9" />
      <path d="M33.7971 0H28.6799L15.5183 40H19.6919L33.7971 0Z" fill="currentColor" opacity="0.45" />
      <path d="M58.5457 0H53.5344V39.995H58.5457V0Z" fill="currentColor" opacity="0.45" />
      <path d="M27.186 4.52887H71.9999V0H28.6798L27.186 4.52887Z" fill="currentColor" opacity="0.9" />
      <mask id="vlw-m1" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="38" y="18" width="5" height="22"><path d="M42.6489 18.1905H38.0918V39.995H42.6489V18.1905Z" fill="white" /></mask>
      <g mask="url(#vlw-m1)"><path d="M42.6489 18.1905H38.0918V39.995H42.6489V18.1905Z" fill="currentColor" opacity="0.7" /></g>
    </g>
    <defs><clipPath id="vlw-clip"><rect width="72" height="40" fill="white" /></clipPath></defs>
  </svg>
</a>

<style>
  .vitlogo { display: inline-flex; line-height: 0; color: #9b9496; }
  .vitlogo:hover { opacity: 0.72; }
  svg { display: block; width: auto; }
  @media (prefers-color-scheme: dark) { :global(:root:not([data-theme='light'])) .vitlogo { color: #b3acae; } }
  :global(:root[data-theme='dark']) .vitlogo { color: #b3acae; }
</style>
