# -*- coding: utf-8 -*-
"""활동형 직업 2종 + 전용 장소 2곳.

파발꾼 (Job 5) @ 역마차 정거장 (zone 11, 좌표 38,2.2,40 — NWP 보정)
    수주하면 무작위 장소가 목적지로 찍히고(전용 화살표 아이콘),
    그 구역에 발을 들이는 순간 자동 정산. 보수 = 거리 x 1.5 (레벨당 +5%).
    화물을 든 채 강탈당하거나 죽으면 화물을 잃는다 (강도에게 +$60).
    승급: 역마차장 — 배달비 +30%, 배달마다 피로 5 회복.

목동 (Job 6) @ 목장 (zone 12, 좌표 -52,4,5 — NWP 보정)
    몰기 시작하면 흰 소(구체)가 벌판에 나타난다. 소는 다가가면 반대쪽으로
    밀려난다 — 몸으로 방향을 잡아 우리(목장 5m 안)로 몰아넣어라. 90초 제한.
    보수 $55 + 레벨당 $3. 승급: 목장주 — 보수 +40%, 소가 더 성큼 밀린다.

시스템 편입: 구역 감지 0~12, 메뉴/라벨/HUD 직업명/승급/사망 정리/광기둥까지.
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

L11 = 'Value In Array(Global Variable(LocPos), 11)'
L12 = 'Value In Array(Global Variable(LocPos), 12)'

# ══ 변수 ══════════════════════════════════════════════════════════
for v in ('HasParcel', 'DelDest', 'DelIcon', 'CowPos', 'CowFx', 'CowOn', 'RunPay', 'CowEnd'):
    assert ': ' + v not in s
sub('\t\t64: Rent\n', '\t\t64: Rent\n\t\t65: HasParcel\n\t\t66: DelDest\n\t\t67: DelIcon\n'
    '\t\t68: CowPos\n\t\t69: CowFx\n\t\t70: CowOn\n\t\t71: RunPay\n\t\t72: CowEnd\n')

# ══ 좌표·반경·구역 감지 ═══════════════════════════════════════════
sub('\t\tModify Global Variable(LocPos, Append To Array, Add(Value In Array(Global Variable(LocPos), 4), Vector(6, 0, 0)));\n',
    '\t\tModify Global Variable(LocPos, Append To Array, Add(Value In Array(Global Variable(LocPos), 4), Vector(6, 0, 0)));\n'
    '\t\tModify Global Variable(LocPos, Append To Array, Vector(38, 2.2, 40));\n'
    '\t\tModify Global Variable(LocPos, Append To Array, Vector(-52, 4, 5));\n')
sub('Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6));', 'Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6, 6, 7));')
sub('For Player Variable(Event Player, Idx, 0, 11, 1);', 'For Player Variable(Event Player, Idx, 0, 13, 1);')
sub('\t\tSet Global Variable At Index(LocPos, 10, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 4), Vector(6, 0, 0))));\n',
    '\t\tSet Global Variable At Index(LocPos, 10, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 4), Vector(6, 0, 0))));\n'
    '\t\tSet Global Variable At Index(LocPos, 11, Nearest Walkable Position(%s));\n' % L11
  + '\t\tSet Global Variable At Index(LocPos, 12, Nearest Walkable Position(%s));\n' % L12)

# ══ 초기화 ════════════════════════════════════════════════════════
sub('\t\tSet Player Variable(Event Player, Adv, 0);\n\t\tSet Player Variable(Event Player, JobXP, Array(0, 0, 0, 0, 0));\n',
    '\t\tSet Player Variable(Event Player, Adv, 0);\n\t\tSet Player Variable(Event Player, JobXP, Array(0, 0, 0, 0, 0, 0, 0));\n'
    '\t\tSet Player Variable(Event Player, HasParcel, 0);\n\t\tSet Player Variable(Event Player, DelDest, -1);\n'
    '\t\tSet Player Variable(Event Player, CowOn, 0);\n')

# ══ 메뉴 수·구역 이름·라벨 ════════════════════════════════════════
sub('Array(1, 4, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4)', 'Array(1, 4, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4, 3, 3)', 4)
sub('Custom String("안내소"), Custom String("대장간")), Add(Local Player.Zone, 1))',
    'Custom String("안내소"), Custom String("대장간"), Custom String("역마차 정거장"), Custom String("목장")), Add(Local Player.Zone, 1))')
NEWLBL = (', Custom String("전직: 파발꾼"), Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("-"), '
          'Custom String("전직: 목동"), Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("-")')
sub('Custom String("말 $3500"), Custom String("황금 동상 $25,000"))',
    'Custom String("말 $3500"), Custom String("황금 동상 $25,000")' + NEWLBL + ')', 2)

# ══ HUD 직업명 (기본/승급) ════════════════════════════════════════
sub('Custom String("현상금 사냥꾼"), Custom String("무법자")), Local Player.Job)',
    'Custom String("현상금 사냥꾼"), Custom String("무법자"), Custom String("파발꾼"), Custom String("목동")), Local Player.Job)')
sub('Custom String("보안관"), Custom String("갱단 두목")), Local Player.Job)',
    'Custom String("보안관"), Custom String("갱단 두목"), Custom String("역마차장"), Custom String("목장주")), Local Player.Job)')

# ══ BuildWorld: 표지판·패널 ═══════════════════════════════════════
SIGNS = (
  T*2 + 'Create In-World Text(All Players(All Teams), Custom String("역마차 정거장"), Add(%s, Vector(0, 2.6, 0)), 1.7, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);' % L11 + NLC
+ T*2 + 'Create In-World Text(And(Distance Between(Local Player, %s) < 13, Local Player.TutOn == 0) ? Local Player : False, Custom String("{0}{1}", Custom String("화물을 받아 찍힌 곳까지 달려라 — 도착하면 자동 정산' % L11 + NL + '보수는 거리만큼 · 화물을 든 채 털리면 빼앗긴다' + NL + '"), Custom String("[{0}] 행동 선택      [{1}] 실행", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)))), Add(%s, Vector(0, 1.5, 0)), 0.95, Do Not Clip, Visible To Position and String, Color(White), Default Visibility);' % L11 + NLC
+ T*2 + 'Create In-World Text(All Players(All Teams), Custom String("목장"), Add(%s, Vector(0, 2.6, 0)), 1.7, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);' % L12 + NLC
+ T*2 + 'Create In-World Text(And(Distance Between(Local Player, %s) < 13, Local Player.TutOn == 0) ? Local Player : False, Custom String("{0}{1}", Custom String("벌판의 소를 몸으로 밀어 우리 안까지 몰아넣어라' % L12 + NL + '소는 네가 다가간 반대쪽으로 도망친다 · 90초 제한' + NL + '"), Custom String("[{0}] 행동 선택      [{1}] 실행", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)))), Add(%s, Vector(0, 1.5, 0)), 0.95, Do Not Clip, Visible To Position and String, Color(White), Default Visibility);' % L12 + NLC)
anchor = '\t\tCreate Dummy Bot(Hero(Jetpack Cat), Team 2, 0,'
i = s.index(anchor)
s = s[:i] + SIGNS + s[i:]

# ══ 광기둥 2개 추가 (낮/밤 규칙) ══════════════════════════════════
sub('\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 14));\n',
    '\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 14));\n'
    '\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 15));\n'
    '\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 16));\n', 2)
DAYADD = (T*2 + 'Create Effect(All Players(All Teams), Light Shaft, Color(White), %s, 1.2, Visible To Position Radius and Color);' % L11 + NLC
        + T*2 + 'Modify Global Variable(SignIds, Append To Array, Last Created Entity());' + NLC
        + T*2 + 'Create Effect(All Players(All Teams), Light Shaft, Color(White), %s, 1.2, Visible To Position Radius and Color);' % L12 + NLC
        + T*2 + 'Modify Global Variable(SignIds, Append To Array, Last Created Entity());' + NLC)
k = s.index('Add(Value In Array(Global Variable(LocPos), 7), Vector(0, 55, 0)), 30, Visible To Position Radius and Color);')
k = s.index('Modify Global Variable(SignIds, Append To Array, Last Created Entity());', k) + len('Modify Global Variable(SignIds, Append To Array, Last Created Entity());') + 1
s = s[:k] + DAYADD + s[k:]

# ══ F 핸들러: zone 11 / 12 ════════════════════════════════════════
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
          + L5 + 'Big Message(All Players(All Teams), Custom String("{0} — %s가 되었다!", Event Player));' % advname + NLC
          + L5 + 'Small Message(Event Player, Custom String("%s"));' % perkmsg + NLC
          + L5 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(%s), Position Of(Event Player), 4);' % color + NLC
          + L5 + 'Play Effect(Event Player, Buff Explosion Sound, Color(%s), Position Of(Event Player), 200);' % color + NLC
          + L4 + 'End;' + NLC)

def hirejob(j, name):
    L4, L5 = T*4, T*5
    return (L4 + 'If(Event Player.Job == %d);' % j + NLC
          + L5 + 'Small Message(Event Player, Custom String("이미 %s이다"));' % name + NLC
          + L5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
          + L4 + 'Else;' + NLC
          + L5 + 'Set Player Variable(Event Player, Job, %d);' % j + NLC
          + L5 + 'Set Player Variable(Event Player, Adv, 0);' + NLC
          + L5 + 'Big Message(Event Player, Custom String("전직 완료 — %s"));' % name + NLC
          + L5 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Position Of(Event Player), 2.5);' + NLC
          + L5 + 'Play Effect(Event Player, Buff Explosion Sound, Color(Sky Blue), Position Of(Event Player), 160);' + NLC
          + L4 + 'End;' + NLC)

ZONE_NAMES = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), Custom String("모텔"), '
              'Custom String("정비소 고물상"), Custom String("술집"), Custom String("협곡 개활지"), Custom String("보안관 초소"), '
              'Custom String("무법자 은신처"), Custom String("안내소"), Custom String("대장간"))')

Z11 = ('\t\tElse If(Event Player.Zone == 11);' + NLC
 + T*3 + 'If(Event Player.MenuIdx == 0);' + NLC
 + hirejob(5, '파발꾼')
 + T*3 + 'Else If(Event Player.MenuIdx == 1);' + NLC
 + T*4 + 'If(Event Player.Job != 5);' + NLC
 + T*5 + 'Small Message(Event Player, Custom String("파발꾼만 수주할 수 있다"));' + NLC
 + T*5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
 + T*4 + 'Else If(Event Player.HasParcel == 1);' + NLC
 + T*5 + 'Small Message(Event Player, Custom String("이미 화물을 들고 있다 — 목적지: {0}", Value In Array(%s, Event Player.DelDest)));' % ZONE_NAMES + NLC
 + T*4 + 'Else;' + NLC
 + T*5 + 'Set Player Variable(Event Player, DelDest, Random Integer(0, 10));' + NLC
 + T*5 + 'Set Player Variable(Event Player, HasParcel, 1);' + NLC
 + T*5 + 'Destroy Icon(Event Player.DelIcon);' + NLC
 + T*5 + 'Create Icon(Event Player, Add(Value In Array(Global Variable(LocPos), Event Player.DelDest), Vector(0, 3, 0)), Arrow: Down, Visible To and Position, Color(Yellow), True);' + NLC
 + T*5 + 'Set Player Variable(Event Player, DelIcon, Last Created Entity());' + NLC
 + T*5 + 'Big Message(Event Player, Custom String("화물 접수 — {0}까지 달려라!", Value In Array(%s, Event Player.DelDest)));' % ZONE_NAMES + NLC
 + T*5 + 'Small Message(Event Player, Custom String("노란 화살표를 따라가라. 도착하면 자동 정산된다"));' + NLC
 + T*5 + 'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);' + NLC
 + T*4 + 'End;' + NLC
 + T*3 + 'Else;' + NLC
 + promo(5, '파발꾼만 승급할 수 있다', '이미 역마차장이다', '역마차장', '배달비 +30% · 배달마다 피로 5 회복', 'Yellow')
 + T*3 + 'End;' + NLC)

Z12 = ('\t\tElse If(Event Player.Zone == 12);' + NLC
 + T*3 + 'If(Event Player.MenuIdx == 0);' + NLC
 + hirejob(6, '목동')
 + T*3 + 'Else If(Event Player.MenuIdx == 1);' + NLC
 + T*4 + 'If(Event Player.Job != 6);' + NLC
 + T*5 + 'Small Message(Event Player, Custom String("목동만 소를 몰 수 있다"));' + NLC
 + T*5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
 + T*4 + 'Else If(Event Player.CowOn == 1);' + NLC
 + T*5 + 'Small Message(Event Player, Custom String("이미 소를 몰고 있다 — 우리로 데려와라"));' + NLC
 + T*4 + 'Else;' + NLC
 + T*5 + 'Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(%s, Vector(Multiply(Random Real(12, 22), Random Integer(0, 1) == 1 ? 1 : -1), 0, Multiply(Random Real(12, 22), Random Integer(0, 1) == 1 ? 1 : -1)))));' % L12 + NLC
 + T*5 + 'Set Player Variable(Event Player, CowOn, 1);' + NLC
 + T*5 + 'Set Player Variable(Event Player, CowEnd, Add(Total Time Elapsed(), 90));' + NLC
 + T*5 + 'Destroy Effect(Event Player.CowFx);' + NLC
 + T*5 + 'Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, Visible To Position Radius and Color);' + NLC
 + T*5 + 'Set Player Variable(Event Player, CowFx, Last Created Entity());' + NLC
 + T*5 + 'Big Message(Event Player, Custom String("소가 벌판에 있다 — 몸으로 밀어 우리로!"));' + NLC
 + T*5 + 'Play Effect(Event Player, Buff Impact Sound, Color(White), Position Of(Event Player), 60);' + NLC
 + T*4 + 'End;' + NLC
 + T*3 + 'Else;' + NLC
 + promo(6, '목동만 승급할 수 있다', '이미 목장주다', '목장주', '몰이 보수 +40% · 소가 더 성큼 밀린다', 'Lime Green')
 + T*3 + 'End;' + NLC)

KEY = 'Custom String("돈이 부족합니다 ($25000 필요)")'
i = s.index(KEY)
j = s.index('\t\t\tEnd;\n\t\tEnd;', i)
j += len('\t\t\tEnd;\n')
s = s[:j] + Z11 + Z12 + s[j:]

# ══ 배달 도착 규칙 ════════════════════════════════════════════════
DELIVER = ('rule("[파발 01] 배달 도착 — 자동 정산")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Event Player.HasParcel == 1;' + NLC
 + T*2 + 'Is Alive(Event Player) == True;' + NLC
 + T*2 + 'Event Player.Zone == Event Player.DelDest;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Distance Between(%s, Value In Array(Global Variable(LocPos), Event Player.DelDest)), 1.5), To Nearest));' % L11 + NLC
 + T*2 + 'Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, Add(1, Multiply(0.05, Min(10, Round To Integer(Divide(Value In Array(Event Player.JobXP, 5), 250), Down))))), To Nearest));' + NLC
 + T*2 + 'If(And(Event Player.Job == 5, Event Player.Adv == 1));' + NLC
 + T*3 + 'Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, 1.3), To Nearest));' + NLC
 + T*3 + 'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 5)));' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);' + NLC
 + T*2 + 'Modify Player Variable(Event Player, Earned, Add, Event Player.RunPay);' + NLC
 + T*2 + 'Set Player Variable At Index(Event Player, JobXP, 5, Add(Value In Array(Event Player.JobXP, 5), 25));' + NLC
 + T*2 + 'Set Player Variable(Event Player, HasParcel, 0);' + NLC
 + T*2 + 'Destroy Icon(Event Player.DelIcon);' + NLC
 + T*2 + 'Big Message(Event Player, Custom String("배달 완료!   +$ {0}", Event Player.RunPay));' + NLC
 + T*2 + 'Play Effect(Event Player, Good Explosion, Color(Yellow), Position Of(Event Player), 2);' + NLC
 + T*2 + 'Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 130);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)

# ══ 소몰이 규칙 ═══════════════════════════════════════════════════
HERD = ('rule("[목동 01] 소몰이")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.Init == 1;' + NLC
 + T*2 + 'Event Player.CowOn == 1;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'If(Or(Not(Is Alive(Event Player)), Total Time Elapsed() > Event Player.CowEnd));' + NLC
 + T*3 + 'Set Player Variable(Event Player, CowOn, 0);' + NLC
 + T*3 + 'Destroy Effect(Event Player.CowFx);' + NLC
 + T*3 + 'Small Message(Event Player, Custom String("소를 잃어버렸다..."));' + NLC
 + T*3 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 60);' + NLC
 + T*3 + 'Abort;' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'If(Distance Between(Event Player.CowPos, %s) < 5);' % L12 + NLC
 + T*3 + 'Set Player Variable(Event Player, CowOn, 0);' + NLC
 + T*3 + 'Destroy Effect(Event Player.CowFx);' + NLC
 + T*3 + 'Set Player Variable(Event Player, RunPay, Add(55, Multiply(3, Min(10, Round To Integer(Divide(Value In Array(Event Player.JobXP, 6), 250), Down)))));' + NLC
 + T*3 + 'If(And(Event Player.Job == 6, Event Player.Adv == 1));' + NLC
 + T*4 + 'Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, 1.4), To Nearest));' + NLC
 + T*3 + 'End;' + NLC
 + T*3 + 'Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);' + NLC
 + T*3 + 'Modify Player Variable(Event Player, Earned, Add, Event Player.RunPay);' + NLC
 + T*3 + 'Set Player Variable At Index(Event Player, JobXP, 6, Add(Value In Array(Event Player.JobXP, 6), 25));' + NLC
 + T*3 + 'Big Message(Event Player, Custom String("우리에 몰아넣었다!   +$ {0}", Event Player.RunPay));' + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Good Explosion, Color(Lime Green), %s, 2.5);' % L12 + NLC
 + T*3 + 'Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 130);' + NLC
 + T*3 + 'Abort;' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'If(Distance Between(Position Of(Event Player), Event Player.CowPos) < 4);' + NLC
 + T*3 + 'Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Event Player.CowPos, Multiply(Vector(X Component Of(Direction Towards(Position Of(Event Player), Event Player.CowPos)), 0, Z Component Of(Direction Towards(Position Of(Event Player), Event Player.CowPos))), Add(1.8, Multiply(0.8, Event Player.Adv))))));' + NLC
 + T*3 + 'Destroy Effect(Event Player.CowFx);' + NLC
 + T*3 + 'Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, Visible To Position Radius and Color);' + NLC
 + T*3 + 'Set Player Variable(Event Player, CowFx, Last Created Entity());' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Wait(0.25, Ignore Condition);' + NLC
 + T*2 + 'Loop If(Event Player.CowOn == 1);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[범죄 01] 황야에서 강도 / 체포 (F)")', DELIVER + HERD + 'rule("[범죄 01] 황야에서 강도 / 체포 (F)")')

# ══ 화물 강탈·사망 연동 ═══════════════════════════════════════════
PSTEAL = (T*4 + 'If(Player Variable(Event Player.Target, HasParcel) == 1);' + NLC
        + T*5 + 'Set Player Variable(Event Player.Target, HasParcel, 0);' + NLC
        + T*5 + 'Destroy Icon(Player Variable(Event Player.Target, DelIcon));' + NLC
        + T*5 + 'Modify Player Variable(Event Player, Money, Add, 60);' + NLC
        + T*5 + 'Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 화물을 가로챘다! (+$60)", Event Player, Event Player.Target));' + NLC
        + T*4 + 'End;' + NLC)
sub('\t\t\t\tSet Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), Subtract(45, Multiply(15, And(Event Player.Job == 4, Event Player.Adv == 1)))));\n',
    '\t\t\t\tSet Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), Subtract(45, Multiply(15, And(Event Player.Job == 4, Event Player.Adv == 1)))));\n' + PSTEAL)
sub('\t\tSet Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));\n',
    '\t\tIf(Event Player.HasParcel == 1);\n'
    '\t\t\tSet Player Variable(Event Player, HasParcel, 0);\n'
    '\t\t\tDestroy Icon(Event Player.DelIcon);\n'
    '\t\t\tSmall Message(Event Player, Custom String("화물을 잃어버렸다"));\n'
    '\t\tEnd;\n'
    '\t\tIf(Event Player.CowOn == 1);\n'
    '\t\t\tSet Player Variable(Event Player, CowOn, 0);\n'
    '\t\t\tDestroy Effect(Event Player.CowFx);\n'
    '\t\tEnd;\n'
    '\t\tSet Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));\n')

# ══ 식당 안내판에 새 직업 언급 ════════════════════════════════════
sub('전직  광부 · 사냥꾼 · 현상금 사냥꾼' + NL,
    '전직  광부 · 사냥꾼 · 현상금 사냥꾼' + NL + '파발꾼은 역마차 정거장에서, 목동은 목장에서 뽑는다' + NL)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('파발꾼 + 목동 + 장소 2곳 + 시스템 편입 완료')
