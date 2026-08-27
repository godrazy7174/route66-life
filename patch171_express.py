# -*- coding: utf-8 -*-
"""[파발 02]에 급행 우편을 편지와 나란히 붙인다.

배달 한 건당 이벤트 하나. 받을 사람이 있으면 50%로 편지, 아니면 급행.
솔로면 받을 사람이 없으니 항상 급행 -> 솔로·멀티 모두 이벤트가 빈다.

둘을 동시에 띄우지 않는 이유: 편지는 우회를 요구하고 급행은 우회를 벌한다.
같이 뜨면 서로를 무효화한다.

급행 성공 판정은 HasParcel == 0만으로는 안 된다 (강탈·취소로도 0이 된다).
[파발 01]의 도착 조건과 같은 Zone == DelDest를 함께 봐서 실제 배달만 인정한다.
마감 시각은 그 갈래에서 놀고 있는 DialTgt에 담는다 — 새 플레이어 변수 0개.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()

a = src.index('rule("[파발 02] 겸사겸사 편지 한 통")')
b = src.index('rule("[파발 03] 그림자 강도")')
blk = src[a:b]

# 1) 편지 갈래에 50% 주사위를 건다
old = '\t\t\tIf(Entity Exists(Event Player.DialTgt));\n'
assert blk.count(old) == 1
blk = blk.replace(old, '\t\t\tIf(And(Entity Exists(Event Player.DialTgt), Random Integer(1, 100) <= 50));\n')

# 2) Else 갈래로 급행 우편
EXPRESS = (
    '\t\t\tElse;\n'
    '\t\t\t\tSet Player Variable(Event Player, DialTgt, Add(Total Time Elapsed(), Add(3, Divide(Distance Between('
    'Position Of(Event Player), Value In Array(Global Variable(LocPos), Event Player.DelDest)), 6))));\n'
    '\t\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String('
    '"급행이다! {0}초 안에 도착하면 보수 2배", Round To Integer(Subtract(Event Player.DialTgt, Total Time Elapsed()), Up)));\n'
    '\t\t\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 3));\n'
    '\t\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 45);\n'
    '\t\t\t\tWait Until(Or(Or(Event Player.HasParcel == 0, Event Player.Busy == 1), Or(Not(Is Alive(Event Player)), '
    'Total Time Elapsed() >= Event Player.DialTgt)), 120);\n'
    '\t\t\t\tIf(And(And(Event Player.HasParcel == 0, Event Player.Zone == Event Player.DelDest), '
    'Total Time Elapsed() < Event Player.DialTgt));\n'
    '\t\t\t\t\tModify Player Variable(Event Player, Money, Add, Event Player.RunPay);\n'
    '\t\t\t\t\tModify Player Variable(Event Player, Earned, Add, Event Player.RunPay);\n'
    '\t\t\t\t\tSmall Message(Event Player, Custom String("급행 성공! 보수 2배 — 추가 +$ {0}", Event Player.RunPay));\n'
    '\t\t\t\t\tPlay Effect(Event Player, Ring Explosion, Color(Orange), Position Of(Event Player), 1.2);\n'
    '\t\t\t\tElse If(And(Event Player.HasParcel >= 1, Is Alive(Event Player)));\n'
    '\t\t\t\t\tSmall Message(Event Player, Custom String("급행 시간을 넘겼다 — 보수는 그대로다"));\n'
    '\t\t\t\tEnd;\n')

# 편지 갈래를 닫는 End; (3탭) 앞에 끼운다
close = '\t\t\t\tEnd;\n\t\t\tEnd;\n\t\tEnd;\n'
assert blk.count(close) == 1, '닫는 End 묶음 %d건' % blk.count(close)
blk = blk.replace(close, '\t\t\t\tEnd;\n' + EXPRESS + '\t\t\tEnd;\n\t\tEnd;\n')

blk = blk.replace('rule("[파발 02] 겸사겸사 편지 한 통")', 'rule("[파발 02] 편지 · 급행 우편")')

src = src[:a] + blk + src[b:]

# 튜토리얼 문구에 급행도 한 줄
tut_old = r"\r\n편지가 딸려오면 표식이 붙은 사람에게 건네라."
tut_new = r"\r\n편지가 딸려오면 건네고, 급행이 걸리면 달려라."
assert src.count(tut_old) == 1
src = src.replace(tut_old, tut_new)

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('급행 우편 추가 — 편지 50% / 급행 50%, 솔로는 급행 100%')
