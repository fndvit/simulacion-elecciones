<script lang="ts">
  // Atlas ScenarioTable: votes, %, seats, ± vs the poll projection, and 2023 seats.
  import { BYID } from '$lib/data';
  import { PARTY, ORDER } from '$lib/parties';
  import { BASE, scopeVotes, scopeValid, scopeSeats, seats2023 } from '$lib/model';
  import { fmtN, dec, sgnInt } from '$lib/format';
  import type { RunResult } from '$lib/types';

  let { cur, scope, projection = false }: { cur: RunResult; scope: string; projection?: boolean } = $props();

  const rows = $derived.by(() => {
    const v = scopeVotes(cur, scope), val = scopeValid(cur, scope), s = scopeSeats(cur, scope), sb = scopeSeats(BASE, scope), s23 = seats2023(scope);
    return [...ORDER, 'OTROS' as const]
      .filter((P) => (v[P] || 0) > 0)
      .map((P) => ({ P, votes: v[P], share: v[P] / val, seats: s[P] || 0, delta: (s[P] || 0) - (sb[P] || 0), s23: s23[P] }))
      .sort((a, b) => (a.P === 'OTROS' ? 1 : 0) - (b.P === 'OTROS' ? 1 : 0) || b.seats - a.seats || b.votes - a.votes);
  });
</script>

<h2 class="hd">Reparto de votos y escaños <strong>{scope === 'ES' ? 'en toda España' : `en ${BYID[scope].n}`}</strong></h2>
<div class="rows" class:proj={projection} role="table" aria-label={projection ? "Votos y escaños en la proyección" : "Votos y escaños en tu escenario"}>
  <div class="rrow rhead" role="row">
    <span aria-hidden="true"></span>
    <span role="columnheader">Partido</span><span class="ar" role="columnheader">Votos</span><span class="ar" role="columnheader">%</span>
    <span class="ar" role="columnheader">Esc.</span>{#if !projection}<span class="ar" role="columnheader">±</span>{/if}<span class="ar c23" role="columnheader">2023</span>
  </div>
  {#each rows as r (r.P)}
    <div class="rrow" role="row">
      <span class="sw" style="background:{PARTY[r.P].c}" aria-hidden="true"></span>
      <span role="cell">{PARTY[r.P].n}</span>
      <span class="ar m" role="cell">{fmtN(r.votes)}</span>
      <span class="ar m" role="cell">{dec(r.share * 100)}</span>
      <span class="ar st" role="cell">{r.P === 'OTROS' ? '' : r.seats}</span>
      {#if !projection}<span class="ar st" class:up={r.delta > 0} class:down={r.delta < 0} role="cell">{r.delta ? sgnInt(r.delta) : ''}</span>{/if}
      <span class="ar c23 m" role="cell">{r.P === 'OTROS' ? '' : (r.s23 ?? '–')}</span>
    </div>
  {/each}
</div>
<p class="method">Escaños repartidos según la fórmula D'Hondt en cada circunscripción, con barrera del 3 % del voto válido (blancos incluidos), como fija la LOREG.{projection ? '' : ' ± compara con la proyección de las encuestas.'} En 2023, Sumar se corresponde con el actual Frente Amplio, Compromís y Podemos.</p>

<style>
  .rows { display: flex; flex-direction: column; font-family: var(--font-ui); font-weight: 400; }
  .rrow { display: grid; grid-template-columns: 14px minmax(0, 1fr) 88px 54px 44px 34px 40px; align-items: center; gap: 10px; padding: 7px 0; border-bottom: 1px solid var(--line); font-size: 14px; color: var(--ink); }
  .proj .rrow { grid-template-columns: 14px minmax(0, 1fr) 88px 54px 44px 40px; }
  .rhead { padding: 4px 0; }
  .rhead span { font-size: 12px; color: var(--muted); font-weight: 700; }
  .ar { text-align: right; font-variant-numeric: tabular-nums; }
  .sw { width: 12px; height: 12px; border-radius: 3px; }
  .m { color: var(--muted); }
  .st { font-weight: 700; }
  @media (max-width: 820px) {
    .rrow { grid-template-columns: 12px minmax(0, 1fr) 74px 48px 36px 30px; }
    .proj .rrow { grid-template-columns: 12px minmax(0, 1fr) 74px 48px 36px; }
    .c23 { display: none; }
  }
</style>
