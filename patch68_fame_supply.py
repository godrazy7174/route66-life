# -*- coding: utf-8 -*-
"""[1] 평판을 명성/악명 이원으로 분리.

    명성(Fame, 0~100)  선행: 체포 +12, 처단 +8, NPC 무법자 처치 +2, 일일 목표 +3
    악명(Noto, 0~100)  악행: 살해 +20, 강탈 +15, 습격 +15, 장물 +5, 무법자 합류 +5
    청산: 벌금 납부 악명 -40, 체포당하면 악명 -30(죗값), 매일 아침 악명 -2(소문 잦아듦)
    가격 연동은 순평판(명성-악명)으로 기존 공식 유지.
    악명 게이트: 무법자 합류에 악명 20 필요("애송이는 안 받는다"),
               악명 50+ 무법자는 장물 165% -> 180%.
    위스키의 평판 -1은 삭제(술 한잔에 악명은 과함).

[4] 육포 재고 공급망 (라이트).
    잡화점 육포 재고(시작 15, 최대 60)가 있어야 육포를 판다.
    사냥꾼이 야수를 잡으면 +1, 목동이 소를 우리에 넣으면 +6 자동 납품.
    재고가 마르면 마을 식량이 사냥꾼·목동 손에 달린다.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

NET = 'Subtract(Event Player.Fame, Event Player.Noto)'

# ══ [1] 변수 ══════════════════════════════════════════════════════
sub('\t\t6: Rep\n', '\t\t6: Fame\n')
sub('\t\t72: CowEnd\n', '\t\t72: CowEnd\n\t\t73: Noto\n')
sub('\t\tSet Player Variable(Event Player, Rep, 0);\n',
    '\t\tSet Player Variable(Event Player, Fame, 0);\n\t\tSet Player Variable(Event Player, Noto, 0);\n')

# ── 가격 공식: 순평판으로 ──────────────────────────────────────────
n = s.count('Multiply(Event Player.Rep, 0.002)')
assert n == 8, n
s = s.replace('Multiply(Event Player.Rep, 0.002)', 'Multiply(%s, 0.002)' % NET)
n = s.count('Multiply(Event Player.Rep, 0.0015)')
assert n == 3, n
s = s.replace('Multiply(Event Player.Rep, 0.0015)', 'Multiply(%s, 0.0015)' % NET)

# ── 선행 -> 명성 ───────────────────────────────────────────────────
sub('Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 3)));',
    'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 3)));')
sub('Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 10)));',
    'Set Player Variable(Event Player, Noto, Max(0, Subtract(Event Player.Noto, 40)));')
sub('Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 2)));',
    'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));')
sub('Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 12)));',
    'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 12)));')
sub('Set Player Variable(Attacker, Rep, Min(100, Add(Player Variable(Attacker, Rep), 8)));',
    'Set Player Variable(Attacker, Fame, Min(100, Add(Player Variable(Attacker, Fame), 8)));')

# ── 악행 -> 악명 ───────────────────────────────────────────────────
sub('\t\t\t\t\tSet Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 1)));\n', '')   # 위스키
sub('Set Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 5)));',
    'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 5)));', 2)                    # 합류·장물
sub('Set Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 15)));',
    'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 15)));', 2)                   # 습격·강탈
sub('Set Player Variable(Event Player.Target, Rep, Max(-100, Subtract(Player Variable(Event Player.Target, Rep), 10)));',
    'Set Player Variable(Event Player.Target, Noto, Max(0, Subtract(Player Variable(Event Player.Target, Noto), 30)));')
sub('Set Player Variable(Attacker, Rep, Max(-100, Subtract(Player Variable(Attacker, Rep), 20)));',
    'Set Player Variable(Attacker, Noto, Min(100, Add(Player Variable(Attacker, Noto), 20)));')
sub('Custom String("장물을 넘겼다 — $ {0}   (평판 -5)", Event Player.SellSum)',
    'Custom String("장물을 넘겼다 — $ {0}   (악명 +5)", Event Player.SellSum)')

# ── HUD: 명성 · 악명 ───────────────────────────────────────────────
sub('Custom String("{0} Lv.{1}   평판 {2}", ',
    'Custom String("{0} Lv.{1}   {2}", ')
sub(', Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 250), Down)), Local Player.Rep))',
    ', Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 250), Down)), Custom String("명성 {0} · 악명 {1}", Local Player.Fame, Local Player.Noto)))')

# ── 아침마다 악명 -2 ───────────────────────────────────────────────
sub('\t\tSet Player Variable(Event Player, DayStart, Event Player.Earned);\n',
    '\t\tSet Player Variable(Event Player, DayStart, Event Player.Earned);\n'
    '\t\tSet Player Variable(Event Player, Noto, Max(0, Subtract(Event Player.Noto, 2)));\n')

# ── 악명 게이트: 무법자 합류 20 ────────────────────────────────────
sub('''				If(Event Player.Job == 4);
					Small Message(Event Player, Custom String("이미 무법자다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else;''',
'''				If(Event Player.Job == 4);
					Small Message(Event Player, Custom String("이미 무법자다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.Noto < 20);
					Small Message(Event Player, Custom String("은신처가 애송이는 안 받는다 — 악명 20을 쌓아 와라 (현재 {0})", Event Player.Noto));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else;''')

# ── 악명 50+ 장물 프리미엄 180% ────────────────────────────────────
sub('''				If(Event Player.Job == 4);
					Set Player Variable(Event Player, SellSum, Round To Integer(Multiply(Event Player.SellSum, 1.65), Down));''',
'''				If(And(Event Player.Job == 4, Event Player.Noto >= 50));
					Set Player Variable(Event Player, SellSum, Round To Integer(Multiply(Event Player.SellSum, 1.8), Down));
				Else If(Event Player.Job == 4);
					Set Player Variable(Event Player, SellSum, Round To Integer(Multiply(Event Player.SellSum, 1.65), Down));''')

# ── 은신처 패널·라벨 갱신 ──────────────────────────────────────────
sub('Custom String("무법자 합류' + NL + '장물 거래 — 무법자 165% / 일반 130%' + NL + '습격 계획' + NL + '")',
    'Custom String("무법자 합류 — 악명 20 필요' + NL + '장물 거래 — 무법자 165% (악명 50+는 180%) / 일반 130%' + NL + '습격 계획' + NL + '")')
sub('Custom String("무법자 합류"), Custom String("장물 거래")',
    'Custom String("무법자 합류 — 악명 20"), Custom String("장물 거래")', 2)

# ══ [4] 육포 재고 공급망 ══════════════════════════════════════════
assert 'JerkyStock' not in s
sub('\t\t35: StatueTxt\n', '\t\t35: StatueTxt\n\t\t36: JerkyStock\n')
sub('\t\tSet Global Variable(StatueTxt, 0);\n',
    '\t\tSet Global Variable(StatueTxt, 0);\n\t\tSet Global Variable(JerkyStock, 15);\n')

# 육포 단품: 재고 1 필요
sub('''			If(Event Player.MenuIdx == 0);
				Set Player Variable(Event Player, Amt, Round To Integer(Multiply(15, Subtract(1, Multiply(%s, 0.002))), To Nearest));
				If(Event Player.Money >= Event Player.Amt);''' % NET,
'''			If(Event Player.MenuIdx == 0);
				Set Player Variable(Event Player, Amt, Round To Integer(Multiply(15, Subtract(1, Multiply(%s, 0.002))), To Nearest));
				If(Global Variable(JerkyStock) < 1);
					Small Message(Event Player, Custom String("육포 재고가 없다 — 사냥꾼·목동이 채워줄 것이다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.Money >= Event Player.Amt);''' % NET)
sub('''					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
					Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 1));''',
'''					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
					Modify Global Variable(JerkyStock, Subtract, 1);
					Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 1));''')

# 묶음: 재고 5 필요
sub('''			Else;
				Set Player Variable(Event Player, Amt, Round To Integer(Multiply(65, Subtract(1, Multiply(%s, 0.002))), To Nearest));
				If(Event Player.Money >= Event Player.Amt);''' % NET,
'''			Else;
				Set Player Variable(Event Player, Amt, Round To Integer(Multiply(65, Subtract(1, Multiply(%s, 0.002))), To Nearest));
				If(Global Variable(JerkyStock) < 5);
					Small Message(Event Player, Custom String("묶음을 만들 재고가 없다 (현재 {0}) — 사냥꾼·목동이 채워줄 것이다", Global Variable(JerkyStock)));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.Money >= Event Player.Amt);''' % NET)
sub('''					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
					Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 5));''',
'''					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
					Modify Global Variable(JerkyStock, Subtract, 5);
					Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 5));''')

# 납품: 야수 처치 +1
sub('\t\tModify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));\n',
    '\t\tModify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));\n'
    '\t\tSet Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 1)));\n')
# 납품: 소몰이 완료 +6
sub('\t\t\tBig Message(Event Player, Custom String("우리에 몰아넣었다!   +$ {0}", Event Player.RunPay));\n',
    '\t\t\tSet Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 6)));\n'
    '\t\t\tBig Message(Event Player, Custom String("우리에 몰아넣었다!   +$ {0}   (잡화점 육포 재고 +6)", Event Player.RunPay));\n')

# 잡화점 패널에 재고 표시
sub('Custom String("육포 $15      물통 $10      육포 5개 묶음 $65' + NL,
    'Custom String("육포 $15 (재고 {0})      물통 $10      묶음 $65' + NL)
sub('원석·가죽도 받아준다 — 정비소 시세의 90%' + NL + '평판이 좋으면 싸게, 나쁘면 비싸게 판다' + NL + '")',
    '원석·가죽도 받아준다 — 정비소 시세의 90%' + NL + '재고는 사냥꾼·목동이 채운다' + NL + '", Global Variable(JerkyStock))')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
assert 'Rep' not in s.replace('Replace existing', '').replace('RepXX', '')
print('[1] 명성/악명 분리 + 게이트 / [4] 육포 재고 공급망')
