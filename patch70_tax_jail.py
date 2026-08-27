# -*- coding: utf-8 -*-
"""[2] 징수원이 마을에 온다 (세금).
    짝수 날 아침 10시, 징수원 도착 공지 -> 2분 안에 보안관 초소에서
    재산세(재산의 5%) 납부 (초소 5번 메뉴). 납부 시 명성 +2.
    소지금 $100 미만은 면제("낼 것도 없다").
    마감까지 안 내면 재산의 10%만큼 현상금(최소 $50) + 악명 +10 —
    감옥 대신 처벌을 현상금 사냥꾼들에게 위임한다.

[3] 곡괭이 탈옥 (체포 후 수감 재설계).
    8초 수면 구금 -> 유치장 수감: 형기 30 + 악명/5 초 (최대 50).
    수감 중 [V] 연타로 벽(내구도 15)을 부순다 — 타격당 1 + 곡괭이 레벨.
    탈옥: 악명 +15, 현상금 +$100, 전 서버 공지.
    만기 출소: 악명 -20 세탁. (체포 즉시 -30 세탁은 삭제 — 복역이 세탁 수단)
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)
L7 = 'Value In Array(Global Variable(LocPos), 7)'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ 변수 ══════════════════════════════════════════════════════════
for v in ('TaxOn', 'TaxRound', 'TaxSeenRound', 'TaxPaidRound', 'JailOn', 'JailEnd', 'WallHP'):
    assert v not in s
sub('\t\t10: Ready\n', '\t\t9: TaxOn\n\t\t10: Ready\n')
sub('\t\t16: Idx\n', '\t\t15: TaxRound\n\t\t16: Idx\n')
sub('\t\t73: Noto\n', '\t\t52: TaxSeenRound\n\t\t73: Noto\n\t\t74: TaxPaidRound\n\t\t75: JailOn\n\t\t76: JailEnd\n\t\t77: WallHP\n')
sub('\t\tSet Global Variable(SellMult, 1);\n\t\tSet Global Variable(DailyGoal, 480);\n',
    '\t\tSet Global Variable(SellMult, 1);\n\t\tSet Global Variable(DailyGoal, 480);\n'
    '\t\tSet Global Variable(TaxOn, 0);\n\t\tSet Global Variable(TaxRound, 0);\n')
sub('\t\tSet Player Variable(Event Player, Noto, 0);\n',
    '\t\tSet Player Variable(Event Player, Noto, 0);\n'
    '\t\tSet Player Variable(Event Player, TaxSeenRound, 0);\n'
    '\t\tSet Player Variable(Event Player, TaxPaidRound, 0);\n'
    '\t\tSet Player Variable(Event Player, JailOn, 0);\n')

# ══ [2] 징수원 규칙 ═══════════════════════════════════════════════
TAX = ('rule("[세금 01] 징수원 도착")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Global;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC + T*2 + 'Global Variable(Ready) == 1;' + NLC + T + '}' + NLC + NLC
 + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Wait Until(And(Modulo(Global Variable(Day), 2) == 0, Global Variable(Clock) >= 600), 99999);' + NLC
 + T*2 + 'Modify Global Variable(TaxRound, Add, 1);' + NLC
 + T*2 + 'Set Global Variable(TaxOn, 1);' + NLC
 + T*2 + 'Big Message(All Players(All Teams), Custom String("징수원이 마을에 도착했다 — 2분 안에 보안관 초소에서 재산세를 내라"));' + NLC
 + T*2 + 'Small Message(All Players(All Teams), Custom String("재산의 5%. 떼먹으면 재산의 10%가 현상금으로 붙는다"));' + NLC
 + T*2 + 'Wait(90, Ignore Condition);' + NLC
 + T*2 + 'Small Message(All Players(All Teams), Custom String("징수원이 곧 떠난다 — 30초"));' + NLC
 + T*2 + 'Wait(30, Ignore Condition);' + NLC
 + T*2 + 'Set Global Variable(TaxOn, 0);' + NLC
 + T*2 + 'Big Message(All Players(All Teams), Custom String("징수원이 떠났다 — 체납자에게 현상금이 붙는다"));' + NLC
 + T*2 + 'Wait Until(Modulo(Global Variable(Day), 2) == 1, 99999);' + NLC
 + T*2 + 'Loop();' + NLC
 + T + '}' + NLC + '}' + NLC + NLC
 + 'rule("[세금 02] 납세 의무 표시")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Global Variable(TaxOn) == 1;' + NLC
 + T*2 + 'Event Player.TaxSeenRound != Global Variable(TaxRound);' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, TaxSeenRound, Global Variable(TaxRound));' + NLC
 + T + '}' + NLC + '}' + NLC + NLC
 + 'rule("[세금 03] 체납 처벌")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Global Variable(TaxOn) == 0;' + NLC
 + T*2 + 'Event Player.TaxSeenRound == Global Variable(TaxRound);' + NLC
 + T*2 + 'Event Player.TaxPaidRound != Global Variable(TaxRound);' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));' + NLC
 + T*2 + 'If(Event Player.Money < 100);' + NLC
 + T*3 + 'Small Message(Event Player, Custom String("털어봤자 먼지뿐 — 징수원이 포기하고 지나갔다"));' + NLC
 + T*2 + 'Else;' + NLC
 + T*3 + 'Set Player Variable(Event Player, Fine, Max(50, Round To Integer(Multiply(Event Player.Money, 0.1), Down)));' + NLC
 + T*3 + 'Modify Player Variable(Event Player, Bounty, Add, Event Player.Fine);' + NLC
 + T*3 + 'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 10)));' + NLC
 + T*3 + 'Big Message(Event Player, Custom String("세금을 떼먹었다 — 현상금 +$ {0} (악명 +10)", Event Player.Fine));' + NLC
 + T*3 + 'Play Effect(Event Player, Explosion Sound, Color(Red), Position Of(Event Player), 150);' + NLC
 + T*2 + 'End;' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[생활 01] DoSleep")', TAX + 'rule("[생활 01] DoSleep")')

# ── 초소 메뉴: 승급을 3번으로 명시하고 4번 재산세 추가 ─────────────
sub('''			Else;
				If(Event Player.Job != 3);''',
'''			Else If(Event Player.MenuIdx == 3);
				If(Event Player.Job != 3);''')
TAXPAY = ('''			Else;
				If(Global Variable(TaxOn) == 0);
					Small Message(Event Player, Custom String("징수 기간이 아니다 — 징수원은 이틀에 한 번 아침 10시에 온다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.TaxPaidRound == Global Variable(TaxRound));
					Small Message(Event Player, Custom String("이미 납부했다"));
				Else If(Event Player.Money < 100);
					Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));
					Small Message(Event Player, Custom String("낼 것도 없다 — 징수원이 혀를 차며 보내줬다"));
				Else;
					Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, 0.05), Down));
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
					Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));
					Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));
					Small Message(Event Player, Custom String("재산세 $ {0} 납부 — 성실한 시민이다 (명성 +2)", Event Player.Amt));
					Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 60);
				End;
''')
KEY = 'Custom String("현상금 사냥꾼만 승급할 수 있다 — 전직은 여기 1번 게시판에서")'
i = s.index(KEY)
j = s.index('\t\t\tEnd;\n\t\tElse If(Event Player.Zone == 8);', i)
s = s[:j] + TAXPAY + s[j:]

sub('Array(1, 1, 4, 4, 2, 3, 4, 3, 4, 4, 1, 4, 3, 3, 1, 1)', 'Array(1, 1, 4, 4, 2, 3, 4, 3, 5, 4, 1, 4, 3, 3, 1, 1)', 4)
sub('Custom String("승급: 보안관 — Lv.4"), Custom String("-"), Custom String("-")',
    'Custom String("승급: 보안관 — Lv.4"), Custom String("재산세 납부 — 징수 기간만"), Custom String("-")', 2)

# ══ [3] 곡괭이 탈옥 ═══════════════════════════════════════════════
sub('\t\t\tSet Player Variable(Event Player.Target, Noto, Max(0, Subtract(Player Variable(Event Player.Target, Noto), 30)));\n', '')
sub('''			Teleport(Event Player.Target, Value In Array(Global Variable(LocPos), 7));
			Set Status(Event Player.Target, Null, Asleep, 8);
			Set Status(Event Player.Target, Null, Phased Out, 8);
			Big Message(Event Player.Target, Custom String("유치장에 처넣어졌다 — 벌금 $ {0}, 8초 구금", Event Player.Fine));''',
'''			Teleport(Event Player.Target, Value In Array(Global Variable(LocPos), 7));
			Set Player Variable(Event Player.Target, JailOn, 1);
			Set Player Variable(Event Player.Target, WallHP, 15);
			Set Player Variable(Event Player.Target, JailEnd, Add(Total Time Elapsed(), Min(50, Add(30, Round To Integer(Divide(Player Variable(Event Player.Target, Noto), 5), Down)))));
			Set Player Variable(Event Player.Target, Busy, 1);
			Set Status(Event Player.Target, Null, Rooted, 9999);
			Set Status(Event Player.Target, Null, Phased Out, 9999);
			Set Primary Fire Enabled(Event Player.Target, False);
			Big Message(Event Player.Target, Custom String("유치장에 갇혔다 — 벌금 $ {0}", Event Player.Fine));
			Small Message(Event Player.Target, Custom String("[V] 연타로 벽을 부수면 탈옥 (악명 +15, 현상금 +$100) · 버티면 만기 출소 (악명 -20)"));''')

JAIL = ('rule("[감옥 01] 만기 출소")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Event Player.JailOn == 1;' + NLC
 + T*2 + 'Total Time Elapsed() >= Event Player.JailEnd;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, JailOn, 0);' + NLC
 + T*2 + 'Clear Status(Event Player, Rooted);' + NLC
 + T*2 + 'Clear Status(Event Player, Phased Out);' + NLC
 + T*2 + 'Set Primary Fire Enabled(Event Player, True);' + NLC
 + T*2 + 'Set Player Variable(Event Player, Busy, 0);' + NLC
 + T*2 + 'Set Player Variable(Event Player, Noto, Max(0, Subtract(Event Player.Noto, 20)));' + NLC
 + T*2 + 'Big Message(Event Player, Custom String("만기 출소 — 죗값을 치렀다 (악명 -20)"));' + NLC
 + T*2 + 'Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 80);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC
 + 'rule("[감옥 02] 벽 부수기 (V 연타)")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Event Player.JailOn == 1;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Melee)) == True;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Modify Player Variable(Event Player, WallHP, Subtract, Add(1, Event Player.Pick));' + NLC
 + T*2 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Gray), Position Of(Event Player), 1);' + NLC
 + T*2 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Gray), Position Of(Event Player), 70);' + NLC
 + T*2 + 'If(Event Player.WallHP > 0);' + NLC
 + T*3 + 'Small Message(Event Player, Custom String("퍽! 벽이 흔들린다 — 내구도 {0}", Event Player.WallHP));' + NLC
 + T*2 + 'Else;' + NLC
 + T*3 + 'Set Player Variable(Event Player, JailOn, 0);' + NLC
 + T*3 + 'Clear Status(Event Player, Rooted);' + NLC
 + T*3 + 'Clear Status(Event Player, Phased Out);' + NLC
 + T*3 + 'Set Primary Fire Enabled(Event Player, True);' + NLC
 + T*3 + 'Set Player Variable(Event Player, Busy, 0);' + NLC
 + T*3 + 'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 15)));' + NLC
 + T*3 + 'Modify Player Variable(Event Player, Bounty, Add, 100);' + NLC
 + T*3 + 'Teleport(Event Player, Nearest Walkable Position(Add(%s, Vector(6, 0, 6))));' % L7 + NLC
 + T*3 + 'Big Message(All Players(All Teams), Custom String("{0} — 유치장 벽을 부수고 탈옥했다!!", Event Player));' + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Event Player), 5);' + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(Event Player), 200);' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Wait(0.25, Ignore Condition);' + NLC
 + T*2 + 'Loop If(And(Event Player.JailOn == 1, Is Button Held(Event Player, Button(Melee))));' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[범죄 02] 살해와 처단")', JAIL + 'rule("[범죄 02] 살해와 처단")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[2] 징수원 3규칙 + 초소 납부 메뉴 / [3] 유치장 수감·탈옥 2규칙')
