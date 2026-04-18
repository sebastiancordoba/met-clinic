import puppeteer from 'puppeteer';
import { writeFileSync, unlinkSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const BASE = __dirname;

// PDF page size (landscape)
const PAGE_W = 1500;
const PAGE_H = 900;

// ── Step 1: capture each .mockup as a screenshot ──────────────────────────
const browser = await puppeteer.launch({
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
});

const page = await browser.newPage();
// Wide viewport so no horizontal scroll; height just needs to be reasonable
await page.setViewport({ width: PAGE_W, height: PAGE_H, deviceScaleFactor: 2 });

const fileUrl = `file://${BASE}/propuestas.html`;
await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 30000 });
await page.evaluate(() => document.fonts.ready);
await new Promise(r => setTimeout(r, 2000)); // let custom fonts paint

// Hide page-level nav and section headers so they don't overlap screenshots
await page.evaluate(() => {
  const nav = document.querySelector('nav');
  if (nav) nav.style.display = 'none';
  document.querySelectorAll('.section__title, .section__desc, .section-label, p.section-label').forEach(el => {
    el.style.visibility = 'hidden';
  });
});

// Grab label text and mockup element for every proposal
const count = await page.evaluate(() => document.querySelectorAll('.proposal').length);
console.log(`Found ${count} proposals — capturing mockups…`);

const images = [];

for (let i = 0; i < count; i++) {
  // Get proposal label text
  const label = await page.evaluate((idx) => {
    const el = document.querySelectorAll('.proposal')[idx];
    const strong = el.querySelector('strong');
    return strong ? strong.textContent.trim() : `Propuesta ${idx + 1}`;
  }, i);

  // Get the .mockup element handle and screenshot it in full (Puppeteer handles overflow)
  const mockupHandle = await page.evaluateHandle((idx) => {
    return document.querySelectorAll('.proposal')[idx].querySelector('.mockup');
  }, i);

  const img = await mockupHandle.screenshot({ type: 'png' });
  await mockupHandle.dispose();

  images.push({ img, label, index: i + 1 });
  console.log(`  [${i + 1}/${count}] ${label}`);
}

await browser.close();

// ── Step 2: assemble images into a PDF ────────────────────────────────────
console.log('\nAssembling PDF…');

const browser2 = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
const pdfPage = await browser2.newPage();

// Embed each screenshot as a base64 data URL
const pages = images.map(({ img, label, index }) => {
  const b64 = img.toString('base64');
  const src = `data:image/png;base64,${b64}`;
  return `
  <div class="pg">
    <div class="card">
      <img src="${src}" alt="${label}">
    </div>
    <div class="pg-label">${index} — ${label.replace('Propuesta ', '')}</div>
  </div>`;
}).join('\n');

const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  @page {
    size: ${PAGE_W}px ${PAGE_H}px;
    margin: 0;
  }

  html, body {
    width: ${PAGE_W}px;
    background: #ebebeb;
  }

  .pg {
    width: ${PAGE_W}px;
    height: ${PAGE_H}px;
    page-break-after: always;
    page-break-inside: avoid;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 14px;
    background: #ebebeb;
    padding: 32px 48px 24px;
    overflow: hidden;
  }

  .pg:last-child {
    page-break-after: avoid;
  }

  .card {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    min-height: 0;
  }

  .card img {
    max-width: ${PAGE_W - 96}px;
    max-height: ${PAGE_H - 96}px;
    object-fit: contain;
    border-radius: 8px;
    box-shadow: 0 8px 48px rgba(0,0,0,0.22);
    display: block;
  }

  .pg-label {
    font-family: -apple-system, 'Helvetica Neue', sans-serif;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #999;
    flex-shrink: 0;
  }
</style>
</head>
<body>
${pages}
</body>
</html>`;

// Write to temp file so we can use goto (avoids setContent timeout with large base64)
const tmpPath = join(BASE, '_pdf_tmp.html');
writeFileSync(tmpPath, html);

await pdfPage.setViewport({ width: PAGE_W, height: PAGE_H });
await pdfPage.goto(`file://${tmpPath}`, { waitUntil: 'load', timeout: 120000 });
await new Promise(r => setTimeout(r, 1000));

const pdfBuffer = await pdfPage.pdf({
  width: `${PAGE_W}px`,
  height: `${PAGE_H}px`,
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});

await browser2.close();

const outPath = join(BASE, 'propuestas_paletas_colores.pdf');
writeFileSync(outPath, pdfBuffer);
try { unlinkSync(tmpPath); } catch {}
console.log(`\n✓ PDF saved: ${outPath}`);
console.log(`  ${images.length} pages · ${(pdfBuffer.length / 1024 / 1024).toFixed(1)} MB`);
