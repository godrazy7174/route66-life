# patch166: 나머지 4개 시스템도 '검증된 좌표만' 방식으로 통일
#  보물 상자 / 금고 마차 / 금괴 호송 / 대사냥 흔적(2곳)
#  오프셋과 Nearest Walkable Position을 제거해 벽 속·좁은 틈 배치를 원천 차단한다.
import io, re

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

POOL = 'Append To Array(Global Variable(RaidPath), Global Variable(LocPos))'
SAFE = 'Filtered Array(' + POOL + ', Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)'
SAFE_LOC = ('Filtered Array(Global Variable(LocPos), '
            'Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)')

def swap(pattern, repl, label):
    global t
    m = re.search(pattern, t, re.S)
    assert m, label
    t = t[:m.start()] + repl + t[m.end():]
    print('  ' + label + ' ok')

swap(r'Set Global Variable\(TreasurePos, Add\(Nearest Walkable Position\(.*?\), Vector\(0, 1, 0\)\)\);',
     'Set Global Variable(TreasurePos, Add(Random Value In Array(' + SAFE + '), Vector(0, 1, 0)));', '보물 상자')

swap(r'Set Global Variable\(WagonPos, Add\(Nearest Walkable Position\(.*?\), Vector\(0, 1, 0\)\)\);',
     'Set Global Variable(WagonPos, Add(Random Value In Array(' + SAFE + '), Vector(0, 1, 0)));', '금고 마차')

FAR = ('Value In Array(Global Variable(LocPos), Random Value In Array(Array Slice(Sorted Array('
       'Filtered Array(Array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12), '
       'Distance Between(Value In Array(Global Variable(LocPos), Current Array Element), Global Variable(SpawnPos)) >= 22), '
       'Distance Between(Value In Array(Global Variable(LocPos), Current Array Element), Value In Array(Global Variable(LocPos), 11))), 4, 8)))')
swap(r'Set Player Variable\(Event Player, EscortPos, Nearest Walkable Position\(Add\(Value In Array\(Global Variable\(LocPos\), Random Value In Array\(Array Slice\(.*?\)\)\)\);',
     'Set Player Variable(Event Player, EscortPos, ' + FAR + ');', '금괴 호송')

# 스폰 회피 '밀어내기'는 전부 제거 — 후보 필터로 대체됨
HUNT = ('Set Global Variable(HuntTrackPos, Nearest Walkable Position(Add(Global Variable(SpawnPos), '
        'Multiply(Direction From Angles(Random Real(-180, 180), 0), Random Real(30, 55)))));')
n = t.count(HUNT)
assert n == 2, n
t = t.replace(HUNT, 'Set Global Variable(HuntTrackPos, Random Value In Array(' + SAFE_LOC + '));')
print('  대사냥 흔적 ok (2곳)')

# 남은 밀어내기(호송/밀수/금고/보물)도 정리
LEFT = re.findall(r'[^\n]*Direction From Angles\(Random Real\(-180, 180\), 0\), Random Real\(30, 55\)[^\n]*', t)
for l in LEFT:
    print('  남은 밀어내기 제거 대상:', l.strip()[:80])
assert t.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch166 ok')
