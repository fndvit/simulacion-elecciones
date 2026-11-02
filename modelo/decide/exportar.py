"""Join cuestionario.py with the Manifesto Project corpus →
  datos/decide/cuestionario.json  (for the app)
  datos/decide/revision.md        (every assignment with its quote, for human review)
  datos/decide/coherencia.md      (MARPOR direction check + automatic 'contra' positions)
python3 modelo/decide/exportar.py

Levels per party and answer: 'p' prioridad, 't' también (hand-picked), 'c' en contra
(hand-picked in cuestionario.py, or automatic from MARPOR direction — origen='auto').
"""
import csv, json, os, re, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from cuestionario import Q, TEMAS
from direccion import DIR, OPUESTAS, MIN_CONTRA, RATIO, SOLO_COMPROBAR

BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'datos')
CFG = json.load(open(os.path.join(os.path.dirname(__file__), 'programas.json'), encoding='utf-8'))
LVL = {'p': 'prioridad', 't': 'también', 'c': 'en contra'}

rows, by_tema, CON = {}, collections.defaultdict(list), set()   # (party, tema) -> sentences
for r in csv.DictReader(open(os.path.join(BASE, 'decide', 'frases.csv'), encoding='utf-8')):
    r['i'] = int(r['i']); rows[(r['party'], r['i'])] = r
    CON.add(r['party'])
    for t in filter(None, r['temas'].split('|')):
        by_tema[(r['party'], t)].append(r)

def ctx(party, i, before=1, after=1):
    """Quote = the sentence plus neighbours from the same section (quasi-sentences are often fragments)."""
    sec = rows[(party, i)]['seccion']
    return ' '.join(rows[(party, j)]['text'] for j in range(i - before, i + after + 1)
                    if (party, j) in rows and rows[(party, j)]['seccion'] == sec)

def cite(party, i):
    r = rows[(party, i)]
    return dict(i=i, texto=r['text'], contexto=ctx(party, i), seccion=r['seccion'], codigo=r['code'], pagina=r.get('page') or None)

errors, data = [], []
md = ['# Revisión del cuestionario — cada asignación con su cita\n']
coh = ['# Coherencia con la dirección del Manifesto Project\n',
       f'\nSolo respuestas con un par de códigos MARPOR a favor/en contra (ver `modelo/decide/direccion.py`). '
       f'Se cuentan las frases del partido dentro del tema de la pregunta. «En contra» automático: el partido no está '
       f'asignado a la respuesta, tiene ≥ {MIN_CONTRA} frases en contra y al menos {RATIO} veces más en contra que a favor.\n']
n_auto = n_flag = n_opp = 0
for q in Q:
    md.append(f"\n## {q['id']} · {TEMAS[q['tema']]}\n\n**{q['q']}**\n")
    qo = dict(id=q['id'], tema=q['tema'], q=q['q'], opts=[])
    for o in q['opts']:
        md.append(f"\n### {o['t']}\n")
        oo = dict(k=o['k'], t=o['t'], partidos=[])
        for party, (lvl, ids) in o['p'].items():
            cites = []
            for i in ids:
                if (party, i) not in rows:
                    errors.append(f"{q['id']}/{o['k']}/{party}: no existe la frase {i}"); continue
                c = cite(party, i); cites.append(c)
                md.append(f"- **{party}** ({LVL[lvl]}) · {i} · [{c['codigo']}] _{c['seccion'][:80]}_\n  > {c['texto']}\n")
            oo['partidos'].append(dict(partido=party, nivel=lvl, origen='manual', citas=cites))

        qo['opts'].append(oo)
    # --- 1. opposite answers: 'p' on one -> 'c' on the other, same quotes
    opts = {oo['k']: oo for oo in qo['opts']}
    for qid, a, b in OPUESTAS:
        if qid != q['id']: continue
        for src, dst in ((a, b), (b, a)):
            have = {x['partido'] for x in opts[dst]['partidos']}
            for x in list(opts[src]['partidos']):
                if x['nivel'] == 'p' and x['origen'] == 'manual' and x['partido'] not in have:
                    opts[dst]['partidos'].append(dict(partido=x['partido'], nivel='c', origen='opuesta', desde=src, citas=x['citas']))
                    n_opp += 1
    # --- 2. Manifesto Project direction
    for o in q['opts']:
        oo = opts[o['k']]
        d = DIR.get((q['id'], o['k']))
        if not d: continue
        pro_c, con_c, rx = d; rx = re.compile(rx, re.I)
        coh.append(f"\n## {q['id']} · {o['t']}\n\nA favor: {', '.join(sorted(pro_c))} · en contra: {', '.join(sorted(con_c))}\n\n")
        have = {x['partido']: x for x in oo['partidos']}
        for party in sorted(CON):
            sent = by_tema[(party, q['tema'])]
            pro = [r for r in sent if r['code'] in pro_c]
            con = [r for r in sent if r['code'] in con_c]
            x = have.get(party)
            if x and x['origen'] == 'manual':
                lvl, ids = o['p'][party]
                bad = [i for i in ids if (party, i) in rows and rows[(party, i)]['code'] in con_c]
                if lvl in 'pt' and bad:
                    n_flag += 1; coh.append(f"- ⚠ **{party}** ({LVL[lvl]}): cita codificada en contra → {bad}\n")
                if lvl in 'pt' and len(con) >= MIN_CONTRA and len(con) > len(pro):
                    n_flag += 1; coh.append(f"- ⚠ **{party}** ({LVL[lvl]}): en el tema tiene más frases en contra ({len(con)}) que a favor ({len(pro)})\n")
            elif x:   # already 'c' from the opposite answer: report agreement with MARPOR
                coh.append(f"- {party} en contra (respuesta opuesta); MARPOR en el tema: {len(con)} en contra / {len(pro)} a favor\n")
            elif (q['id'], o['k']) not in SOLO_COMPROBAR and len(con) >= MIN_CONTRA and len(con) >= RATIO * len(pro):
                topical = [r for r in con if rx.search(r['text']) or rx.search(r['text_en'] or '')]
                if not topical:
                    coh.append(f"- ({party}: {len(con)} en contra / {len(pro)} a favor, pero ninguna frase trata del asunto → no se marca)\n")
                    continue
                n_auto += 1
                picks = sorted(topical, key=lambda r: -len(r['text']))[:2]
                oo['partidos'].append(dict(partido=party, nivel='c', origen='auto',
                                           citas=[cite(party, r['i']) for r in picks],
                                           frases_a_favor=len(pro), frases_en_contra=len(con)))
                coh.append(f"- **{party}** en contra (auto; {len(con)} en contra / {len(pro)} a favor)\n"
                           + ''.join(f"  > [{r['code']}] {r['text'][:220]}\n" for r in picks))
    data.append(qo)

json.dump(dict(
    version='borrador-3', fecha='2026-11-01', edicion=CFG['edicion'],
    origenes={'manual': 'elegida a mano', 'opuesta': 'prioridad del partido en la respuesta contraria', 'auto': 'dirección de la codificación del Manifesto Project'},
    fuente='Programas electorales divididos en frases y clasificados según el método del Manifesto Project',
    niveles=LVL, fuentes_partido={k: v['fuente'] for k, v in CFG['partidos'].items()},
    partidos=[k for k in CFG['partidos'] if k in CON], sin_programa=[k for k in CFG['partidos'] if k not in CON],
    temas=TEMAS, preguntas=data), open(os.path.join(BASE, 'decide', 'cuestionario.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(BASE, 'decide', 'revision.md'), 'w', encoding='utf-8').write(''.join(md))
open(os.path.join(BASE, 'decide', 'coherencia.md'), 'w', encoding='utf-8').write(''.join(coh))

cov = {p: 0 for p in sorted(CON)}
for q in data:
    for p in sorted(CON):
        if any(p == x['partido'] for o in q['opts'] for x in o['partidos']): cov[p] += 1
print('preguntas:', len(Q), '| opciones:', sum(len(q['opts']) for q in Q), '| en contra por respuesta opuesta:', n_opp, '| en contra automáticos (MARPOR):', n_auto, '| avisos:', n_flag)
print('cobertura por partido (con «en contra»):', cov)
print('errores:', len(errors)); [print(' ', e) for e in errors]
