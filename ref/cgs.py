import json, re, io, sys
s = io.open('cgs.ts', encoding='utf-8').read()
a = s.index('//begin-json') + len('//begin-json'); b = s.index('//end-json')
t = s[a:b]
t = re.sub(r'([\n{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', t)
t = re.sub(r',(\s*[}\]])', r'\1', t)
d = json.loads(t)

def nm(v):
    return v.get('en-US', '?') if isinstance(v, dict) else str(v)

def dump(node, indent=2):
    vals = node.get('values', {}) if isinstance(node, dict) else {}
    if not isinstance(vals, dict): return
    for k, v in vals.items():
        if not isinstance(v, dict):
            print(' '*indent + str(k) + ' = ' + str(v)); continue
        sub = v.get('values')
        extra = ''
        if isinstance(sub, dict) and sub:
            opts = [nm(x) for x in sub.values() if isinstance(x, dict)]
            if opts:
                extra = '  {' + ('|'.join(opts) if len(opts) <= 8 else str(len(opts)) + ' options') + '}'
        if 'min' in v:
            extra = '  [%s..%s def=%s]' % (v.get('min'), v.get('max'), v.get('default'))
        elif not extra and 'default' in v:
            extra = '  [def=%s]' % v.get('default')
        print(' '*indent + nm(v) + extra)

for key in sys.argv[1:]:
    print('===== ' + key + ' =====')
    node = d
    for part in key.split('.'):
        node = (node.get('values') if isinstance(node.get('values'), dict) else node).get(part, {})
    dump(node)
    print()
