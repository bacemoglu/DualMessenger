import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fontTools import subset
from fontTools.ttLib import TTFont
SRC = '/usr/share/fonts/opentype/inter/'
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
UNI = ("U+0020-007E,U+00A0-00FF,U+0100-017F,U+02BC,U+02C6,U+02DA,U+02DC,U+2010-2015,U+2018-201E,"
       "U+2020-2022,U+2026,U+2030,U+2032-2033,U+2039-203A,U+2044,U+20AC,U+20BA,U+2122,U+2190-2193,U+2212")
for src, out in [('InterDisplay-Bold.otf', 'inter-display-700.woff2'), ('Inter-Regular.otf', 'inter-400.woff2'),
                 ('Inter-Medium.otf', 'inter-500.woff2'), ('Inter-SemiBold.otf', 'inter-600.woff2')]:
    o = os.path.join(OUT, out)
    subset.main([SRC + src, '--unicodes=' + UNI, '--flavor=woff2', '--output-file=' + o,
                 '--layout-features+=tnum,case', '--name-IDs=*', '--no-hinting'])
    f = TTFont(o)
    names = {n.nameID: n.toUnicode() for n in f['name'].names}
    print(out, os.path.getsize(o), 'bytes | glyphs', len(f.getGlyphOrder()), '|', names.get(1), '|', (names.get(13) or '')[:60])
