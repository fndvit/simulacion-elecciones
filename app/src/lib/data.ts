import app from './data/app_data.json';
import hex from './data/hex.json';
import type { AppData, Province } from './types';

export const DATA = { ...(app as unknown as Omit<AppData, 'hex'>), hex } as AppData;
export const PROV: Province[] = DATA.prov;
export const BYID: Record<string, Province> = Object.fromEntries(PROV.map((p) => [p.id, p]));
