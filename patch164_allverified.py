# patch164: 나머지 6곳도 '검증된 좌표만' 방식으로 통일
#  밀수 접선지 / 금괴 호송 목적지 / 금고 마차 / 보물 상자 / 대사냥 흔적(2곳)
#  - 오프셋 + Nearest Walkable Position 제거 (벽 속·좁은 틈 배치의 원인)
#  - 스폰 근처는 밀어내지 말고 후보에서 제외
import io, re

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

POOL_G = 'Append To Array(Global Variable(RaidPath), Global Variable(LocPos))'
SAFE_G = f'Filtered Array({POOL_G}, Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)'
SAFE_LOC = ('Filtered Array(Global Variable(LocPos), '
            'Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)')

pairs = []

# --- 보물 상자 ---
old = re.search(r'Set Global Variable\(TreasurePos, Add\(Nearest Walkable Position\(.*?\), Vector\(0, 1, 0\)\)\);', t, re.S).group(0)
pairs.append((old, f'Set Global Variable(TreasurePos, Add(Random Value In Array({SAFE_G}), Vector(0, 1, 0)));'))

# --- 금고 마차 ---
old = re.search(r'Set Global Variable\(WagonPos, Add\(Nearest Walkable Position\(.*?\), Vector\(0, 1, 0\)\)\);', t, re.S).group(0)
pairs.append((old, f'Set Global Variable(WagonPos, Add(Random Value In Array({SAFE_G}), Vector(0, 1, 0)));'))

# --- 밀수 접선지 ---
old = re.search(r'Set Player Variable\(Event Player, SmugglePos, Nearest Walkable Position\(.*?\)\);\n', t, re.S).group(0)
ind = re.match(r'\s*', old).group(0)
pairs.append((old, f'Set Player Variable(Event Player, SmugglePos, Random Value In Array({SAFE_G}));\n'))

# --- 금괴 호송: '먼 건물' 규칙 유지, 오프셋/NWP만 제거 ---
old = re.search(r'Set Player Variable\(Event Player, EscortPos, Nearest Walkable Position\(Add\(Value In Array\(Global Variable\(LocPos\), Random Value In Array\(Array Slice\(.*?\)\)\)\);', t, re.S).group(0)
FAR = ('Value In Array(Global Variable(LocPos), Random Value In Array(Array Slice(Sorted Array('
       'Filtered Array(Array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12), '
       'Distance Between(Value In Array(Global Variable(LocPos), Current Array Element), Global Variable(SpawnPos)) >= 22), '
       'Distance Between(Value In Array(Global Variable(LocPos), Current Array Element), Value In Array(Global Variable(LocPos), 11))), 4, 8)))')
pairs.append((old, f'Set Player Variable(Event Player, EscortPos, {FAR});'))

for o, n in pairs:
    assert t.count(o) == 1, o[:70]
    t = t.replace(o, n)

# --- 대사냥 흔적 2곳: 밀어내기 제거하고 안전 후보에서 재추첨 ---
HUNT_OLD = ('Set Global Variable(HuntTrackPos, Nearest Walkable Position(Add(Global Variable(SpawnPos), '
            'Multiply(Direction From Angles(Random Real(-180, 180), 0), Random Real(30, 55)))));')
n_hunt = t.count(HUNT_OLD)
assert n_hunt == 2, n_hunt
t = t.replace(HUNT_OLD, f'Set Global Variable(HuntTrackPos, Random Value In Array({SAFE_LOC}));')

assert 'Direction From Angles(Random Real(-180, 180), 0), Random Real(30, 55)' not in t
assert 'Nearest Walkable Position' in t          # 다른 정당한 용도(소·쥐 등)는 남아 있어야 한다
assert t.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch164 ok — all 6 systems on verified coordinates')
