# -*- coding: utf-8 -*-
"""범죄 대형 콘텐츠 2/3 — 대열차 강도.

  주기   3일마다(3·6·9일차...) 저녁 8시, 협곡 철길목(정거장~개활지 중간)
  준비   대장간에서 화약 $200 구매 -> 열차의 날 낮에 철길목 [F] 8초 설치
         (설치 순간 전서버에 익명 경고 + 위치 5초 노출, 악명 +5)
  실행   8시 열차 폭파 정차, 90초 안에 금고 3칸을 각 [F] 5초로 개방
         칸당 자루 $300~500 · 악명 +10 · 현상금 +$150 (선착순, 경쟁 개방)
  도주   장물 자루 규칙 적용 — 은신처 정산, 질주 불가, 죽으면 소실
  화약 미설치 시 열차는 무사 통과
"""
import io

T = chr(9)
N = chr(10)
RN = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

def block(depth, *lines):
    return ''.join(T*depth + ln + N for ln in lines)

# ── 1. 변수 ────────────────────────────────────────────────────────
sub(T*2 + '104: HeistEnd' + N + '}',
    T*2 + '104: HeistEnd' + N + T*2 + '105: HasPowder' + N + '}')
sub(T*2 + '41: AlarmIco' + N,
    T*2 + '41: AlarmIco' + N + T*2 + '42: TrainPos' + N + T*2 + '43: TrainOn' + N
    + T*2 + '44: TrainVault' + N + T*2 + '45: TrainEnd' + N + T*2 + '46: PowderSet' + N
    + T*2 + '47: TrainFx' + N + T*2 + '48: TrainIco' + N)
sub(T*2 + 'Set Global Variable(AlarmIco, 0);' + N,
    T*2 + 'Set Global Variable(AlarmIco, 0);' + N
    + block(2, 'Set Global Variable(TrainOn, 0);', 'Set Global Variable(TrainVault, 0);',
               'Set Global Variable(TrainEnd, 0);', 'Set Global Variable(PowderSet, 0);',
               'Set Global Variable(TrainFx, Empty Array);', 'Set Global Variable(TrainIco, 0);'))

# ── 2. 철길목 위치 + 표지 (BuildWorld) ─────────────────────────────
sub(T*2 + 'Set Global Variable At Index(LocPos, 14, Nearest Walkable Position(Value In Array(Global Variable(LocPos), 14)));' + N,
    T*2 + 'Set Global Variable At Index(LocPos, 14, Nearest Walkable Position(Value In Array(Global Variable(LocPos), 14)));' + N
    + block(2, 'Set Global Variable(TrainPos, Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 11), Value In Array(Global Variable(LocPos), 6)), 0.5)));',
               'Create In-World Text(All Players(All Teams), Custom String("협곡 철길목 — 사흘에 한 번, 저녁 8시 열차"), Add(Global Variable(TrainPos), Vector(0, 2.2, 0)), 1.2, Do Not Clip, Visible To and Position, Color(Orange), Default Visibility);'))

# ── 3. 아침 공지 (열차의 날) ───────────────────────────────────────
JOBLINE = 'Big Message(All Players(All Teams), Custom String("새 아침 — 오늘은 {0}의 날! 해당 직업 보수 1.5배"'
i = s.index(JOBLINE)
j = s.index(N, i) + 1
TRAIN_NOTICE = (block(3, 'If(Modulo(Global Variable(Day), 3) == 0);')
    + block(4, 'Small Message(All Players(All Teams), Custom String("오늘은 열차의 날 — 저녁 8시, 열차가 협곡 철길목을 지난다"));')
    + block(3, 'End;'))
s = s[:j] + TRAIN_NOTICE + s[j:]

# ── 4. 대장간 화약 메뉴 ────────────────────────────────────────────
sub('Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 4, 4, 4, 2, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 4, 4, 5, 2, 2, 1, 1)', 3)
sub('Custom String("말 $5500"), Custom String("황금 동상 $40,000")',
    'Custom String("말 $5500"), Custom String("화약 $200 — 열차의 날"), Custom String("황금 동상 $40,000")')
POWDER_MENU = (block(3, 'Else If(Event Player.MenuIdx == 3);')
    + block(4, 'If(Event Player.HasPowder == 1);')
    + block(5, 'Small Message(Event Player, Custom String("화약은 이미 챙겼다"));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(4, 'Else If(Event Player.Money >= 200);')
    + block(5, 'Modify Player Variable(Event Player, Money, Subtract, 200);',
               'Set Player Variable(Event Player, HasPowder, 1);')
    + block(5, 'If(And(Entity Exists(Value In Array(Global Variable(BldOwner), 10)), Value In Array(Global Variable(BldOwner), 10) != Event Player);'.replace('Event Player);', 'Event Player));'))
    + block(6, 'Set Player Variable(Value In Array(Global Variable(BldOwner), 10), Rent, Max(1, Round To Integer(Multiply(200, 0.1), To Nearest)));',
               'Modify Player Variable(Value In Array(Global Variable(BldOwner), 10), Money, Add, Player Variable(Value In Array(Global Variable(BldOwner), 10), Rent));',
               'Small Message(Value In Array(Global Variable(BldOwner), 10), Custom String("임대 수입 +$ {0}", Player Variable(Value In Array(Global Variable(BldOwner), 10), Rent)));')
    + block(5, 'End;')
    + block(5, 'Big Message(Event Player, Custom String("화약을 챙겼다 — 열차의 날, 철길목에서 [{0}]로 설치", Input Binding String(Button(Interact))));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 70);')
    + block(4, 'Else;')
    + block(5, 'Small Message(Event Player, Custom String("돈이 부족합니다 ($200 필요)"));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(4, 'End;'))
sub(T*3 + 'Else If(Event Player.MenuIdx == 3);' + N + T*4 + 'If(Event Player.Money >= 40000);',
    POWDER_MENU + T*3 + 'Else If(Event Player.MenuIdx == 4);' + N + T*4 + 'If(Event Player.Money >= 40000);')

# ── 5. 열차 규칙 3종 ───────────────────────────────────────────────
def mkgrule(name, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Global;' + N + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N + ''.join(T*2 + c + N for c in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + acts + T + '}' + N + '}' + N + N)

def mkrule(name, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N + ''.join(T*2 + c + N for c in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + acts + T + '}' + N + '}' + N + N)

TRAIN_RULES = (
  mkrule('[열차 01] 화약 설치 (F 8초)',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;', 'Event Player.Busy == 0;',
     'Global Variable(ArchOn) == 0;', 'Is Alive(Event Player) == True;',
     'Event Player.HasPowder == 1;', 'Global Variable(PowderSet) == 0;',
     'Modulo(Global Variable(Day), 3) == 0;', 'Global Variable(Clock) < 1200;',
     'Distance Between(Position Of(Event Player), Global Variable(TrainPos)) < 5;',
     'Is Button Held(Event Player, Button(Crouch)) == False;',
     'Is Button Held(Event Player, Button(Interact)) == True;'],
    block(2, 'Set Player Variable(Event Player, Busy, 1);',
             'Set Player Variable(Event Player, WorkProg, 0);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);',
             'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("화약 설치 중..."), Top, 0, Color(Orange), Color(White), Visible To Values and Color, Default Visibility);',
             'Set Player Variable(Event Player, WorkBar, Last Text ID());',
             'Chase Player Variable Over Time(Event Player, WorkProg, 100, 8, Destination and Duration);',
             'Wait Until(Or(Or(Distance Between(Position Of(Event Player), Global Variable(TrainPos)) > 7, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 8.5);',
             'Stop Chasing Player Variable(Event Player, WorkProg);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);')
    + block(2, 'If(Or(Or(Distance Between(Position Of(Event Player), Global Variable(TrainPos)) > 7, Not(Is Alive(Event Player))), Event Player.WorkProg < 99));')
    + block(3, 'Small Message(Event Player, Custom String("손을 뗐다 — 화약은 아직 품 안에 있다"));')
    + block(2, 'Else;')
    + block(3, 'Set Player Variable(Event Player, HasPowder, 0);',
               'Set Global Variable(PowderSet, 1);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 5)));',
               'Big Message(Event Player, Custom String("화약을 심었다 — 저녁 8시를 기다려라"));',
               'Small Message(All Players(All Teams), Custom String("철길목에서 수상한 인기척이 있었다..."));',
               'Destroy Icon(Global Variable(TrainIco));',
               'Create Icon(All Players(All Teams), Add(Global Variable(TrainPos), Vector(0, 3, 0)), Warning, Visible To and Position, Color(Orange), True);',
               'Set Global Variable(TrainIco, Last Created Entity());',
               'Wait(5, Ignore Condition);',
               'Destroy Icon(Global Variable(TrainIco));')
    + block(2, 'End;')
    + block(2, 'Set Player Variable(Event Player, Busy, 0);'))
+ mkgrule('[열차 02] 열차 통과',
    ['Global Variable(Ready) == 1;'],
    block(2, 'Wait Until(And(Modulo(Global Variable(Day), 3) == 0, Global Variable(Clock) >= 1200), 99999);')
    + block(2, 'If(Global Variable(PowderSet) == 0);')
    + block(3, 'Big Message(All Players(All Teams), Custom String("열차가 협곡을 무사히 지나갔다"));')
    + block(2, 'Else;')
    + block(3, 'Set Global Variable(PowderSet, 0);',
               'Set Global Variable(TrainOn, 1);',
               'Set Global Variable(TrainVault, 3);',
               'Set Global Variable(TrainEnd, Add(Total Time Elapsed(), 90));',
               'Set Global Variable(TrainFx, Empty Array);',
               'Create Effect(All Players(All Teams), Sphere, Color(Orange), Add(Global Variable(TrainPos), Vector(-3, 1.2, 0)), 1.4, None);',
               'Modify Global Variable(TrainFx, Append To Array, Last Created Entity());',
               'Create Effect(All Players(All Teams), Sphere, Color(Orange), Add(Global Variable(TrainPos), Vector(0, 1.4, 0)), 1.6, None);',
               'Modify Global Variable(TrainFx, Append To Array, Last Created Entity());',
               'Create Effect(All Players(All Teams), Sphere, Color(Orange), Add(Global Variable(TrainPos), Vector(3, 1.2, 0)), 1.4, None);',
               'Modify Global Variable(TrainFx, Append To Array, Last Created Entity());',
               'Create Icon(All Players(All Teams), Add(Global Variable(TrainPos), Vector(0, 4, 0)), Skull, Visible To and Position, Color(Orange), True);',
               'Set Global Variable(TrainIco, Last Created Entity());',
               'Big Message(All Players(All Teams), Custom String("폭발!! 열차가 철길목에 멈췄다 — 금고 3칸, 90초"));',
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Global Variable(TrainPos), 10);',
               'Play Effect(All Players(All Teams), Explosion Sound, Color(Orange), Global Variable(TrainPos), 250);',
               'Wait Until(Or(Global Variable(TrainOn) == 0, Total Time Elapsed() > Global Variable(TrainEnd)), 95);',
               'Set Global Variable(TrainOn, 0);')
    + block(3, 'For Global Variable(Idx, 0, 3, 1);')
    + block(4, 'Destroy Effect(Value In Array(Global Variable(TrainFx), Global Variable(Idx)));')
    + block(3, 'End;')
    + block(3, 'Destroy Icon(Global Variable(TrainIco));',
               'Big Message(All Players(All Teams), Custom String("열차가 다시 움직인다 — 강도극이 끝났다"));')
    + block(2, 'End;')
    + block(2, 'Wait Until(Modulo(Global Variable(Day), 3) != 0, 99999);')
    + block(2, 'Loop();'))
+ mkrule('[열차 03] 금고 개방 (F 5초)',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;', 'Event Player.Busy == 0;',
     'Global Variable(ArchOn) == 0;', 'Global Variable(TrainOn) == 1;', 'Global Variable(TrainVault) > 0;',
     'Is Alive(Event Player) == True;',
     'Distance Between(Position Of(Event Player), Global Variable(TrainPos)) < 5;',
     'Is Button Held(Event Player, Button(Crouch)) == False;',
     'Is Button Held(Event Player, Button(Interact)) == True;'],
    block(2, 'Set Player Variable(Event Player, Busy, 1);',
             'Set Player Variable(Event Player, WorkProg, 0);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);',
             'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("금고를 뜯는 중..."), Top, 0, Color(Orange), Color(White), Visible To Values and Color, Default Visibility);',
             'Set Player Variable(Event Player, WorkBar, Last Text ID());',
             'Chase Player Variable Over Time(Event Player, WorkProg, 100, 5, Destination and Duration);',
             'Wait Until(Or(Or(Distance Between(Position Of(Event Player), Global Variable(TrainPos)) > 7, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 5.5);',
             'Stop Chasing Player Variable(Event Player, WorkProg);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);')
    + block(2, 'If(Or(Or(Distance Between(Position Of(Event Player), Global Variable(TrainPos)) > 7, Not(Is Alive(Event Player))), Event Player.WorkProg < 99));')
    + block(3, 'Small Message(Event Player, Custom String("손을 뗐다"));')
    + block(2, 'Else If(Or(Global Variable(TrainOn) == 0, Global Variable(TrainVault) <= 0));')
    + block(3, 'Small Message(Event Player, Custom String("한발 늦었다 — 금고가 비어 있다"));')
    + block(2, 'Else;')
    + block(3, 'Modify Global Variable(TrainVault, Subtract, 1);',
               'Set Player Variable(Event Player, Loot, Random Integer(300, 500));',
               'Modify Player Variable(Event Player, Sack, Add, Event Player.Loot);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 10)));',
               'Modify Player Variable(Event Player, Bounty, Add, 150);',
               'Big Message(All Players(All Teams), Custom String("{0}이(가) 열차 금고를 뜯었다! (+$ {1}) — 남은 금고 {2}", Event Player, Event Player.Loot, Global Variable(TrainVault)));',
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 3);')
    + block(3, 'If(Global Variable(TrainVault) <= 0);')
    + block(4, 'Set Global Variable(TrainOn, 0);')
    + block(3, 'End;')
    + block(2, 'End;')
    + block(2, 'Set Player Variable(Event Player, Busy, 0);')))

sub('rule("[감옥 01] 만기 출소")', TRAIN_RULES + 'rule("[감옥 01] 만기 출소")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('대열차 강도 적용')
