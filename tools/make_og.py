import json, os, subprocess, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import build
jobs = []
for code, slug, hreflang, name in build.available():
    if len(sys.argv) > 1 and code not in sys.argv[1:]: continue
    t = build.strings(code)
    jobs.append(dict(code=code, lang=t['lang'], dir=t['dir'], l1=html.escape(t['hero']['title_1']), l2=html.escape(t['hero']['title_2'])))
env = dict(os.environ, NODE_PATH=subprocess.check_output(['npm', 'root', '-g'], text=True).strip())
subprocess.run(['node', os.path.join(ROOT, 'tools', 'og.js'), json.dumps(jobs, ensure_ascii=False)], check=True, env=env)
from PIL import Image
for j in jobs:
    p = os.path.join(ROOT, 'static', 'img', j['code'], 'og.png')
    Image.open(p).convert('RGB').save(p, optimize=True)
print('og images:', len(jobs))
