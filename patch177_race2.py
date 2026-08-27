# -*- coding: utf-8 -*-
"""축 2 — 사망 시 남는 불완전 상태 2건.

A) 유치장에서 죽으면 감옥 상태가 그대로 남는다.
   총격 판정은 Phased Out을 제외하도록 고쳤지만, [월드 03] 결핍 패널티의
   자해 피해(허기·갈증 0이면 5초마다 8)는 유치장 안에서도 들어간다.
   체포는 '체력 절반 미만'이 조건이라 반쯤 죽은 채로 갇히는 게 정상이고,
   굶주린 상태라면 형기 50초 안에 죽을 수 있다.
   그렇게 죽으면 JailOn이 1로 남고 Set Primary Fire Enabled(False)도
   상태이상이 아니라 사망으로 풀리지 않아, 식당에 서서 총을 못 쏘는
   기묘한 상태가 된다. 게다가 [감옥 02] 벽 부수기가 여전히 성립해
   식당 한복판에서 '탈옥'이 가능해진다.
   -> 죽으면 형을 치른 것으로 보고 감옥 상태를 깨끗이 푼다.
      (만기 출소의 악명 -20 보상은 주지 않는다)

B) 튜토리얼 중에도 허기·갈증이 줄어 굶어 죽을 수 있다.
   튜토리얼은 슬라이드마다 입력을 기다리므로 시간 제한이 없고,
   방치하면 결핍 피해로 사망 -> 카메라 연출 도중 식당으로 튕긴다.
   -> 튜토리얼 중에는 욕구가 줄지 않게 한다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()

# A) 사망 처리에 감옥 해제
old = ('\t\tSet Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));\n'
       '\t\tSet Player Variable(Event Player, Thirst, Max(Event Player.Thirst, 40));\n')
assert src.count(old) == 1
new = ('\t\tIf(Event Player.JailOn == 1);\n'
       '\t\t\tSet Player Variable(Event Player, JailOn, 0);\n'
       '\t\t\tClear Status(Event Player, Rooted);\n'
       '\t\t\tClear Status(Event Player, Phased Out);\n'
       '\t\t\tSet Primary Fire Enabled(Event Player, True);\n'
       '\t\t\tSmall Message(Event Player, Custom String("유치장에서 쓰러졌다 — 죗값은 치른 셈이 됐다"));\n'
       '\t\tEnd;\n') + old
src = src.replace(old, new)
print('  OK 사망 처리 — 유치장 상태 해제')

# B) 튜토리얼 중 욕구 감소 정지
old = ('\t\tWait(10, Ignore Condition);\n'
       '\t\tSet Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.2)));\n'
       '\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, '
       'Event Player.Rebuild >= 1 ? 1.2 : 1.5)));\n'
       '\t\tSet Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 0.5)));\n')
assert src.count(old) == 1
new = ('\t\tWait(10, Ignore Condition);\n'
       '\t\tIf(Event Player.TutOn == 0);\n'
       '\t\t\tSet Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.2)));\n'
       '\t\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, '
       'Event Player.Rebuild >= 1 ? 1.2 : 1.5)));\n'
       '\t\t\tSet Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 0.5)));\n'
       '\t\tEnd;\n')
src = src.replace(old, new)
print('  OK 욕구 감소 — 튜토리얼 중 정지')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('done')
