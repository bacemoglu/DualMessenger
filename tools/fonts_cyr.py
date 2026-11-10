import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from fontTools import subset
from fontTools.ttLib import TTFont
SRC = '/usr/share/fonts/opentype/inter/'
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
UNI = "U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"
for src, out in [('InterDisplay-Bold.otf', 'inter-display-700-cyr.woff2'), ('Inter-Regular.otf', 'inter-400-cyr.woff2'),
                 ('Inter-Medium.otf', 'inter-500-cyr.woff2'), ('Inter-SemiBold.otf', 'inter-600-cyr.woff2')]:
    o = os.path.join(OUT, out)
    subset.main([SRC + src, '--unicodes=' + UNI, '--flavor=woff2', '--output-file=' + o,
                 '--layout-features+=tnum,case', '--name-IDs=*', '--no-hinting'])
    f = TTFont(o); print(out, os.path.getsize(o), 'bytes | glyphs', len(f.getGlyphOrder()))
