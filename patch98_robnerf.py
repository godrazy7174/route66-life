# -*- coding: utf-8 -*-
"""강도/체포 채널 밸런스 조정.

채널 시간을 늘리고, 시전자 체력 스냅샷을 이용해 피격 시 채널을
중단하며, 실패 재사용 대기시간과 피해자 안내 문구를 조정한다.
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

# 1. 채널 시작 체력 스냅샷 (기존 Take 변수 재사용)
sub(T*2 + 'Set Player Variable(Event Player, Busy, 1);' + N
    + T*2 + 'Set Player Variable(Event Player, WorkProg, 0);' + N
    + T*2 + 'If(Player Variable(Event Player.Target, Bounty) > 0);',
    T*2 + 'Set Player Variable(Event Player, Busy, 1);' + N
    + T*2 + 'Set Player Variable(Event Player, WorkProg, 0);' + N
    + T*2 + 'Set Player Variable(Event Player, Take, Health(Event Player));' + N
    + T*2 + 'If(Player Variable(Event Player.Target, Bounty) > 0);')

# 2. 체포/강도 채널 시간 증가
sub('? 1.2 : 1.8, Destination and Duration',
    '? 2 : 3, Destination and Duration')

# 3. 거리 이탈/사망뿐 아니라 피격 시에도 채널 대기 중단
sub('Wait Until(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3);',
    'Wait Until(Or(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3.5);')

# 4. 피격 중단을 실패 분기로 연결
sub('If(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Not(Is Alive(Event Player))));',
    'If(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))));')

# 5. 피해자에게 반격 가능 안내
sub('{0}이(가) 당신을 체포하려 한다 — 도망쳐라',
    '{0}이(가) 당신을 체포하려 한다 — 도망치거나 쏴서 뿌리쳐라')
sub('{0}이(가) 총을 겨눴다 — 도망쳐라',
    '{0}이(가) 총을 겨눴다 — 도망치거나 쏴서 뿌리쳐라')

# 6. 실패 재사용 대기시간 증가 (놓침/빈털터리 분기)
sub('Set Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 6));',
    'Set Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 10));', 2)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('강도/체포 채널 밸런스 조정 적용')
