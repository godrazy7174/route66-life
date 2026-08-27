# -*- coding: utf-8 -*-
"""부동산 + 사치 과시 (grill 라운드 2 합의안) + 개활지 이동.

건물 소유  : 6개 상업 건물, [웅크리기+F]로 매입/인수 (메뉴 슬롯 소모 0)
             식당 $10k / 술집 $12k / 모텔 $14k / 잡화점 $16k / 정비소 $18k / 대장간 $20k
징수       : 남이 그 건물에서 쓰는 돈의 10%가 소유주에게 즉시 입금
             정비소·잡화점 매입은 '지급'이라 예외로 두면 정비소가 수입 0인
             죽은 자산이 되므로, 판매액의 10%를 소유주 보너스로 지급(판매자 몫은 그대로)
인수       : 남의 건물은 직전 거래가의 1.5배 — 전액이 전 소유주에게 (50% 차익)
불꽃놀이   : 술집 4번 슬롯 $3,000 — 전 서버 연출
황금 동상  : 대장간 4번 슬롯 $25,000 — 식당 앞, 다음 구매자가 덮어쓸 때까지
개활지     : LocPos[6] = (58.16, 1.39, 23.4)  (설계자 모드로 잡은 좌표)
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

OWNER = lambda z: 'Value In Array(Global Variable(BldOwner), %d)' % z
NAMES = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), '
         'Custom String("모텔"), Custom String("정비소 고물상"), Custom String("술집"), '
         'Custom String("협곡 개활지"), Custom String("보안관 초소"), Custom String("무법자 은신처"), '
         'Custom String("안내소"), Custom String("대장간"))')

# ══ 개활지 이동 ═══════════════════════════════════════════════════
sub('Vector(-16.38, 3.31, -27.15)', 'Vector(58.16, 1.39, 23.4)')

# ══ 변수 ══════════════════════════════════════════════════════════
assert 'BldOwner' not in s and ': Rent' not in s
sub('\t\t31: SellMult\n', '\t\t31: SellMult\n\t\t32: BldOwner\n\t\t33: BldPrice\n\t\t34: StatueFx\n\t\t35: StatueTxt\n')
sub('\t\t63: Adv\n', '\t\t63: Adv\n\t\t64: Rent\n')
sub('\t\tSet Global Variable(SellMult, 1);\n\t\tSet Global Variable(DailyGoal, 480);\n',
    '\t\tSet Global Variable(SellMult, 1);\n\t\tSet Global Variable(DailyGoal, 480);\n'
    '\t\tSet Global Variable(BldOwner, Array(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0));\n'
    '\t\tSet Global Variable(BldPrice, Array(10000, 0, 16000, 14000, 18000, 12000, 0, 0, 0, 0, 20000));\n'
    '\t\tSet Global Variable(StatueFx, 0);\n'
    '\t\tSet Global Variable(StatueTxt, 0);\n')

# ══ 메뉴 수 (술집 3->4, 대장간 3->4) 및 라벨 ══════════════════════
sub('Array(1, 4, 3, 4, 2, 3, 3, 2, 3, 4, 1, 3)', 'Array(1, 4, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4)', 4)
sub('Custom String("소문 듣기"), Custom String("-")',
    'Custom String("소문 듣기"), Custom String("불꽃놀이 $3,000")', 2)
sub('Custom String("말 $3500"), Custom String("-")',
    'Custom String("말 $3500"), Custom String("황금 동상 $25,000")', 2)

# ══ 건물 거래 룰 (웅크리기+F) ═════════════════════════════════════
ZO = 'Value In Array(Global Variable(BldOwner), Event Player.Zone)'
ZP = 'Value In Array(Global Variable(BldPrice), Event Player.Zone)'
ZN = 'Value In Array(%s, Event Player.Zone)' % NAMES
TRADE = ('rule("[부동산 01] 건물 매입/인수 (웅크리기+F)")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC
 + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Is Dummy Bot(Event Player) == False;' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Event Player.Busy == 0;' + NLC
 + T*2 + 'Global Variable(ArchOn) == 0;' + NLC
 + T*2 + 'Is Alive(Event Player) == True;' + NLC
 + T*2 + 'Event Player.Zone != -1;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Crouch)) == True;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Interact)) == True;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'If(%s <= 0);' % ZP + NLC
 + T*3 + 'Small Message(Event Player, Custom String("여긴 살 수 있는 건물이 아니다"));' + NLC
 + T*3 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
 + T*2 + 'Else If(%s == Event Player);' % ZO + NLC
 + T*3 + 'Small Message(Event Player, Custom String("내 건물이다 — 남이 노리는 값은 $ {0}", %s));' % ZP + NLC
 + T*2 + 'Else If(Event Player.Money < %s);' % ZP + NLC
 + T*3 + 'Small Message(Event Player, Custom String("돈이 부족합니다 ($ {0} 필요)", %s));' % ZP + NLC
 + T*3 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
 + T*2 + 'Else;' + NLC
 + T*3 + 'Modify Player Variable(Event Player, Money, Subtract, %s);' % ZP + NLC
 + T*3 + 'If(Entity Exists(%s));' % ZO + NLC
 + T*4 + 'Modify Player Variable(%s, Money, Add, %s);' % (ZO, ZP) + NLC
 + T*4 + 'Big Message(All Players(All Teams), Custom String("{0}이(가) {1}에게서 {2}을(를) 인수했다!", Event Player, %s, %s));' % (ZO, ZN) + NLC
 + T*3 + 'Else;' + NLC
 + T*4 + 'Big Message(All Players(All Teams), Custom String("{0} — {1}의 주인이 되었다!", Event Player, %s));' % ZN + NLC
 + T*3 + 'End;' + NLC
 + T*3 + 'Set Global Variable At Index(BldOwner, Event Player.Zone, Event Player);' + NLC
 + T*3 + 'Set Global Variable At Index(BldPrice, Event Player.Zone, Round To Integer(Multiply(%s, 1.5), To Nearest));' % ZP + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 4);' + NLC
 + T*3 + 'Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 200);' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Wait Until(Not(Is Button Held(Event Player, Button(Interact))), 10);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[범죄 01] 황야에서 강도 / 체포 (F)")', TRADE + 'rule("[범죄 01] 황야에서 강도 / 체포 (F)")')

# ══ 소유 안내판 (건물마다) ════════════════════════════════════════
SIGN = ''
for z in (0, 2, 3, 5, 4, 10):
    o = OWNER(z)
    SIGN += (T*2 + 'Create In-World Text(And(Distance Between(Local Player, Value In Array(Global Variable(LocPos), %d)) < 13, Local Player.TutOn == 0) ? Local Player : False, '
             'Custom String("소유주  {0}      [웅크리기+F] 인수 $ {1}", Entity Exists(%s) ? %s : Custom String("없음 — 매물"), Value In Array(Global Variable(BldPrice), %d)), '
             'Add(Value In Array(Global Variable(LocPos), %d), Vector(0, 0.9, 0)), 0.8, Do Not Clip, Visible To Position and String, Color(Yellow), Default Visibility);' % (z, o, o, z, z) + NLC)
sub('\t\tFor Global Variable(Idx, 0, 3, 1);\n', 'PLACEHOLDER_NEVER', 0) if False else None
anchor = '\t\tCreate Dummy Bot(Hero(Jetpack Cat), Team 2, 0,'
i = s.index(anchor)
s = s[:i] + SIGN + s[i:]

# ══ 징수 헬퍼 삽입 ════════════════════════════════════════════════
def levy(z, amt, tabs):
    o = OWNER(z)
    L = T * tabs
    return (L + 'If(And(Entity Exists(%s), %s != Event Player));' % (o, o) + NLC
          + L + T + 'Set Player Variable(%s, Rent, Max(1, Round To Integer(Multiply(%s, 0.1), To Nearest)));' % (o, amt) + NLC
          + L + T + 'Modify Player Variable(%s, Money, Add, Player Variable(%s, Rent));' % (o, o) + NLC
          + L + T + 'Small Message(%s, Custom String("임대 수입 +$ {0}", Player Variable(%s, Rent)));' % (o, o) + NLC
          + L + 'End;' + NLC)

AMT = 'Event Player.Amt'
SITES = [
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\t\t\t\tSet Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 55)));\n', 0, AMT, 5, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\t\t\t\tSet Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 1));\n', 2, AMT, 5, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\t\t\t\tSet Player Variable At Index(Event Player, Inv, 1, Add(Value In Array(Event Player.Inv, 1), 1));\n', 2, AMT, 5, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\t\t\t\tSet Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 5));\n', 2, AMT, 5, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 7000);\n', 3, '7000', 5, 0),
    ('\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\tSet Player Variable(Event Player, Busy, 1);\n\t\tSet Status(Event Player, Null, Asleep, 4.6);\n', 3, AMT, 2, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\t\t\t\tModify Player Variable(Event Player, Whisky, Add, 1);\n', 5, AMT, 5, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 50);\n\t\t\t\t\tSet Player Variable(Event Player, Busy, 1);\n', 5, '50', 5, 0),
    ('\t\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, Event Player.Amt);\n\t\t\t\t\t\tModify Player Variable(Event Player, Pick, Add, 1);\n', 10, AMT, 6, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 1800);\n', 10, '1800', 5, 0),
    ('\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 3500);\n', 10, '3500', 5, 0),
]
for anchor, z, amt, tabs, _ in SITES:
    assert s.count(anchor) == 1, anchor[:60]
    s = s.replace(anchor, anchor + levy(z, amt, tabs), 1)

# 판매 보너스: 정비소 두 갈래 + 잡화점 매입 (판매자 몫은 그대로, 소유주 +10%)
SELL_SITES = [
    ('원석 {0}개 판매', 4), ('가죽 {0}장 판매', 4), ('잡화점에 전부 넘겼다', 2),
]
for key, z in SELL_SITES:
    k = s.index('Custom String("' + key)
    j = s.index(NLC, k) + 1
    tabs = 5 if z == 4 else 5
    s = s[:j] + levy(z, 'Event Player.SellSum', tabs) + s[j:]

# ══ 술집: 불꽃놀이 ════════════════════════════════════════════════
FIRE = ('''			Else If(Event Player.MenuIdx == 3);
				If(Event Player.Money >= 3000);
					Modify Player Variable(Event Player, Money, Subtract, 3000);
''' + levy(5, '3000', 5)
+ '''				Big Message(All Players(All Teams), Custom String("{0}이(가) 하늘에 불꽃을 쏘아 올렸다!!", Event Player));
					Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Position Of(Event Player), Vector(0, 18, 0)), 8);
					Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Add(Position Of(Event Player), Vector(-6, 24, 4)), 6);
					Play Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Add(Position Of(Event Player), Vector(5, 30, -5)), 7);
					Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 250);
				Else;
					Small Message(Event Player, Custom String("돈이 부족합니다 ($3000 필요)"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				End;
''')
FIRE = FIRE.replace(NLC + T*5 + 'If(And(Entity Exists', NLC + T*5 + 'If(And(Entity Exists')
sub('''			Else;
				Small Message(Event Player, Custom String("소문 — 원석 $ {0}, 가죽 $ {1}", Global Variable(OrePrice), Global Variable(HidePrice)));''',
'''			Else If(Event Player.MenuIdx == 2);
				Small Message(Event Player, Custom String("소문 — 원석 $ {0}, 가죽 $ {1}", Global Variable(OrePrice), Global Variable(HidePrice)));''')
KEY5 = 'Custom String("소문 — 오늘은 조용하다")'
i = s.index(KEY5)
j = s.index('\t\t\tEnd;\n\t\tElse If(Event Player.Zone == 6);', i)
s = s[:j] + FIRE + s[j:]

# ══ 대장간: 황금 동상 ═════════════════════════════════════════════
STATUE = ('''			Else If(Event Player.MenuIdx == 3);
				If(Event Player.Money >= 25000);
					Modify Player Variable(Event Player, Money, Subtract, 25000);
''' + levy(10, '25000', 5)
+ '''				Destroy Effect(Global Variable(StatueFx));
					Destroy In-World Text(Global Variable(StatueTxt));
					Create Effect(All Players(All Teams), Sphere, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 0), Vector(2.5, 1.4, 2.5)), 0.9, Visible To Position Radius and Color);
					Set Global Variable(StatueFx, Last Created Entity());
					Create In-World Text(All Players(All Teams), Custom String("『 {0} 』", Event Player), Add(Value In Array(Global Variable(LocPos), 0), Vector(2.5, 3, 2.5)), 1.6, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);
					Set Global Variable(StatueTxt, Last Text ID());
					Big Message(All Players(All Teams), Custom String("{0} — 식당 앞에 황금 동상을 세웠다!! ($25,000)", Event Player));
					Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 0), Vector(2.5, 1.4, 2.5)), 6);
					Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 250);
				Else;
					Small Message(Event Player, Custom String("돈이 부족합니다 ($25000 필요)"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				End;
''')
sub('''			Else;
				If(Event Player.HasHorse == 1);''',
'''			Else If(Event Player.MenuIdx == 2);
				If(Event Player.HasHorse == 1);''')
KEY10 = 'Custom String("돈이 부족합니다 ($3500 필요)")'
i = s.index(KEY10)
j = s.index('\t\t\tEnd;\n\t\tEnd;', i)
s = s[:j] + STATUE + s[j:]

# ══ 패널 문구 ═════════════════════════════════════════════════════
sub('위스키 $25 — 피로 회복' + NL + '카드 도박 $50' + NL + '소문 듣기' + NL,
    '위스키 $25 — 피로 회복' + NL + '카드 도박 $50      소문 듣기' + NL + '불꽃놀이 $3000 — 전 서버에 쏘아 올린다' + NL)
sub('말 $3500 — 시온 변신, 바이크 해금' + NL,
    '말 $3500 — 시온 변신, 바이크 해금' + NL + '황금 동상 $25000 — 식당 앞에 이름을 새긴다' + NL)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('부동산 6건물 + 징수 14곳 + 인수 + 불꽃놀이 + 동상 + 개활지 이동 완료')
