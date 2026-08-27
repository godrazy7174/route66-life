# patch150 (전수조사 #1, #2)
#  [버그 A] 검증식의 자릿수 계산 오류로 마스터리(장인) 달성자의 세이브 코드가 항상 거부됨
#  [버그 B] 누적 수입(Earned)이 세이브에 없어 재접속 시 칭호가 초기화됨
#  → EnterC의 비어 있던 100·10 자리에 누적 수입(2000단위)을 담고, 잘못된 검증 항목을 제거
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

# --- 1) 패킹: SaveC에 누적 수입 2자리 추가 ---
OLD_PACK = ('Set Player Variable(Event Player, SaveC, Add(Add(Multiply(Event Player.Rebuild, 100000), '
            'Multiply(Event Player.Rebirth, 10000)), Multiply(Min(9, Round To Integer(Divide(Event Player.Giant, 10), Down)), 1000)));')
NEW_PACK = ('Set Player Variable(Event Player, SaveC, Add(Add(Add(Multiply(Event Player.Rebuild, 100000), '
            'Multiply(Event Player.Rebirth, 10000)), Multiply(Min(9, Round To Integer(Divide(Event Player.Giant, 10), Down)), 1000)), '
            'Multiply(Min(99, Round To Integer(Divide(Event Player.Earned, 2000), Down)), 10)));')
assert t.count(OLD_PACK) == 1
t = t.replace(OLD_PACK, NEW_PACK)

# --- 2) 검증식: 잘못된 미사용 자릿수 검사 제거 ---
OLD_V = 'Or(Modulo(Round To Integer(Divide(Event Player.EnterC, 10000), Down), 10) > 5, Modulo(Event Player.Roll, 1000) != 0)'
NEW_V = 'Modulo(Round To Integer(Divide(Event Player.EnterC, 10000), Down), 10) > 5'
assert t.count(OLD_V) == 1
t = t.replace(OLD_V, NEW_V)

# --- 3) 복원: 누적 수입 + DayStart 동기화(환생 가호 오지급 방지) ---
ANCHOR = 'Set Player Variable(Event Player, Giant, Multiply(Modulo(Round To Integer(Divide(Event Player.EnterC, 1000), Down), 10), 10));'
assert t.count(ANCHOR) == 1
lines = t.split('\n')
i = next(k for k, l in enumerate(lines) if ANCHOR in l)
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines[i + 1:i + 1] = [
    ind + 'Set Player Variable(Event Player, Earned, Multiply(Modulo(Event Player.Roll, 100), 2000));',
    ind + 'Set Player Variable(Event Player, DayStart, Event Player.Earned);',
]
t = '\n'.join(lines)

assert t.count('Modulo(Event Player.Roll, 1000)') == 0
assert t.count('Multiply(Modulo(Event Player.Roll, 100), 2000)') == 1
assert t.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch150 ok')
