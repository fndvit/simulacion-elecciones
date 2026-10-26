import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
declare const process: { env: Record<string, string | undefined> };
export default defineConfig({
  plugins: [sveltekit()],
  // the Vercel build (VERCEL=1) is the only one that loads Vercel Web Analytics
  define: { __VERCEL__: JSON.stringify(!!process.env.VERCEL) },
  // the single-file build (artifact, opened from disk) carries its fonts inside; on Vercel they are separate files
  build: { assetsInlineLimit: (file: string) => (file.endsWith('.woff2') ? !process.env.VERCEL : undefined) }
});
