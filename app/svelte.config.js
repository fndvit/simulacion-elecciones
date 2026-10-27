import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// Two builds from the same code:
//  · on Vercel (VERCEL=1): real paths (/, /simula, /escenarios). The site is a single-page app: every path is
//    served index.html (fallback + the rewrite in vercel.json) and the client router picks the view.
//  · everywhere else (GitHub Actions, local, claude.ai artifact): one self-contained index.html with hash
//    routing (#/simula), which also works when opened straight from the disk.
const paths = !!process.env.VERCEL;

/** @type {import('@sveltejs/kit').Config} */
export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ pages: 'build', assets: 'build', fallback: paths ? 'index.html' : undefined, strict: true }),
    output: { bundleStrategy: 'inline' },
    router: { type: paths ? 'pathname' : 'hash' },
    paths: { relative: !paths },
    // on Vercel, src/lib/assets is also published as is, so the share image has a fixed address (/og.png)
    files: { assets: paths ? 'src/lib/assets' : 'static' }
  }
};
