// Renders one 1200x630 link-preview image per language.  usage: node og.js '<json list of {code,lang,dir,l1,l2}>'
const { chromium } = require('playwright');
const fs = require('fs');
const ROOT = '/home/claude/site/web/';
const page = (j) => `<!DOCTYPE html><html lang="${j.lang}" dir="${j.dir}"><head><meta charset="utf-8">
<link rel="stylesheet" href="${ROOT}static/site.css">
<style>
  html, body { width: 1200px; height: 630px; overflow: hidden; }
  body { background: radial-gradient(900px 620px at ${j.dir === 'rtl' ? '100%' : '0'} 0, rgba(190,235,205,.95), rgba(190,235,205,0) 70%), #F3F9F4; }
  .og { display: flex; justify-content: space-between; width: 1200px; height: 630px; padding: 64px 72px 0; }
  .copy { width: 640px; flex: none; }
  .og .brand { font-size: 30px; gap: 16px; }
  .og .brand img { width: 64px; height: 64px; border-radius: 15px; }
  .og h1 { margin-top: 70px; font-size: 92px; text-wrap: wrap; hyphens: manual; }
  .og h1 span { display: block; }
  .og h1.nowrap span { white-space: nowrap; width: max-content; }
  .art { position: relative; width: 440px; height: 760px; margin-top: -20px; flex: none; display: grid; place-items: center; }
  .art svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
  .art .phone { --w: 330px; }
</style></head><body>
<div class="og">
  <div class="copy">
    <span class="brand"><img src="${ROOT}static/img/icon-192.png" alt=""><span dir="ltr">Dual Messenger+</span></span>
    <h1 id="h" class="${/^(ja|zh)/.test(j.lang) ? 'nowrap' : ''}"><span>${j.l1}</span><span>${j.l2}</span></h1>
  </div>
  <div class="art">
    <svg viewBox="0 0 560 640" preserveAspectRatio="xMidYMid meet">
      <g fill="#FFDDBB"><ellipse cx="385" cy="420" rx="175" ry="155"/><path d="M521 516c3 40 13 68 27 90-34-2-66-20-84-48z"/></g>
      <g fill="#C9EBD5"><ellipse cx="190" cy="250" rx="190" ry="170"/><path d="M42 355c-2 45-12 75-28 97 36-2 71-22 90-51z"/></g>
    </svg>
    <div class="phone"><div class="screen"><img src="${ROOT}static/img/${j.code}/screen-main.webp" alt=""><span class="island"></span></div></div>
  </div>
</div>
</body></html>`;
(async () => {
  const jobs = JSON.parse(process.argv[2]);
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
  for (const j of jobs) {
    const f = ROOT + 'tools/_og_tmp.html';
    fs.writeFileSync(f, page(j));
    const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
    await p.goto('file://' + f, { waitUntil: 'networkidle' });
    const size = await p.evaluate(async () => {
      await document.fonts.ready;
      await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {})));
      const h = document.getElementById('h'); let s = 92;
      const bad = () => Array.from(h.children).some(c => c.getBoundingClientRect().width > 641 || c.scrollWidth > 641) || h.getBoundingClientRect().height > 372;
      while (s > 44 && bad()) { s -= 2; h.style.fontSize = s + 'px'; }
      return s;
    });
    fs.mkdirSync(ROOT + 'static/img/' + j.code, { recursive: true });
    await p.screenshot({ path: ROOT + 'static/img/' + j.code + '/og.png' });
    console.log(j.code, 'headline', size + 'px');
    await p.close();
  }
  await b.close();
})();
