# patch145: 늑대 가드를 '우리 도착 판정' 안으로 이동
#  기존 위치는 소 밀기 로직(Abort로 스킵)까지 막고 메시지를 1초마다 반복했다.
#  이동 후: 소는 정상적으로 밀리고, 우리에 도착했을 때만 정산이 보류된다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

g = next(i for i, l in enumerate(lines) if '늑대가 소에 붙어 있다' in l)
start = g - 1                       # If(And(DialCur < 12, ...));
assert lines[start].strip() == 'If(And(Event Player.DialCur < 12, Event Player.DialPin < 3));', lines[start]
assert lines[g + 1].strip() == 'Wait(1, Ignore Condition);'
assert lines[g + 2].strip() == 'Abort;'
assert lines[g + 3].strip() == 'End;'
del lines[start:g + 4]

# 우리 도착 판정 바로 다음 줄에 한 단계 깊은 들여쓰기로 재삽입
i = next(k for k, l in enumerate(lines)
         if 'If(Distance Between(Event Player.CowPos, Value In Array(Global Variable(LocPos), 12)) < 6);' in l)
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))] + '\t'
guard = [
    ind + 'If(And(Event Player.DialCur < 12, Event Player.DialPin < 3));',
    ind + '\tSmall Message(Event Player, Custom String("늑대가 소에 붙어 있다 — 쫓아내야 우리에 넣는다"));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 50);',
    ind + '\tWait(2, Ignore Condition);',
    ind + '\tAbort;',
    ind + 'End;',
]
lines[i + 1:i + 1] = guard

out = '\n'.join(lines)
assert out.count('늑대가 소에 붙어 있다') == 1
assert out.count('rule("') == 129
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch145 ok')
