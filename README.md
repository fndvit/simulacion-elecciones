# Simulador del 29N (Congreso)

- `app/` — SvelteKit (Svelte 5), mismo sistema de diseño y componentes que la rama `advanced-scenarios` del Atlas electoral local.
  - `npm install`, luego `npm run dev` para desarrollar y `npm run build` para generar.
  - `npm run build` genera `app/build/index.html`, una sola página con JS y CSS en línea, con router por hash, que se abre directamente desde el disco. Copia esa página a `../index.html` y deja en `app/build/artifact.html` la versión para publicar como artefacto de claude.ai.
  - `src/lib/model.ts` — motor del escenario (ajuste proporcional, provincias, participación, D'Hondt con barrera del 3 %, transferencias desde 2023).
  - `src/lib/hex.ts` — cartograma de hexágonos (un escaño por hexágono; referencia: proyección o 2023).
- `datos/` — resultados de Interior (2019A, 2019N, 2023), encuestas (`polls.csv`), cartograma y datos de la app.
- `modelo/` — Python:
  - `fetch_polls.py` lee las encuestas de Wikipedia (`tests/` comprueba el lector con un HTML de muestra); `actualizar.py` lo envuelve con validación y respaldo, y `comprobar.py` revisa los datos de la app antes de publicar.
  - `polls.py` hace la media de encuestas al estilo 538.
  - `projection.py` y `export.py` generan `datos/app_data.json`.
  - `hexmap.py` genera `datos/hex.json` y `voronoi.py`, `datos/vor.json` (mapa geográfico); solo hay que volver a ejecutarlos si cambia el reparto de escaños.

## Actualización diaria (GitHub Actions)

`.github/workflows/actualizar-encuestas.yml` se ejecuta cada día a las 07:17 UTC (08:17 en Madrid en invierno, 09:17 en verano) y también a mano con «Run workflow»:

1. Tests del lector de Wikipedia.
2. `modelo/actualizar.py` descarga las encuestas (tres intentos) y las **valida** contra el último fichero bueno: al menos 50 encuestas, no pierde más del 10 %, la más reciente no retrocede, sin fechas futuras, PP y PSOE con valores razonables, ninguna encuesta que sume más del 115 %.
3. Si son válidas: copia fechada del `polls.csv` anterior en `datos/respaldo/` (las 30 últimas), nuevo `polls.csv`, recálculo de la media y la proyección para la fecha del día (`export.py`), comprobación de cordura (`comprobar.py`: 52 circunscripciones, 350 escaños, media que suma ~100 %), compilación y commit. **Vercel** publica cada commit de `main` según `vercel.json` (instala y compila `app/`, sirve `app/build/`).

**Si algo falla, nunca se publica nada a medias:**

- Wikipedia caída, cambio de formato o datos raros → no se toca `datos/polls.csv` (el último bueno) ni la página publicada.
- Falla el cálculo, la comprobación o la compilación → no hay commit, así que Vercel no despliega nada nuevo; la página sigue siendo la del último día correcto. Si fallara la compilación en Vercel, Vercel mantiene el despliegue anterior.
- En ambos casos se abre un issue con la etiqueta `fallo-datos` (o se comenta el que ya esté abierto), y GitHub te avisa. Cuando vuelve a funcionar, el issue se cierra solo.
- Para volver atrás a mano: copia el fichero que quieras de `datos/respaldo/` sobre `datos/polls.csv` y lanza el workflow, o usa el historial de git.

Para reproducir un día concreto: `SIM_TODAY=2026-11-20 python3 modelo/export.py`.

## Crear el repositorio en GitHub

La carpeta ya es un repositorio git con un primer commit en `main`. Para subirlo:

1. En github.com → **New repository**, por ejemplo `fndvit/simulacion-elecciones`, **vacío** (sin README, licencia ni .gitignore).
2. En esta carpeta:
   ```
   git remote add origin https://github.com/fndvit/simulacion-elecciones.git
   git push -u origin main
   ```
   (con GitHub CLI basta `gh repo create fndvit/simulacion-elecciones --public --source . --push`)
3. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
4. **Settings → Actions → General → Workflow permissions: Read and write permissions.**
5. **Actions → Actualizar encuestas → Run workflow** para la primera publicación. La URL aparece en Settings → Pages (por ejemplo, `https://fndvit.github.io/simulacion-elecciones/`).

Nota: GitHub desactiva los workflows programados de un repositorio sin actividad durante 60 días. Como este hace un commit cada día que hay datos, no debería pasar; si pasa, se reactiva en la pestaña Actions.

A mano: `pip install -r modelo/requirements.txt && python3 modelo/actualizar.py && python3 modelo/export.py && python3 modelo/comprobar.py && cd app && npm run data && npm run build`.
