const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const base = process.argv[2];            // e.g. http://127.0.0.1:8765/
  const outDir = process.argv[3];
  const jobs = JSON.parse(process.argv[4]); // [{name, path, w, h, full}]
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  for (const j of jobs) {
    const ctx = await b.newContext({ viewport: { width: j.w, height: j.h || 900 }, deviceScaleFactor: j.dpr || 1, isMobile: !!j.mobile, hasTouch: !!j.mobile });
    const p = await ctx.newPage();
    const bad = [];
    p.on('response', r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); });
    p.on('console', m => { if (m.type() === 'error') bad.push('console: ' + m.text()); });
    await p.goto(base + j.path, { waitUntil: 'networkidle' });
    await p.evaluate(async () => { await document.fonts.ready; const imgs = Array.from(document.images); imgs.forEach(i => { i.loading = 'eager'; }); await Promise.all(imgs.map(i => i.decode().catch(() => {}))); });
    await p.waitForTimeout(400);
    const info = await p.evaluate(() => ({
      fonts: Array.from(document.fonts).map(f => f.family + ' ' + f.weight + ' ' + f.status),
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
      h: document.documentElement.scrollHeight,
      imgs: Array.from(document.images).filter(i => !i.complete || i.naturalWidth === 0).map(i => i.src),
    }));
    await p.screenshot({ path: `${outDir}/${j.name}.png`, fullPage: j.full !== false });
    console.log(j.name, JSON.stringify(info), bad.length ? 'PROBLEMS ' + JSON.stringify(bad) : '');
    await ctx.close();
  }
  await b.close();
})();
