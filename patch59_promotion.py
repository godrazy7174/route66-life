# -*- coding: utf-8 -*-
"""승급(상위 전직) 시스템.

경험 750(= Lv.4) 도달 시 자기 일터에서 승급한다. 새 행동이 아니라
기존 행동을 강화하고, HUD 직업명이 상위 직업명으로 바뀐다.

    광부   -> 광산주      @협곡 광산   : 정밀 탐사 무료 · 채굴 10% 확률 수확 2배
    사냥꾼 -> 맹수 사냥꾼  @협곡 개활지 : 내 추적에서 거대·전설 확률 2배
    현상금 -> 보안관      @보안관 초소 : 체포 1.8초 -> 1.2초 · NPC 처치금 +$30
    무법자 -> 갱단 두목    @무법자 은신처: 습격 3회 -> 2회 · 강탈 쿨 45 -> 30초

직업을 바꾸면 승급은 사라진다 (경험은 남으니 재승급 가능).
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

# ══ 변수 ══════════════════════════════════════════════════════════
assert '63: Adv' not in s and ': Adv' not in s
sub('\t\t62: PlanPay\n', '\t\t62: PlanPay\n\t\t63: Adv\n')
sub('\t\tSet Player Variable(Event Player, Job, 0);\n',
    '\t\tSet Player Variable(Event Player, Job, 0);\n\t\tSet Player Variable(Event Player, Adv, 0);\n')

# ══ 직업 변경 시 승급 초기화 ══════════════════════════════════════
for j in (1, 2, 3):
    sub('\t\t\t\t\tSet Player Variable(Event Player, Job, %d);\n' % j,
        '\t\t\t\t\tSet Player Variable(Event Player, Job, %d);\n'
        '\t\t\t\t\tSet Player Variable(Event Player, Adv, 0);\n' % j)
sub('\t\t\t\t\tSet Player Variable(Event Player, Job, 4);\n',
    '\t\t\t\t\tSet Player Variable(Event Player, Job, 4);\n'
    '\t\t\t\t\tSet Player Variable(Event Player, Adv, 0);\n')

# ══ 메뉴 수 / 라벨 ════════════════════════════════════════════════
sub('Array(1, 4, 2, 4, 2, 3, 3, 1, 2, 3, 1, 3)', 'Array(1, 4, 3, 4, 2, 3, 3, 2, 3, 4, 1, 3)', 4)
sub('Custom String("정밀 탐사 $30"), Custom String("-")',
    'Custom String("정밀 탐사 $30"), Custom String("승급: 광산주 — Lv.4")', 2)
sub('Custom String("흔적 추적 — 야수 몰아내기"), Custom String("-")',
    'Custom String("흔적 추적 — 야수 몰아내기"), Custom String("승급: 맹수 사냥꾼 — Lv.4")', 2)
sub('Custom String("현상금 게시판"), Custom String("-")',
    'Custom String("현상금 게시판"), Custom String("승급: 보안관 — Lv.4")', 2)
sub('Custom String("습격 계획 (무법자 전용)"), Custom String("-")',
    'Custom String("습격 계획 (무법자 전용)"), Custom String("승급: 갱단 두목 — Lv.4")', 2)

# ══ HUD 직업명: 승급 반영 ═════════════════════════════════════════
BASE = ('Value In Array(Array(Custom String("뜨내기"), Custom String("광부"), Custom String("사냥꾼"), '
        'Custom String("현상금 사냥꾼"), Custom String("무법자")), Local Player.Job)')
ADVN = ('Value In Array(Array(Custom String("뜨내기"), Custom String("광산주"), Custom String("맹수 사냥꾼"), '
        'Custom String("보안관"), Custom String("갱단 두목")), Local Player.Job)')
sub('Custom String("{0} Lv.{1}   평판 {2}", ' + BASE,
    'Custom String("{0} Lv.{1}   평판 {2}", Local Player.Adv == 1 ? ' + ADVN + ' : ' + BASE)

# ══ 승급 처리 블록 생성기 ═════════════════════════════════════════
def promo(job, guard, already, advname, perkmsg, color):
    L4, L5 = T*4, T*5
    return (L4 + 'If(Event Player.Job != %d);' % job + NLC
          + L5 + 'Small Message(Event Player, Custom String("%s"));' % guard + NLC
          + L5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
          + L4 + 'Else If(Event Player.Adv == 1);' + NLC
          + L5 + 'Small Message(Event Player, Custom String("%s"));' % already + NLC
          + L5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
          + L4 + 'Else If(Value In Array(Event Player.JobXP, %d) < 750);' % job + NLC
          + L5 + 'Small Message(Event Player, Custom String("경험이 부족하다 — {0} / 750", Value In Array(Event Player.JobXP, %d)));' % job + NLC
          + L5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
          + L4 + 'Else;' + NLC
          + L5 + 'Set Player Variable(Event Player, Adv, 1);' + NLC
          + L5 + 'Big Message(All Players(All Teams), Custom String("{0} — %s(으)로 올라섰다!", Event Player));' % advname + NLC
          + L5 + 'Small Message(Event Player, Custom String("%s"));' % perkmsg + NLC
          + L5 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(%s), Position Of(Event Player), 4);' % color + NLC
          + L5 + 'Play Effect(Event Player, Buff Explosion Sound, Color(%s), Position Of(Event Player), 200);' % color + NLC
          + L4 + 'End;' + NLC)

# ══ 광산 (zone 1): 탐사 무료 + 승급 메뉴 ══════════════════════════
sub('''			Else;
				If(Event Player.Money >= 30);
					Modify Player Variable(Event Player, Money, Subtract, 30);''',
'''			Else If(Event Player.MenuIdx == 1);
				Set Player Variable(Event Player, Amt, And(Event Player.Job == 1, Event Player.Adv == 1) ? 0 : 30);
				If(Event Player.Money >= Event Player.Amt);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);''')
sub('Custom String("돈이 부족합니다 ($30 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt)')
i = s.index('Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt)')
j = s.index('\t\t\tEnd;\n\t\tElse If(Event Player.Zone == 2);', i)
s = s[:j] + '\t\t\tElse;\n' + promo(1, '광부만 승급할 수 있다', '이미 광산주다', '광산주',
    '정밀 탐사 무료 · 채굴 10% 확률로 수확 2배', 'Yellow') + s[j:]

# ══ 개활지 (zone 6): 승급 메뉴 ════════════════════════════════════
sub('''		Else If(Event Player.Zone == 6);
			Call Subroutine(DoHunt);''',
'''		Else If(Event Player.Zone == 6);
			If(Event Player.MenuIdx == 0);
				Call Subroutine(DoHunt);
			Else;
''' + promo(2, '사냥꾼만 승급할 수 있다', '이미 맹수 사냥꾼이다', '맹수 사냥꾼',
    '내 추적에서 거대·전설 야수 확률 2배', 'Orange') + '\t\t\tEnd;')

# ══ 초소 (zone 7): 승급 메뉴 ══════════════════════════════════════
KEY7 = 'Custom String("현상금은 범인의 주머니에서 나온다 — 빈털터리는 잡아도 못 번다"));'
i = s.index(KEY7)
j = s.index('\t\t\tEnd;\n\t\tElse If(Event Player.Zone == 8);', i)
old7 = s[s.index('\t\t\tElse;\n\t\t\t\tSmall Message(Event Player, Custom String("현상금 게시판 —'):j]
s = s.replace('\t\t\tElse;\n\t\t\t\tSmall Message(Event Player, Custom String("현상금 게시판 —',
              '\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tSmall Message(Event Player, Custom String("현상금 게시판 —', 1)
j = s.index('\t\t\tEnd;\n\t\tElse If(Event Player.Zone == 8);')
s = s[:j] + '\t\t\tElse;\n' + promo(3, '현상금 사냥꾼만 승급할 수 있다', '이미 보안관이다', '보안관',
    '체포 1.2초 · 무법자 처치금 +$30', 'Sky Blue') + s[j:]

# ══ 은신처 (zone 8): 승급 메뉴 ════════════════════════════════════
sub('''			Else;
				If(Event Player.Job != 4);''',
'''			Else If(Event Player.MenuIdx == 2);
				If(Event Player.Job != 4);''')
sub('''					Call Subroutine(DoPlan);
				End;
			End;
		Else If(Event Player.Zone == 9);''',
'''					Call Subroutine(DoPlan);
				End;
			Else;
''' + promo(4, '무법자만 승급할 수 있다', '이미 갱단 두목이다', '갱단 두목',
    '습격 계획 2회면 결행 · 강탈 쿨타임 30초', 'Purple') + '''			End;
		Else If(Event Player.Zone == 9);''')

# ══ 효과 구현 ═════════════════════════════════════════════════════
# 광산주: 채굴 10% 수확 2배
sub('\t\t\tModify Player Variable(Event Player, MineGain, Add, Event Player.Pick);\n',
    '\t\t\tModify Player Variable(Event Player, MineGain, Add, Event Player.Pick);\n'
    '\t\t\tIf(And(And(Event Player.Job == 1, Event Player.Adv == 1), Random Integer(1, 100) <= 10));\n'
    '\t\t\t\tModify Player Variable(Event Player, MineGain, Multiply, 2);\n'
    '\t\t\t\tBig Message(Event Player, Custom String("광산주의 눈 — 이번 수확 2배!"));\n'
    '\t\t\t\tPlay Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1.5);\n'
    '\t\t\tEnd;\n')

# 맹수 사냥꾼: 거대·전설 문턱 2배 (전설 1->2, 거대 11->21)
sub('\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2)));\n\t\tIf(Count Of(Event Player.Target) > 0);',
    '\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2)));\n'
    '\t\tSet Player Variable(Event Player, Roll, Event Player.Job == 2 ? Event Player.Adv : 0);\n'
    '\t\tIf(Count Of(Event Player.Target) > 0);')
for n in range(3):
    TGT = 'Value In Array(Event Player.Target, %d)' % n
    sub('Set Player Variable(%s, Giant, Player Variable(%s, Roll) <= 11 ? 1 : 0);' % (TGT, TGT),
        'Set Player Variable(%s, Giant, Player Variable(%s, Roll) <= Add(11, Multiply(10, Event Player.Roll)) ? 1 : 0);' % (TGT, TGT))
    sub('If(Player Variable(%s, Roll) <= 1);' % TGT,
        'If(Player Variable(%s, Roll) <= Add(1, Event Player.Roll));' % TGT)

# 보안관: 체포 게이지 1.2초 (체포일 때만)
sub('Chase Player Variable Over Time(Event Player, WorkProg, 100, 1.8, Destination and Duration);\n\t\tWait Until(Or(Or(',
    'Chase Player Variable Over Time(Event Player, WorkProg, 100, And(And(Event Player.Job == 3, Event Player.Adv == 1), Player Variable(Event Player.Target, Bounty) > 0) ? 1.2 : 1.8, Destination and Duration);\n\t\tWait Until(Or(Or(')
# 보안관: NPC 처치금 +$30
sub('\t\t\t\t\t\tModify Player Variable(Event Player, HuntPay, Add, 40);\n',
    '\t\t\t\t\t\tModify Player Variable(Event Player, HuntPay, Add, 40);\n'
    '\t\t\t\t\t\tIf(Event Player.Adv == 1);\n'
    '\t\t\t\t\t\t\tModify Player Variable(Event Player, HuntPay, Add, 30);\n'
    '\t\t\t\t\t\tEnd;\n')

# 갱단 두목: 습격 3회 -> 2회 (DoPlan 은 무법자 전용 경로라 Adv 만 보면 됨)
sub('\t\tIf(Event Player.Plan >= 3);', '\t\tIf(Event Player.Plan >= Subtract(3, Event Player.Adv));')
sub('Custom String("계획 {0}/3 — 정찰비 $ {1}", Event Player.Plan, Event Player.PlanPay)',
    'Custom String("계획 {0}/{1} — 정찰비 $ {2}", Event Player.Plan, Subtract(3, Event Player.Adv), Event Player.PlanPay)')
# 갱단 두목: 강탈 쿨 45 -> 30
sub('Set Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 45));',
    'Set Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), Subtract(45, Multiply(15, And(Event Player.Job == 4, Event Player.Adv == 1)))));')

# ══ 식당 안내 한 줄 ═══════════════════════════════════════════════
sub('일할수록 레벨이 오르고 그 직업의 수입이 늘어난다' + NL,
    '일할수록 레벨이 오르고 그 직업의 수입이 늘어난다' + NL + 'Lv.4가 되면 자기 일터에서 승급할 수 있다' + NL)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('승급 시스템 구현 완료 — 4개 일터, 8개 효과')
