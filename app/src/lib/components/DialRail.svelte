<script lang="ts">
  // Left rail (atlas DialRail): "Simula el 29N en [ámbito] si …" + one vote slider per party,
  // turnout, and how the voters who join (or leave) split between parties.
  import LibDrop from './LibDrop.svelte';
  import { PROV, BYID } from '$lib/data';
  import { PARTY } from '$lib/parties';
  import { BASE, V0, VNAT, CENSUS, partiesIn, scopeVotes, scopeValid, hasScopeChanges, s2m, m2s } from '$lib/model';
  import { pct, pp, fmtSigned, sortEs } from '$lib/format';
  import type { Scenario, RunResult, PartyKey } from '$lib/types';

  let { scope = $bindable(), st = $bindable(), cur, focusParty = $bindable() }:
    { scope: string; st: Scenario; cur: RunResult; focusParty: string } = $props();

  const isES = $derived(scope === 'ES');
  const scopeOpts = [{ value: 'ES', label: 'toda España', ct: '350' }, ...[...PROV].sort((a, b) => sortEs(a.n, b.n)).map((p) => ({ value: p.id, label: p.n, ct: String(p.seats) }))];

  const parties = $derived(partiesIn(scope));
  const deltas = $derived(isES ? st.nat : st.prov[scope] || {});
  const valid0 = $derived(isES ? VNAT : V0[scope]);
  const dials = $derived(parties.map((P) => {
    const baseShare = (scopeVotes(BASE, scope)[P] || 0) / scopeValid(BASE, scope);
    const range = isES ? (PARTY[P].statewide ? 10 : 2) : 15;
    return { P, baseShare, min: -Math.min(range, Math.floor(baseShare * 1000) / 10), max: range };
  }).sort((a, b) => b.baseShare - a.baseShare));
  // all parties in one list, by share in the poll projection (stable while dragging)
  const shown = $derived(dials);
  const sorted = $derived(dials.map((d) => d.P));
  function setVote(P: PartyKey, v: number) {
    if (isES) st.nat[P] = v;
    else (st.prov[scope] ||= {})[P] = v;
    focusParty = P;
  }
  const nowShare = (P: string) => (scopeVotes(cur, scope)[P] || 0) / scopeValid(cur, scope);

  // turnout
  const tv = $derived(isES ? st.turnNat : st.turnProv[scope] || 0);
  const tMax = $derived(isES ? 15 : 20);
  const t0 = $derived(isES ? BASE.turnout : BASE.prov[scope].turnout);
  const tNow = $derived(isES ? cur.turnout : cur.prov[scope].turnout);
  const census = $derived(isES ? CENSUS : BYID[scope].census);
  function setTurn(v: number) { if (isES) st.turnNat = v; else st.turnProv[scope] = v; }

  // newcomer distribution
  const effTurn = $derived(isES ? st.turnNat || (Object.values(st.turnProv).some(Boolean) ? 1 : 0) : st.turnNat + (st.turnProv[scope] || 0));
  const dist = $derived(isES ? st.distNat : st.distProv[scope] || st.distNat);
  const custom = $derived(Object.values(dist || {}).some((v) => v !== 1));
  const distShare = $derived.by(() => {
    const sh = scopeVotes(cur, scope), val = scopeValid(cur, scope);
    let W = isES ? 0.009 : BYID[scope].bl;
    const w: Record<string, number> = {};
    for (const P of [...parties, 'OTROS']) { w[P] = ((sh[P] || 0) / val) * (dist[P] != null ? dist[P] : 1); W += w[P]; }
    return Object.fromEntries(parties.map((P) => [P, w[P] / W]));
  });
  function setDist(P: string, slider: number) {
    const m = s2m(slider);
    if (isES) st.distNat[P] = m;
    else (st.distProv[scope] ||= { ...st.distNat })[P] = m;
  }

  function resetScope() {
    if (isES) { st.nat = {}; st.turnNat = 0; st.distNat = {}; }
    else { delete st.prov[scope]; delete st.turnProv[scope]; delete st.distProv[scope]; }
  }

  // readout under the handle, centred on it (atlas DialRail)
  const pos = (v: number, min: number, max: number) => `left: clamp(46px, calc(8px + ${(v - min) / (max - min)} * (100% - 16px)), calc(100% - 46px))`;
</script>

<div class="rail">
  <h1 class="title">
    Qué pasaría en
    <span class="sel"><LibDrop bind:value={scope} options={scopeOpts} label="Circunscripción" filter /></span>
    si …
  </h1>

  <div class="gl">… el voto cambia así <small>puntos sobre el voto válido</small></div>
  <div class="dials" role="group" aria-label="Voto de cada partido">
    {#each shown as d (d.P)}
      {@const v = deltas[d.P] || 0}
      {@const now = nowShare(d.P)}
      <div class="dial">
        <label class="dlabel" for="v-{d.P}">
          <span class="sw" style="background:{PARTY[d.P].c}"></span><strong>{PARTY[d.P].n}</strong>
          <span class="pct">{#if Math.abs(now - d.baseShare) > 0.0005}{pct(d.baseShare)} → <b>{pct(now)}</b>{:else}<b>{pct(d.baseShare)}</b>{/if}</span>
        </label>
        <input id="v-{d.P}" type="range" min={d.min} max={d.max} step="0.1" value={v} oninput={(e) => setVote(d.P, +e.currentTarget.value)} />
        <div class="ends"><span>−</span>{#if v}<span class="val" style={pos(v, d.min, d.max)}><b>{pp(v)} p. · {fmtSigned((v / 100) * valid0)} votos</b></span>{/if}<span>+</span></div>
      </div>
    {/each}
  </div>

  <div class="gl"><span>… la participación {tv > 0 ? 'sube' : tv < 0 ? 'baja' : 'cambia'}</span><small>puntos sobre el censo</small></div>
  <div class="dial">
    <label class="dlabel" for="turn">
      {isES ? 'Participación en toda España' : `Participación en ${BYID[scope].n}`}
      <span class="pct">{#if Math.abs(tNow - t0) > 0.0005}{pct(t0)} → <b>{pct(tNow)}</b>{:else}<b>{pct(t0)}</b>{/if}</span>
    </label>
    <input id="turn" type="range" min="-15" max={tMax} step="0.5" value={tv} oninput={(e) => setTurn(+e.currentTarget.value)} />
    <div class="ends"><span>−</span>{#if tv}<span class="val" style={pos(tv, -15, tMax)}><b>{pp(tv)} p. · {fmtSigned((tv / 100) * census)} votantes</b></span>{/if}<span>+</span></div>
  </div>
  {#if !isES && st.turnNat}<p class="note">Se suma a los {pp(st.turnNat)} puntos fijados para toda España.</p>{/if}

  <div class="gl"><span>… y los que {effTurn < 0 ? 'se quedan en casa votaban' : 'se suman votan'} {custom ? 'así' : 'como el resto'}</span><small>% del total</small></div>
  <div class="dist">
    <p class="note">En el centro, cada partido se lleva lo mismo que del resto del voto. Hacia +, capta más; hacia −, menos.</p>
    {#each sorted as P (P)}
      <div class="drow">
        <label class="nm" for="d-{P}"><i style="background:{PARTY[P].c}"></i>{PARTY[P].n}</label>
        <input id="d-{P}" type="range" min="-1" max="1" step="0.05" value={m2s(dist[P] != null ? dist[P] : 1)} oninput={(e) => setDist(P, +e.currentTarget.value)} />
        <span class="pc">{pct(distShare[P] || 0, 0)}</span>
      </div>
    {/each}
    {#if !effTurn}<p class="note">No tiene efecto hasta que muevas la participación.</p>
    {:else if !isES && !st.distProv[scope]}<p class="note">Ahora usa el reparto fijado para toda España; si lo cambias, solo se aplica aquí.</p>{/if}
  </div>

  <button class="reset" onclick={resetScope} disabled={!hasScopeChanges(st, scope)}>
    <svg xmlns="http://www.w3.org/2000/svg" height="16" viewBox="0 -960 960 960" width="16" fill="currentColor" aria-hidden="true"><path d="M480-160q-134 0-227-93t-93-227q0-134 93-227t227-93q69 0 132 28.5T720-690v-110h80v280H520v-80h168q-32-56-87.5-88T480-720q-100 0-170 70t-70 170q0 100 70 170t170 70q77 0 139-44t87-116h84q-28 106-114 173t-196 67Z"/></svg>
    Restablecer {isES ? 'los ajustes nacionales' : BYID[scope].n}
  </button>
  {#if !isES}<button class="reset" onclick={() => (scope = 'ES')}>← Volver a toda España</button>{/if}
</div>

<style>
  .rail { display: flex; flex-direction: column; gap: var(--s2); }
  .title { font-family: var(--font-ui); font-weight: 200; color: var(--ink); font-size: 24px; line-height: 36px; letter-spacing: -0.01em; margin: 0; }
  .sel { display: inline-flex; vertical-align: middle; }
  .sel :global(.word) { font-size: 24px; line-height: 30px; padding: 3px 11px; font-weight: 200; }
  .sel :global(.menu) { min-width: max-content; max-height: 360px; }
  .sel :global(.opts) { max-height: 320px; overflow-y: auto; }
  .sel :global(.opt) { font-size: 17px; line-height: 26px; }

  .gl { font-family: var(--font-ui); font-weight: 700; font-size: 20px; line-height: 28px; color: var(--ink); }
  .gl small { display: block; font-weight: 400; font-size: 12px; line-height: 16px; color: var(--muted); }
  .dials { display: flex; flex-direction: column; gap: 16px; }
  .dial { display: flex; flex-direction: column; }
  .dlabel { font-family: var(--font-ui); font-size: 15px; line-height: 20px; color: var(--ink); display: flex; align-items: center; gap: 7px; font-weight: 300; }
  .dlabel .sw { width: 10px; height: 10px; border-radius: 3px; flex: none; }
  .dlabel strong { font-weight: 700; }
  .dlabel .pct { margin-left: auto; color: var(--muted); font-size: 13px; font-variant-numeric: tabular-nums; font-weight: 400; white-space: nowrap; }
  .dlabel .pct b { color: var(--ink); }
  .ends { position: relative; display: flex; justify-content: space-between; font-family: var(--font-ui); font-size: 13px; color: var(--muted); height: 18px; font-weight: 400; }
  .val { position: absolute; top: 0; transform: translateX(-50%); white-space: nowrap; font-variant-numeric: tabular-nums; pointer-events: none; }
  .val b { color: var(--ink); font-weight: 700; }

  .dist { display: flex; flex-direction: column; gap: 10px; margin-top: -8px; }
  .drow { display: grid; grid-template-columns: 96px 1fr 40px; gap: 8px; align-items: center; font-family: var(--font-ui); font-size: 13px; color: var(--ink); }
  .drow .nm { display: flex; gap: 6px; align-items: center; white-space: nowrap; overflow: hidden; }
  .drow .nm i { width: 8px; height: 8px; border-radius: 2px; flex: none; }
  .drow .pc { text-align: right; font-variant-numeric: tabular-nums; color: var(--muted); }
  .drow input { margin: 0; }

  .reset { align-self: flex-start; display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-ui); font-size: 13px; color: var(--fg); background: none; border: 0; padding: 0; cursor: pointer; }
  .reset:disabled { opacity: 0.35; cursor: default; }

  @media (max-width: 820px) { .title, .sel :global(.word) { font-size: 24px; line-height: 34px; } }
</style>
