// Vercel Web Analytics: cookie-free, aggregated page views. Only in the Vercel build (real paths); the
// self-contained index.html (GitHub, claude.ai artifact, opened from disk) sends nothing to anyone.
import { dev } from '$app/environment';
import { injectAnalytics } from '@vercel/analytics/sveltekit';

if (__VERCEL__) {
  injectAnalytics({
    mode: dev ? 'development' : 'production',
    // a shared scenario travels in ?e=…; it is not personal, but we keep it out of the statistics anyway
    beforeSend: (event) => {
      const u = new URL(event.url);
      u.searchParams.delete('e');
      return { ...event, url: u.toString() };
    }
  });
}
