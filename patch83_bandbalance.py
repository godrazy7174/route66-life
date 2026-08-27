# -*- coding: utf-8 -*-
"""수익 밴드 정렬 — 전 직업 평균을 목동~파발꾼 사이로 (시뮬레이션 수렴값).

  광부   연속 보너스 상한 25 (트리거당 최대 $100)          294/564 $/분
  사냥꾼 가죽 4~6+3+Lv5 -> 1~2+1+Lv2 · 시세 6~12 -> 4~7    518/614 $/분
         큰놈 15%·$150 -> 10%·$60 · 거대 +$400 -> +$50
         전설 +$2000 -> +$250 (가죽 50배·거대 5배는 유지)
         맹수 사냥꾼 특전: 거대·전설 2배 -> 거대 11->15%
  무법자 정찰 $10~20 -> $8~15 · 결행 $150~300 -> $80~160   389/589 $/분
  파발꾼·목동 = 밴드 경계, 무변경 (527/789 · 108/234)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

# ── 광부: 연속 보너스 상한 ─────────────────────────────────────────
sub('Set Player Variable(Event Player, StreakPay, Multiply(Event Player.Streak, 4));',
    'Set Player Variable(Event Player, StreakPay, Multiply(Min(Event Player.Streak, 25), 4));')

# ── 사냥꾼: 가죽량·현금 보너스·시세·특전 ──────────────────────────
sub('Set Player Variable(Attacker, Yield, Random Integer(4, 6));',
    'Set Player Variable(Attacker, Yield, Random Integer(1, 2));')
sub('Modify Player Variable(Attacker, Yield, Add, 3);',
    'Modify Player Variable(Attacker, Yield, Add, 1);')
sub('Modify Player Variable(Attacker, Yield, Add, Min(5, Round To Integer(Divide(Value In Array(Player Variable(Attacker, JobXP), 2), 250), Down)));',
    'Modify Player Variable(Attacker, Yield, Add, Min(2, Round To Integer(Divide(Value In Array(Player Variable(Attacker, JobXP), 2), 250), Down)));')
sub('Modify Player Variable(Attacker, Money, Add, 2000);', 'Modify Player Variable(Attacker, Money, Add, 250);')
sub('Modify Player Variable(Attacker, Earned, Add, 2000);', 'Modify Player Variable(Attacker, Earned, Add, 250);')
sub('가죽 +{1}장 + $2000', '가죽 +{1}장 + $250')
sub('Modify Player Variable(Attacker, Money, Add, 400);', 'Modify Player Variable(Attacker, Money, Add, 50);')
sub('Modify Player Variable(Attacker, Earned, Add, 400);', 'Modify Player Variable(Attacker, Earned, Add, 50);')
sub('가죽 +{1}장 + $400', '가죽 +{1}장 + $50')
sub('Else If(Random Integer(1, 100) <= 15);', 'Else If(Random Integer(1, 100) <= 10);')
sub('Modify Player Variable(Attacker, Money, Add, 150);', 'Modify Player Variable(Attacker, Money, Add, 60);')
sub('Modify Player Variable(Attacker, Earned, Add, 150);', 'Modify Player Variable(Attacker, Earned, Add, 60);')
sub('가죽 +{1}장 + $150', '가죽 +{1}장 + $60')
sub('Add(11, Multiply(10, Event Player.Roll))', 'Add(11, Multiply(4, Event Player.Roll))')
sub('<= Add(1, Event Player.Roll));', '<= 1);')
sub('Set Global Variable(HidePrice, Random Integer(6, 12));',
    'Set Global Variable(HidePrice, Random Integer(4, 7));')
sub('내 추적에서 거대·전설 야수 확률 2배', '내 추적에서 거대 야수 확률 15%')

# ── 무법자: 정찰비·결행 보상 ───────────────────────────────────────
sub('Set Player Variable(Event Player, PlanPay, Random Integer(10, 20));',
    'Set Player Variable(Event Player, PlanPay, Random Integer(8, 15));')
sub('Set Player Variable(Event Player, PlanPay, Random Integer(150, 300));',
    'Set Player Variable(Event Player, PlanPay, Random Integer(80, 160));')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('밴드 정렬 완료: 광부 스트릭 캡 25 · 사냥꾼 축소 · 무법자 축소')
