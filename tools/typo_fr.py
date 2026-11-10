#!/usr/bin/env python3
"""French typography: non-breaking spaces before ; : ! ? and inside guillemets.  Usage: typo_fr.py FILE..."""
import re, sys
NB, NNB = ' ', ' '
for path in sys.argv[1:]:
    s = open(path, encoding='utf-8').read()
    t = re.sub(r'(?<=\S) ([;!?])', NNB + r'\1', s)
    t = re.sub(r'(?<=\S) :', NB + ':', t)
    t = t.replace('« ', '«' + NB).replace(' »', NB + '»')
    if t != s:
        open(path, 'w', encoding='utf-8').write(t)
    print(path, s.count(' ') - t.count(' '), 'spaces made non-breaking')
