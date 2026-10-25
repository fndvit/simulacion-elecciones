# Simulador del 29N (Congreso)

- `app/` — SvelteKit (Svelte 5), mismo sistema de diseño y componentes que la rama `advanced-scenarios` del Atlas electoral local.
  - `npm install`, luego `npm run dev` para desarrollar y `npm run build` para generar.
  - `npm run build` genera `app/build/index.html`, una sola página con JS y CSS en línea, con router por hash, que se abre directamente desde el disco. Copia esa página a `../index.html` y deja en `app/build/artifact.html` la versión para publicar como artefacto de claude.ai.
  - `src/lib/model.ts` — motor del escenario (ajuste proporcional, provincias, participación, D'Hondt con barrera del 3 %, transferencias desde 2023).
  - `src/lib/hex.ts` — cartograma de hexágonos (un escaño por hexágono; referencia: proyección o 2023).
- `datos/` — resultados de Interior (2019A, 2019N, 2023), encuestas (`polls.csv`), cartograma y datos de la app.
- `modelo/` — Python:
  - `fetch_polls.py` lee las encuestas de Wikipedia (`tests/` comprueba el lector con un HTML de muestra); `fetch_en.py` lee la tabla de la Wikipedia en inglés para la comprobación cruzada; `actualizar.py` valida, compara con la lista aprobada y prepara el pull request de revisión, y `comprobar.py` revisa los datos de la app antes de publicar.
  - `polls.py` hace la media de encuestas al estilo 538.
  - `projection.py` y `export.py` generan `datos/app_data.json`.
  - `hexmap.py` genera `datos/hex.json` y `voronoi.py`, `datos/vor.json` (mapa geográfico); solo hay que volver a ejecutarlos si cambia el reparto de escaños.

## Actualización diaria (GitHub Actions)

`.github/workflows/actualizar-encuestas.yml` se ejecuta cada día a las 07:17 UTC (08:17 en Madrid en invierno, 09:17 en verano) y también a mano con «Run workflow». **Ninguna encuesta llega a la web sin que una persona la apruebe.**

1. **Revisar** (trabajo `revisar`):
   - Tests de los dos lectores de Wikipedia.
   - `modelo/actualizar.py` descarga la tabla de la Wikipedia en español (tres intentos) y anota la **revisión exacta** (`revid`, fecha y enlace `oldid`), y la **valida**: al menos 50 encuestas, no pierde más del 10 %, la más reciente no retrocede, sin fechas futuras, PP y PSOE con valores razonables, ninguna encuesta que sume más del 115 %. Cada encuesta lleva el enlace a su fuente original (la nota al pie de Wikipedia).
   - La compara con la lista aprobada (`datos/polls.csv` en `main`) por empresa y fecha de fin de campo: nuevas, cambiadas y retiradas.
   - Cada encuesta nueva o cambiada se busca en la Wikipedia en inglés (misma empresa, ±1 día) y se comparan PP, PSOE y Vox: *coincide*, *difiere* o *no figura*. Es solo una comprobación: no entra en la media.
   - Si hay cambios, los sube a la rama `encuestas-pendientes` (con `datos/fuente.json` y la copia de respaldo) y abre o actualiza un **pull request** con la etiqueta `revision-encuestas` y una tabla con cada cambio, su fuente y la comprobación en inglés.
2. **Aprobar** (una persona): revisa el pull request —sobre todo las filas marcadas *difiere* o *no figura*— y, si está bien, lo **fusiona** (merge). Si algo no cuadra, puede corregir `datos/polls.csv` en la misma rama o cerrar el pull request. Mientras no se apruebe, cada mañana se actualiza el mismo pull request.
3. **Publicar** (trabajo `publicar`): siempre con la lista aprobada de `main`. Recalcula la media y la proyección para la fecha del día (`export.py`; las encuestas pierden peso con los días, así que se publica cada día aunque no haya encuestas nuevas), comprueba los datos (`comprobar.py`: 52 circunscripciones, 350 escaños, media que suma ~100 %), compila y hace commit. Al fusionar un pull request de encuestas, el push a `main` lanza este trabajo al momento. **Vercel** publica cada commit de `main` según `vercel.json`.

La tabla de Wikipedia se publica con licencia **CC BY-SA 4.0**; `datos/polls.csv` es una obra derivada con la misma licencia, y la metodología lo indica con la atribución y el enlace a la revisión usada.

**Si algo falla, nunca se publica nada a medias:**

- Wikipedia caída, cambio de formato o datos raros → no se propone nada; la web sigue con la lista aprobada.
- Si no se puede leer la Wikipedia en inglés, el pull request lo dice y la revisión se hace sin esa comprobación.
- Falla el cálculo, la comprobación o la compilación → no hay commit, así que Vercel no despliega nada nuevo; la página sigue siendo la del último día correcto.
- En ambos casos se abre un issue con la etiqueta `fallo-datos` (o se comenta el que ya esté abierto), y GitHub te avisa. Cuando vuelve a funcionar, el issue se cierra solo.
- Para volver atrás a mano: copia el fichero que quieras de `datos/respaldo/` sobre `datos/polls.csv` en `main` (eso relanza la publicación), o usa el historial de git.

**Configuración (una vez):**

- **Settings → Actions → General → Workflow permissions:** «Read and write permissions» y marcar **«Allow GitHub Actions to create and approve pull requests»**. Con GitHub CLI: `gh api -X PUT repos/fndvit/simulacion-elecciones/actions/permissions/workflow -f default_workflow_permissions=write -F can_approve_pull_request_reviews=true`.
- Opcional: variable de repositorio `REVISOR` (Settings → Secrets and variables → Actions → Variables) con el usuario de GitHub de quien aprueba; se le asigna el pull request y se le pide revisión. Con GitHub CLI: `gh variable set REVISOR --body <usuario>`.
- Nota: los pull requests que abre el propio workflow no lanzan otros workflows (es una regla de GitHub); por eso la publicación se dispara con el push a `main` al fusionar.

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

A mano: `pip install -r modelo/requirements.txt && REVISION_MD=/tmp/revision.md python3 modelo/actualizar.py && python3 modelo/export.py && python3 modelo/comprobar.py && cd app && npm run data && npm run build`.
