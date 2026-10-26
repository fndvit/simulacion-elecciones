// Internal links. With the hash router (single-file build) keep only the #/… part, so links work from
// file:// and inside the artifact; with the path router (Vercel) this is just the resolved path.
import { resolve as res } from '$app/paths';
export type Path = '/' | '/simula' | '/escenarios' | '/metodologia' | '/quienes-somos' | '/privacidad';
export const href = (p: Path) => {
  const r = res(p);
  const i = r.indexOf('#');
  return i >= 0 ? r.slice(i) : r;
};
