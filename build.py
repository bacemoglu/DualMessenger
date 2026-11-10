#!/usr/bin/env python3
"""Builds the Dual Messenger+ website in every language that has content.

  dist/     the real site for GitHub Pages: English at /, other languages at /<slug>/, each with
            /privacy/ and /terms/; plus 404.html, sitemap.xml and assets/
  preview/  one self-contained index.html (all languages and pages, switched by the hash) + assets/

Content lives in content/<code>/ (site.json, privacy.md, terms.md), layout in templates/, styles in static/.
"""
import json, os, re, shutil
import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://www.dualmessengerplus.com/'
APP_ID = '1131873369'
STORE = 'https://apps.apple.com/app/id' + APP_ID
EMAIL = 'info@dualmessengerplus.com'

# code (content folder), slug (URL folder), hreflang, name in the language itself: in menu order
LANGS = [
    ('en', '', 'en', 'English'),
    ('de', 'de', 'de', 'Deutsch'),
    ('es', 'es', 'es', 'Español'),
    ('fr', 'fr', 'fr', 'Français'),
    ('id', 'id', 'id', 'Bahasa Indonesia'),
    ('it', 'it', 'it', 'Italiano'),
    ('nl', 'nl', 'nl', 'Nederlands'),
    ('pt-PT', 'pt', 'pt-PT', 'Português'),
    ('tr', 'tr', 'tr', 'Türkçe'),
    ('ru', 'ru', 'ru', 'Русский'),
    ('he', 'he', 'he', 'עברית'),
    ('ar', 'ar', 'ar', 'العربية'),
    ('hi', 'hi', 'hi', 'हिन्दी'),
    ('ja', 'ja', 'ja', '日本語'),
    ('zh-Hans', 'zh', 'zh-Hans', '简体中文'),
]
SYSTEM_FONT_LANGS = {'ar', 'he', 'hi', 'ja', 'zh-Hans'}   # scripts Inter does not cover
RTL_MARK_LANGS = {'ar', 'he'}
LRM = '‎'
KINDS = ('home', 'privacy', 'terms')

env = Environment(loader=FileSystemLoader(os.path.join(ROOT, 'templates')), autoescape=True, undefined=StrictUndefined)
env.globals.update(email=EMAIL, app_id=APP_ID, site=SITE)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def available():
    return [l for l in LANGS if all(os.path.isfile(os.path.join(ROOT, 'content', l[0], f)) for f in ('site.json', 'privacy.md', 'terms.md'))]


def keep_plus_right(text):
    """In right-to-left text the "+" of the app name would jump to the left; a left-to-right mark pins it."""
    return re.sub(r'(Dual ?Messenger\+)(?!' + LRM + ')', r'\1' + LRM, text)


def deep_map(value, fn):
    if isinstance(value, dict): return {k: deep_map(v, fn) for k, v in value.items()}
    if isinstance(value, list): return [deep_map(v, fn) for v in value]
    return fn(value) if isinstance(value, str) else value


def strings(code):
    t = json.loads(read('content', code, 'site.json'))
    if code in RTL_MARK_LANGS:
        app = t['app']; t = deep_map(t, keep_plus_right); t['app'] = app
    return t


def legal_html(code, name, prefix, toc_title, privacy_url):
    """Markdown -> HTML. Section ids come from the section numbers (p-1, t-4 …), so they are the same in every language."""
    counter = [0]

    def slug(value, sep):
        m = re.match(r'\s*(\d+)[.．、]', value)
        counter[0] += 1
        return prefix + (m.group(1) if m else 'x%d' % counter[0])

    src = read('content', code, name + '.md').replace('{{privacy_url}}', privacy_url)
    if code in RTL_MARK_LANGS:
        src = keep_plus_right(src)
    md = markdown.Markdown(extensions=['md_in_html', 'toc', 'smarty', 'sane_lists'],
                           extension_configs={'toc': {'title': toc_title, 'toc_depth': '2-2', 'slugify': slug},
                                              'smarty': {'smart_quotes': code == 'en', 'smart_dashes': code == 'en', 'smart_ellipses': True}},
                           output_format='html')
    return md.convert(src)


def em_width(s):
    """Rough width of a headline line in em (bold system typeface), for languages that do not use Inter."""
    import unicodedata
    w = 0.0
    for ch in s:
        o = ord(ch); cat = unicodedata.category(ch)
        if ch == ' ': w += 0.28
        elif cat == 'Mn': w += 0.0                                    # vowel points, virama, harakat
        elif cat == 'Mc': w += 0.32                                   # spacing vowel signs (Devanagari)
        elif 0x0590 <= o <= 0x05FF: w += 0.62                         # Hebrew
        elif 0x0600 <= o <= 0x06FF: w += 0.34 if cat.startswith('P') else 0.6   # Arabic
        elif 0x0900 <= o <= 0x097F: w += 0.34 if cat.startswith('P') else 0.72  # Devanagari
        elif o < 0x2E80: w += 0.3 if cat.startswith('P') else (0.66 if (ch.isupper() or ch.isdigit()) else 0.58)
        else: w += 1.0
    return w


FIT_MARGIN = {'ja': 0.9, 'zh-Hans': 0.9, 'ar': 1.0, 'he': 0.6, 'hi': 0.8}


def headline_fit(code, t):
    if code not in FIT_MARGIN:
        return None
    return round(max(em_width(t['hero']['title_1']), em_width(t['hero']['title_2'])) + FIT_MARGIN[code], 2)


def badge(slug):
    return (slug or 'en').upper()


def preload_fonts(code):
    if code in SYSTEM_FONT_LANGS: return []
    if code == 'ru': return ['inter-display-700-cyr.woff2', 'inter-400-cyr.woff2', 'inter-400.woff2']
    return ['inter-display-700.woff2', 'inter-400.woff2']


def page_path(slug, kind):
    return (slug + '/' if slug else '') + ('' if kind == 'home' else kind + '/')


def rel(from_path, to_path):
    return ('../' * from_path.count('/') + to_path) or './'


def copy_assets(dest, langs):
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(os.path.join(dest, 'img'))
    src = os.path.join(ROOT, 'static', 'img')
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if os.path.isfile(p): shutil.copy(p, os.path.join(dest, 'img', f))
    for code, *_ in langs:
        shutil.copytree(os.path.join(src, code), os.path.join(dest, 'img', code))
    shutil.copytree(os.path.join(ROOT, 'static', 'fonts'), os.path.join(dest, 'fonts'))


def build_dist():
    langs = available()
    T = {code: strings(code) for code, *_ in langs}
    out = os.path.join(ROOT, 'dist')
    for name in os.listdir(out) if os.path.isdir(out) else []:
        p = os.path.join(out, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    copy_assets(os.path.join(out, 'assets'), langs)
    shutil.copy(os.path.join(ROOT, 'static', 'site.css'), os.path.join(out, 'assets', 'site.css'))
    shutil.copy(os.path.join(ROOT, 'static', 'favicon.ico'), os.path.join(out, 'favicon.ico'))
    page = env.get_template('page.j2')
    ids = dict(features='features', how='how-it-works', contact='contact', questions='questions', languages='languages')
    urls = []

    for code, slug, hreflang, name in langs:
        t = T[code]
        for kind in KINDS:
            here = page_path(slug, kind)
            home = rel(here, page_path(slug, 'home'))
            anchors = '' if kind == 'home' else home
            og_file = 'assets/img/%s/og.png' % code
            u = dict(root=rel(here, '') if here else '', assets=rel(here, 'assets/'), img=rel(here, 'assets/img/%s/' % code), home=home,
                     features=anchors + '#features', how=anchors + '#how-it-works', contact=anchors + '#contact',
                     privacy=rel(here, page_path(slug, 'privacy')), terms=rel(here, page_path(slug, 'terms')),
                     languages='#languages', store=STORE,
                     english=rel(here, page_path('', kind)) if (code != 'en' and kind != 'home') else '')
            if u['root'] == './': u['root'] = ''
            menu = [dict(name=n, hreflang=h, href=rel(here, page_path(s, kind)), current=(c == code), home_key='') for c, s, h, n in langs]
            alternates = [dict(hreflang=h, url=SITE + page_path(s, kind)) for c, s, h, n in langs] + [dict(hreflang='x-default', url=SITE + page_path('', kind))]
            hint_map = {c: [T[c]['language']['hint'], rel(here, page_path(s, kind))] for c, s, h, n in langs if c != code}
            common = dict(t=t, u=u, ids=ids, langs=menu, alternates=alternates if len(langs) > 1 else [], hint_map=hint_map,
                          badge=badge(slug), preload=preload_fonts(code), canonical=SITE + here, robots='',
                          og_image=SITE + (og_file if os.path.isfile(os.path.join(ROOT, 'static', 'img', code, 'og.png')) else 'assets/img/og.png'))
            if kind == 'home':
                html = page.render(kind='home', current='', title=t['meta']['home_title'], description=t['meta']['home_description'],
                                   fit=headline_fit(code, t), **common)
            else:
                prefix = 'p-' if kind == 'privacy' else 't-'
                body = legal_html(code, kind, prefix, t['legal']['toc_title'], rel(here, page_path(slug, 'privacy')))
                heading = t['meta'][kind + '_title']
                html = page.render(kind='legal', current=kind, heading=heading, body=body, title=heading + ' – ' + T[code]['app'],
                                   description=t['meta'][kind + '_description'], fit=None, **common)
            write(os.path.join(out, here, 'index.html'), html)
            urls.append(SITE + here)

    t = T['en']
    u = dict(root='/', assets='/assets/', img='/assets/img/en/', home='/', features='/#features', how='/#how-it-works', contact='/#contact',
             privacy='/privacy/', terms='/terms/', languages='#languages', store=STORE, english='')
    menu = [dict(name=n, hreflang=h, href='/' + page_path(s, 'home'), current=(c == 'en'), home_key='') for c, s, h, n in langs]
    write(os.path.join(out, '404.html'), page.render(
        kind='notfound', current='', t=t, u=u, ids=ids, langs=menu, alternates=[], hint_map={}, badge='EN', preload=preload_fonts('en'),
        title=t['meta']['notfound_title'] + ' – ' + t['app'], description=t['meta']['notfound_text'], canonical=SITE, robots='noindex',
        og_image=SITE + 'assets/img/og.png', fit=None))

    write(os.path.join(out, 'robots.txt'), 'User-agent: *\nAllow: /\n\nSitemap: ' + SITE + 'sitemap.xml\n')
    write(os.path.join(out, 'sitemap.xml'),
          '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + ''.join('  <url><loc>%s</loc></url>\n' % x for x in urls) + '</urlset>\n')
    write(os.path.join(out, '.nojekyll'), '')
    # GitHub Pages reads the custom domain from this file
    write(os.path.join(out, 'CNAME'), SITE.split('://', 1)[1].strip('/') + '\n')
    return out, len(langs)


def build_preview(title='Dual Messenger+'):
    langs = available()
    T = {code: strings(code) for code, *_ in langs}
    out = os.path.join(ROOT, 'preview')
    copy_assets(os.path.join(out, 'assets'), langs)
    for junk in ('og.png', 'apple-touch-icon.png', 'favicon-32.png', 'favicon-48.png', 'favicon-96.png'):
        p = os.path.join(out, 'assets', 'img', junk)
        if os.path.isfile(p): os.remove(p)
    for code, *_ in langs:
        p = os.path.join(out, 'assets', 'img', code, 'og.png')
        if os.path.isfile(p): os.remove(p)
    css = read('static', 'site.css').replace('url("fonts/', 'url("assets/fonts/')

    def home_key(slug): return slug or 'home'
    sites = []
    for code, slug, hreflang, name in langs:
        t = T[code]; pre = (slug + '-') if slug else ''
        ids = dict(home=home_key(slug), privacy=pre + 'privacy', terms=pre + 'terms', features=pre + 'features', how=pre + 'how-it-works',
                   contact=pre + 'contact', questions=pre + 'questions', languages=pre + 'languages')
        u = dict(root='', assets='assets/', img='assets/img/%s/' % code, home='#' + ids['home'], features='#' + ids['features'],
                 how='#' + ids['how'], contact='#' + ids['contact'], privacy='#' + ids['privacy'], terms='#' + ids['terms'],
                 languages='#' + ids['languages'], store=STORE,
                 english_privacy='#privacy' if code != 'en' else '', english_terms='#terms' if code != 'en' else '')
        menu = [dict(name=n, hreflang=h, href='#' + home_key(s), current=(c == code), home_key=home_key(s)) for c, s, h, n in langs]
        sites.append(dict(t=t, u=u, ids=ids, langs=menu, badge=badge(slug), fit=headline_fit(code, t),
                          privacy_body=legal_html(code, 'privacy', pre + 'p-', t['legal']['toc_title'], '#' + ids['privacy']),
                          terms_body=legal_html(code, 'terms', pre + 't-', t['legal']['toc_title'], '#' + ids['privacy'])))
    hint_map = {c: [T[c]['language']['hint'], home_key(s)] for c, s, h, n in langs}
    write(os.path.join(out, 'index.html'), env.get_template('preview.j2').render(sites=sites, css=css, title=title, hint_map=hint_map))
    return out, len(langs)


if __name__ == '__main__':
    for base, n in (build_dist(), build_preview(title='Dual Messenger+ new site')):
        total = sum(os.path.getsize(os.path.join(r, f)) for r, _, files in os.walk(base) for f in files)
        print(os.path.relpath(base, ROOT), n, 'language(s)', round(total / 1024), 'KB')
