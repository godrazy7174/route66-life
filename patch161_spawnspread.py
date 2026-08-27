# patch161: 보물 상자·금고 마차·밀수 접선지가 늘 비슷한 곳에만 나오는 문제
#  원인: '건물 좌표 + 작은 무작위 오프셋 -> Nearest Walkable Position' 방식은
#        협곡 지형에서 여러 오프셋이 같은 보행 지점으로 스냅되어 후보가 뭉친다.
#  해결: 절반의 확률로 '역마차 경로 위 연속 지점'을 후보로 쓰고(샛길에서 검증된 방식),
#        건물 쪽을 고를 때도 오프셋 범위를 넓혀 스냅 뭉침을 줄인다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

def path_pick(idx_expr):
    seg = f'Value In Array(Global Variable(RaidPath), {idx_expr})'
    nxt = f'Value In Array(Global Variable(RaidPath), Add({idx_expr}, 1))'
    return f'Add({seg}, Multiply(Subtract({nxt}, {seg}), Random Real(0.15, 0.85)))'

PATH_G = path_pick('Global Variable(Tmp)')          # 전역 규칙용
PATH_P = path_pick('Event Player.Roll')             # 플레이어 규칙용

# ---- 1) 보물 상자 (오프셋 14 -> 24, 절반은 경로 위) ----
OLD = ('Set Global Variable(TreasurePos, Add(Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), '
       'Random Integer(0, 10)), Vector(Random Real(-14, 14), 0, Random Real(-14, 14)))), Vector(0, 1, 0)));')
NEW = ('Set Global Variable(Tmp, Random Integer(0, 11));\n'
       '\t\tSet Global Variable(TreasurePos, Add(Nearest Walkable Position(Random Integer(1, 100) <= 50 ? '
       f'{PATH_G} : '
       'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 10)), Vector(Random Real(-24, 24), 0, Random Real(-24, 24)))), Vector(0, 1, 0)));')
assert t.count(OLD) == 1
t = t.replace(OLD, NEW)

# ---- 2) 금고 마차 (오프셋 22 -> 30, 절반은 경로 위) ----
OLD = ('Set Global Variable(WagonPos, Add(Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), '
       'Random Integer(0, 12)), Vector(Random Real(-22, 22), 0, Random Real(-22, 22)))), Vector(0, 1, 0)));')
NEW = ('Set Global Variable(Tmp, Random Integer(0, 11));\n'
       '\t\tSet Global Variable(WagonPos, Add(Nearest Walkable Position(Random Integer(1, 100) <= 50 ? '
       f'{PATH_G} : '
       'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-30, 30), 0, Random Real(-30, 30)))), Vector(0, 1, 0)));')
assert t.count(OLD) == 1
t = t.replace(OLD, NEW)

# ---- 3) 밀수 접선지 (오프셋 10 -> 20, 절반은 경로 위) ----
OLD = ('Set Player Variable(Event Player, SmugglePos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), '
       'Random Integer(0, 12)), Vector(Random Real(-10, 10), 0, Random Real(-10, 10)))));')
NEW = ('Set Player Variable(Event Player, Roll, Random Integer(0, 11));\n'
       '\t\t\t\tSet Player Variable(Event Player, SmugglePos, Nearest Walkable Position(Random Integer(1, 100) <= 50 ? '
       f'{PATH_P} : '
       'Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-20, 20), 0, Random Real(-20, 20)))));')
assert t.count(OLD) == 1
t = t.replace(OLD, NEW)

assert t.count('Random Integer(1, 100) <= 50 ? Add(Value In Array(Global Variable(RaidPath)') == 3
assert t.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch161 ok')
