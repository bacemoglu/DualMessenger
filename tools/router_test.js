// Walks through the one-file preview (all languages, all pages) the way a visitor would and prints what is visible.
// Usage: node tools/router_test.js [base]   (default http://127.0.0.1:8766/)
const { chromium } = require('playwright');
(async () => {
  const base = process.argv[2] || 'http://127.0.0.1:8766/';
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  let failures = 0;
  const run = async (locale) => {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, locale });
    const p = await ctx.newPage();
    const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
    const state = async (label, want) => {
      const s = await p.evaluate(() => {
        const site = Array.from(document.querySelectorAll('[data-site]')).filter(v => !v.hidden);
        const view = Array.from(document.querySelectorAll('[data-view]')).filter(v => !v.hidden);
        const bar = document.querySelector('[data-lang-hint]');
        return {
          site: site.map(v => v.getAttribute('data-site')).join(','), view: view.map(v => v.getAttribute('data-view')).join(','),
          html: document.documentElement.lang + '/' + document.documentElement.dir, y: Math.round(window.scrollY), hash: location.hash,
          current: Array.from(document.querySelectorAll('[data-site]:not([hidden]) .site-nav a[aria-current]')).map(a => a.getAttribute('data-nav')).join(','),
          hint: bar.hidden ? '' : bar.textContent.trim() + ' -> ' + bar.firstElementChild.getAttribute('href'),
        };
      });
      const ok = !want || (s.site + ' ' + s.view) === want;
      if (!ok) failures++;
      console.log((ok ? 'ok   ' : 'FAIL ') + label.padEnd(40), JSON.stringify(s), ok ? '' : 'expected ' + want);
      return s;
    };
    const vis = '[data-site]:not([hidden]) ';
    const click = async (sel) => { await p.click(sel); await p.waitForTimeout(700); };
    const top = async (id) => p.evaluate((id) => Math.round(document.getElementById(id).getBoundingClientRect().top), id);
    await p.goto(base, { waitUntil: 'networkidle' });
    await state(`[${locale}] load`, 'en home');
    if (locale !== 'en-US') {
      const shown = await p.evaluate(() => !document.querySelector('[data-lang-hint]').hidden);
      if (shown) { await click('[data-lang-hint] a'); const s = await state('follow the hint bar'); if (s.hint || s.site === 'en') { failures++; console.log('FAIL hint did not lead to the language'); } }
      else { failures++; console.log('FAIL no hint bar for ' + locale); }
      await ctx.close(); return errs;
    }
    await click(vis + '.lang-nav a[lang="tr"]'); await state('footer: Türkçe', 'tr home');
    await click(vis + '.nav-links a[data-nav="privacy"]'); await state('nav: privacy', 'tr privacy');
    const sec = await p.evaluate(() => document.querySelectorAll('[data-site]:not([hidden]) [data-view="privacy"] .toc a')[3].getAttribute('href'));
    await click(vis + `.toc a[href="${sec}"]`); await p.waitForTimeout(1500); const s1 = await state('contents link ' + sec, 'tr privacy'); const t1 = await top(sec.slice(1));
    if (Math.abs(t1) > 40) { failures++; console.log('FAIL section top', t1); } else console.log('     section top', t1);
    await click(vis + '.nav-lang'); const s2 = await state('globe link (language list)', 'tr privacy');
    await click(vis + '.lang-nav a[lang="ar"]'); await state('language list: Arabic, same page', 'ar privacy');
    await click(vis + '[data-view="privacy"] .legal-note a'); await state('link to the English version', 'en privacy');
    await click(vis + '.lang-nav a[lang="ru"]'); await state('language list: Russian', 'ru privacy');
    await click(vis + '.footer-nav a:nth-child(2)'); await state('footer: terms', 'ru terms');
    await click(vis + '[data-view="terms"] .legal-body a[href$="privacy"]'); await state('terms -> privacy policy link', 'ru privacy');
    await click(vis + '.nav-links a:first-child'); const s3 = await state('nav: features', 'ru home');
    if (s3.y < 200) { failures++; console.log('FAIL features did not scroll'); }
    await click(vis + '.brand'); await state('brand', 'ru home');
    const deep = await p.evaluate(() => { const v = document.querySelector('[data-site="de"] [data-view="terms"]'); return v.querySelectorAll('h2')[3].id; });
    await p.goto(base + '#' + deep, { waitUntil: 'networkidle' }); await p.waitForTimeout(2500);
    await state('deep link #' + deep, 'de terms'); const t2 = await top(deep);
    if (Math.abs(t2) > 40) { failures++; console.log('FAIL deep link top', t2); } else console.log('     section top', t2);
    await p.goto(base + '#nonsense', { waitUntil: 'networkidle' }); await state('unknown hash', 'en home');
    const dup = await p.evaluate(() => { const seen = {}; const d = []; document.querySelectorAll('[id]').forEach(e => { if (seen[e.id]) d.push(e.id); seen[e.id] = 1; }); return d; });
    const dead = await p.evaluate(() => Array.from(document.querySelectorAll('a[href^="#"]')).map(a => a.getAttribute('href')).filter(h => h.length > 1 && !document.getElementById(decodeURIComponent(h.slice(1)))));
    if (dup.length || dead.length) failures++;
    console.log('duplicate ids:', JSON.stringify(dup.slice(0, 6)), '| links without a target:', JSON.stringify(Array.from(new Set(dead)).slice(0, 6)));
    await ctx.close();
    return errs;
  };
  for (const locale of (process.argv[3] ? process.argv[3].split(',') : ['en-US', 'tr-TR', 'ar-SA'])) {
    const errs = await run(locale);
    if (errs.length) { failures++; console.log('errors:', JSON.stringify(errs)); }
  }
  console.log(failures ? 'FAILURES: ' + failures : 'all good');
  await b.close();
})();
