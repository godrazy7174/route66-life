# -*- coding: utf-8 -*-
"""[1] 작업 시간 단축 (게이지와 실제 대기를 항상 같은 값으로 유지)
[2] 모텔 취침을 수면총 맞은 것처럼 — Phased Out 대신 Asleep 상태
[3] 화면 떨림
    카메라 기준점이 Eye Position 이었다. 오버워치의 시점은 걸을 때
    머리가 위아래로 흔들리는데(head bob), 카메라 위치와 시선 지점을
    둘 다 거기에 매달아 놨으니 발걸음마다 화면이 같이 떨렸다.
    -> 흔들리지 않는 발밑 기준(Position Of)에 고정 높이 1.6m 를 더해 쓴다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
L = io.open(P, encoding='utf-8').read().split(chr(10))

# ── [1] 작업 시간 ──────────────────────────────────────────────────
SPEED = [
    (1352, '100, 4.5,', '100, 3.2,', '채굴 게이지'),
    (1354, 'Wait(4.5,', 'Wait(3.2,', '채굴 대기'),
    (1442, '100, 2.5,', '100, 1.8,', '흔적 추적 게이지'),
    (1443, 'Wait(2.5,', 'Wait(1.8,', '흔적 추적 대기'),
    (1618, '100, 3.5,', '100, 2.5,', '습격 계획 게이지'),
    (1619, 'Wait(3.5,', 'Wait(2.5,', '습격 계획 대기'),
    (1679, '100, 6,',   '100, 4.5,', '취침 게이지'),
    (1680, 'Wait(6,',   'Wait(4.5,', '취침 대기'),
    (1852, '100, 2.5,', '100, 1.8,', '강도/체포 게이지'),
]
for n, old, new, label in SPEED:
    i = n - 1
    assert old in L[i], (n, label)
    L[i] = L[i].replace(old, new, 1)
    print('  %-14s %s -> %s' % (label, old.strip(', '), new.strip(', ')))

i = 1853 - 1
assert 'Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 4);' in L[i]
L[i] = L[i].replace('Event Player.WorkProg >= 99), 4);', 'Event Player.WorkProg >= 99), 3);', 1)
print('  %-14s 4 -> 3' % '강도/체포 제한')

# ── [2] 취침 — 수면총 ──────────────────────────────────────────────
i = 1674 - 1
assert 'Set Status(Event Player, Null, Phased Out, 6.5);' in L[i]
L[i] = L[i].replace('Set Status(Event Player, Null, Phased Out, 6.5);',
                    'Set Status(Event Player, Null, Asleep, 4.6);\n'
                    '\t\tSet Status(Event Player, Null, Phased Out, 4.6);', 1)
# Asleep 이 이미 못 움직이게 하므로 위치 고정은 불필요 (쓰러지는 연출과도 충돌)
for n in (1673, 1683):
    i = n - 1
    assert 'Forcing Player Position' in L[i], n
for n in sorted((1673, 1683), reverse=True):
    L.pop(n - 1)
print('  취침           Phased Out 6.5초 -> Asleep + Phased Out 4.6초, 위치 고정 제거')

# ── [3] 카메라 기준점 ──────────────────────────────────────────────
s = chr(10).join(L)
EYE = 'Eye Position(Event Player)'
ANCHOR = 'Add(Position Of(Event Player), Vector(0, 1.6, 0))'
OLDC = ('Start Camera(Event Player, Ray Cast Hit Position(%(e)s, '
        'Add(%(e)s, Multiply(Facing Direction Of(Event Player), -3.2)), '
        'Empty Array, All Players(All Teams), False), '
        'Add(%(e)s, Multiply(Facing Direction Of(Event Player), 6)), 70);') % {'e': EYE}
NEWC = ('Start Camera(Event Player, Ray Cast Hit Position(%(a)s, '
        'Add(%(a)s, Multiply(Facing Direction Of(Event Player), -3.2)), '
        'Empty Array, All Players(All Teams), False), '
        'Add(%(a)s, Multiply(Facing Direction Of(Event Player), 6)), 70);') % {'a': ANCHOR}
n = s.count(OLDC)
assert n == 2, n
s = s.replace(OLDC, NEWC)
print('  카메라 기준점  Eye Position(머리 흔들림 포함) -> 발밑 + 1.6m 고정')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('완료')
