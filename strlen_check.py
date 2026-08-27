# Custom String 리터럴 길이 검사 (렌더 한계 128자, \r\n은 2자로 계산)
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

lines = io.open('ROUTE66_LIFE_EN.ow', encoding='utf-8').read().split('\n')
rules = []
i = 0
while i < len(lines):
    m = re.match(r'rule\("(.+)"\)', lines[i])
    if m:
        d = 0
        for k in range(i, len(lines)):
            d += lines[k].count('{') - lines[k].count('}')
            if d == 0 and k > i:
                rules.append({'n': m.group(1), 'b': lines[i:k+1], 's': i})
                i = k
                break
    i += 1

PAT = re.compile(r'Custom String\("([^"]*)"')
over = []
for r in rules:
    for k, l in enumerate(r['b']):
        for m in PAT.finditer(l):
            s = m.group(1)
            eff = len(s.replace('\\r\\n', 'XX'))
            if eff > 110:
                over.append((eff, r['n'][:26], r['s'] + k + 1, s[:70]))
over.sort(reverse=True)
for eff, rn, ln, txt in over[:25]:
    mark = '!!초과' if eff > 128 else ' 주의 '
    print(f'[{mark}] {eff:3}자 L{ln:5} [{rn}] {txt}...')
print(f'\n110자 초과: {len(over)}건 | 128자 초과: {sum(1 for e, _, _, _ in over if e > 128)}건')
