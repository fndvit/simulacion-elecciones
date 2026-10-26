declare global {
  // set in vite.config.ts: true only when building on Vercel
  const __VERCEL__: boolean;
}
export {};
