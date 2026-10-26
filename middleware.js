// Temporary password gate for the whole site, while TresCincuenta.es is not public yet.
// Vercel Routing Middleware with HTTP Basic auth: the browser asks for a password once and remembers it.
// The password lives in the SITE_PASSWORD environment variable (Vercel → Settings → Environment Variables);
// if it is not set, the site is open. To open the site for good, delete this file (or the variable).
export const config = { matcher: '/:path*' };

export default function middleware(request) {
  const password = process.env.SITE_PASSWORD;
  if (!password) return;                                   // no password configured: let everything through
  const auth = request.headers.get('authorization') || '';
  if (auth.startsWith('Basic ')) {
    try {
      const decoded = atob(auth.slice(6));
      if (decoded.slice(decoded.indexOf(':') + 1) === password) return;   // any user name, right password
    } catch {}
  }
  return new Response('Acceso restringido. TresCincuenta.es aún no es público.', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="TresCincuenta.es", charset="UTF-8"',
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Robots-Tag': 'noindex, nofollow'
    }
  });
}
