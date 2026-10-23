<script lang="ts">
  // Shares a link that reopens exactly this scenario (?e=…); on phones, through the system share sheet.
  import { PARTY, ORDER } from '$lib/parties';
  import { BASE, type HistoryEntry } from '$lib/model';
  import { pct, sgnInt } from '$lib/format';
  import { shareUrl } from '$lib/share';
  import type { RunResult, Scenario, PartyKey } from '$lib/types';

  let { entries, st, cur }: { entries: HistoryEntry[]; st: Scenario; cur: RunResult } = $props();
  const nm = (k: string) => PARTY[k as PartyKey].n;
  let copied = $state(false);

  function summary() {
    const s = cur.seats, tmp = document.createElement('div');
    const lines = [
      'Simulación 29N — escaños en el Congreso',
      ORDER.filter((P) => s[P]).sort((a, b) => s[b] - s[a]).map((P) => { const d = (s[P] || 0) - (BASE.seats[P] || 0); return `${nm(P)} ${s[P]}` + (d ? ` (${sgnInt(d)})` : ''); }).join(' · ')
    ];
    if (entries.length) { lines.push('Supuestos:'); for (const e of entries) { tmp.innerHTML = e.html; lines.push('- ' + tmp.textContent); } }
    lines.push(`Participación: ${pct(cur.turnout)}`);
    return lines.join('\n');
  }
  function fallback(txt: string) {
    const t = document.createElement('textarea'); t.value = txt; document.body.appendChild(t); t.select();
    try { document.execCommand('copy'); done(); } catch {}
    t.remove();
  }
  function done() { copied = true; setTimeout(() => (copied = false), 1800); }
  // a link that opens exactly this scenario; on phones, the system share sheet (with a text summary)
  async function share() {
    const url = shareUrl(st);
    const touch = matchMedia('(pointer: coarse)').matches;
    if (touch && navigator.share) { try { await navigator.share({ title: 'Mi escenario para el 29N', text: summary(), url }); return; } catch (e) { if ((e as Error).name === 'AbortError') return; } }
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(done, () => fallback(url)); else fallback(url);
  }
</script>

<button class="share" aria-label="Compartir mi escenario" class:on={copied} onclick={share} title="Copia un enlace que abre el simulador con todos tus ajustes">
  <svg width="15" height="15" viewBox="0 -960 960 960" fill="currentColor" aria-hidden="true"><path d="M720-80q-50 0-85-35t-35-85q0-7 1-14.5t3-13.5L322-392q-17 15-38 23.5t-44 8.5q-50 0-85-35t-35-85q0-50 35-85t85-35q23 0 44 8.5t38 23.5l282-164q-2-6-3-13.5t-1-14.5q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35q-23 0-44-8.5T638-672L356-508q2 6 3 13.5t1 14.5q0 7-1 14.5t-3 13.5l282 164q17-15 38-23.5t44-8.5q50 0 85 35t35 85q0 50-35 85t-85 35Z"/></svg>
  <span class="lbl">{copied ? '¡Enlace copiado!' : 'Compartir mi escenario'}</span>
</button>

<style>
  .share { display: inline-flex; align-items: center; gap: 7px; font-family: var(--font-ui); font-weight: 400; font-size: 14px; cursor: pointer; border: 0; border-radius: 999px; background: var(--ink); color: var(--bg); padding: 7px 16px; white-space: nowrap; }
  .share:hover { opacity: 0.85; }
  @media (max-width: 560px) { .lbl { display: none; } .share { padding: 8px; } }
</style>
