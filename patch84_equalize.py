# -*- coding: utf-8 -*-
"""전 직업 수익 균등화 — 사냥꾼 수준(분당 신입 ~300 / 숙련 ~400~460)으로 수렴.

  시뮬레이션 수렴값 (분당 순수익):
    광부 291/446 · 사냥꾼 302/398 · 파발꾼 287/444 · 목동 287/443 · 무법자 308/466

  변경:
    파발   거리 계수 2.4 -> 1.3
    무법자 결행 $80~160 -> $65~125
    목동   기본 $65 -> $165 · 목장주 배율 1.4 -> 1.15
    광부   탐사 보너스 22 -> 8pp · 금맥 레벨 보너스 캡 12 -> 4
           정밀 탐사 $45 -> $20 (보너스 축소에 맞춘 가격 인하)
    사냥꾼 맹수 사냥꾼 특전에 가죽 +1장 (승급 이득 +10% -> +32%)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
RN = chr(92) + 'r' + chr(92) + 'n'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

# ── 파발: 거리 계수 ────────────────────────────────────────────────
sub('Event Player.DelDest)), 2.4))', 'Event Player.DelDest)), 1.3))', 2)

# ── 무법자: 결행 보상 ──────────────────────────────────────────────
sub('Set Player Variable(Event Player, PlanPay, Random Integer(80, 160));',
    'Set Player Variable(Event Player, PlanPay, Random Integer(65, 125));')

# ── 목동: 기본 보수·목장주 배율 ────────────────────────────────────
sub('Set Player Variable(Event Player, RunPay, Add(65, Multiply(3, Min(10,',
    'Set Player Variable(Event Player, RunPay, Add(165, Multiply(3, Min(10,')
sub('Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, 1.4), To Nearest));',
    'Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, 1.15), To Nearest));')
sub('몰이 보수 +40% · 소가 더 성큼 밀린다', '몰이 보수 +15% · 소가 더 성큼 밀린다')

# ── 광부: 탐사 보너스·금맥 레벨 캡·탐사비 ──────────────────────────
sub('Modify Player Variable(Event Player, Roll, Subtract, 22);',
    'Modify Player Variable(Event Player, Roll, Subtract, 8);')
sub('Modify Player Variable(Event Player, Roll, Subtract, Min(12, Round To Integer(Divide(Value In Array(Event Player.JobXP, 1), 250), Down)));',
    'Modify Player Variable(Event Player, Roll, Subtract, Min(4, Round To Integer(Divide(Value In Array(Event Player.JobXP, 1), 250), Down)));')
sub('? 0 : 45);', '? 0 : 20);')
sub('정밀 탐사 — 다음 3회 채굴의 대박 확률 급상승', '정밀 탐사 — 다음 3회 채굴의 대박 확률 상승')
sub('Custom String("정밀 탐사 $45")', 'Custom String("정밀 탐사 $20")')
sub('정밀 탐사 $45' + RN, '정밀 탐사 $20' + RN)

# ── 사냥꾼: 승급 특전 가죽 +1 ──────────────────────────────────────
sub('Modify Player Variable(Attacker, Yield, Add, 1);',
    'Modify Player Variable(Attacker, Yield, Add, Add(1, Value In Array(Player Variable(Attacker, Adv), 2)));')
sub('내 추적에서 거대 야수 확률 1.5%', '내 추적에서 거대 야수 확률 1.5% · 가죽 +1장')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('수익 균등화 완료')
