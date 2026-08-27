# -*- coding: utf-8 -*-
"""합법 대형 콘텐츠 — 금괴 호송 계약.

  역마차 정거장에서 금괴를 받아 무작위 인계지까지 걸어서 운반한다.
  운반 중 질주가 막히고 범죄자에게 위치가 주기적으로 노출되며, 사망·강탈 시 계약이 끝난다.
  인계지에서 3초간 넘기면 거리 비례 보수와 명성 +8을 받고 60초 재사용 대기한다.
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

def mkrule(name, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N + ''.join(T*2 + c + N for c in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + acts + T + '}' + N + '}' + N + N)

EFF_RED = 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);'

# ── 1. 플레이어 변수 ────────────────────────────────────────────────
sub(T*2 + '115: SmuggleFlash' + N + '}',
    T*2 + '115: SmuggleFlash' + N + T*2 + '116: Escort' + N
    + T*2 + '117: EscortPos' + N + T*2 + '118: EscortIco' + N
    + T*2 + '119: EscortPay' + N + T*2 + '120: EscortCd' + N
    + T*2 + '121: EscortFlash' + N + T*2 + '122: EscortFx' + N + '}', 1)

# ── 2. 역마차 정거장 메뉴 2 -> 3 ───────────────────────────────────
sub('Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 2, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 3, 2, 1, 1)', 3)
sub('Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("-")',
    'Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("금괴 호송 계약")', 1)

# ── 3. 역마차 정거장 금괴 호송 수주 ────────────────────────────────
sub(T*3 + 'Else;' + N + T*4 + 'If(Event Player.Job != 5);',
    T*3 + 'Else If(Event Player.MenuIdx == 1);' + N + T*4 + 'If(Event Player.Job != 5);', 1)

ESCORT_MENU = (block(3, 'Else;')
    + block(4, 'If(Event Player.Escort == 1);')
    + block(5, 'Small Message(Event Player, Custom String("이미 금괴를 호송 중이다 — 노란 표식으로 가라"));', EFF_RED)
    + block(4, 'Else If(Event Player.Bounty > 0);')
    + block(5, 'Small Message(Event Player, Custom String("현상금 붙은 자에게 금괴를 맡길 수는 없다"));', EFF_RED)
    + block(4, 'Else If(Total Time Elapsed() < Event Player.EscortCd);')
    + block(5, 'Small Message(Event Player, Custom String("다음 금괴 마차가 아직이다 — {0}초 뒤에 다시", Round To Integer(Subtract(Event Player.EscortCd, Total Time Elapsed()), Up)));', EFF_RED)
    + block(4, 'Else If(Event Player.Energy < 4);')
    + block(5, 'Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Set Player Variable(Event Player, EscortPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-15, 15), 0, Random Real(-15, 15)))));',
               'Set Player Variable(Event Player, EscortPay, Round To Integer(Add(40, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2.5)), To Nearest));',
               'Set Player Variable(Event Player, Escort, 1);',
               'Destroy Icon(Event Player.EscortIco);',
               'Create Icon(Event Player, Add(Event Player.EscortPos, Vector(0, 3, 0)), Diamond, Visible To and Position, Color(Yellow), True);',
               'Set Player Variable(Event Player, EscortIco, Last Created Entity());',
               'Destroy Effect(Event Player.EscortFx);',
               'Create Effect(All Players(All Teams), Sphere, Color(Yellow), Add(Position Of(Event Player), Vector(0, 2.4, 0)), 0.3, Visible To Position Radius and Color);',
               'Set Player Variable(Event Player, EscortFx, Last Created Entity());',
               'Big Message(Event Player, Custom String("금괴 상자를 실었다 — 노란 표식까지 (보수 $ {0})", Event Player.EscortPay));',
               'Small Message(Event Player, Custom String("질주할 수 없다 · 죽거나 털리면 끝 — 악명 높은 자들이 냄새를 맡는다"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);')
    + block(4, 'End;'))

ZONE11_END = block(4, 'End;') + block(3, 'End;') + block(2, 'Else If(Event Player.Zone == 12);')
sub(ZONE11_END,
    block(4, 'End;') + ESCORT_MENU + block(3, 'End;') + block(2, 'Else If(Event Player.Zone == 12);'), 1)

# ── 4. 호송 중 질주 금지 ───────────────────────────────────────────
sub(T*2 + 'Event Player.Sack == 0;' + N,
    T*2 + 'Event Player.Sack == 0;' + N + T*2 + 'Event Player.Escort == 0;' + N, 1)

# ── 5. 범죄자 대상 위치 노출 + 금괴 인계 ──────────────────────────
ESCORT_RULES = (
  mkrule('[호송 01] 금괴의 소문',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;',
     'Event Player.Escort == 1;', 'Is Alive(Event Player) == True;'],
    block(2, 'Create Icon(Filtered Array(All Players(All Teams), Or(Player Variable(Current Array Element, Noto) >= 30, Player Variable(Current Array Element, Bounty) > 0)), Add(Position Of(Event Player), Vector(0, 2.6, 0)), Circle, Visible To and Position, Color(Yellow), True);',
             'Set Player Variable(Event Player, EscortFlash, Last Created Entity());',
             'Wait(3, Ignore Condition);',
             'Destroy Icon(Event Player.EscortFlash);',
             'Wait(17, Ignore Condition);',
             'Loop If(And(Event Player.Escort == 1, Is Alive(Event Player)));'))
  + mkrule('[호송 02] 금괴 인계 (F 3초)',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;',
     'Event Player.Busy == 0;', 'Global Variable(ArchOn) == 0;',
     'Event Player.Escort == 1;', 'Is Alive(Event Player) == True;',
     'Distance Between(Position Of(Event Player), Event Player.EscortPos) < 4;',
     'Is Button Held(Event Player, Button(Crouch)) == False;',
     'Is Button Held(Event Player, Button(Interact)) == True;'],
    block(2, 'Set Player Variable(Event Player, Busy, 1);',
             'Set Player Variable(Event Player, WorkProg, 0);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);',
             'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("금괴 인계 중..."), Top, 0, Color(Yellow), Color(White), Visible To Values and Color, Default Visibility);',
             'Set Player Variable(Event Player, WorkBar, Last Text ID());',
             'Chase Player Variable Over Time(Event Player, WorkProg, 100, 3, Destination and Duration);',
             'Wait Until(Or(Or(Distance Between(Position Of(Event Player), Event Player.EscortPos) > 6, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3.5);',
             'Stop Chasing Player Variable(Event Player, WorkProg);',
             'Destroy Progress Bar HUD Text(Event Player.WorkBar);')
    + block(2, 'If(Or(Or(Distance Between(Position Of(Event Player), Event Player.EscortPos) > 6, Not(Is Alive(Event Player))), Event Player.WorkProg < 99));')
    + block(3, 'Small Message(Event Player, Custom String("손을 뗐다"));')
    + block(2, 'Else;')
    + block(3, 'Modify Player Variable(Event Player, Money, Add, Event Player.EscortPay);',
               'Modify Player Variable(Event Player, Earned, Add, Event Player.EscortPay);',
               'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 8)));',
               'Set Player Variable(Event Player, Escort, 0);',
               'Destroy Icon(Event Player.EscortIco);',
               'Destroy Effect(Event Player.EscortFx);',
               'Set Player Variable(Event Player, EscortCd, Add(Total Time Elapsed(), 60));',
               'Small Message(Event Player, Custom String("금괴를 지켜냈다 — +$ {0} (명성 +8)", Event Player.EscortPay));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 120);')
    + block(2, 'End;',
               'Set Player Variable(Event Player, Busy, 0);')))

sub('rule("[감옥 01] 만기 출소")', ESCORT_RULES + 'rule("[감옥 01] 만기 출소")', 1)

# ── 6. 사망 시 금괴 소실 ───────────────────────────────────────────
DEATH_SMUGGLE = (block(2, 'If(Event Player.Contraband == 1);')
    + block(3, 'Set Player Variable(Event Player, Contraband, 0);',
               'Destroy Icon(Event Player.SmuggleIco);',
               'Small Message(Event Player, Custom String("밀수 화물을 잃었다 — 접선은 없던 일이 됐다"));')
    + block(2, 'End;'))
DEATH_ESCORT = (block(2, 'If(Event Player.Escort == 1);')
    + block(3, 'Set Player Variable(Event Player, Escort, 0);',
               'Destroy Icon(Event Player.EscortIco);',
               'Destroy Effect(Event Player.EscortFx);',
               'Small Message(Event Player, Custom String("금괴를 잃었다 — 호송은 실패로 끝났다"));')
    + block(2, 'End;'))
sub(DEATH_SMUGGLE, DEATH_SMUGGLE + DEATH_ESCORT, 1)

# ── 7. 강탈 성공 시 금괴 가로채기 ─────────────────────────────────
ROB_SMUGGLE = (block(4, 'If(Player Variable(Event Player.Target, Contraband) == 1);')
    + block(5, 'Set Player Variable(Event Player.Target, Contraband, 0);',
               'Destroy Icon(Player Variable(Event Player.Target, SmuggleIco));',
               'Modify Player Variable(Event Player, Money, Add, 80);',
               'Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 밀수 화물을 가로챘다! (+$80)", Event Player, Event Player.Target));')
    + block(4, 'End;'))
ROB_ESCORT = (block(4, 'If(Player Variable(Event Player.Target, Escort) == 1);')
    + block(5, 'Set Player Variable(Event Player.Target, Escort, 0);',
               'Destroy Icon(Player Variable(Event Player.Target, EscortIco));',
               'Destroy Effect(Player Variable(Event Player.Target, EscortFx));',
               'Modify Player Variable(Event Player, Money, Add, 120);',
               'Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 금괴 호송을 털었다! (+$120)", Event Player, Event Player.Target));',
               'Small Message(Event Player.Target, Custom String("금괴를 빼앗겼다 — 호송 실패"));')
    + block(4, 'End;'))
sub(ROB_SMUGGLE, ROB_SMUGGLE + ROB_ESCORT, 1)

# ── 8. 역마차 정거장 안내판 ───────────────────────────────────────
SIGN_OLD = '배달 완료 — 허기 2 · 갈증 3 · 피로 4' + B
SIGN_NEW = SIGN_OLD + '금괴 호송 — 수배 없는 자만 · 질주 불가 · 악명 높은 자들이 노린다' + B
sub(SIGN_OLD, SIGN_NEW, 1)

io.open(P, 'w', encoding='utf-8', newline=N).write(s)
print('금괴 호송 계약 적용')
