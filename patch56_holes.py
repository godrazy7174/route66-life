# -*- coding: utf-8 -*-
"""허점 봉합 (grill 세션 합의안).

Q1① 현상금 = 범인 소지금에서 차감 (있는 만큼만). 화폐 발행 차단.
Q2① 강탈·체포·처단 수익은 '오늘 목표'(Earned)에서 제외.
Q3① 소모품·숙박 가격 평판 연동: x(1 - Rep*0.002) -> 평판 100이면 20% 할인.
Q3③+Q4① 정비소 판매가 평판 연동: x(1 + Rep*0.0015) -> 85~115%.
       은신처 장물(130/165%)은 그대로 — 평판 낮은 무법자의 판로로 분화.
Q5① 사망 부활 시 허기·갈증 최소 40 보장 (아사 루프 차단).
Q6② 취침 무적은 그대로.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

BUY = lambda base: ('Round To Integer(Multiply(%d, Subtract(1, Multiply(Event Player.Rep, 0.002))), To Nearest)' % base)

# ══ Q1① 체포: 현상금을 범인 주머니에서 ═══════════════════════════
sub('''			Set Player Variable(Event Player, Take, Player Variable(Event Player.Target, Bounty));''',
'''			Set Player Variable(Event Player, Take, Min(Player Variable(Event Player.Target, Bounty), Player Variable(Event Player.Target, Money)));
			Set Player Variable(Event Player.Target, Money, Subtract(Player Variable(Event Player.Target, Money), Event Player.Take));''')
sub('''			Modify Player Variable(Event Player, Money, Add, Event Player.Take);
			Modify Player Variable(Event Player, Earned, Add, Event Player.Take);
			Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 12)));''',
'''			Modify Player Variable(Event Player, Money, Add, Event Player.Take);
			Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 12)));''')

# ══ Q1① 처단: 같은 원칙 ══════════════════════════════════════════
sub('''			Set Player Variable(Attacker, KillPay, Player Variable(Victim, Bounty));
			Modify Player Variable(Attacker, Money, Add, Player Variable(Attacker, KillPay));
			Modify Player Variable(Attacker, Earned, Add, Player Variable(Attacker, KillPay));''',
'''			Set Player Variable(Attacker, KillPay, Min(Player Variable(Victim, Bounty), Player Variable(Victim, Money)));
			Set Player Variable(Victim, Money, Subtract(Player Variable(Victim, Money), Player Variable(Attacker, KillPay)));
			Modify Player Variable(Attacker, Money, Add, Player Variable(Attacker, KillPay));''')

# ══ Q2① 강탈 수익도 목표 집계 제외 ════════════════════════════════
sub('''				Modify Player Variable(Event Player, Money, Add, Event Player.Take);
				Modify Player Variable(Event Player, Earned, Add, Event Player.Take);
				Modify Player Variable(Event Player, Bounty, Add, Event Player.Take);''',
'''				Modify Player Variable(Event Player, Money, Add, Event Player.Take);
				Modify Player Variable(Event Player, Bounty, Add, Event Player.Take);''')

# ══ Q3① 소모품·숙박 가격 평판 연동 ════════════════════════════════
# 식사 $12
sub('''				If(Event Player.Money >= 12);
					Modify Player Variable(Event Player, Money, Subtract, 12);''',
'''				Set Player Variable(Event Player, Amt, %s);
				If(Event Player.Money >= Event Player.Amt);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);''' % BUY(12))
sub('Custom String("돈이 부족합니다 ($12 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt)')
# 육포 $15
sub('''				If(Event Player.Money >= 15);
					Modify Player Variable(Event Player, Money, Subtract, 15);''',
'''				Set Player Variable(Event Player, Amt, %s);
				If(Event Player.Money >= Event Player.Amt);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);''' % BUY(15))
sub('Custom String("돈이 부족합니다 ($15 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt)')
# 물통 $10
sub('''				If(Event Player.Money >= 10);
					Modify Player Variable(Event Player, Money, Subtract, 10);''',
'''				Set Player Variable(Event Player, Amt, %s);
				If(Event Player.Money >= Event Player.Amt);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);''' % BUY(10))
sub('Custom String("돈이 부족합니다 ($10 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt)')
# 묶음 $65
sub('''				If(Event Player.Money >= 65);
					Modify Player Variable(Event Player, Money, Subtract, 65);''',
'''				Set Player Variable(Event Player, Amt, %s);
				If(Event Player.Money >= Event Player.Amt);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);''' % BUY(65))
sub('Custom String("돈이 부족합니다 ($65 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt)')
# 위스키 $25
sub('''				Else If(Event Player.Money >= 25);
					Modify Player Variable(Event Player, Money, Subtract, 25);''',
'''				Else If(Event Player.Money >= %s);
					Set Player Variable(Event Player, Amt, %s);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);''' % (BUY(25), BUY(25)))
sub('Custom String("돈이 부족합니다 ($25 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", %s)' % BUY(25))
# 숙박 $60 (DoSleep)
sub('''		If(Event Player.Money < 60);
			Small Message(Event Player, Custom String("숙박비가 부족합니다 ($60 필요)"));''',
'''		Set Player Variable(Event Player, Amt, %s);
		If(Event Player.Money < Event Player.Amt);
			Small Message(Event Player, Custom String("숙박비가 부족합니다 ($ {0} 필요)", Event Player.Amt));''' % BUY(60))
sub('''		Modify Player Variable(Event Player, Money, Subtract, 60);
		Set Player Variable(Event Player, Busy, 1);''',
'''		Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
		Set Player Variable(Event Player, Busy, 1);''')

# ══ Q3③ 정비소 판매가 평판 연동 (85~115%) ═════════════════════════
REPMUL = 'Add(1, Multiply(Event Player.Rep, 0.0015))'
sub('Set Player Variable(Event Player, SellSum, Multiply(Multiply(Event Player.SellQty, Global Variable(OrePrice)), Global Variable(SellMult)));',
    'Set Player Variable(Event Player, SellSum, Round To Integer(Multiply(Multiply(Multiply(Event Player.SellQty, Global Variable(OrePrice)), Global Variable(SellMult)), %s), To Nearest));' % REPMUL)
sub('Set Player Variable(Event Player, SellSum, Multiply(Multiply(Event Player.SellQty, Global Variable(HidePrice)), Global Variable(SellMult)));',
    'Set Player Variable(Event Player, SellSum, Round To Integer(Multiply(Multiply(Multiply(Event Player.SellQty, Global Variable(HidePrice)), Global Variable(SellMult)), %s), To Nearest));' % REPMUL)

# ══ Q5① 사망 시 허기·갈증 바닥 보장 ═══════════════════════════════
sub('''		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Set Player Variable(Event Player, Busy, 0);
		Set Player Variable(Event Player, WorkProg, 0);
		Wait Until(Is Alive(Event Player), 40);''',
'''		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Set Player Variable(Event Player, Busy, 0);
		Set Player Variable(Event Player, WorkProg, 0);
		Set Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));
		Set Player Variable(Event Player, Thirst, Max(Event Player.Thirst, 40));
		Wait Until(Is Alive(Event Player), 40);''')

# ══ 안내 문구 ═════════════════════════════════════════════════════
sub('Custom String("밤에는 2배. 수배된 사람을 잡아도 그 현상금을 받는다")',
    'Custom String("현상금은 범인의 주머니에서 나온다 — 빈털터리는 잡아도 못 번다")')
sub('Custom String("육포 $15      물통 $10      육포 5개 묶음 $65' + NL + '")',
    'Custom String("육포 $15      물통 $10      육포 5개 묶음 $65' + NL + '평판이 좋으면 싸게, 나쁘면 비싸게 판다' + NL + '")')
sub('Custom String("원석  $ {0}       가죽  $ {1}' + NL + '시세는 매일 아침 바뀐다' + NL + '", ',
    'Custom String("원석  $ {0}       가죽  $ {1}' + NL + '시세는 매일 아침 바뀐다 — 평판이 좋으면 값을 후하게 쳐준다' + NL + '", ')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('Q1 현상금 몰수제 / Q2 목표 집계 제외 / Q3 가격 평판 연동 / Q5 아사 루프 차단')
