# Decide: de los programas al cuestionario

## Cuando lleguen los programas del 29N

1. Guardar cada PDF en `datos/programas/pdf/` con el nombre que indica `programas.json` (`PP.pdf`, `PSOE.pdf`, …).
2. En `programas.json`, cambiar `"edicion"` a `"202611"`.
3. `pip install scikit-learn pdfplumber joblib` (una vez).
4. `python3 modelo/decide/codificador.py` — entrena el codificador con el corpus del Manifesto Project que hay en
   `datos/programas/` (unos minutos; guarda `datos/decide/codificador.joblib`).
5. `python3 modelo/decide/pdf_a_corpus.py --todos` — cada PDF → `datos/programas/<PARTIDO>_202611.csv`, con el formato
   del Manifesto Project (text, text_en, cmp_code, eu_code) más `page` y `conf`.
6. `python3 modelo/decide/extraer.py` → `datos/decide/frases.csv`.
7. Rehacer las asignaciones de `cuestionario.py` con los nuevos números de frase: `buscar.py 'regex' [partidos]` y
   `evidencia.py` proponen candidatas; cada asignación se elige y comprueba a mano.
8. `python3 modelo/decide/exportar.py` (genera `cuestionario.json`, `revision.md`, `coherencia.md`) y
   `cd app && node scripts/copy-data.js`.

Si un partido no tiene PDF ni corpus para la edición, la página lo muestra como «Todavía no ha publicado su programa».

## Calidad de la cadena (programas de 2023, comparados con la versión del Manifesto Project)

- Codificador, validación dejando fuera un programa cada vez (`codificador.py --evaluar`): categoría exacta 56 %,
  dominio 68 % (Vox, el más distinto: 35 %). Con probabilidad ≥ 0,5 (60–70 % de las frases) acierta un 70 %.
- PDF completo (`prueba_pdf.py`, codificador entrenado sin ese partido): PSOE recupera el 92 % de las frases del MP y
  coincide en la categoría en el 57 %; PP, 83 % y 50 %. El corte en cuasi-frases coincide en algo más de la mitad: el
  MP parte también las frases con varias propuestas unidas por «y».
- Los «en contra» automáticos (`direccion.py`) solo usan pares de categorías a favor / en contra y exigen una frase que
  trate del asunto; las citas del cuestionario siempre se eligen a mano.

Si se puede descargar el modelo del propio Manifesto Project (manifestoberta, xlm-roberta en HuggingFace) y torch,
conviene usarlo en lugar de `codificador.py`: está entrenado con todo el corpus internacional.
