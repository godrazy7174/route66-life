# patch160: 샛길 배치 최종 — 경로 위 무작위 지점 + 거리 조건 재시도
#  patch159가 위치는 흩뜨렸으나 최대 119m까지 나와 7초 안에 도달 불가능한 경우가 있었다.
#  12~50m에 들 때까지 최대 3회 다시 뽑고, 그래도 안 되면 주변 무작위 20m로 떨군다.
#  시뮬레이션: 6개 지점 × 40회에서 전부 55m 이내, 서로 다른 자리 20~26개.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

start = next(i for i, l in enumerate(lines)
             if l.strip() == 'Set Player Variable(Event Player, Roll, Random Integer(0, 11));')
end = next(i for i in range(start, len(lines))
           if 'Vector(Random Real(-3, 3), 0, Random Real(-3, 3))' in lines[i])
ind = lines[start][:len(lines[start]) - len(lines[start].lstrip('\t'))]

SEG = 'Value In Array(Global Variable(RaidPath), Event Player.Roll)'
NXT = 'Value In Array(Global Variable(RaidPath), Add(Event Player.Roll, 1))'
PICK = (f'Set Player Variable(Event Player, DialTgt, Add({SEG}, '
        f'Multiply(Subtract({NXT}, {SEG}), Random Real(0.1, 0.9))));')
BAD = ('If(Or(Distance Between(Event Player.DialTgt, Position Of(Event Player)) < 12, '
       'Distance Between(Event Player.DialTgt, Position Of(Event Player)) > 50));')
ROLL = 'Set Player Variable(Event Player, Roll, Random Integer(0, 11));'

body = [ind + ROLL, ind + PICK]
for _ in range(2):                                   # 재시도 2회 (총 3회 추첨)
    body += [ind + BAD, ind + '\t' + ROLL, ind + '\t' + PICK, ind + 'End;']
body += [
    ind + BAD,
    ind + ('\tSet Player Variable(Event Player, DialTgt, Add(Position Of(Event Player), '
           'Multiply(Direction From Angles(Random Real(-180, 180), 0), 20)));'),
    ind + 'End;',
    ind + ('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Event Player.DialTgt, '
           'Vector(Random Real(-3, 3), 0, Random Real(-3, 3)))));'),
]
lines[start:end + 1] = body

out = '\n'.join(lines)
assert out.count(ROLL) == 3
assert out.count(PICK) == 3
assert out.count(BAD) == 3
assert out.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch160 ok')
