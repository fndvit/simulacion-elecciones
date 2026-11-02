// Copies the model outputs from ../datos into the app (run after `python3 modelo/export.py` / `modelo/hexmap.py`,
// and after `python3 modelo/decide/exportar.py` + `modelo/decide/cis_temas.py` for the questionnaire).
import fs from 'node:fs';
for (const f of ['app_data.json', 'hex.json', 'vor.json']) fs.copyFileSync(`../datos/${f}`, `src/lib/data/${f}`);
// Decide: questionnaire + CIS shares per topic, in one file; quotes keep only what the page shows
if (fs.existsSync('../datos/decide/cuestionario.json')) {
  const q = JSON.parse(fs.readFileSync('../datos/decide/cuestionario.json', 'utf8'));
  const cis = JSON.parse(fs.readFileSync('../datos/decide/cis_temas.json', 'utf8'));
  for (const p of q.preguntas) for (const o of p.opts) for (const x of o.partidos)
    x.citas = x.citas.map((c) => ({ i: c.i, t: c.texto, x: c.contexto, s: c.seccion, ...(c.pagina ? { p: c.pagina } : {}) }));
  q.cis = { estudio: cis.estudio, n: cis.n, temas: Object.fromEntries(Object.entries(cis.temas).map(([k, v]) => [k, { es: v.espana, pe: v.personal }])) };
  fs.writeFileSync('src/lib/data/decide.json', JSON.stringify(q));
}
console.log('datos copiados');
