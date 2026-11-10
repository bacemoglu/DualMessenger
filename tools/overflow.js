// Loads every page of dist/ at phone and desktop width and reports horizontal overflow, clipped text and failed requests.
const { chromium } = require('playwright');
(async () => {
  const base = process.argv[2]; const paths = JSON.parse(process.argv[3]);
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  let problems = 0;
  for (const [w, mobile] of [[360, true], [390, true], [1280, false]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: 800 }, isMobile: mobile, hasTouch: mobile });
    const p = await ctx.newPage();
    for (const path of paths) {
      const bad = [];
      const onResp = r => { if (r.status() >= 400) bad.push(r.status() + ' ' + r.url()); };
      p.on('response', onResp);
      await p.goto(base + path, { waitUntil: 'load' });
      const r = await p.evaluate(async () => {
        await document.fonts.ready;
        const de = document.documentElement; const out = [];
        if (de.scrollWidth > de.clientWidth + 1) out.push('page scrolls sideways: ' + de.scrollWidth + ' > ' + de.clientWidth);
        document.querySelectorAll('h1,h2,h3,p,a,dt,dd,li,span').forEach(e => {
          const r = e.getBoundingClientRect();
          if (r.width === 0 || e.closest('.skip') || e.closest('.nav-links')) return;
          if (r.right > de.clientWidth + 1 || r.left < -1) out.push('outside viewport: <' + e.tagName.toLowerCase() + '> ' + (e.textContent || '').trim().slice(0, 40));
        });
        const links = document.querySelector('.nav-links'); const cta = document.querySelector('.site-header .btn'); const brand = document.querySelector('.site-header .brand');
        const navRows = (getComputedStyle(links).display === 'contents' ? 'wide' : (links.scrollWidth > links.clientWidth + 1 ? 'scrolls' : 'fits')) + (Math.abs(cta.getBoundingClientRect().top - brand.getBoundingClientRect().top) > 20 ? ' BUTTON-WRAPPED' : '');
        const h1 = document.querySelector('h1'); const lh = parseFloat(getComputedStyle(h1).lineHeight);
        return { out: out.slice(0, 4), navRows: navRows, h1Lines: Math.round(h1.getBoundingClientRect().height / lh), h1Size: Math.round(parseFloat(getComputedStyle(h1).fontSize)) };
      });
      p.off('response', onResp);
      if (r.out.length || bad.length) { problems++; console.log('PROBLEM', w, path, JSON.stringify(r.out), JSON.stringify(bad)); }
      if (path.split('/').filter(Boolean).length <= 1 && !path.includes('privacy') && !path.includes('terms')) console.log(String(w).padStart(5), path.padEnd(6), 'nav', r.navRows, '| h1', r.h1Size + 'px', r.h1Lines, 'lines');
    }
    await ctx.close();
  }
  console.log('pages with problems:', problems);
  await b.close();
})();
