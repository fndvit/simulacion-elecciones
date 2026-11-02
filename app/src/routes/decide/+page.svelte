<script lang="ts">
  // Decide: a questionnaire that sends each person to the parts of the manifestos that matter to them.
  // · pick the problems that worry you (the CIS barometer's list, in the order the CIS finds them)
  // · for each question, the answers that convince you (several allowed) → who proposes each one, who opposes it,
  //   who prefers another, who says nothing, with the manifestos' own words
  // · a plain count per party over all the answers chosen: proposes, prefers another, against, says nothing.
  //   No percentage, no compass.
  // Data: datos/decide/cuestionario.json (modelo/decide/exportar.py), copied by scripts/copy-data.js.
  import { onMount } from 'svelte';
  import { slide } from 'svelte/transition';
  import PageHead from '$lib/components/PageHead.svelte';
  import { PARTY } from '$lib/parties';
  import { href } from '$lib/nav';
  import DECIDE from '$lib/data/decide.json';

  type Cita = { i: number; t: string; x: string; s: string; p?: number | string | null };
  type Pos = { partido: string; nivel: 'p' | 't' | 'c'; origen: 'manual' | 'opuesta' | 'auto'; citas: Cita[]; frases_a_favor?: number; frases_en_contra?: number; desde?: string };
  type Opt = { k: string; t: string; partidos: Pos[] };
  type Q = { id: string; tema: string; q: string; opts: Opt[] };
  const D = DECIDE as unknown as {
    temas: Record<string, string>; preguntas: Q[]; partidos: string[]; sin_programa: string[];
    cis: { estudio: string; n: number; temas: Record<string, { es: number; pe: number }> }; fuentes_partido: Record<string, string>;
  };

  const PARTIES = D.partidos;
  const pname = (k: string) => PARTY[k as keyof typeof PARTY]?.n ?? k;
  const pcol = (k: string) => PARTY[k as keyof typeof PARTY]?.c ?? '#b9b3aa';
  const pct = (x: number) => String(Math.round(x)).replace('.', ',');

  // topics in the order of the CIS (mean of «problem of Spain» and «affects me»)
  const cisOf = (t: string) => D.cis.temas[t] ?? { es: 0, pe: 0 };
  const TOPICS = Object.keys(D.temas).sort((a, b) => cisOf(b).es + cisOf(b).pe - (cisOf(a).es + cisOf(a).pe));
  const nQ = (t: string) => D.preguntas.filter((q) => q.tema === t).length;

  // ── state (kept in this browser only) ───────────────────────────────────
  let picked = $state<string[]>([]);
  let answers = $state<Record<string, string[]>>({}); // question id → chosen answer keys; ['-'] = none convinces
  let open = $state<Record<string, string>>({});      // 'question:answer' → party whose quotes are open
  let openParty = $state<string | null>(null);        // party opened in the results
  let started = $state(false);
  let ready = false;
  onMount(() => {
    try {
      const s = JSON.parse(localStorage.getItem('decide29n') || 'null');
      if (s) {
        const qs = new Set(D.preguntas.map((q) => q.id));
        picked = (s.picked ?? []).filter((t: string) => t in D.temas);
        // older saves kept one answer per question as a string
        answers = Object.fromEntries(Object.entries(s.answers ?? {}).filter(([k, v]) => qs.has(k) && v).map(([k, v]) => [k, Array.isArray(v) ? v : [v as string]]));
        started = !!s.started;
      }
    } catch {}
    ready = true;
  });
  $effect(() => {
    const snap = JSON.stringify({ picked, answers, started });
    if (!ready) return;
    try { localStorage.setItem('decide29n', snap); } catch {}
  });

  const toggle = (t: string) => (picked = picked.includes(t) ? picked.filter((x) => x !== t) : [...picked, t]);
  const questions = $derived(TOPICS.filter((t) => picked.includes(t)).flatMap((t) => D.preguntas.filter((q) => q.tema === t)));
  const chosen = (q: Q) => (answers[q.id] ?? []).filter((k) => k !== '-');

  function start() {
    started = true;
    requestAnimationFrame(() => document.getElementById('preguntas')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  }
  function choose(q: Q, k: string) {
    const cur = answers[q.id] ?? [];
    let next: string[];
    if (k === '-') next = cur.includes('-') ? [] : ['-'];
    else next = cur.includes(k) ? cur.filter((x) => x !== k) : [...cur.filter((x) => x !== '-'), k];
    answers = { ...answers, [q.id]: next };
  }
  function reset() { picked = []; answers = {}; started = false; open = {}; openParty = null; scrollTo({ top: 0, behavior: 'smooth' }); }

  // ── what each party says about one answer ────────────────────────────────
  type Verdict = 'si' | 'otra' | 'contra' | 'nada';
  function verdict(q: Q, k: string, party: string): { v: Verdict; pos?: Pos; other?: Opt } {
    const o = q.opts.find((x) => x.k === k);
    const pos = o?.partidos.find((x) => x.partido === party);
    if (pos) return { v: pos.nivel === 'c' ? 'contra' : 'si', pos };
    const other = q.opts.find((x) => x.k !== k && x.partidos.some((y) => y.partido === party && y.nivel !== 'c'));
    if (other) return { v: 'otra', pos: other.partidos.find((y) => y.partido === party), other };
    return { v: 'nada' };
  }
  function grouped(q: Q, k: string) {
    const g: Record<Verdict, { party: string; pos?: Pos }[]> = { si: [], contra: [], otra: [], nada: [] };
    for (const p of PARTIES) { const r = verdict(q, k, p); g[r.v].push({ party: p, pos: r.pos }); }
    g.si.sort((a, b) => (a.pos?.nivel === 'p' ? 0 : 1) - (b.pos?.nivel === 'p' ? 0 : 1));
    return g;
  }

  // ── tally over every answer chosen ─────────────────────────────────────────
  const picks = $derived(questions.flatMap((q) => chosen(q).map((k) => ({ q, k, o: q.opts.find((o) => o.k === k)! }))));
  const tally = $derived.by(() =>
    PARTIES.map((p) => {
      const t = { party: p, si: 0, prio: 0, otra: 0, contra: 0, nada: 0, items: [] as { q: Q; k: string; o: Opt; v: Verdict }[] };
      for (const x of picks) {
        const r = verdict(x.q, x.k, p);
        t[r.v]++; if (r.v === 'si' && r.pos?.nivel === 'p') t.prio++;
        t.items.push({ ...x, v: r.v });
      }
      return t;
    }).sort((a, b) => b.si - a.si || a.contra - b.contra || b.prio - a.prio)
  );

  const LVL: Record<string, string> = { p: 'Lo propone como prioridad', t: 'También lo recoge', c: 'Está en contra' };
  const VLAB: Record<Verdict, string> = { si: 'Lo propone', otra: 'Prefiere otra', contra: 'En contra', nada: 'No dice nada' };
  const GROUPS: [Verdict, string][] = [['si', 'Lo proponen'], ['contra', 'En contra'], ['otra', 'Prefieren otra']];
  // the quote's own sentence in bold inside its context
  function mark(c: Cita) {
    const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const i = c.x.indexOf(c.t);
    return i < 0 ? `<b>${esc(c.t)}</b>` : esc(c.x.slice(0, i)) + `<b>${esc(c.t)}</b>` + esc(c.x.slice(i + c.t.length));
  }
  function why(q: Q, pos: Pos) {
    if (pos.origen === 'opuesta') {
      const o = q.opts.find((x) => x.k === pos.desde);
      return o ? `Su prioridad es la contraria: «${o.t}».` : '';
    }
    if (pos.origen === 'auto') return `Según la clasificación del Manifesto Project, en este tema su programa tiene ${pos.frases_en_contra} frases en contra y ${pos.frases_a_favor} a favor.`;
    return '';
  }
  const slot = (q: Q, k: string) => `${q.id}:${k}`;
  const nada = (g: ReturnType<typeof grouped>) => [...g.nada.map((e) => pname(e.party)), ...D.sin_programa.map(pname)];
</script>

<svelte:head><title>Decide · TresCincuenta.es</title></svelte:head>

<PageHead kicker="Decide" title="¿Qué ofrece <strong>cada partido</strong> para lo que te preocupa?"
  lede="Elige los problemas que más te importan y quédate con las soluciones que te convencen. Te enseñamos <strong>qué dice cada programa</strong> sobre ellas, con sus propias palabras." />

<div class="page">
  <!-- topics -->
  <section class="sec">
    <h2 class="hd w">¿Qué <strong>te preocupa</strong>?</h2>
    <p class="lede w">Estos son los problemas que la gente menciona en el barómetro del CIS, ordenados de más a menos citados. La barra indica qué parte de los entrevistados lo nombra entre los tres principales problemas de España; los interrogantes, cuántas preguntas tenemos sobre cada uno. <span class="on-mouse">Clica</span><span class="on-touch">Toca</span> todos los que quieras.</p>
    <div class="topics w9">
      {#each TOPICS as t}
        <button type="button" class="topic" class:on={picked.includes(t)} aria-pressed={picked.includes(t)} onclick={() => toggle(t)}>
          <span class="tn">{D.temas[t]}</span>
          <span class="tmeta">
            <span class="tbar" aria-hidden="true"><span style:width={cisOf(t).es + '%'}></span></span>
            <span class="tpct">{pct(cisOf(t).es)} %</span>
            <span class="tq" aria-label={`${nQ(t)} ${nQ(t) === 1 ? 'pregunta' : 'preguntas'}`}>{'?'.repeat(nQ(t))}</span>
          </span>
        </button>
      {/each}
    </div>
    <div class="w row">
      <button type="button" class="pill" disabled={!picked.length} onclick={start}>{started ? 'Ir a las preguntas' : 'Empezar'}{picked.length ? ` · ${questions.length} preguntas` : ''}</button>
      {#if picked.length < TOPICS.length}<button type="button" class="pill ghost" onclick={() => (picked = [...TOPICS])}>Todos los temas</button>{/if}
      {#if picked.length || picks.length}<button type="button" class="pill ghost" onclick={reset}>Borrar mis respuestas</button>{/if}
    </div>
    <p class="note w">{D.cis.estudio}, {D.cis.n.toLocaleString('es-ES')} entrevistas.</p>
  </section>

  <!-- questions -->
  {#if started && questions.length}
    <section class="sec" id="preguntas">
      <h2 class="hd w">¿Qué soluciones <strong>te convencen</strong>?</h2>
      <p class="lede w">Puedes elegir más de una respuesta en cada pregunta. Debajo de cada una verás qué partidos la proponen en su programa, cuáles están en contra y cuáles prefieren otra.</p>
    </section>
    {#each questions as q, qi (q.id)}
      {@const sel = answers[q.id] ?? []}
      <section class="sec qcard" id={'q-' + q.id}>
        <div class="c7w qhead">
          <span class="qtema">{D.temas[q.tema]} · {qi + 1} de {questions.length}</span>
          <h3 class="qq">{q.q}</h3>
        </div>
        <div class="c7w opts" role="group" aria-label={q.q}>
          {#each q.opts as o}
            <button type="button" role="checkbox" aria-checked={sel.includes(o.k)} class="opt" class:on={sel.includes(o.k)} onclick={() => choose(q, o.k)}>
              <span class="box" aria-hidden="true"></span>{o.t}
            </button>
          {/each}
          <button type="button" role="checkbox" aria-checked={sel.includes('-')} class="opt none" class:on={sel.includes('-')} onclick={() => choose(q, '-')}>
            <span class="box" aria-hidden="true"></span>Ninguna me convence
          </button>
        </div>

        {#each chosen(q) as k (k)}
          {@const g = grouped(q, k)}
          {@const o = q.opts.find((x) => x.k === k)!}
          <div class="c7w who" transition:slide={{ duration: 220 }}>
            {#if chosen(q).length > 1}<p class="whoh">«{o.t}»</p>{/if}
            {#each GROUPS as [v, lab]}
              {#if g[v].length}
                <div class="grp">
                  <div class="glab">{lab}</div>
                  <div class="chips">
                    {#each g[v] as e}
                      <button type="button" class="pchip {v}" class:prio={e.pos?.nivel === 'p' && v === 'si'} class:open={open[slot(q, k)] === e.party}
                        aria-expanded={open[slot(q, k)] === e.party} onclick={() => (open = { ...open, [slot(q, k)]: open[slot(q, k)] === e.party ? '' : e.party })}>
                        <i style:background={pcol(e.party)}></i>{pname(e.party)}
                      </button>
                    {/each}
                  </div>
                </div>
              {/if}
            {/each}
            {#if nada(g).length}<p class="silent">No dicen nada: {nada(g).join(', ')}.</p>{/if}

            {#if open[slot(q, k)]}
              {@const party = open[slot(q, k)]}
              {@const r = verdict(q, k, party)}
              {#if r.pos}
                <div class="quotes" transition:slide={{ duration: 200 }}>
                  <div class="qh"><i style:background={pcol(party)}></i><strong>{pname(party)}</strong> · {r.v === 'otra' ? `Prefiere «${r.other?.t}»` : LVL[r.pos.nivel]}</div>
                  {#if why(q, r.pos)}<p class="why">{why(q, r.pos)}</p>{/if}
                  {#each r.pos.citas as c}
                    <blockquote>
                      <p>{@html mark(c)}</p>
                      <footer class="note">{D.fuentes_partido[party] ?? 'Programa electoral'}{c.p ? `, p. ${c.p}` : ''}{c.s ? ` · ${c.s}` : ''}</footer>
                    </blockquote>
                  {/each}
                </div>
              {/if}
            {/if}
          </div>
        {/each}
      </section>
    {/each}

    <!-- results -->
    <section class="sec" id="resultado">
      <h2 class="hd w">Con quién <strong>coincides</strong></h2>
      {#if picks.length}
        <p class="lede w">De las {picks.length} {picks.length === 1 ? 'respuesta que has elegido' : 'respuestas que has elegido'}, cuántas propone cada programa, en cuántas prefiere otra solución, en cuántas está en contra y sobre cuántas no dice nada. No es una recomendación de voto: <span class="on-mouse">clica</span><span class="on-touch">toca</span> un partido para ver el detalle.</p>
        <div class="w9 tally">
          {#each tally as t (t.party)}
            <button type="button" class="trow" class:open={openParty === t.party} aria-expanded={openParty === t.party} onclick={() => (openParty = openParty === t.party ? null : t.party)}>
              <span class="tname"><i style:background={pcol(t.party)}></i>{pname(t.party)}</span>
              <span class="rbar" aria-hidden="true">
                {#each ['si', 'otra', 'contra', 'nada'] as v}<span class="seg {v}" style:flex-grow={t[v as Verdict]}></span>{/each}
              </span>
              <span class="tnum"><b>{t.si}</b> propone{#if t.contra}{' · '}<span class="down">{t.contra} en contra</span>{/if}{#if t.otra}{` · ${t.otra} otra`}{/if}{#if t.nada}{` · ${t.nada} nada`}{/if}</span>
            </button>
            {#if openParty === t.party}
              <ul class="titems" transition:slide={{ duration: 200 }}>
                {#each t.items as it}
                  <li><span class="vt {it.v}">{VLAB[it.v]}</span>
                    <a href={'#q-' + it.q.id} onclick={(e) => { e.preventDefault(); open = { ...open, [slot(it.q, it.k)]: t.party }; document.getElementById('q-' + it.q.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }}>{it.o.t}</a></li>
                {/each}
              </ul>
            {/if}
          {/each}
          {#each D.sin_programa as p}
            <div class="trow static"><span class="tname"><i style:background={pcol(p)}></i>{pname(p)}</span><span class="silent">Todavía no ha publicado su programa.</span></div>
          {/each}
        </div>
        <div class="legend w9">
          <span><i class="seg si"></i>Lo propone</span><span><i class="seg otra"></i>Prefiere otra</span><span><i class="seg contra"></i>En contra</span><span><i class="seg nada"></i>No dice nada</span>
        </div>
      {:else}
        <p class="lede w">Elige al menos una respuesta para ver el recuento.</p>
      {/if}
    </section>
  {/if}

  <section class="sec method-notes">
    <h2 class="hd w">Cómo lo <strong>hemos hecho</strong></h2>
    <div class="w prose">
      <p>Las preguntas salen de los problemas que la gente cita en el barómetro del CIS. Para cada problema hemos recogido las soluciones que proponen los partidos y, para cada partido, la frase de su programa que lo dice. Todas las citas son literales.</p>
      <p>Los programas están divididos en frases y clasificados por tema y por sentido, a favor o en contra, con el método del <a href="https://manifesto-project.wzb.eu" target="_blank" rel="noopener">Manifesto Project</a> (Centro de Ciencias Sociales de Berlín, WZB). Un partido está «en contra» de una respuesta cuando su prioridad es la contraria o cuando esa clasificación muestra que su programa va claramente en la dirección opuesta en ese tema.</p>
      <p>No calculamos ninguna afinidad ideológica ni ordenamos a los partidos en un eje: solo contamos cuántas de tus respuestas propone cada programa. Tus respuestas se quedan en tu navegador.</p>
    </div>
  </section>
</div>

<style>
  .page { max-width: calc(1262px + 32px); margin: 0 auto; padding: 0 16px var(--s4); display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); column-gap: 10px; row-gap: var(--s3); }
  .sec > .w9 { grid-column: 2 / 11; }
  @media (max-width: 900px) { .sec > .w9 { grid-column: 1 / -1; } }

  /* topics */
  .topics { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 8px; }
  .topic { text-align: left; display: flex; flex-direction: column; justify-content: space-between; gap: 10px; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: var(--bg); cursor: pointer; font-family: var(--font-ui); color: var(--fg); transition: background 0.15s, border-color 0.15s; }
  .topic:hover { border-color: var(--muted); }
  .topic.on { background: var(--highlight); border-color: var(--ink); }
  .tn { font-size: 15px; font-weight: 700; line-height: 1.25; color: var(--ink); }
  .topic.on .tn, .topic.on .tpct, .topic.on .tq { color: var(--hl-ink); }
  .tmeta { display: flex; align-items: center; gap: 8px; }
  .tbar { flex: 0 0 64px; height: 8px; border-radius: 2px; background: var(--map-empty); overflow: hidden; box-shadow: inset 0 0 0 1px var(--line); }
  .tbar span { display: block; height: 100%; background: var(--ink); }
  .tpct { font-size: 13px; font-weight: 700; color: var(--fg); min-width: 34px; }
  .tq { margin-left: auto; font-family: var(--font-ui); font-size: 15px; font-weight: 700; letter-spacing: 1px; color: var(--ink); }
  .row { display: flex; flex-wrap: wrap; gap: 8px; }

  /* site buttons: ink pill */
  .pill { font-family: var(--font-ui); font-size: 14px; font-weight: 400; padding: 7px 16px; border-radius: 999px; border: 1px solid var(--ink); background: var(--ink); color: var(--bg); cursor: pointer; }
  .pill:hover { opacity: 0.85; }
  .pill:disabled { opacity: 0.35; cursor: default; }
  .pill.ghost { background: transparent; color: var(--ink); }

  /* questions: heading in the site's .hd style (light UI face) */
  .qcard { scroll-margin-top: calc(var(--nav-h) + 16px); }
  .qtema { font-family: var(--font-ui); font-size: 12px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); }
  .qq { font-family: var(--font-ui); font-size: 24px; line-height: 32px; font-weight: 200; color: var(--ink); margin-top: 4px; }
  .opts { display: flex; flex-direction: column; gap: 6px; }
  .opt { display: flex; align-items: flex-start; gap: 10px; text-align: left; font-family: var(--font-body); font-size: 16px; line-height: 1.5; font-weight: 300; padding: 10px 14px; border-radius: 10px; border: 1px solid var(--line); background: var(--bg); color: var(--fg); cursor: pointer; transition: background 0.15s, border-color 0.15s; }
  .opt:hover { border-color: var(--muted); }
  .opt.on { background: var(--highlight); border-color: var(--ink); color: var(--hl-ink); }
  .box { flex: none; width: 16px; height: 16px; margin-top: 4px; border-radius: 4px; border: 1.5px solid var(--muted); background: var(--bg); }
  .opt.on .box { border-color: var(--ink); background: var(--ink); box-shadow: inset 0 0 0 3px var(--highlight); }
  .opt.none { font-size: 15px; color: var(--muted); border-style: dashed; }

  .who { display: flex; flex-direction: column; gap: 10px; padding: 14px; border-radius: 12px; background: var(--panel); }
  .whoh { margin: 0; font-family: var(--font-body); font-size: 15px; color: var(--ink); }
  .grp { display: grid; grid-template-columns: 120px minmax(0, 1fr); align-items: start; gap: 6px 10px; }
  .glab { font-family: var(--font-ui); font-size: 12px; font-weight: 700; color: var(--fg); padding-top: 6px; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .pchip { display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-ui); font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 999px; border: 1px solid var(--line); background: var(--bg); color: var(--ink); cursor: pointer; }
  .pchip i, .tname i, .qh i { width: 10px; height: 10px; border-radius: 2px; display: inline-block; flex: none; }
  .pchip.si:not(.prio) { font-weight: 400; }
  .pchip.prio { border-color: var(--up); }
  .pchip.contra { border-color: var(--down); }
  .pchip.otra { font-weight: 400; color: var(--fg); }
  .pchip.open { box-shadow: 0 0 0 2px var(--ink); }
  .silent { margin: 0; font-family: var(--font-body); font-size: 15px; line-height: 1.6; color: var(--fg); }
  .quotes { display: flex; flex-direction: column; gap: 8px; border-top: 1px solid var(--line); padding-top: 10px; }
  .qh { display: flex; align-items: center; gap: 6px; font-family: var(--font-ui); font-size: 14px; color: var(--fg); }
  .why { margin: 0; font-family: var(--font-body); font-size: 15px; line-height: 1.6; color: var(--fg); }
  blockquote { margin: 0; padding: 4px 0 4px 14px; border-left: 3px solid var(--line); }
  blockquote p { margin: 0 0 4px; font-size: 15px; line-height: 1.6; color: var(--muted); }
  blockquote p :global(b) { color: var(--ink); font-weight: 400; background: color-mix(in srgb, var(--highlight) 60%, transparent); }

  /* tally */
  .tally { display: flex; flex-direction: column; }
  .trow { display: grid; grid-template-columns: 150px minmax(0, 1fr) 260px; align-items: center; gap: 12px; padding: 8px 0; border: 0; border-bottom: 1px solid var(--line); background: none; text-align: left; font-family: var(--font-ui); font-size: 14px; font-weight: 400; color: var(--fg); cursor: pointer; }
  .trow.static { cursor: default; grid-template-columns: 150px minmax(0, 1fr); }
  .trow:hover:not(.static) .tname { text-decoration: underline; text-underline-offset: 3px; }
  .tname { display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--ink); }
  .rbar { display: flex; height: 14px; border-radius: 3px; overflow: hidden; background: var(--map-empty); }
  .seg { flex: 0 0 0; min-width: 0; }
  .seg.si { background: var(--up); }
  .seg.otra { background: #c9b9a6; }
  .seg.contra { background: var(--down); }
  .seg.nada { background: var(--map-empty); }
  .tnum { font-size: 13px; font-weight: 400; color: var(--fg); }
  .tnum b { color: var(--ink); font-weight: 700; }
  .titems { list-style: none; margin: 0; padding: 8px 0 12px 162px; display: flex; flex-direction: column; gap: 6px; font-family: var(--font-ui); font-size: 13px; font-weight: 400; }
  .titems a { color: var(--ink); font-weight: 400; text-decoration: underline; text-decoration-color: var(--muted); text-underline-offset: 3px; }
  .titems a:hover { text-decoration-color: var(--ink); }
  .vt { display: inline-block; min-width: 110px; font-weight: 700; }
  .vt.si { color: var(--up); } .vt.contra { color: var(--down); } .vt.otra, .vt.nada { color: var(--fg); }
  .legend { display: flex; flex-wrap: wrap; gap: 16px; font-family: var(--font-ui); font-size: 13px; font-weight: 400; color: var(--fg); }
  .legend span { display: inline-flex; align-items: center; gap: 6px; }
  .legend .seg { display: inline-block; width: 12px; height: 12px; border-radius: 2px; flex: none; }
  .method-notes { margin-top: var(--s2); }
  .prose p { font-size: 16px; line-height: 1.72; margin: 0 0 12px; }

  @media (max-width: 700px) {
    .topics { grid-template-columns: 1fr 1fr; }
    .trow { grid-template-columns: 110px minmax(0, 1fr); }
    .tnum { grid-column: 1 / -1; }
    .titems { padding-left: 0; }
    .vt { min-width: 0; margin-right: 6px; }
    .grp { grid-template-columns: minmax(0, 1fr); }
    .glab { padding-top: 0; }
    .qq { font-size: 21px; line-height: 28px; }
  }
</style>
