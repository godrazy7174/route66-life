# -*- coding: utf-8 -*-
"""범죄 대형 콘텐츠 1/3 — 장물 자루(공용) + 은행 금고 털기.

  장물 자루: 강탈물은 즉시 현금이 아니라 자루 — 은신처 도착 시 정산,
             질주 불가, 죽으면 전량 소실
  은행 털기: 밤 + 재건 3단계 이상 + 안내소에서 [V] (대상 없을 때)
    1막 다이얼 — R 돌리고 F 시도, 크다/작다 힌트로 핀 3개 (조용한 단계)
    2막 경보 — 해정 순간 전서버 경보 + 위치 노출 + 120초 제한
    3막 굴착 — V 연타, 금고벽 내구 30 (곡괭이 반영)
    보상 자루 $600~1,000 · 악명 +25 · 현상금 +$400 · 은행 2일 잠금
    실패(이탈·사망·시간초과·새벽) 시 빈손, 경보 울렸으면 1일 잠금
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

def insert_into(rule_header, section, insertion):
    global s
    assert s.count(rule_header) == 1, rule_header
    i = s.index(rule_header)
    key = section + N + T + '{' + N
    j = s.index(key, i) + len(key)
    s = s[:j] + insertion + s[j:]

# ── 1. 변수 ────────────────────────────────────────────────────────
sub(T*2 + '97: WantedTier' + N + '}',
    T*2 + '97: WantedTier' + N + T*2 + '98: Sack' + N + T*2 + '99: DialOn' + N
    + T*2 + '100: DialTgt' + N + T*2 + '101: DialPin' + N + T*2 + '102: DialCur' + N
    + T*2 + '103: DrillOn' + N + T*2 + '104: HeistEnd' + N + '}')
sub(T*2 + '39: RebuildFxN' + N,
    T*2 + '39: RebuildFxN' + N + T*2 + '40: BankLockDay' + N + T*2 + '41: AlarmIco' + N)
sub(T*2 + 'Set Global Variable(RebuildFxN, 0);' + N,
    T*2 + 'Set Global Variable(RebuildFxN, 0);' + N
    + block(2, 'Set Global Variable(BankLockDay, 0);', 'Set Global Variable(AlarmIco, 0);'))

# ── 2. 장물 자루 — 질주 금지·사망 소실·은신처 정산 ─────────────────
insert_into('rule("[조작 04] 달리기 (Shift)")', 'conditions',
    T*2 + 'Event Player.Sack == 0;' + N)
sub(T*2 + 'Set Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));' + N,
    block(2, 'If(Event Player.Sack > 0);')
    + block(3, 'Set Player Variable(Event Player, Loot, Event Player.Sack);',
               'Set Player Variable(Event Player, Sack, 0);',
               'Small Message(Event Player, Custom String("장물 자루를 흘렸다 — $ {0} 소실", Event Player.Loot));')
    + block(2, 'End;')
    + T*2 + 'Set Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));' + N)

def mkrule(name, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N + ''.join(T*2 + c + N for c in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + acts + T + '}' + N + '}' + N + N)

SACK_RULE = mkrule('[장물 01] 자루 정산 — 은신처',
    ['Event Player.Init == 1;', 'Event Player.Sack > 0;', 'Event Player.Zone == 8;', 'Is Alive(Event Player) == True;'],
    block(2, 'Set Player Variable(Event Player, Loot, Event Player.Sack);',
             'Set Player Variable(Event Player, Sack, 0);',
             'Modify Player Variable(Event Player, Money, Add, Event Player.Loot);',
             'Big Message(Event Player, Custom String("장물을 부렸다 — +$ {0}", Event Player.Loot));',
             'Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 140);'))

# ── 3. 은행 털기 시작 — [범죄 01]의 '대상 없음' 분기 확장 ──────────
OLD_NOTGT = (block(2, 'If(Not(Entity Exists(Event Player.Target)));')
    + block(3, 'Small Message(Event Player, Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Melee))));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
               'Abort;')
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
    + block(3, 'Else;')
    + block(4, 'Small Message(Event Player, Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Melee))));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(3, 'End;')
    + block(3, 'Abort;')
    + block(2, 'End;'))
sub(OLD_NOTGT, NEW_NOTGT)

# ── 4. 은행 규칙 4종 ───────────────────────────────────────────────
BANK_RULES = (
  mkrule('[은행 01] 다이얼 돌리기 (R)',
    ['Event Player.DialOn == 1;', 'Is Button Held(Event Player, Button(Reload)) == True;'],
    block(2, 'Set Player Variable(Event Player, DialCur, Modulo(Add(Event Player.DialCur, 1), 10));',
             'Play Effect(Event Player, Debuff Impact Sound, Color(White), Position Of(Event Player), 35);'))
+ mkrule('[은행 02] 다이얼 시도 (F)',
    ['Event Player.DialOn == 1;', 'Is Button Held(Event Player, Button(Interact)) == True;'],
    block(2, 'If(Event Player.DialCur == Event Player.DialTgt);')
    + block(3, 'Modify Player Variable(Event Player, DialPin, Add, 1);',
               'Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 70);')
    + block(3, 'If(Event Player.DialPin > 3);')
    + block(4, 'Set Player Variable(Event Player, DialOn, 0);',
               'Set Player Variable(Event Player, DrillOn, 1);',
               'Set Player Variable(Event Player, WallHP, 30);',
               'Set Player Variable(Event Player, HeistEnd, Add(Total Time Elapsed(), 120));',
               'Destroy HUD Text(Event Player.KeyHud);',
               'Create HUD Text(Event Player, Custom String("금고 굴착   내구 {0}", Event Player.WallHP), Custom String("남은 시간 {0}초", Max(0, Round To Integer(Subtract(Event Player.HeistEnd, Total Time Elapsed()), Down))), Custom String("[V] 연타 — 곡괭이가 좋을수록 빠르다"), Left, 5, Color(Red), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);',
               'Set Player Variable(Event Player, KeyHud, Last Text ID());',
               'Destroy Icon(Global Variable(AlarmIco));',
               'Create Icon(All Players(All Teams), Add(Value In Array(Global Variable(LocPos), 9), Vector(0, 4, 0)), Warning, Visible To and Position, Color(Red), True);',
               'Set Global Variable(AlarmIco, Last Created Entity());',
               'Big Message(All Players(All Teams), Custom String("은행 경보가 울린다!! — 안내소로!"));',
               'Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Value In Array(Global Variable(LocPos), 9), 250);')
    + block(3, 'Else;')
    + block(4, 'Set Player Variable(Event Player, DialTgt, Random Integer(0, 9));',
               'Small Message(Event Player, Custom String("철컥 — 핀이 물렸다 ({0} / 3)", Subtract(Event Player.DialPin, 1)));')
    + block(3, 'End;')
    + block(2, 'Else;')
    + block(3, 'Small Message(Event Player, Event Player.DialTgt > Event Player.DialCur ? Custom String("헛돎 — 더 크다") : Custom String("헛돎 — 더 작다"));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Gray), Position Of(Event Player), 45);')
    + block(2, 'End;')
    + block(2, 'Wait Until(Not(Is Button Held(Event Player, Button(Interact))), 3);'))
+ mkrule('[은행 03] 금고 굴착 (V 연타)',
    ['Event Player.DrillOn == 1;', 'Is Alive(Event Player) == True;', 'Is Button Held(Event Player, Button(Melee)) == True;'],
    block(2, 'Modify Player Variable(Event Player, WallHP, Subtract, Add(1, Event Player.Pick));',
             'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 1);',
             'Play Effect(Event Player, Debuff Impact Sound, Color(Gray), Position Of(Event Player), 70);')
    + block(2, 'If(Event Player.WallHP <= 0);')
    + block(3, 'Set Player Variable(Event Player, DrillOn, 0);',
               'Set Player Variable(Event Player, Busy, 0);',
               'Destroy HUD Text(Event Player.KeyHud);',
               'Destroy Icon(Global Variable(AlarmIco));',
               'Set Global Variable(BankLockDay, Add(Global Variable(Day), 2));',
               'Set Player Variable(Event Player, Loot, Random Integer(600, 1000));',
               'Modify Player Variable(Event Player, Sack, Add, Event Player.Loot);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 25)));',
               'Modify Player Variable(Event Player, Bounty, Add, 400);',
               'Big Message(All Players(All Teams), Custom String("{0}이(가) 은행 금고를 뚫었다!! (+$ {1})", Event Player, Event Player.Loot));',
               'Small Message(Event Player, Custom String("장물 자루를 졌다 — 은신처에 가야 현금이 된다. 죽으면 잃고, 질주도 못 한다"));',
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 5);',
               'Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Orange), Position Of(Event Player), 200);')
    + block(2, 'End;')
    + block(2, 'Wait(0.25, Ignore Condition);')
    + block(2, 'Loop If(And(Event Player.DrillOn == 1, Is Button Held(Event Player, Button(Melee))));'))
+ mkrule('[은행 04] 작업 중단',
    ['Add(Event Player.DialOn, Event Player.DrillOn) > 0;',
     'Or(Or(Event Player.Zone != 9, Is Alive(Event Player) == False), Or(And(Event Player.DrillOn == 1, Total Time Elapsed() > Event Player.HeistEnd), Or(Global Variable(IsNight) == 0, Is Button Held(Event Player, Button(Crouch)) == True))) == True;'],
    block(2, 'If(Event Player.DrillOn == 1);')
    + block(3, 'Set Global Variable(BankLockDay, Add(Global Variable(Day), 1));',
               'Destroy Icon(Global Variable(AlarmIco));',
               'Small Message(All Players(All Teams), Custom String("은행 경보가 멎었다 — 도둑은 빈손으로 사라졌다"));')
    + block(2, 'End;')
    + block(2, 'Set Player Variable(Event Player, DialOn, 0);',
               'Set Player Variable(Event Player, DrillOn, 0);',
               'Set Player Variable(Event Player, Busy, 0);',
               'Destroy HUD Text(Event Player.KeyHud);',
               'Big Message(Event Player, Custom String("금고가 잠겼다 — 빈손으로 물러난다"));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 70);')))

sub('rule("[감옥 01] 만기 출소")', SACK_RULE + BANK_RULES + 'rule("[감옥 01] 만기 출소")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('장물 자루 + 은행 털기 적용')
