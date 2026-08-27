# -*- coding: utf-8 -*-
"""범죄 대형 콘텐츠 3/3 — 밀수 호송.

  은신처에서 [V]로 밀수 화물을 받아 무작위 접선지까지 운반한다.
  운반 중 질주가 막히고 주기적으로 위치가 노출되며, 사망·강탈 시 화물을 잃는다.
  접선지에서 3초간 인계하면 거리 비례 보수와 악명 +8을 받고 60초 재사용 대기한다.
"""
import io

T = chr(9)
N = chr(10)
B = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

def block(depth, *lines):
    return ''.join(T*depth + ln + N for ln in lines)

def insert_into(rule_header, section, insertion):
    global s
    assert s.count(rule_header) == 1, rule_header
    i = s.index(rule_header)
    key = section + N + T + '{' + N
    assert s.count(key, i) >= 1, (rule_header, section)
    j = s.index(key, i) + len(key)
    s = s[:j] + insertion + s[j:]

def mkrule(name, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N + ''.join(T*2 + c + N for c in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + acts + T + '}' + N + '}' + N + N)

# ── 1. 플레이어 변수 ────────────────────────────────────────────────
sub(T*2 + '109: BrewReady' + N + '}',
    T*2 + '109: BrewReady' + N + T*2 + '110: Contraband' + N
    + T*2 + '111: SmugglePos' + N + T*2 + '112: SmuggleIco' + N
    + T*2 + '113: SmugglePay' + N + T*2 + '114: SmuggleCd' + N
    + T*2 + '115: SmuggleFlash' + N + '}')

# ── 2. 은신처 [V] 수주 — [범죄 01]의 대상 없음 분기 확장 ───────────
OLD_NOTGT = (block(2, 'If(Not(Entity Exists(Event Player.Target)));')
    + block(3, 'If(And(And(Event Player.Zone == 9, Global Variable(IsNight) == 1), And(And(Global Variable(RebuildMax) >= 3, Global Variable(Day) >= Global Variable(BankLockDay)), Event Player.JailOn == 0)));')
    + block(4, 'Set Player Variable(Event Player, Busy, 1);',
               'Set Player Variable(Event Player, DialOn, 1);',
               'Set Player Variable(Event Player, DialTgt, Random Integer(0, 9));',
               'Set Player Variable(Event Player, DialPin, 1);',
               'Set Player Variable(Event Player, DialCur, 0);',
               'Destroy HUD Text(Event Player.KeyHud);',
               'Create HUD Text(Event Player, Custom String("은행 다이얼   [ {0} ]", Event Player.DialCur), Custom String("핀 {0} / 3", Event Player.DialPin), Custom String("[R] 돌리기      [F] 시도      [웅크리기] 포기"), Left, 5, Color(Orange), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);',
               'Set Player Variable(Event Player, KeyHud, Last Text ID());',
               'Big Message(Event Player, Custom String("은행 뒷문에 붙었다 — 다이얼을 맞혀라"));',
               'Small Message(Event Player, Custom String("아직은 조용하다 — 해정하는 순간 마을이 깬다"));')
    + block(3, 'Else;')
    + block(4, 'Small Message(Event Player, Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Melee))));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(3, 'End;')
    + block(3, 'Abort;')
    + block(2, 'End;'))
NEW_NOTGT = (block(2, 'If(Not(Entity Exists(Event Player.Target)));')
    + block(3, 'If(And(And(Event Player.Zone == 9, Global Variable(IsNight) == 1), And(And(Global Variable(RebuildMax) >= 3, Global Variable(Day) >= Global Variable(BankLockDay)), Event Player.JailOn == 0)));')
    + block(4, 'Set Player Variable(Event Player, Busy, 1);',
               'Set Player Variable(Event Player, DialOn, 1);',
               'Set Player Variable(Event Player, DialTgt, Random Integer(0, 9));',
               'Set Player Variable(Event Player, DialPin, 1);',
               'Set Player Variable(Event Player, DialCur, 0);',
               'Destroy HUD Text(Event Player.KeyHud);',
               'Create HUD Text(Event Player, Custom String("은행 다이얼   [ {0} ]", Event Player.DialCur), Custom String("핀 {0} / 3", Event Player.DialPin), Custom String("[R] 돌리기      [F] 시도      [웅크리기] 포기"), Left, 5, Color(Orange), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);',
               'Set Player Variable(Event Player, KeyHud, Last Text ID());',
               'Big Message(Event Player, Custom String("은행 뒷문에 붙었다 — 다이얼을 맞혀라"));',
               'Small Message(Event Player, Custom String("아직은 조용하다 — 해정하는 순간 마을이 깬다"));')
    + block(3, 'Else If(And(And(Event Player.Zone == 8, Event Player.Contraband == 0), Total Time Elapsed() >= Event Player.SmuggleCd));')
    + block(4, 'Set Player Variable(Event Player, SmugglePos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-15, 15), 0, Random Real(-15, 15)))));',
               'Set Player Variable(Event Player, SmugglePay, Round To Integer(Add(30, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 8), Event Player.SmugglePos), 2.5)), To Nearest));',
               'Set Player Variable(Event Player, Contraband, 1);',
               'Destroy Icon(Event Player.SmuggleIco);',
               'Create Icon(Event Player, Add(Event Player.SmugglePos, Vector(0, 3, 0)), Diamond, Visible To and Position, Color(Purple), True);',
               'Set Player Variable(Event Player, SmuggleIco, Last Created Entity());',
               'Big Message(Event Player, Custom String("밀수 화물을 받았다 — 접선지로 (보수 $ {0})", Event Player.SmugglePay));',
               'Small Message(Event Player, Custom String("화물을 진 동안 질주할 수 없고, 죽으면 끝이다 — 자주색 표식을 따라가라"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Purple), Position Of(Event Player), 60);')
    + block(3, 'Else;')
    + block(4, 'Small Message(Event Player, Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Melee))));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(3, 'End;')
    + block(3, 'Abort;')
    + block(2, 'End;'))
sub(OLD_NOTGT, NEW_NOTGT)

# ── 3. 운반 중 질주 금지 ───────────────────────────────────────────
insert_into('rule("[조작 04] 달리기 (Shift)")', 'conditions',
    T*2 + 'Event Player.Contraband == 0;' + N)

# ── 4. 주기 노출 + 접선 인계 ───────────────────────────────────────
SMUGGLE_RULES = (
  mkrule('[밀수 01] 화물 냄새',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;',
     'Event Player.Contraband == 1;', 'Is Alive(Event Player) == True;'],
    block(2, 'Create Icon(All Players(All Teams), Add(Position Of(Event Player), Vector(0, 2.6, 0)), Circle, Visible To and Position, Color(Purple), True);',
             'Set Player Variable(Event Player, SmuggleFlash, Last Created Entity());',
             'Wait(3, Ignore Condition);',
             'Destroy Icon(Event Player.SmuggleFlash);',
             'Wait(17, Ignore Condition);',
             'Loop If(And(Event Player.Contraband == 1, Is Alive(Event Player)));'))
+ mkrule('[밀수 02] 접선 인계 (F 3초)',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;',
     'Event Player.Busy == 0;', 'Global Variable(ArchOn) == 0;',
     'Event Player.Contraband == 1;', 'Is Alive(Event Player) == True;',
     'Distance Between(Position Of(Event Player), Event Player.SmugglePos) < 4;',
     'Is Button Held(Event Player, Button(Crouch)) == False;',
     'Is Button Held(Event Player, Button(Interact)) == True;'],
    block(2, 'Set Player Variable(Event Player, Busy, 1);',
             'Set Player Variable(Event Player, WorkProg, 0);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);',
             'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("화물 인계 중..."), Top, 0, Color(Purple), Color(White), Visible To Values and Color, Default Visibility);',
             'Set Player Variable(Event Player, WorkBar, Last Text ID());',
             'Chase Player Variable Over Time(Event Player, WorkProg, 100, 3, Destination and Duration);',
             'Wait Until(Or(Or(Distance Between(Position Of(Event Player), Event Player.SmugglePos) > 6, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3.5);',
             'Stop Chasing Player Variable(Event Player, WorkProg);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);')
    + block(2, 'If(Or(Or(Distance Between(Position Of(Event Player), Event Player.SmugglePos) > 6, Not(Is Alive(Event Player))), Event Player.WorkProg < 99));')
    + block(3, 'Small Message(Event Player, Custom String("손을 뗐다"));')
    + block(2, 'Else;')
    + block(3, 'Modify Player Variable(Event Player, Money, Add, Event Player.SmugglePay);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 8)));',
               'Set Player Variable(Event Player, Contraband, 0);',
               'Destroy Icon(Event Player.SmuggleIco);',
               'Set Player Variable(Event Player, SmuggleCd, Add(Total Time Elapsed(), 60));',
               'Small Message(Event Player, Custom String("화물을 넘겼다 — +$ {0} (악명 +8)", Event Player.SmugglePay));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 120);')
    + block(2, 'End;',
               'Set Player Variable(Event Player, Busy, 0);')))

sub('rule("[감옥 01] 만기 출소")', SMUGGLE_RULES + 'rule("[감옥 01] 만기 출소")')

# ── 5. 사망 시 밀수 화물 소실 ──────────────────────────────────────
OLD_DEATH = (block(2, 'If(Event Player.Sack > 0);')
    + block(3, 'Set Player Variable(Event Player, Loot, Event Player.Sack);',
               'Set Player Variable(Event Player, Sack, 0);',
               'Small Message(Event Player, Custom String("장물 자루를 흘렸다 — $ {0} 소실", Event Player.Loot));')
    + block(2, 'End;'))
NEW_DEATH = (OLD_DEATH
    + block(2, 'If(Event Player.Contraband == 1);')
    + block(3, 'Set Player Variable(Event Player, Contraband, 0);',
               'Destroy Icon(Event Player.SmuggleIco);',
               'Small Message(Event Player, Custom String("밀수 화물을 잃었다 — 접선은 없던 일이 됐다"));')
    + block(2, 'End;'))
sub(OLD_DEATH, NEW_DEATH)

# ── 6. 강탈 성공 시 밀수 화물 가로채기 ────────────────────────────
OLD_INTERCEPT = (block(4, 'If(Player Variable(Event Player.Target, HasParcel) == 1);')
    + block(5, 'Set Player Variable(Event Player.Target, HasParcel, 0);',
               'Destroy Icon(Player Variable(Event Player.Target, DelIcon));',
               'Modify Player Variable(Event Player, Money, Add, 60);',
               'Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 화물을 가로챘다! (+$60)", Event Player, Event Player.Target));')
    + block(4, 'End;'))
NEW_INTERCEPT = (OLD_INTERCEPT
    + block(4, 'If(Player Variable(Event Player.Target, Contraband) == 1);')
    + block(5, 'Set Player Variable(Event Player.Target, Contraband, 0);',
               'Destroy Icon(Player Variable(Event Player.Target, SmuggleIco));',
               'Modify Player Variable(Event Player, Money, Add, 80);',
               'Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 밀수 화물을 가로챘다! (+$80)", Event Player, Event Player.Target));')
    + block(4, 'End;'))
sub(OLD_INTERCEPT, NEW_INTERCEPT)

# ── 7. 은신처 안내판 ────────────────────────────────────────────────
SIGN_OLD = '밤의 큰 건 — 은행(재건 3단계)과 열차는 간 큰 자를 기다린다' + B
SIGN_NEW = SIGN_OLD + '밀수 — [V]로 화물 수주, 접선지 인계 (질주 불가·죽으면 소실)' + B
sub(SIGN_OLD, SIGN_NEW)

io.open(P, 'w', encoding='utf-8', newline=N).write(s)
print('밀수 호송 적용')
