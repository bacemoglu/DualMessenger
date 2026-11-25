"""Puts the feature cards in the order funny, lock, notes, bot, voice (1.5.0 site) and updates the lock
screen's alt text to the new screen ("Dual Messenger+" with a space, as the new lock screen shows it).
  python3 tools/reorder_features.py CODE ..."""
import json, sys
ORDER = ['funny', 'lock', 'notes', 'bot', 'voice']
for code in sys.argv[1:]:
    p = f'content/{code}/site.json'
    raw = open(p, encoding='utf-8').read()
    d = json.loads(raw)
    items = d['features']['items']
    by = {i['img']: i for i in items}
    assert sorted(by) == sorted(ORDER) and len(items) == len(ORDER), (code, list(by))
    d['features']['items'] = [by[k] for k in ORDER]
    lock = by['lock']
    assert lock['alt'].count('DualMessenger+') == 1, (code, lock['alt'])
    lock['alt'] = lock['alt'].replace('DualMessenger+', 'Dual Messenger+')
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2) + ('\n' if raw.endswith('\n') else ''))
    print(code, [i['img'] for i in d['features']['items']], '|', lock['alt'])
