# -*- coding: utf-8 -*-
"""서버 대형 콘텐츠 — 전설의 야수 대사냥.

  사흘 주기의 대사냥 날 아침에 나타난 흔적을 세 번 조사하면 대야수가 깨어난다.
  참가자는 피해 기여를 기록하고 토벌 시 가죽·돈·명성을 나눠 받으며, 일등 공신은 추가 보상을 받는다.
  밤까지 끝내지 못한 흔적과 대야수는 물러나고 다음 대사냥 날을 기다린다.
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

def block(depth, *lines):
    return ''.join(T*depth + ln + N for ln in lines)

def mkrule(name, event_lines, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N
      + ''.join(T*2 + line + N for line in event_lines) + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N
      + ''.join(T*2 + cond + N for cond in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + acts + T + '}' + N + '}' + N + N)

# ── 1. 전역·플레이어 변수 ──────────────────────────────────────────
sub(T*2 + '48: TrainIco' + N,
    T*2 + '48: TrainIco' + N + T*2 + '49: HuntPhase' + N
    + T*2 + '50: HuntBeast' + N + T*2 + '51: HuntTrackPos' + N
    + T*2 + '52: HuntTrackIco' + N + T*2 + '53: HuntTrackFx' + N
    + T*2 + '54: HuntDay' + N + T*2 + '55: HuntArr' + N
    + T*2 + '56: HuntIdx' + N, 1)
sub(T*2 + '122: EscortFx' + N,
    T*2 + '122: EscortFx' + N + T*2 + '123: HuntDmg' + N, 1)

# ── 2. 대형·전설 야수 체력 채우기 ─────────────────────────────────
sub(T*4 + 'Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 50, False);' + N,
    T*4 + 'Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 50, False);' + N
    + T*4 + 'Heal(Value In Array(Event Player.Target, Event Player.Idx), Null, 9999);' + N, 1)
sub(T*4 + 'Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 2.4, False);' + N,
    T*4 + 'Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 2.4, False);' + N
    + T*4 + 'Heal(Value In Array(Event Player.Target, Event Player.Idx), Null, 9999);' + N, 1)

# ── 3. 일반 사냥 대상에서 대야수 제외 ─────────────────────────────
sub('Set Player Variable(Event Player, Target, Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))));',
    'Set Player Variable(Event Player, Target, Filtered Array(All Players(Team 2), And(And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element)), Current Array Element != Global Variable(HuntBeast))));', 1)

# ── 4. 전설의 야수 대사냥 ─────────────────────────────────────────
HUNT_RULES = (
  mkrule('[대사냥 01] 대야수의 흔적',
    ['Ongoing - Global;'],
    ['Global Variable(Ready) == 1;',
     'Modulo(Global Variable(Day), 3) == 1;',
     'Global Variable(Day) >= 4;',
     'Global Variable(Day) > Global Variable(HuntDay);',
     'Global Variable(IsNight) == 0;'],
    block(2, 'Set Global Variable(HuntDay, Global Variable(Day));',
             'Set Global Variable(HuntPhase, 1);',
             'Set Global Variable(HuntTrackPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-18, 18), 0, Random Real(-18, 18)))));',
             'Destroy Icon(Global Variable(HuntTrackIco));',
             'Destroy Effect(Global Variable(HuntTrackFx));',
             'Create Effect(All Players(All Teams), Light Shaft, Color(Orange), Global Variable(HuntTrackPos), 1.5, Visible To Position Radius and Color);',
             'Set Global Variable(HuntTrackFx, Last Created Entity());',
             'Create Icon(All Players(All Teams), Add(Global Variable(HuntTrackPos), Vector(0, 3, 0)), Circle, Visible To and Position, Color(Orange), True);',
             'Set Global Variable(HuntTrackIco, Last Created Entity());',
             'Big Message(All Players(All Teams), Custom String("대사냥의 날 — 대야수의 흔적이 나타났다! 주황 표식을 조사하라"));',
             'Play Effect(All Players(All Teams), Buff Impact Sound, Color(Orange), Global Variable(HuntTrackPos), 200);'))
  + mkrule('[대사냥 02] 흔적 조사 (F)',
    ['Ongoing - Each Player;', 'All;', 'All;'],
    ['Is Dummy Bot(Event Player) == False;',
     'Event Player.Init == 1;',
     'Event Player.Busy == 0;',
     'Global Variable(ArchOn) == 0;',
     'Global Variable(HuntPhase) >= 1;',
     'Global Variable(HuntPhase) <= 3;',
     'Is Alive(Event Player) == True;',
     'Distance Between(Position Of(Event Player), Global Variable(HuntTrackPos)) < 5;',
     'Is Button Held(Event Player, Button(Crouch)) == False;',
     'Is Button Held(Event Player, Button(Interact)) == True;'],
    block(2, 'Destroy Icon(Global Variable(HuntTrackIco));',
             'Destroy Effect(Global Variable(HuntTrackFx));',
             'If(Global Variable(HuntPhase) <= 2);')
    + block(3, 'Modify Global Variable(HuntPhase, Add, 1);',
               'Set Global Variable(HuntTrackPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-18, 18), 0, Random Real(-18, 18)))));',
               'Create Effect(All Players(All Teams), Light Shaft, Color(Orange), Global Variable(HuntTrackPos), 1.5, Visible To Position Radius and Color);',
               'Set Global Variable(HuntTrackFx, Last Created Entity());',
               'Create Icon(All Players(All Teams), Add(Global Variable(HuntTrackPos), Vector(0, 3, 0)), Circle, Visible To and Position, Color(Orange), True);',
               'Set Global Variable(HuntTrackIco, Last Created Entity());',
               'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));',
               'Big Message(All Players(All Teams), Custom String("흔적을 찾았다 — 냄새가 짙어진다. 다음 표식으로"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 60);')
    + block(2, 'Else;')
    + block(3, 'Set Global Variable(HuntPhase, 4);',
               'Set Global Variable(HuntBeast, First Of(Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element)))));',
               'Set Player Variable(Global Variable(HuntBeast), RevealEnd, Add(Total Time Elapsed(), 9999));',
               'Set Player Variable(Global Variable(HuntBeast), Giant, 0);',
               'Set Max Health(Global Variable(HuntBeast), 1000);',
               'Remove All Health Pools From Player(Global Variable(HuntBeast));',
               'Add Health Pool To Player(Global Variable(HuntBeast), Health, 8000, True, True);',
               'Heal(Global Variable(HuntBeast), Null, 9999);',
               'Start Scaling Player(Global Variable(HuntBeast), 30, False);',
               'Clear Status(Global Variable(HuntBeast), Phased Out);',
               'Set Invisible(Global Variable(HuntBeast), None);',
               'Teleport(Global Variable(HuntBeast), Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-5, 5), 0, Random Real(-5, 5)))));',
               'Set Player Variable(All Players(All Teams), HuntDmg, 0);',
               'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));',
               'Big Message(All Players(All Teams), Custom String("대야수가 깨어났다!! 협곡 개활지다 — 쓰러뜨린 몫은 기여만큼 나눈다"));',
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Global Variable(HuntBeast)), 20);',
               'Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(Global Variable(HuntBeast)), 300);')
    + block(2, 'End;',
               'Wait(0.3, Ignore Condition);'))
  + mkrule('[대사냥 03] 기여 기록',
    ['Player Dealt Damage;', 'All;', 'All;'],
    ['Global Variable(HuntPhase) == 4;',
     'Victim == Global Variable(HuntBeast);',
     'Is Dummy Bot(Event Player) == False;'],
    block(2, 'Modify Player Variable(Event Player, HuntDmg, Add, Event Damage);'))
  + mkrule('[대사냥 04] 대야수 토벌',
    ['Player Died;', 'Team 2;', 'All;'],
    ['Is Dummy Bot(Victim) == True;',
     'Global Variable(HuntPhase) == 4;',
     'Victim == Global Variable(HuntBeast);'],
    block(2, 'Set Global Variable(HuntPhase, 0);',
             'Set Global Variable(HuntArr, Sorted Array(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, HuntDmg) >= 1), Subtract(0, Player Variable(Current Array Element, HuntDmg))));',
             'For Global Variable(HuntIdx, 0, Count Of(Global Variable(HuntArr)), 1);')
    + block(3, 'Modify Player Variable At Index(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Inv, 3, Add, 15);',
               'Set Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Fame, Min(100, Add(Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Fame), 10)));',
               'Modify Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Money, Add, 200);',
               'Modify Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Earned, Add, 200);',
               'Small Message(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Custom String("대사냥 보상 — 가죽 15장 · $200 · 명성 +10"));')
    + block(2, 'End;',
               'If(Count Of(Global Variable(HuntArr)) >= 1);')
    + block(3, 'Modify Player Variable At Index(First Of(Global Variable(HuntArr)), Inv, 3, Add, 35);',
               'Modify Player Variable(First Of(Global Variable(HuntArr)), Money, Add, 300);',
               'Modify Player Variable(First Of(Global Variable(HuntArr)), Earned, Add, 300);',
               'Big Message(All Players(All Teams), Custom String("{0} — 대야수 토벌의 일등 공신! (가죽 +35 · +$300)", First Of(Global Variable(HuntArr))));')
    + block(2, 'End;',
               'Big Message(All Players(All Teams), Custom String("대야수가 쓰러졌다!! 참가자 모두에게 몫이 돌아간다"));',
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Victim), 20);',
               'Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Red), Position Of(Victim), 300);',
               'Set Player Variable(Victim, RevealEnd, 0);',
               'Set Player Variable(All Players(All Teams), HuntDmg, 0);',
               'Set Global Variable(HuntBeast, Null);'))
  + mkrule('[대사냥 05] 밤이 오면 물러난다',
    ['Ongoing - Global;'],
    ['Global Variable(HuntPhase) >= 1;',
     'Global Variable(IsNight) == 1;'],
    block(2, 'If(Global Variable(HuntPhase) == 4);')
    + block(3, 'Set Player Variable(Global Variable(HuntBeast), RevealEnd, 0);')
    + block(2, 'Else;')
    + block(3, 'Destroy Icon(Global Variable(HuntTrackIco));',
               'Destroy Effect(Global Variable(HuntTrackFx));')
    + block(2, 'End;',
               'Set Global Variable(HuntPhase, 0);',
               'Set Global Variable(HuntBeast, Null);',
               'Set Player Variable(All Players(All Teams), HuntDmg, 0);',
               'Big Message(All Players(All Teams), Custom String("대야수의 기척이 밤 속으로 사라졌다 — 사흘 뒤를 노려라"));')))

sub('rule("[감옥 01] 만기 출소")', HUNT_RULES + 'rule("[감옥 01] 만기 출소")', 1)

io.open(P, 'w', encoding='utf-8', newline=N).write(s)
print('전설의 야수 대사냥 적용')
