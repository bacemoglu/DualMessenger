#!/usr/bin/env python3
"""Checks one translated language against the English source.  Usage: check_lang.py CODE [CODE ...]"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECT = {  # code: (lang attribute, dir)
    'tr': ('tr', 'ltr'), 'de': ('de', 'ltr'), 'nl': ('nl', 'ltr'), 'fr': ('fr', 'ltr'), 'es': ('es', 'ltr'), 'it': ('it', 'ltr'),
    'pt-PT': ('pt-PT', 'ltr'), 'ru': ('ru', 'ltr'), 'id': ('id', 'ltr'), 'ja': ('ja', 'ltr'), 'zh-Hans': ('zh-Hans', 'ltr'),
    'ar': ('ar', 'rtl'), 'he': ('he', 'rtl'), 'hi': ('hi', 'ltr'),
}
KEEP = ['Dual Messenger+', 'WhatsApp', 'RevenueCat', 'App Store', 'Face ID', 'Touch ID', 'iPhone', 'iPad', 'Premium']
BRAZILIAN = r'\b(arquivos?|telas?|celular(es)?|usuári[oa]s?|salvar|salve|exclu(ir|a|ído)|aplicativos?|contato|senhas?|configurações|compartilh\w+|assinaturas?|figurinhas?|você|vocês|digite|escanear|baixar|cadastr\w+)\b'
URL = re.compile(r'https?://[^\s)\]>"]+|mailto:[^\s)\]>"]+')


def read(code, name):
    with open(os.path.join(ROOT, 'content', code, name), encoding='utf-8') as f:
        return f.read()


def walk(en, tr, path, errors, same):
    if isinstance(en, dict):
        if not isinstance(tr, dict):
            errors.append(f'{path}: expected an object'); return
        for k in en:
            if k not in tr: errors.append(f'{path}.{k}: key missing')
        for k in tr:
            if k not in en: errors.append(f'{path}.{k}: unexpected key')
        for k in en:
            if k in tr: walk(en[k], tr[k], f'{path}.{k}', errors, same)
    elif isinstance(en, list):
        if not isinstance(tr, list) or len(tr) != len(en):
            errors.append(f'{path}: expected a list of {len(en)} items'); return
        for i, (a, b) in enumerate(zip(en, tr)): walk(a, b, f'{path}[{i}]', errors, same)
    else:
        if not isinstance(tr, str) or not tr.strip():
            errors.append(f'{path}: empty or not a string'); return
        if path.endswith('.img') and tr != en: errors.append(f'{path}: "img" must stay "{en}"')
        if '<' in tr or '{{' in tr: errors.append(f'{path}: contains markup or a placeholder')
        if '‎' in tr or '‏' in tr: errors.append(f'{path}: contains a direction mark')
        if tr == en and len(en) > 24 and not path.endswith('.img'): same.append(path)


def md_shape(text):
    lines = text.split('\n')
    return dict(
        h2=[re.match(r'## (\d+)\.', l).group(1) if re.match(r'## (\d+)\.', l) else '?' for l in lines if l.startswith('## ')],
        items=sum(1 for l in lines if l.startswith('- ')),
        bold_leads=sum(1 for l in lines if l.startswith('**')),
        bold_items=sum(1 for l in lines if l.startswith('- **')),
        paragraphs=sum(1 for b in re.split(r'\n\s*\n', text.strip()) if b.strip()),
        urls=sorted(URL.findall(text)),
        toc=lines.count('[TOC]'), open=lines.count('<div class="summary" markdown="1">'), close=lines.count('</div>'),
        ph=text.count('{{privacy_url}}'),
    )


def check(code):
    errors, warnings = [], []
    if code not in EXPECT:
        print(f'{code}: unknown code'); return 1
    try:
        en = json.loads(read('en', 'site.json')); tr = json.loads(read(code, 'site.json'))
    except Exception as e:
        print(f'{code}: ERROR site.json does not load: {e}'); return 1
    same = []
    walk(en, tr, 'site', errors, same)
    if tr.get('lang') != EXPECT[code][0]: errors.append(f'site.lang must be "{EXPECT[code][0]}"')
    if tr.get('dir') != EXPECT[code][1]: errors.append(f'site.dir must be "{EXPECT[code][1]}"')
    if tr.get('app') != 'Dual Messenger+': errors.append('site.app must stay "Dual Messenger+"')
    for p in same: warnings.append(f'{p}: identical to English')
    flat = json.dumps(tr, ensure_ascii=False)
    en_flat = json.dumps(en, ensure_ascii=False)
    for name in KEEP:
        if flat.count(name) < en_flat.count(name) - 3: warnings.append(f'site.json: "{name}" appears {flat.count(name)}x (English {en_flat.count(name)}x)')
    for name in ('privacy', 'terms'):
        try:
            a = md_shape(read('en', name + '.md')); raw = read(code, name + '.md'); b = md_shape(raw)
        except Exception as e:
            errors.append(f'{name}.md: cannot read ({e})'); continue
        for k in ('h2', 'items', 'bold_leads', 'bold_items', 'urls', 'toc', 'open', 'close', 'ph'):
            if a[k] != b[k]:
                detail = f'expected {a[k]}, found {b[k]}' if k not in ('urls',) else f'missing {sorted(set(a[k]) - set(b[k]))} extra {sorted(set(b[k]) - set(a[k]))} (count {len(a[k])} vs {len(b[k])})'
                errors.append(f'{name}.md: {k} differs: {detail}')
        if a['paragraphs'] != b['paragraphs']: warnings.append(f'{name}.md: {b["paragraphs"]} blocks, English has {a["paragraphs"]}')
        if '‎' in raw or '‏' in raw: errors.append(f'{name}.md: contains a direction mark')
        if re.search(r'<(?!div class="summary" markdown="1">|/div>)[a-zA-Z/]', raw): errors.append(f'{name}.md: contains HTML other than the summary wrapper')
        en_lines = set(l.strip() for l in read('en', name + '.md').split('\n') if len(l.strip()) > 40)
        dup = [l[:60] for l in raw.split('\n') if l.strip() in en_lines]
        if dup: warnings.append(f'{name}.md: {len(dup)} line(s) still in English, e.g. "{dup[0]}"')
        flat += raw
    if code == 'pt-PT':
        hits = sorted(set(m.group(0).lower() for m in re.finditer(BRAZILIAN, flat, re.I)))
        if hits: errors.append('Brazilian Portuguese words found: ' + ', '.join(hits))
    if re.search(r'\b(theme|themes)\b', flat, re.I) and code != 'en': warnings.append('the word "theme" appears; themes must not be mentioned as a feature')
    for e in errors: print(f'{code}: ERROR {e}')
    for w in warnings: print(f'{code}: warning {w}')
    print(f'{code}: {"OK" if not errors else str(len(errors)) + " error(s)"}, {len(warnings)} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(max([check(c) for c in sys.argv[1:]] or [1]))
