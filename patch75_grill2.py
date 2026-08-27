# -*- coding: utf-8 -*-
"""점검 2차 합의 구현.

Q1 금고 마차 — 밤마다 1회, 맵 어딘가에 금고 마차 스폰(주황 구체+해골 표식).
   [F] 5초 털기: $80~150 + 악명 +10, 전 서버 공지. 수익은 '오늘 목표' 제외(범죄).
   새벽까지 아무도 안 털면 떠난다. 솔로 방의 악명 사다리 + 밤 컨텐츠.

Q2 은행 회수 — 건물 소유주가 서버를 떠나면 10초 안에 소유권 해제 +
   가격을 기본가로 리셋, "은행이 회수했다 — 매물" 전 서버 공지.

Q3 명성 게이트 — 보안관 승급에 명성 30 요구.
   명성 70+ 특전: 벌금 $100 -> $50, 재산세 5% -> 2.5%.
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

NAMES15 = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), Custom String("모텔"), '
           'Custom String("정비소 고물상"), Custom String("술집"), Custom String("협곡 개활지"), Custom String("보안관 초소"), '
           'Custom String("무법자 은신처"), Custom String("안내소"), Custom String("대장간"))')

# ══ 변수 ══════════════════════════════════════════════════════════
for v in ('WagonOn', 'WagonPos', 'WagonFx', 'WagonIco', 'BldBase'):
    assert v not in s
sub('\t\t16: Idx\n', '\t\t16: Idx\n\t\t18: WagonOn\n\t\t19: WagonPos\n\t\t20: WagonFx\n\t\t21: WagonIco\n\t\t22: BldBase\n')
sub('\t\tSet Global Variable(TaxRound, 0);\n',
    '\t\tSet Global Variable(TaxRound, 0);\n'
    '\t\tSet Global Variable(WagonOn, 0);\n'
    '\t\tSet Global Variable(WagonPos, Vector(0, 0, 0));\n'
    '\t\tSet Global Variable(WagonFx, 0);\n'
    '\t\tSet Global Variable(WagonIco, 0);\n'
    '\t\tSet Global Variable(BldBase, Array(15000, 0, 24000, 21000, 27000, 18000, 0, 0, 0, 0, 30000));\n')

# ══ Q1 금고 마차 ══════════════════════════════════════════════════
WSPAWN = 'Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-22, 22), 0, Random Real(-22, 22))))'
WAGON = ('rule("[밤 01] 금고 마차 출현")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Global;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC + T*2 + 'Global Variable(Ready) == 1;' + NLC + T + '}' + NLC + NLC
 + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Wait Until(Global Variable(IsNight) == 1, 99999);' + NLC
 + T*2 + 'Set Global Variable(WagonPos, Add(%s, Vector(0, 1, 0)));' % WSPAWN + NLC
 + T*2 + 'Set Global Variable(WagonOn, 1);' + NLC
 + T*2 + 'Create Effect(All Players(All Teams), Sphere, Color(Orange), Global Variable(WagonPos), 1.1, Visible To Position Radius and Color);' + NLC
 + T*2 + 'Set Global Variable(WagonFx, Last Created Entity());' + NLC
 + T*2 + 'Create Icon(All Players(All Teams), Global Variable(WagonPos), Skull, Visible To and Position, Color(Orange), True);' + NLC
 + T*2 + 'Set Global Variable(WagonIco, Last Created Entity());' + NLC
 + T*2 + 'Big Message(All Players(All Teams), Custom String("금고 마차가 어둠 속 어딘가에 멈춰 섰다"));' + NLC
 + T*2 + 'Small Message(All Players(All Teams), Custom String("[F] 5초 — 터는 자는 돈과 악명을 얻는다"));' + NLC
 + T*2 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Global Variable(WagonPos), 3);' + NLC
 + T*2 + 'Wait Until(Or(Global Variable(WagonOn) == 0, Global Variable(IsNight) == 0), 400);' + NLC
 + T*2 + 'If(Global Variable(WagonOn) == 1);' + NLC
 + T*3 + 'Set Global Variable(WagonOn, 0);' + NLC
 + T*3 + 'Destroy Effect(Global Variable(WagonFx));' + NLC
 + T*3 + 'Destroy Icon(Global Variable(WagonIco));' + NLC
 + T*3 + 'Small Message(All Players(All Teams), Custom String("금고 마차가 아무 일 없이 떠났다"));' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Wait Until(Global Variable(IsNight) == 0, 99999);' + NLC
 + T*2 + 'Loop();' + NLC
 + T + '}' + NLC + '}' + NLC + NLC
 + 'rule("[밤 02] 금고 마차 털기 (F 5초)")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Is Dummy Bot(Event Player) == False;' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Event Player.Busy == 0;' + NLC
 + T*2 + 'Global Variable(ArchOn) == 0;' + NLC
 + T*2 + 'Global Variable(WagonOn) == 1;' + NLC
 + T*2 + 'Is Alive(Event Player) == True;' + NLC
 + T*2 + 'Distance Between(Position Of(Event Player), Global Variable(WagonPos)) < 4;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Crouch)) == False;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Interact)) == True;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, Busy, 1);' + NLC
 + T*2 + 'Set Player Variable(Event Player, WorkProg, 0);' + NLC
 + T*2 + 'Destroy Progress Bar HUD Text(Event Player.WorkBar);' + NLC
 + T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("금고를 터는 중..."), Top, 0, Color(Orange), Color(White), Visible To Values and Color, Default Visibility);' + NLC
 + T*2 + 'Set Player Variable(Event Player, WorkBar, Last Text ID());' + NLC
 + T*2 + 'Chase Player Variable Over Time(Event Player, WorkProg, 100, 5, Destination and Duration);' + NLC
 + T*2 + 'Wait Until(Or(Or(Distance Between(Position Of(Event Player), Global Variable(WagonPos)) > 6, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 5.5);' + NLC
 + T*2 + 'Stop Chasing Player Variable(Event Player, WorkProg);' + NLC
 + T*2 + 'Destroy Progress Bar HUD Text(Event Player.WorkBar);' + NLC
 + T*2 + 'If(Or(Or(Distance Between(Position Of(Event Player), Global Variable(WagonPos)) > 6, Not(Is Alive(Event Player))), Event Player.WorkProg < 99));' + NLC
 + T*3 + 'Small Message(Event Player, Custom String("손을 뗐다"));' + NLC
 + T*2 + 'Else If(Global Variable(WagonOn) == 0);' + NLC
 + T*3 + 'Small Message(Event Player, Custom String("한발 늦었다 — 금고가 비어 있다"));' + NLC
 + T*2 + 'Else;' + NLC
 + T*3 + 'Set Global Variable(WagonOn, 0);' + NLC
 + T*3 + 'Destroy Effect(Global Variable(WagonFx));' + NLC
 + T*3 + 'Destroy Icon(Global Variable(WagonIco));' + NLC
 + T*3 + 'Set Player Variable(Event Player, Loot, Random Integer(80, 150));' + NLC
 + T*3 + 'Modify Player Variable(Event Player, Money, Add, Event Player.Loot);' + NLC
 + T*3 + 'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 10)));' + NLC
 + T*3 + 'Big Message(All Players(All Teams), Custom String("{0}이(가) 금고 마차를 털었다! (+$ {1}, 악명 +10)", Event Player, Event Player.Loot));' + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 4);' + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Explosion Sound, Color(Orange), Position Of(Event Player), 180);' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Set Player Variable(Event Player, Busy, 0);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[도파민 02] 보물 상자 출현")', WAGON + 'rule("[도파민 02] 보물 상자 출현")')

# ══ Q2 은행 회수 ══════════════════════════════════════════════════
BANK = ('rule("[부동산 02] 은행 회수 — 떠난 주인")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Global;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC + T*2 + 'Global Variable(Ready) == 1;' + NLC + T + '}' + NLC + NLC
 + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'For Global Variable(Idx, 0, 11, 1);' + NLC
 + T*3 + 'If(And(Value In Array(Global Variable(BldPrice), Global Variable(Idx)) > 0, And(Value In Array(Global Variable(BldOwner), Global Variable(Idx)) != 0, Not(Entity Exists(Value In Array(Global Variable(BldOwner), Global Variable(Idx)))))));' + NLC
 + T*4 + 'Set Global Variable At Index(BldOwner, Global Variable(Idx), 0);' + NLC
 + T*4 + 'Set Global Variable At Index(BldPrice, Global Variable(Idx), Value In Array(Global Variable(BldBase), Global Variable(Idx)));' + NLC
 + T*4 + 'Big Message(All Players(All Teams), Custom String("{0}의 주인이 마을을 떠났다 — 은행이 회수해 매물로 내놨다", Value In Array(%s, Global Variable(Idx))));' % NAMES15 + NLC
 + T*3 + 'End;' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Wait(10, Ignore Condition);' + NLC
 + T*2 + 'Loop();' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[부동산 01] 건물 매입/인수 (웅크리기+F)")', BANK + 'rule("[부동산 01] 건물 매입/인수 (웅크리기+F)")')

# ══ Q3① 보안관 승급 명성 30 ═══════════════════════════════════════
sub('''				Else If(Value In Array(Event Player.JobXP, 3) < 750);
					Small Message(Event Player, Custom String("경험이 부족하다 — {0} / 750", Value In Array(Event Player.JobXP, 3)));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else;''',
'''				Else If(Value In Array(Event Player.JobXP, 3) < 750);
					Small Message(Event Player, Custom String("경험이 부족하다 — {0} / 750", Value In Array(Event Player.JobXP, 3)));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.Fame < 30);
					Small Message(Event Player, Custom String("명성이 부족하다 — 보안관은 신뢰가 필요하다 ({0} / 30)", Event Player.Fame));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else;''')
sub('Custom String("승급: 보안관 — Lv.4")', 'Custom String("승급: 보안관 — Lv.4·명성 30")')

# ══ Q3② 명성 70+ 특전 ════════════════════════════════════════════
sub('''				Else If(Event Player.Money >= 100);
					Modify Player Variable(Event Player, Money, Subtract, 100);
					Set Player Variable(Event Player, Bounty, 0);''',
'''				Else If(Event Player.Money >= (Event Player.Fame >= 70 ? 50 : 100));
					Set Player Variable(Event Player, Amt, Event Player.Fame >= 70 ? 50 : 100);
					Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
					Set Player Variable(Event Player, Bounty, 0);''')
sub('Custom String("돈이 부족합니다 ($100 필요)")', 'Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Fame >= 70 ? 50 : 100)')
sub('벌금 $100 — 수배 말소, 악명 -40', '벌금 $100 (명성 70+는 $50) — 수배 말소, 악명 -40')
sub('Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, 0.05), Down));',
    'Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, Event Player.Fame >= 70 ? 0.025 : 0.05), Down));')
sub('Custom String("재산의 5%. 떼먹으면 재산의 10%가 현상금으로 붙는다")',
    'Custom String("재산의 5% (명성 70+는 절반). 떼먹으면 재산의 10%가 현상금으로 붙는다")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('금고 마차 2규칙 / 은행 회수 1규칙 / 명성 게이트·특전')
