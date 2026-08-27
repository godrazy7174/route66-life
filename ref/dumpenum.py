import json, re, io, sys
s = io.open('constants.ts', encoding='utf-8').read()
a = s.index('//begin-json') + len('//begin-json'); b = s.index('//end-json')
t = s[a:b]
t = re.sub(r'([\n{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', t)
t = re.sub(r',(\s*[}\]])', r'\1', t)
d = json.loads(t)
for g in sys.argv[1:]:
    grp = d.get(g)
    if not grp:
        print('!! no group ' + g); continue
    vals = grp.get('values', grp)
    names = []
    for k, v in vals.items():
        names.append(v.get('en-US', k) if isinstance(v, dict) else k)
    print(g + ' (' + str(len(names)) + '): ' + ' | '.join(names))
    print()
