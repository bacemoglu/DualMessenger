import os, numpy as np
from PIL import Image
S = '/home/claude/shots/screens/'; OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'img')
ICON = '/mnt/user-data/uploads/Desktop/DualMessenger/DualMessenger/Assets.xcassets/AppIcon.appiconset/icon-1024-green.png'

def notes_title_fix(im):
    """The app's Notes title is now "Notes" (was "Dual Notes"): move the word, keep the real glyphs."""
    a = np.array(im.convert('RGB')).astype(int)
    bar = a[200, 60]                                   # flat orange of the nav bar
    y0, y1, x0, x1 = 215, 300, 380, 830
    reg = a[y0:y1, x0:x1]
    white = (reg.max(axis=2) < 150)                    # title glyph pixels (black on orange)
    cols = np.where(white.any(axis=0))[0]; rows = np.where(white.any(axis=1))[0]
    # split words at the widest empty gap
    gaps = [(cols[i + 1] - cols[i], cols[i], cols[i + 1]) for i in range(len(cols) - 1)]
    g = max(gaps); left_end, right_start = g[1], g[2]
    word = a[y0 + rows[0] - 2:y0 + rows[-1] + 3, x0 + right_start - 2:x0 + cols[-1] + 3].copy()
    a[y0 + rows[0] - 4:y0 + rows[-1] + 5, x0 + cols[0] - 4:x0 + cols[-1] + 5] = bar
    h, w = word.shape[:2]; cx = a.shape[1] // 2
    a[y0 + rows[0] - 2:y0 + rows[0] - 2 + h, cx - w // 2:cx - w // 2 + w] = word
    print('notes title: gap', g[0], 'px, word width', w, 'bar', tuple(bar))
    return Image.fromarray(a.astype('uint8'))

def zh_notes_title(im):
    """The Chinese Notes title is now 笔记 (was 备注)."""
    from PIL import ImageDraw, ImageFont
    a = np.array(im.convert('RGB')).astype(int)
    bar = tuple(int(v) for v in a[200, 60]); y0, y1, x0, x1 = 215, 300, 380, 830
    dark = (a[y0:y1, x0:x1].max(axis=2) < 150)
    cols = np.where(dark.any(axis=0))[0]; rows = np.where(dark.any(axis=1))[0]
    out = im.convert('RGB').copy(); d = ImageDraw.Draw(out)
    d.rectangle((x0 + cols[0] - 6, y0 + rows[0] - 6, x0 + cols[-1] + 6, y0 + rows[-1] + 6), fill=bar)
    f = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc', 50, index=2)
    d.text((im.width / 2, (2 * y0 + rows[0] + rows[-1]) / 2), '\u7b14\u8bb0', font=f, fill=(0, 0, 0), anchor='mm')
    return out


def relabel(im, box, text, font_path, center_x=None, size=None, baseline=None):
    """Replaces a short dark label inside `box` (x0, y0, x1, y1) with `text`, on the flat background found next to it.
    The new label keeps the old cap height and baseline (pass size and baseline when the old label had descenders);
    it is centred on the old label unless center_x is given."""
    from PIL import ImageDraw, ImageFont
    x0, y0, x1, y1 = box
    a = np.array(im.convert('RGB')).astype(int)
    bg = tuple(int(v) for v in a[y0 + 2, x0 + 2])
    dark = (a[y0:y1, x0:x1].max(axis=2) < 110)
    cols = np.where(dark.any(axis=0))[0]; rows = np.where(dark.any(axis=1))[0]
    top, bottom, left, right = y0 + rows[0], y0 + rows[-1], x0 + cols[0], x0 + cols[-1]
    out = im.convert('RGB').copy(); d = ImageDraw.Draw(out)
    d.rectangle((left - 8, top - 8, right + 8, bottom + 8), fill=bg)
    if size is None: size = round((bottom - top + 1) / 0.727)   # Inter's cap height is 0.727 em
    if baseline is None: baseline = bottom + 1
    f = ImageFont.truetype(font_path, size)
    cx = (left + right) / 2 if center_x is None else center_x
    d.text((cx, baseline), text, font=f, fill=(0, 0, 0), anchor='ms')
    print('relabel', repr(text), 'size', size, 'old box', (int(left), int(top), int(right), int(bottom)), 'bg', bg)
    return out

INTER = '/usr/share/fonts/opentype/inter/'
LANGS = ['en', 'tr', 'de', 'nl', 'fr', 'es', 'it', 'pt-PT', 'ru', 'id', 'ja', 'zh-Hans', 'ar', 'he', 'hi']
shots = {'main': '01.png', 'lock': '02.png', 'voice': '03.png', 'bot': '04.png', 'notes': '05.png'}
import shutil
for old in [f for f in os.listdir(OUT) if f.startswith('screen-')]:
    os.remove(os.path.join(OUT, old))
total = 0
for code in LANGS:
    src = S if code == 'en' else S + code + '/'
    d = os.path.join(OUT, code); os.makedirs(d, exist_ok=True)
    for name, f in shots.items():
        im = Image.open(src + f).convert('RGB')
        assert im.size == (1206, 2622), (code, f, im.size)
        if name == 'notes' and code in ('en', 'nl'): im = notes_title_fix(im)
        if name == 'notes' and code == 'zh-Hans': im = zh_notes_title(im)
        # labels that changed in the app after these screenshots were taken
        if name == 'main' and code == 'pt-PT': im = relabel(im, (330, 1700, 880, 1900), 'Iniciar sess\u00e3o', INTER + 'Inter-Regular.otf')
        if name == 'voice' and code == 'nl': im = relabel(im, (200, 215, 632, 300), 'Transcriptie', INTER + 'Inter-SemiBold.otf', center_x=410, size=51, baseline=270)
        o = os.path.join(d, f'screen-{name}.webp')
        im.resize((640, 1391), Image.LANCZOS).save(o, 'WEBP', quality=84, method=6)
        total += os.path.getsize(o)
    print(code, sum(os.path.getsize(os.path.join(d, x)) for x in os.listdir(d)) // 1024, 'KB')
print('all screens', total // 1024, 'KB')

if os.path.exists(ICON):
    ic = Image.open(ICON).convert('RGB')
    ic.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, 'icon-192.png'), optimize=True)
    ic.resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, 'apple-touch-icon.png'), optimize=True)
    # favicon: the green disc on transparent
    big = ic.resize((512, 512), Image.LANCZOS).convert('RGBA'); a = np.array(big)
    g = np.array(ic.convert('RGB').resize((512, 512), Image.LANCZOS)).astype(int)
    notwhite = (g.min(axis=2) < 235); ys, xs = np.where(notwhite)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2; r = (xs.max() - xs.min()) / 2
    yy, xx = np.mgrid[0:512, 0:512]; d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    a[..., 3] = np.clip((r - d + 0.5) * 255, 0, 255).astype('uint8')
    disc = Image.fromarray(a).crop((int(cx - r), int(cy - r), int(cx + r) + 1, int(cy + r) + 1))
    for s in (32, 48, 96):
        disc.resize((s, s), Image.LANCZOS).save(os.path.join(OUT, f'favicon-{s}.png'), optimize=True)
    disc.resize((64, 64), Image.LANCZOS).save(os.path.join(OUT, '..', 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    print('icon disc radius', round(r), 'of 256; files:', sorted(os.listdir(OUT)))
else:
    print('icon source not available here: icons left as they are')
