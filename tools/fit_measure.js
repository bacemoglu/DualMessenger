// Measures how wide each headline line really is (in em) for the languages that size their headline with --fit.
const { chromium } = require('playwright');
(async () => {
  const base = process.argv[2]; const slugs = JSON.parse(process.argv[3]);
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  for (const w of [390, 1280]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 800 } }); const p = await ctx.newPage();
    for (const s of slugs) {
      await p.goto(base + s + '/', { waitUntil: 'load' });
      const r = await p.evaluate(async () => {
        await document.fonts.ready;
        const h1 = document.querySelector('.hero h1'); const cs = getComputedStyle(h1); const fs = parseFloat(cs.fontSize);
        const parts = h1.innerHTML.split(/<br\s*\/?>/i);
        const widths = parts.map(t => { const sp = document.createElement('span'); sp.style.cssText = 'white-space:nowrap;position:absolute;visibility:hidden;font:' + cs.font + ';letter-spacing:' + cs.letterSpacing; sp.innerHTML = t; h1.appendChild(sp); const x = sp.getBoundingClientRect().width; sp.remove(); return x; });
        return { fs, box: h1.getBoundingClientRect().width, em: widths.map(x => +(x / fs).toFixed(2)), fit: h1.style.getPropertyValue('--fit'), lines: Math.round(h1.getBoundingClientRect().height / parseFloat(cs.lineHeight)), family: cs.fontFamily.split(',')[0] };
      });
      console.log(String(w).padStart(5), s.padEnd(3), JSON.stringify(r));
    }
    await ctx.close();
  }
  await b.close();
})();
