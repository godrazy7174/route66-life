# -*- coding: utf-8 -*-
"""핫픽스 — 플레이어 변수 128 초과 (워크샵 한계 0~127).

patch95가 129번째 변수(128: RanchCare)를 선언해 인게임 오류
"243번째 줄의 '128'에 범위 밖의 변수" 발생.
Ranch 변수를 제거하고 소유 판정을 RanchPens >= 1 로 겸용해
124 RanchPens / 125 RanchEnd / 126 RanchReady / 127 RanchCare 로 재배치.
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

# 1. 선언부 — Ranch 제거, 뒤 번호 한 칸씩 당김
sub(T*2 + '124: Ranch' + N + T*2 + '125: RanchPens' + N + T*2 + '126: RanchEnd' + N
    + T*2 + '127: RanchReady' + N + T*2 + '128: RanchCare' + N,
    T*2 + '124: RanchPens' + N + T*2 + '125: RanchEnd' + N
    + T*2 + '126: RanchReady' + N + T*2 + '127: RanchCare' + N)

# 2. 소유 판정 치환 (건설 멀티플렉스 + 증설, 2곳)
sub('If(Event Player.Ranch == 0);', 'If(Event Player.RanchPens == 0);', 2)

# 3. 건설 시 Ranch=1 설정 제거 (바로 아래 RanchPens=1이 소유 표식)
sub(T*6 + 'Set Player Variable(Event Player, Ranch, 1);' + N, '')

# 4. 숙성 규칙 조건
sub(T*2 + 'Event Player.Ranch == 1;' + N, T*2 + 'Event Player.RanchPens >= 1;' + N)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('변수 한계 핫픽스 적용')
