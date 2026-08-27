import json, re, sys, io

def load(fn):
    s = io.open(fn, encoding='utf-8').read()
    a = s.index('//begin-json') + len('//begin-json')
    b = s.index('//end-json')
    t = s[a:b]
    t = re.sub(r'([\n{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', t)
    t = re.sub(r',(\s*[}\]])', r'\1', t)
    return json.loads(t)

DB = {}
for fn in ('actions.ts', 'values.ts', 'constants.ts'):
    for k, v in load(fn).items():
        if isinstance(v, dict) and v.get('en-US'):
            DB.setdefault(v['en-US'], (fn, k, v))

def show(name):
    if name not in DB:
        print('!! NOT FOUND: ' + name)
        for n in sorted(DB):
            if name.lower() in n.lower() or n.lower() in name.lower():
                print('   maybe: ' + n)
        return
    fn, k, v = DB[name]
    parts = []
    for a in (v.get('args') or []):
        t = a.get('type')
        t = t if isinstance(t, str) else json.dumps(t)
        d = a.get('default')
        parts.append(a['name'] + ':' + t + ('' if d is None else '=' + str(d)))
    print('[' + fn.split('.')[0] + '] ' + name + '(' + ', '.join(parts) + ')  ->  ' + str(v.get('return')))

for n in sys.argv[1:]:
    show(n)
