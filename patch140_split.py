# patch140 (작업 2): [조작 03c] 를 Zone 별 4개 규칙으로 분할
# 방식: 각 Zone 본문을 그대로(들여쓰기 무변경) 옮기고, 헤더/공통 전처리를 복제한다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

start = next(i for i, l in enumerate(lines) if l.startswith('rule("[조작 03c]'))
# rule end by brace depth
d = 0
for k in range(start, len(lines)):
    d += lines[k].count('{') - lines[k].count('}')
    if d == 0 and k > start:
        end = k
        break
block = lines[start:end + 1]

# locate landmarks inside block
act = next(i for i, l in enumerate(block) if l == '\tactions')          # 'actions'
assert block[act + 1] == '\t{'
pre_start = act + 2                                                     # first line of actions body
z9 = next(i for i, l in enumerate(block) if l.strip() == 'If(Event Player.Zone == 9);')
z10 = next(i for i, l in enumerate(block) if l.strip() == 'Else If(Event Player.Zone == 10);')
z11 = next(i for i, l in enumerate(block) if l.strip() == 'Else If(Event Player.Zone == 11);')
z12 = next(i for i, l in enumerate(block) if l.strip() == 'Else If(Event Player.Zone == 12);')
assert pre_start < z9 < z10 < z11 < z12
# trailing: 'End;' (closes zone chain), '\t}', '}'
assert block[-1] == '}' and block[-2] == '\t}', (block[-2], block[-1])
assert block[-3].strip() == 'End;', block[-3]

header = block[:pre_start]          # rule("...") ... actions {
preamble = block[pre_start:z9]      # 공통 전처리 (수배범 거래 차단)
bodies = {
    9:  block[z9 + 1:z10],
    10: block[z10 + 1:z11],
    11: block[z11 + 1:z12],
    12: block[z12 + 1:len(block) - 3],
}
names = {9: '안내소', 10: '대장간', 11: '정거장', 12: '목장'}
tags = {9: '03c', 10: '03d', 11: '03e', 12: '03f'}

new = []
for z in (9, 10, 11, 12):
    h = list(header)
    h[0] = f'rule("[조작 {tags[z]}] 행동 실행 — {names[z]}")'
    new += h
    new += preamble
    new.append(f'\t\tIf(Event Player.Zone == {z});')
    new += bodies[z]
    new.append('\t\tEnd;')
    new.append('\t}')
    new.append('}')
    new.append('')
new.pop()  # trailing blank

lines[start:end + 1] = new
out = '\n'.join(lines)

assert out.count('rule("') == 125, out.count('rule("')
for z in (9, 10, 11, 12):
    assert f'rule("[조작 {tags[z]}] 행동 실행 — {names[z]}")' in out
assert 'Else If(Event Player.Zone == 10);' not in out
assert '[조작 03c] 행동 실행 — 안내소·대장간·정거장·목장' not in out
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch140 ok rules=', out.count('rule("'))
