#!/usr/bin/env node
// Navegador headless para pesquisa: abre uma página, executa interações em ordem e imprime o texto.
// Uso: node tools/browse.mjs <url> [ações...]
//   --click "<seletor>"      clica (seletor Playwright: css, text=..., role=button[name="..."])
//   --fill "<seletor>=valor" preenche campo        --press "<Tecla>"   ex.: Enter
//   --select "<seletor>=valor" escolhe opção de <select>
//   --wait <ms|seletor>      espera tempo ou elemento
//   --eval "<js>"            roda JS na página e imprime o resultado (JSON)
//   --grep "<regex>"         imprime só as linhas do texto que casam (com --ctx N linhas de contexto)
//   --max <n>                limite de caracteres do texto (padrão 6000; 0 = não imprime texto)
//   --shot <arquivo.png>     salva captura de tela     --html <arquivo>  salva o HTML final
import { createRequire } from 'node:module';
import { writeFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); }
catch { pw = require(require('node:child_process').execSync('npm root -g').toString().trim() + '/playwright'); }

const [url, ...args] = process.argv.slice(2);
if (!url) { console.error('uso: node tools/browse.mjs <url> [ações]'); process.exit(2); }
const browser = await pw.chromium.launch();
const ctx = await browser.newContext({
  locale: 'pt-BR', timezoneId: 'America/Sao_Paulo', viewport: { width: 1366, height: 900 },
  userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
});
const page = await ctx.newPage();
let max = 6000, grep = null, nctx = 0, code = 0;
try {
  const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  console.error(`[http ${resp?.status()}] ${page.url()}`);
  await page.waitForLoadState('networkidle', { timeout: 8000 }).catch(() => {});
  for (let i = 0; i < args.length; i++) {
    const a = args[i], v = args[i + 1];
    const kv = () => { const k = v.lastIndexOf('='); return [v.slice(0, k), v.slice(k + 1)]; };
    if (a === '--click') { await page.locator(v).first().click({ timeout: 15000 }); i++; }
    else if (a === '--fill') { const [s, x] = kv(); await page.locator(s).first().fill(x); i++; }
    else if (a === '--select') { const [s, x] = kv(); await page.locator(s).first().selectOption(x); i++; }
    else if (a === '--press') { await page.keyboard.press(v); i++; }
    else if (a === '--wait') { /^\d+$/.test(v) ? await page.waitForTimeout(+v) : await page.locator(v).first().waitFor({ timeout: 20000 }); i++; }
    else if (a === '--eval') { console.log(JSON.stringify(await page.evaluate(v), null, 1)); i++; }
    else if (a === '--shot') { await page.screenshot({ path: v, fullPage: false }); i++; }
    else if (a === '--html') { writeFileSync(v, await page.content()); i++; }
    else if (a === '--max') { max = +v; i++; }
    else if (a === '--grep') { grep = new RegExp(v, 'i'); i++; }
    else if (a === '--ctx') { nctx = +v; i++; }
    else { throw new Error('opção desconhecida: ' + a); }
    if (['--click', '--select', '--press'].includes(a)) await page.waitForLoadState('networkidle', { timeout: 6000 }).catch(() => {});
  }
  console.error(`[final] ${page.url()} | ${await page.title()}`);
  let text = (await page.locator('body').innerText()).replace(/\n\s*\n+/g, '\n');
  if (grep) {
    const L = text.split('\n'), keep = new Set();
    L.forEach((l, i) => { if (grep.test(l)) for (let j = i - nctx; j <= i + nctx; j++) keep.add(j); });
    text = [...keep].sort((a, b) => a - b).filter(i => L[i] !== undefined).map(i => L[i]).join('\n');
  }
  if (max) console.log(text.slice(0, max));
} catch (e) { console.error('ERRO: ' + e.message.split('\n')[0]); code = 1; }
await browser.close();
process.exit(code);
