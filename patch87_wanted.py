# -*- coding: utf-8 -*-
"""범죄 다듬기 — 수배 등급(전단·추방) + 체포 우위.

  전단   현상금 $300+ : 30초마다 위치 스컬 5초 전서버 노출
  추방   현상금 $800+ : 상업 시설 8곳 거래 거부 (은신처·초소·안내소는 허용)
  생존로 은신처 신메뉴 '뒷골목 은신 $40' (허기·갈증 +45, 피로 +30)
  벌금   $100 고정 -> max($100, 현상금 30%) (명성 70+ 절반)
  처단   회수 50%로 반토막(피해자는 전액 몰수), 명성 +8 -> +4
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

def insert_after_actions(rule_header, insertion):
    global s
    assert s.count(rule_header) == 1, rule_header
    i = s.index(rule_header)
    key = 'actions' + N + T + '{' + N
    j = s.index(key, i) + len(key)
    s = s[:j] + insertion + s[j:]

# ── 1. 변수 ────────────────────────────────────────────────────────
sub(T*2 + '95: PadC' + N + '}',
    T*2 + '95: PadC' + N + T*2 + '96: WantedIco' + N + T*2 + '97: WantedTier' + N + '}')

# ── 2. 추방 게이트 (조작 03a/b/c 액션 서두) ────────────────────────
GATE = (block(2, 'If(And(Event Player.Bounty >= 800, Array Contains(Array(0, 2, 3, 4, 5, 10, 13, 14), Event Player.Zone)));')
      + block(3, 'Small Message(Event Player, Custom String("수배범과는 거래하지 않는다 — 은신처로 가라"));',
                 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
                 'Abort;')
      + block(2, 'End;'))
insert_after_actions('rule("[조작 03a] 행동 실행 — 식당·광산·잡화점·모텔·정비소")', GATE)
insert_after_actions('rule("[조작 03b] 행동 실행 — 술집·개활지·초소·은신처")', GATE)
insert_after_actions('rule("[조작 03c] 행동 실행 — 안내소·대장간·정거장·목장")', GATE)

# ── 3. 수배 규칙 4종 ───────────────────────────────────────────────
def mkrule(name, conds, acts):
    return ('rule("%s")' % name + N + '{' + N
      + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
      + T + 'conditions' + N + T + '{' + N + ''.join(T*2 + c + N for c in conds) + T + '}' + N + N
      + T + 'actions' + N + T + '{' + N + ''.join(T*2 + a + N for a in acts) + T + '}' + N + '}' + N + N)

RULES = (
  mkrule('[수배 01] 전단 노출',
    ['Is Dummy Bot(Event Player) == False;', 'Event Player.Init == 1;',
     'Event Player.Bounty >= 300;', 'Is Alive(Event Player) == True;'],
    ['Create Icon(All Players(All Teams), Add(Position Of(Event Player), Vector(0, 2.6, 0)), Skull, Visible To and Position, Color(Red), True);',
     'Set Player Variable(Event Player, WantedIco, Last Created Entity());',
     'Wait(5, Ignore Condition);',
     'Destroy Icon(Event Player.WantedIco);',
     'Wait(25, Ignore Condition);',
     'Loop If(And(Event Player.Bounty >= 300, Is Alive(Event Player)));'])
+ mkrule('[수배 02] 전단 경고',
    ['Event Player.Init == 1;', 'Event Player.Bounty >= 300;', 'Event Player.WantedTier == 0;'],
    ['Set Player Variable(Event Player, WantedTier, 1);',
     'Big Message(Event Player, Custom String("수배 전단이 나돌기 시작했다 — 위치가 주기적으로 드러난다"));',
     'Small Message(All Players(All Teams), Custom String("{0}의 수배 전단이 마을에 붙었다 — 현상금 $ {1}", Event Player, Event Player.Bounty));',
     'Play Effect(Event Player, Explosion Sound, Color(Red), Position Of(Event Player), 140);'])
+ mkrule('[수배 03] 추방 경고',
    ['Event Player.Init == 1;', 'Event Player.Bounty >= 800;', 'Event Player.WantedTier == 1;'],
    ['Set Player Variable(Event Player, WantedTier, 2);',
     'Big Message(Event Player, Custom String("마을이 너를 추방했다 — 은신처만이 너를 받아준다"));',
     'Small Message(All Players(All Teams), Custom String("{0}이(가) 마을에서 추방됐다 — 상점 거래 불가", Event Player));',
     'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Event Player), 4);'])
+ mkrule('[수배 04] 전단 철회',
    ['Event Player.Init == 1;', 'Event Player.Bounty < 300;', 'Event Player.WantedTier >= 1;'],
    ['Set Player Variable(Event Player, WantedTier, 0);',
     'Small Message(Event Player, Custom String("전단이 거둬졌다 — 다시 마을을 걸을 수 있다"));']))
sub('rule("[감옥 01] 만기 출소")', RULES + 'rule("[감옥 01] 만기 출소")')

# ── 4. 은신처 '뒷골목 은신' 메뉴 ───────────────────────────────────
sub('Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 3, 4, 4, 2, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 4, 4, 4, 2, 2, 1, 1)', 3)
sub('Custom String("장물 거래"), Custom String("습격 계획"), Custom String("승급: 갱단 두목 — Lv.4"), Custom String("-"), Custom String("-"), Custom String("-")',
    'Custom String("장물 거래"), Custom String("습격 계획"), Custom String("뒷골목 은신 $40"), Custom String("승급: 갱단 두목 — Lv.4"), Custom String("-"), Custom String("-")')
sub(T*3 + 'Else If(Event Player.MenuIdx == 1);' + N + T*4 + 'Call Subroutine(DoPlan);' + N,
    T*3 + 'Else If(Event Player.MenuIdx == 1);' + N + T*4 + 'Call Subroutine(DoPlan);' + N
    + block(3, 'Else If(Event Player.MenuIdx == 2);')
    + block(4, 'If(Event Player.Money >= 40);')
    + block(5, 'Modify Player Variable(Event Player, Money, Subtract, 40);',
               'Set Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 45)));',
               'Set Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 45)));',
               'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 30)));',
               'Small Message(Event Player, Custom String("뒷골목에서 몸을 숨기고 숨을 돌렸다 (허기·갈증 +45, 피로 +30)"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Purple), Position Of(Event Player), 60);')
    + block(4, 'Else;')
    + block(5, 'Small Message(Event Player, Custom String("돈이 부족합니다 ($40 필요)"));',
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(4, 'End;'))
sub('습격 계획 — 허기 3 · 갈증 3 · 피로 8' + RN,
    '습격 계획 — 허기 3 · 갈증 3 · 피로 8' + RN + '뒷골목 은신 $40 — 추방자도 여기선 먹고 잔다' + RN)

# ── 5. 벌금 = 현상금 연동 ──────────────────────────────────────────
sub('Set Player Variable(Event Player, Amt, Event Player.Fame >= 70 ? 50 : 100);',
    'Set Player Variable(Event Player, Amt, Max(Event Player.Fame >= 70 ? 50 : 100, Round To Integer(Multiply(Event Player.Bounty, Event Player.Fame >= 70 ? 0.15 : 0.3), To Nearest)));')
sub('Custom String("벌금 납부 $100 — 현상금 말소")',
    'Custom String("벌금 납부 — 현상금의 30% (최소 $100)")')
sub('벌금 $100 (명성 70+는 $50) — 수배 말소, 악명 -40',
    '벌금 = 현상금의 30% · 최소 $100 (명성 70+ 절반) — 수배 말소, 악명 -40')

# ── 6. 처단 반토막 ─────────────────────────────────────────────────
sub('Set Player Variable(Victim, Money, Subtract(Player Variable(Victim, Money), Player Variable(Attacker, KillPay)));' + N,
    'Set Player Variable(Victim, Money, Subtract(Player Variable(Victim, Money), Player Variable(Attacker, KillPay)));' + N
    + T*3 + 'Set Player Variable(Attacker, KillPay, Round To Integer(Multiply(Player Variable(Attacker, KillPay), 0.5), Down));' + N)
sub('Add(Player Variable(Attacker, Fame), 8)', 'Add(Player Variable(Attacker, Fame), 4)')
sub('Big Message(All Players(All Teams), Custom String("{0}이(가) 수배범 {1}을(를) 처단했다 — $ {2}", Attacker, Victim, Player Variable(Attacker, KillPay)));' + N,
    'Big Message(All Players(All Teams), Custom String("{0}이(가) 수배범 {1}을(를) 처단했다 — $ {2}", Attacker, Victim, Player Variable(Attacker, KillPay)));' + N
    + T*3 + 'Small Message(Attacker, Custom String("산 채로 데려왔다면 두 배였다"));' + N)

# ── 7. 튜토리얼 두 줄 ──────────────────────────────────────────────
sub('훔친 물건은 여기서 제값보다 비싸게 넘길 수 있다."',
    '훔친 물건은 여기서 제값보다 비싸게 넘길 수 있다.' + RN
    + '목값 $300이면 전단이 돌고, $800이면 마을이 문을 걸어 잠근다."')
sub('쫓기는 쪽이라면 여기서 벌금을 내고 수배를 지운다."',
    '쫓기는 쪽이라면 여기서 벌금을 내고 수배를 지운다.' + RN
    + '산 채로 잡으면 전액, 쏴 죽이면 절반만 남는다."')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('수배 등급 + 체포 우위 적용 완료')
