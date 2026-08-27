# patch144 (작업 8): 늑대 무시 플레이 봉쇄 3중 수정
#  (1) 소 스폰 거리 35~55m -> 55~85m (몰이 구간 확보)
#  (2) 목장 25m 안에서는 늑대 미출현
#  (3) 늑대가 붙어 있는 동안 우리 정산 보류
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def one(sub):
    idxs = [i for i, l in enumerate(lines) if sub in l]
    assert len(idxs) == 1, f'{sub!r}: {len(idxs)}'
    return idxs[0]

# ---- (1) 스폰 거리 ----
i = one('Random Real(35, 55)')
lines[i] = lines[i].replace('Random Real(35, 55)', 'Random Real(55, 85)')

# ---- (2) 목장 근처에서는 늑대 미출현 ----
i = one('If(And(And(Event Player.CowOn >= 1, Is Alive(Event Player)), Random Integer(1, 100) <= 45));')
lines[i] = lines[i].replace(
    'Random Integer(1, 100) <= 45));',
    'And(Random Integer(1, 100) <= 45, Distance Between(Event Player.CowPos, Value In Array(Global Variable(LocPos), 12)) > 25)));')

# ---- (2b) 늑대 상태 초기화: 소몰이 시작 시 '늑대 없음'으로 ----
i = one('Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 12), Multiply(Direction Towards(Value In Array(Global Variable(LocPos), 12)')
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines.insert(i + 1, ind + 'Set Player Variable(Event Player, DialCur, 99);')

# ---- (3) 늑대 활성 중 정산 보류 ----
i = one('If(Distance Between(Event Player.CowPos, Value In Array(Global Variable(LocPos), 12)) < 6);')
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
guard = [
    ind + 'If(And(Event Player.DialCur < 12, Event Player.DialPin < 3));',
    ind + '\tSmall Message(Event Player, Custom String("늑대가 소에 붙어 있다 — 쫓아내야 우리에 넣는다"));',
    ind + '\tWait(1, Ignore Condition);',
    ind + '\tAbort;',
    ind + 'End;',
]
lines[i:i] = guard

out = '\n'.join(lines)
assert out.count('Random Real(55, 85)') == 1
assert out.count('늑대가 소에 붙어 있다') == 1
assert out.count('Set Player Variable(Event Player, DialCur, 99);') == 2
assert out.count('rule("') == 129
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch144 ok')
