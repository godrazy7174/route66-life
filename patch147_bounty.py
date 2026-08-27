# patch147: 현상금 사냥꾼 — 배지 조건(명성 30 / 악명 20 이하) + 상시 이동 속도 115%
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# ---- 1) 이동 속도 복원 3곳 뒤에 현상금 사냥꾼 보정 ----
BASE = 'Set Move Speed(Event Player, And(Event Player.HasBag == 0, Event Player.HasHorse == 0) ? 110 : 100);'
idxs = [i for i, l in enumerate(lines) if l.strip() == BASE]
assert len(idxs) == 3, len(idxs)
for i in reversed(idxs):
    ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
    lines[i + 1:i + 1] = [
        ind + 'If(Event Player.Job == 3);',
        ind + '\tSet Move Speed(Event Player, 115);',
        ind + 'End;',
    ]

# ---- 2) 배지 수령 조건 ----
g = next(i for i, l in enumerate(lines) if '이미 현상금 사냥꾼이다' in l)
head = g - 1
assert lines[head].strip() == 'If(Event Player.Job == 3);', lines[head]
tail = next(i for i in range(g, len(lines)) if lines[i].strip() == 'Else;')
assert tail - g < 5, (g, tail)
ind = lines[head][:len(lines[head]) - len(lines[head].lstrip('\t'))]
gate = [
    ind + 'Else If(Event Player.Fame < 30);',
    ind + '\tSmall Message(Event Player, Custom String("마을의 신뢰가 모자란다 — 명성 {0} / 30", Event Player.Fame));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
    ind + 'Else If(Event Player.Noto > 20);',
    ind + '\tSmall Message(Event Player, Custom String("죄지은 손에 배지를 맡길 수는 없다 — 악명 {0} (20 이하라야 한다)", Event Player.Noto));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
]
lines[tail:tail] = gate

out = '\n'.join(lines)
assert out.count('Set Move Speed(Event Player, 115);') == 3
assert out.count('명성 {0} / 30') == 1
assert out.count('악명 {0} (20 이하라야 한다)') == 1
assert out.count('rule("') == 129
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch147 ok')
