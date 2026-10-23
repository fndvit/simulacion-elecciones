// After `vite build`: build/index.html is a full single-file page (open it directly).
// Also writes build/artifact.html — the same page without <!doctype>/<html>/<head>/<body>,
// the form a claude.ai Artifact expects — and copies index.html to the project root.
import fs from 'node:fs';
const html = fs.readFileSync('build/index.html', 'utf8');
const head = html.match(/<head>([\s\S]*?)<\/head>/)[1].replace(/<meta charset[^>]*>|<meta name="viewport"[^>]*>/g, '');
// the inlined JS contains an error-page template with its own <body>…</body>: take the first opening and LAST closing tag
const bStart = html.indexOf('>', html.indexOf('<body')) + 1;
const body = html.slice(bStart, html.lastIndexOf('</body>'));
fs.writeFileSync('build/artifact.html', head.trim() + '\n' + body.trim() + '\n');
if (fs.existsSync('../datos')) fs.copyFileSync('build/index.html', '../index.html');
console.log('build/index.html, build/artifact.html y ../index.html listos');
