import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ pages: 'build', assets: 'build', fallback: undefined, strict: true }),
    // one self-contained index.html (JS + CSS inlined) that works from file:// and as a published page
    output: { bundleStrategy: 'inline' },
    router: { type: 'hash' },
    paths: { relative: true }
  }
};
