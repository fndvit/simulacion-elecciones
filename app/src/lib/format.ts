// thousands with a dot from 1.000 up (Intl's es-ES only groups from 10.000)
const group = (n: number) => String(Math.abs(Math.round(n))).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
export const fmtN = (n: number) => (Math.round(n) < 0 ? '−' : '') + group(n);
export const fmtSigned = (n: number) => (n > 0 ? '+' : n < 0 ? '−' : '') + group(n);
export const pct = (x: number, d = 1) => (x * 100).toFixed(d).replace('.', ',') + ' %';
export const pp = (x: number) => (x > 0 ? '+' : x < 0 ? '−' : '') + Math.abs(x).toFixed(1).replace('.', ',');
export const dec = (x: number, d = 1) => x.toFixed(d).replace('.', ',');
export const sgnInt = (d: number) => (d > 0 ? '+' : '−') + Math.abs(d);
export const sortEs = (a: string, b: string) => a.localeCompare(b, 'es');
export const longDate = (iso: string) => new Date(iso).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
