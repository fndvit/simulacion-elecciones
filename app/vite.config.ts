import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
declare const process: { env: Record<string, string | undefined> };
export default defineConfig({
  plugins: [sveltekit()],
  // the Vercel build (VERCEL=1) is the only one that loads Vercel Web Analytics
  define: { __VERCEL__: JSON.stringify(!!process.env.VERCEL) }
});
