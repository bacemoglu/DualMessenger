"""Checks every page in dist/: local href/src targets exist, #anchors exist, lang/dir attributes, hreflang set."""
import os, re, html, sys
from urllib.parse import urljoin, urlparse
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist')
pages = {}
for r, _, files in os.walk(D):
    for f in files:
        if f.endswith('.html'):
            rel = os.path.relpath(os.path.join(r, f), D).replace(os.sep, '/')
            url = '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
            pages[url] = open(os.path.join(r, f), encoding='utf-8').read()
ids = {u: set(re.findall(r'\sid="([^"]+)"', t)) for u, t in pages.items()}
bad = 0; ext = set()
for url, t in sorted(pages.items()):
    dup = [i for i in ids[url] if len(re.findall(r'\sid="%s"' % re.escape(i), t)) > 1]
    if dup: print('DUPLICATE ID', url, dup); bad += 1
    for attr, v in re.findall(r'\s(href|src)="([^"]*)"', t):
        v = html.unescape(v)
        if v.startswith(('mailto:', 'https://', 'http://')): ext.add(v); continue
        pu = urlparse(urljoin('https://x' + url, v)); path = pu.path
        fs = os.path.join(D, path.lstrip('/'))
        if path.endswith('/'): fs = os.path.join(fs, 'index.html')
        if not os.path.isfile(fs): print('MISSING', url, v); bad += 1; continue
        if pu.fragment and path in pages and pu.fragment not in ids[path]: print('NO ANCHOR', url, v); bad += 1
    if url != '/404.html':
        n = len(re.findall(r'<link rel="alternate" hreflang=', t))
        expect = len([p for p in pages if p.endswith('/privacy/')]) + 1
        if n != expect: print('HREFLANG', url, n, 'expected', expect); bad += 1
langs = sorted(set(re.search(r'<html lang="([^"]+)" dir="([^"]+)"', t).groups() for t in pages.values()))
print('pages', len(pages), '| broken', bad, '| lang/dir:', ' '.join('%s(%s)' % x for x in langs))
print('external links:', len(ext))
sys.exit(1 if bad else 0)
