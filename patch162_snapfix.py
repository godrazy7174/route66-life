# patch162: 스폰 위치가 한 곳으로 뭉치는 진짜 원인 교정
#  원인: 협곡은 고저차가 커서 '건물 좌표 + 큰 수평 오프셋'은 대부분 공중/절벽 속이 된다.
#        그 지점을 Nearest Walkable Position으로 보내면 전부 같은 통로 바닥으로 스냅된다.
#        오프셋이 클수록 심해진다 — patch161에서 오프셋을 키운 것은 잘못된 처방이었다.
#  해결: 오프셋을 아주 작게(±5~7m) 줄여 스냅이 원래 지점을 지키게 하고,
#        다양성은 '후보 개수'로 확보한다(건물 13곳 + 역마차 경로 12구간의 연속 지점).
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

def path(idx):
    seg = f'Value In Array(Global Variable(RaidPath), {idx})'
    nxt = f'Value In Array(Global Variable(RaidPath), Add({idx}, 1))'
    return f'Add({seg}, Multiply(Subtract({nxt}, {seg}), Random Real(0.15, 0.85)))'

PG, PP = path('Global Variable(Tmp)'), path('Event Player.Roll')

PAIRS = [
 # 보물 상자 — 오프셋 24 -> 6
 (f'Set Global Variable(TreasurePos, Add(Nearest Walkable Position(Random Integer(1, 100) <= 50 ? {PG} : '
  'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-24, 24), 0, Random Real(-24, 24)))), Vector(0, 1, 0)));',
  f'Set Global Variable(TreasurePos, Add(Nearest Walkable Position(Random Integer(1, 100) <= 50 ? {PG} : '
  'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-6, 6), 0, Random Real(-6, 6)))), Vector(0, 1, 0)));'),
 # 금고 마차 — 30 -> 7
 (f'Set Global Variable(WagonPos, Add(Nearest Walkable Position(Random Integer(1, 100) <= 50 ? {PG} : '
  'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-30, 30), 0, Random Real(-30, 30)))), Vector(0, 1, 0)));',
  f'Set Global Variable(WagonPos, Add(Nearest Walkable Position(Random Integer(1, 100) <= 50 ? {PG} : '
  'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-7, 7), 0, Random Real(-7, 7)))), Vector(0, 1, 0)));'),
 # 밀수 — 20 -> 6
 (f'Set Player Variable(Event Player, SmugglePos, Nearest Walkable Position(Random Integer(1, 100) <= 50 ? {PP} : '
  'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-20, 20), 0, Random Real(-20, 20)))));',
  f'Set Player Variable(Event Player, SmugglePos, Nearest Walkable Position(Random Integer(1, 100) <= 50 ? {PP} : '
  'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-6, 6), 0, Random Real(-6, 6)))));'),
 # 금괴 호송 — 26 -> 8
 ('Vector(Random Real(-26, 26), 0, Random Real(-26, 26))', 'Vector(Random Real(-8, 8), 0, Random Real(-8, 8))'),
 # 샛길 — 흔들기 3 -> 2 (경로 위 지점을 최대한 유지)
 ('Vector(Random Real(-3, 3), 0, Random Real(-3, 3))', 'Vector(Random Real(-2, 2), 0, Random Real(-2, 2))'),
]
for o, n in PAIRS:
    c = t.count(o)
    assert c == 1, f'{c}: {o[:70]}'
    t = t.replace(o, n)

# 보물 상자는 건물 후보가 0~10이었다 — 정거장/목장(11,12)도 포함되도록 이미 위에서 0~12로 통일됨
assert t.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch162 ok')
