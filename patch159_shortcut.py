# patch159: 샛길이 늘 같은 자리에만 뜨는 문제 (3번째 시도 — 근본 원인 교정)
#  원인: 후보가 '점 26개(역마차 웨이포인트 13 + 건물 13)'로 유한한데, 거기서
#        '내 주변 12~34m'로 거르면 대부분의 위치에서 후보가 1개만 남아 늘 같은 곳이 뽑혔다.
#  해결: 후보를 점 목록이 아니라 '역마차 경로 12개 구간 위의 연속 지점'으로 바꾼다.
#        구간을 무작위로 고르고 그 구간 안에서도 무작위 비율을 잡으므로 후보가 사실상 무한하다.
#        경로는 사용자가 직접 걸어 만든 것이라 반드시 도달 가능하다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

start = next(i for i, l in enumerate(lines)
             if 'If(Count Of(Filtered Array(Append To Array(Global Variable(RaidPath), Global Variable(LocPos))' in l)
end = next(i for i in range(start, len(lines))
           if 'Vector(Random Real(-4, 4), 0, Random Real(-4, 4))' in lines[i])
ind = lines[start][:len(lines[start]) - len(lines[start].lstrip('\t'))]

SEG = 'Value In Array(Global Variable(RaidPath), Event Player.Roll)'
NXT = 'Value In Array(Global Variable(RaidPath), Add(Event Player.Roll, 1))'
PICK = (f'Set Player Variable(Event Player, DialTgt, Add({SEG}, '
        f'Multiply(Subtract({NXT}, {SEG}), Random Real(0.1, 0.9))));')

body = [
    ind + 'Set Player Variable(Event Player, Roll, Random Integer(0, 11));',
    ind + PICK,
    # 너무 가까우면 다른 구간으로 한 번 더 뽑는다
    ind + 'If(Distance Between(Event Player.DialTgt, Position Of(Event Player)) < 9);',
    ind + '\tSet Player Variable(Event Player, Roll, Modulo(Add(Event Player.Roll, Random Integer(4, 8)), 12));',
    ind + '\t' + PICK,
    ind + 'End;',
    ind + ('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Event Player.DialTgt, '
           'Vector(Random Real(-3, 3), 0, Random Real(-3, 3)))));'),
]
lines[start:end + 1] = body

out = '\n'.join(lines)
assert out.count('Set Player Variable(Event Player, Roll, Random Integer(0, 11));') == 1
assert out.count(PICK) == 2
assert 'Append To Array(Global Variable(RaidPath), Global Variable(LocPos))' not in out
assert out.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch159 ok')
