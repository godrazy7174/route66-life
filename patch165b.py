# patch165b: patch163 오적용 복구 + 샛길/밀수를 '검증된 좌표만' 방식으로 교체
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def rule_span(prefix):
    s = next(i for i, l in enumerate(lines) if l.startswith('rule("' + prefix))
    d = 0
    for k in range(s, len(lines)):
        d += lines[k].count('{') - lines[k].count('}')
        if d == 0 and k > s:
            return s, k
    raise AssertionError(prefix)

POOL = 'Append To Array(Global Variable(RaidPath), Global Variable(LocPos))'
SAFE = 'Filtered Array(' + POOL + ', Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)'
NEAR = ('Filtered Array(' + SAFE + ', And(Distance Between(Current Array Element, Position Of(Event Player)) >= 11, '
        'Distance Between(Current Array Element, Position Of(Event Player)) <= 55))')

# A) 밀수 복구
cs, ce = rule_span('[범죄 01]')
b = next(i for i in range(cs, ce) if 'Set Player Variable(Event Player, DialTgt, Random Value In Array' in lines[i]) - 1
assert lines[b].strip().startswith('If(Count Of(')
d = 0
for k in range(b, ce):
    st = lines[k].strip()
    if st.startswith('If('):
        d += 1
    elif st == 'End;':
        d -= 1
        if d == 0:
            bend = k
            break
ind = lines[b][:len(lines[b]) - len(lines[b].lstrip('\t'))]
lines[b:bend + 1] = [ind + 'Set Player Variable(Event Player, SmugglePos, Random Value In Array(' + SAFE + '));']

# B) 샛길 교체
ps, pe = rule_span('[파발 02]')
s = next(i for i in range(ps, pe) if lines[i].strip() == 'Set Player Variable(Event Player, Roll, Random Integer(0, 11));')
e = next(i for i in range(s, pe) if 'Global Variable(SpawnPos), Multiply(Direction From Angles' in lines[i])
e = next(i for i in range(e, pe) if lines[i].strip() == 'End;')
ind = lines[s][:len(lines[s]) - len(lines[s].lstrip('\t'))]
lines[s:e + 1] = [
    ind + 'If(Count Of(' + NEAR + ') >= 1);',
    ind + '\tSet Player Variable(Event Player, DialTgt, Random Value In Array(' + NEAR + '));',
    ind + 'Else;',
    ind + '\tSet Player Variable(Event Player, DialTgt, Random Value In Array(' + SAFE + '));',
    ind + 'End;',
]

# C) 샛길에 남은 흔들기+NWP 제거
ps2, pe2 = rule_span('[파발 02]')
drop = [i for i in range(ps2, pe2)
        if 'Nearest Walkable Position(Add(Event Player.DialTgt, Vector(Random Real' in lines[i]]
assert len(drop) <= 1, len(drop)

if drop: del lines[drop[0]]

out = '\n'.join(lines)
assert out.count('Set Player Variable(Event Player, SmugglePos, Random Value In Array') == 1
assert out.count('Set Player Variable(Event Player, DialTgt, Random Value In Array') == 2
assert out.count('Nearest Walkable Position(Add(Event Player.DialTgt') == 1
assert out.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch165b ok')
