// Copies the model outputs from ../datos into the app (run after `python3 modelo/export.py` / `modelo/hexmap.py`).
import fs from 'node:fs';
for (const f of ['app_data.json', 'hex.json', 'vor.json']) fs.copyFileSync(`../datos/${f}`, `src/lib/data/${f}`);
console.log('datos copiados');
