import type { PartyKey } from './types';

export const PARTY: Record<PartyKey, { n: string; c: string; statewide?: boolean }> = {
  PP: { n: 'PP', c: '#005aaa', statewide: true },
  PSOE: { n: 'PSOE', c: '#ee3135', statewide: true },
  VOX: { n: 'Vox', c: '#63be21', statewide: true },
  FA: { n: 'Frente Amplio', c: '#e51c6b', statewide: true },
  PODEMOS: { n: 'Podemos', c: '#7b55c7', statewide: true },
  SALF: { n: 'SALF', c: '#8c7a6b', statewide: true },
  COMP: { n: 'Compromís', c: '#f07d2a' },
  ERC: { n: 'ERC', c: '#f6c500' },
  JUNTS: { n: 'Junts', c: '#00c3b2' },
  BILDU: { n: 'EH Bildu', c: '#9fca3a' },
  PNV: { n: 'PNV', c: '#0aa04b' },
  BNG: { n: 'BNG', c: '#6a9bca' },
  CC: { n: 'CC', c: '#e0b000' },
  UPC: { n: 'Unidad P. Canario', c: '#a3528c' },
  UPN: { n: 'UPN', c: '#2a52be' },
  AA: { n: 'Adelante And.', c: '#45b37a' },
  AC: { n: 'Aliança Cat.', c: '#3f7f9f' },
  OTROS: { n: 'Otros', c: '#b9b3aa' }
};
/** by national size — sliders, table */
export const ORDER: PartyKey[] = ['PP', 'PSOE', 'VOX', 'FA', 'PODEMOS', 'SALF', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'COMP', 'BNG', 'AA', 'AC', 'CC', 'UPC', 'UPN'];
/** by bloc — seat bar, map legend: PSOE far left … PP far right */
export const BLOC: PartyKey[] = ['PSOE', 'FA', 'COMP', 'PODEMOS', 'ERC', 'BILDU', 'BNG', 'AA', 'PNV', 'JUNTS', 'UPC', 'CC', 'UPN', 'AC', 'SALF', 'VOX', 'PP'];
/** parties that voted for the 2023 investiture (Sumar ≈ FA + Compromís + Podemos) */
export const INVEST23: PartyKey[] = ['PSOE', 'FA', 'COMP', 'PODEMOS', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPC'];

export const partyLabel = (k: string) => (k === 'ABST' ? 'Abstención' : k === 'OTROS' ? 'Otros y blanco' : (PARTY[k as PartyKey]?.n ?? k));
export const partyColor = (k: string) => PARTY[k as PartyKey]?.c ?? '#b9b3aa';
