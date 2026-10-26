export type PartyKey =
  | 'PP' | 'PSOE' | 'VOX' | 'FA' | 'PODEMOS' | 'SALF' | 'COMP' | 'ERC' | 'JUNTS'
  | 'BILDU' | 'PNV' | 'BNG' | 'CC' | 'UPC' | 'UPN' | 'AA' | 'AC' | 'OTROS';

export interface Province {
  id: string; n: string; ca: string; seats: number; seats23: number; census: number;
  t0: number; nr: number; bl: number;
  /** projected share of valid vote per party (blank excluded) */
  s: Partial<Record<PartyKey, number>>;
  /** 2023 result: v = share of valid vote (SUMAR whole, OTROS = small parties; blank apart), s = seats (Sumar as FA) */
  r23: { v: Record<string, number>; s: Partial<Record<PartyKey, number>>; valid: number; blank: number; null: number; census: number };
}
export interface Poll {
  p: string; f: string; end: string; fw: string; n: number | null; w: number;
  c: Record<string, number>; v: Record<string, number>; he: Record<string, number>;
}
export interface AppData {
  today: string; election: string; S: Record<string, number>; compSplit: number; halfLife: number;
  ratings: Record<string, [number, number]>; he: Record<string, Record<string, number>>; heN: Record<string, number>;
  wElec: Record<string, number>; polls: Poll[];
  /** vote transfers 2023 → projection per province (CIS recall × intention fitted to each province's totals) */
  fuente?: { wikipedia_es?: { title: string; revid: number; timestamp: string; url: string }; wikipedia_en?: { revid: number; url: string } | null; leido?: string };
  /** who joins / stays home when turnout changes: multiplier per party on its provincial vote (2023 polling-station abstention) */
  tp: Record<string, { up: Record<string, number>; down: Record<string, number> }>; tpMeta: { fuente: string; mesas: number };
  tr: Record<string, [string, string, number][]>; trMeta: { study: string; title: string; n: number }; series: ({ d: string } & Record<string, number>)[];
  prov: Province[]; census: number;
  hex: { R: number; hexes: { id: string; x: number; y: number; r: number; c: number }[] };
}

/** Everything the user can move. */
export interface Scenario {
  nat: Record<string, number>;                     // national Δ pp of valid vote per party
  prov: Record<string, Record<string, number>>;    // province → party → Δ pp
  turnNat: number;                                 // national Δ pp of census
  turnProv: Record<string, number>;                // province → extra Δ pp (adds to national)
  distNat: Record<string, number>;                 // newcomer multipliers (×1 = like everyone else)
  distProv: Record<string, Record<string, number>>;
}

export interface DhondtResult {
  seats: Record<string, number>;
  last: { k: string; q: number; v: number } | null;
  chal: { k: string; need: number } | null;
}
export interface ProvResult extends DhondtResult {
  votes: Record<string, number>; blank: number; valid: number; turnout: number;
}
export interface RunResult {
  prov: Record<string, ProvResult>;
  votes: Record<string, number>; seats: Record<string, number>; valid: number; turnout: number;
}
