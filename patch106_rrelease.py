# -*- coding: utf-8 -*-
"""핫픽스 — 스킬바 직후 [R] 잔류 입력이 행동 커서를 넘기는 문제.

[조작 01]은 Busy==0 조건이라 미니게임 중엔 안 돌지만, 판정 직후
Busy가 풀리는 순간 R이 아직 눌려 있으면 조건 전이로 커서가 1칸 이동.
DoSkillBar 종료부에 R 해제 대기(최대 3초)를 넣어 세 이벤트 공통 해결.
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

old = (T*2 + 'Destroy HUD Text(Event Player.KeyHud);' + N
       + T*2 + 'Set Player Variable(Event Player, WorkProg, 0);' + N)
new = (T*2 + 'Wait Until(Not(Is Button Held(Event Player, Button(Reload))), 3);' + N
       + old)
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('OK: R release wait added to DoSkillBar tail')
