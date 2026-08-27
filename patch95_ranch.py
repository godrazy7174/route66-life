# -*- coding: utf-8 -*-
"""합법 대형 콘텐츠 — 내 목장 경영.

  건설  목장 메뉴, $2,000 + 명성 30 필요 (우리 1칸)
  사육  물통 2개 + 육포 1개 -> 게임 1일(720초), 중간에 한 번 돌보면 우리당 3마리
  방치  돌보지 않으면 우리당 야윈 소 1마리
  판매  역마차 정거장 — 마리당 $60 (목장주는 $70), 합법 수입
  증설  우리 2칸 $5,000 -> 최대 6마리/일
  사업은 회차(방) 자산 — 세이브 코드에는 저장하지 않는다
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

EFF_RED = 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);'

# ── 1. 플레이어 변수 ────────────────────────────────────────────────
sub(T*2 + '123: HuntDmg' + N,
    T*2 + '123: HuntDmg' + N + T*2 + '124: Ranch' + N
    + T*2 + '125: RanchPens' + N + T*2 + '126: RanchEnd' + N
    + T*2 + '127: RanchReady' + N + T*2 + '128: RanchCare' + N, 1)

# ── 2. 정거장·목장 메뉴 슬롯과 라벨 ───────────────────────────────
sub('Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 3, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 4, 4, 1, 1)', 3)
sub('Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("금괴 호송 계약"), Custom String("-")',
    'Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("금괴 호송 계약"), Custom String("가축 출하 — 마리당 $60")', 1)
sub('Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("-"), Custom String("-")',
    'Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("내 목장"), Custom String("우리 증설 $5000")', 1)

# ── 3. 역마차 정거장 가축 출하 ────────────────────────────────────
sub(T*3 + 'Else;' + N + T*4 + 'If(Event Player.Escort == 1);',
    T*3 + 'Else If(Event Player.MenuIdx == 2);' + N + T*4 + 'If(Event Player.Escort == 1);', 1)

CATTLE_SHIP = (block(3, 'Else;')
    + block(4, 'If(Event Player.RanchReady <= 0);')
    + block(5, 'Small Message(Event Player, Custom String("넘길 소가 없다 — 목장에서 길러 와라"));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Set Player Variable(Event Player, SellQty, Event Player.RanchReady);',
               'Set Player Variable(Event Player, Amt, Value In Array(Event Player.Adv, 6) == 1 ? 70 : 60);',
               'Set Player Variable(Event Player, SellSum, Multiply(Event Player.SellQty, Event Player.Amt));',
               'Set Player Variable(Event Player, RanchReady, 0);',
               'Modify Player Variable(Event Player, Money, Add, Event Player.SellSum);',
               'Modify Player Variable(Event Player, Earned, Add, Event Player.SellSum);',
               'Small Message(Event Player, Custom String("소 {0}마리를 넘겼다 — +$ {1}", Event Player.SellQty, Event Player.SellSum));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 120);')
    + block(4, 'End;'))

ZONE11_END = block(4, 'End;') + block(3, 'End;') + block(2, 'Else If(Event Player.Zone == 12);')
sub(ZONE11_END,
    block(4, 'End;') + CATTLE_SHIP + block(3, 'End;') + block(2, 'Else If(Event Player.Zone == 12);'), 1)

# ── 4. 내 목장 건설·사육·돌봄·증설 ───────────────────────────────
sub(T*3 + 'Else;' + N + T*4 + 'If(Event Player.Job != 6);',
    T*3 + 'Else If(Event Player.MenuIdx == 1);' + N + T*4 + 'If(Event Player.Job != 6);', 1)

PROMOTION_TAIL = (block(5, 'Small Message(Event Player, Custom String("몰이 보수 +15% · 소가 더 성큼 밀린다"));',
                           'Play Effect(All Players(All Teams), Ring Explosion, Color(Lime Green), Position Of(Event Player), 4);',
                           'Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 200);')
    + block(4, 'End;'))

RANCH_MENU = (block(3, 'Else If(Event Player.MenuIdx == 2);')
    + block(4, 'If(Event Player.Ranch == 0);')
    + block(5, 'If(Event Player.Fame < 30);')
    + block(6, 'Small Message(Event Player, Custom String("목장은 신용이 필요하다 — 명성 30을 쌓아 와라 (현재 {0})", Event Player.Fame));', EFF_RED)
    + block(5, 'Else If(Event Player.Money >= 2000);')
    + block(6, 'Modify Player Variable(Event Player, Money, Subtract, 2000);',
               'Set Player Variable(Event Player, Ranch, 1);',
               'Set Player Variable(Event Player, RanchPens, 1);',
               'Big Message(Event Player, Custom String("내 목장을 차렸다 — 물통 2개와 육포 1개면 소를 들인다"));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 140);')
    + block(5, 'Else;')
    + block(6, 'Small Message(Event Player, Custom String("돈이 부족합니다 ($2000 필요)"));', EFF_RED)
    + block(5, 'End;')
    + block(4, 'Else If(Event Player.RanchReady > 0);')
    + block(5, 'Small Message(Event Player, Custom String("출하 준비 {0}마리 — 역마차 정거장에서 넘겨라", Event Player.RanchReady));')
    + block(4, 'Else If(Event Player.RanchEnd > Total Time Elapsed());')
    + block(5, 'If(Event Player.RanchCare == 0);')
    + block(6, 'Set Player Variable(Event Player, RanchCare, 1);',
               'Small Message(Event Player, Custom String("물과 여물을 챙겨줬다 — 소가 살이 오른다"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);')
    + block(5, 'Else;')
    + block(6, 'Small Message(Event Player, Custom String("소는 잘 크고 있다 — {0}초 뒤 출하", Round To Integer(Subtract(Event Player.RanchEnd, Total Time Elapsed()), Up)));')
    + block(5, 'End;')
    + block(4, 'Else If(And(Value In Array(Event Player.Inv, 1) >= 2, Value In Array(Event Player.Inv, 0) >= 1));')
    + block(5, 'Set Player Variable At Index(Event Player, Inv, 1, Subtract(Value In Array(Event Player.Inv, 1), 2));',
               'Set Player Variable At Index(Event Player, Inv, 0, Subtract(Value In Array(Event Player.Inv, 0), 1));',
               'Set Player Variable(Event Player, RanchEnd, Add(Total Time Elapsed(), 720));',
               'Set Player Variable(Event Player, RanchCare, 0);',
               'Big Message(Event Player, Custom String("소를 들였다 — 하루 뒤 출하. 크는 동안 한 번은 들러서 돌봐라"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);')
    + block(4, 'Else;')
    + block(5, 'Small Message(Event Player, Custom String("물통 2개와 육포 1개가 필요하다 (물 {0} · 육포 {1})", Value In Array(Event Player.Inv, 1), Value In Array(Event Player.Inv, 0)));', EFF_RED)
    + block(4, 'End;')
    + block(3, 'Else If(Event Player.MenuIdx == 3);')
    + block(4, 'If(Event Player.Ranch == 0);')
    + block(5, 'Small Message(Event Player, Custom String("목장부터 차려라"));', EFF_RED)
    + block(4, 'Else If(Event Player.RanchPens >= 2);')
    + block(5, 'Small Message(Event Player, Custom String("이미 최대 규모다 — 한 번에 6마리"));', EFF_RED)
    + block(4, 'Else If(Event Player.Money >= 5000);')
    + block(5, 'Modify Player Variable(Event Player, Money, Subtract, 5000);',
               'Set Player Variable(Event Player, RanchPens, 2);',
               'Big Message(Event Player, Custom String("우리를 늘렸다 — 이제 한 번에 6마리"));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 140);')
    + block(4, 'Else;')
    + block(5, 'Small Message(Event Player, Custom String("돈이 부족합니다 ($5000 필요)"));', EFF_RED)
    + block(4, 'End;'))

sub(PROMOTION_TAIL, PROMOTION_TAIL + RANCH_MENU, 1)

# ── 5. 소 성장 완료 규칙 ─────────────────────────────────────────
RANCH_RULE = ('rule("[목장 02] 소가 다 컸다")' + N + '{' + N
  + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
  + T + 'conditions' + N + T + '{' + N
  + T*2 + 'Event Player.Ranch == 1;' + N
  + T*2 + 'Event Player.RanchEnd > 0;' + N
  + T*2 + 'Total Time Elapsed() >= Event Player.RanchEnd;' + N
  + T + '}' + N + N
  + T + 'actions' + N + T + '{' + N
  + block(2, 'Set Player Variable(Event Player, RanchEnd, 0);',
             'Set Player Variable(Event Player, RanchReady, Multiply(Event Player.RanchCare == 1 ? 3 : 1, Event Player.RanchPens));')
  + block(2, 'If(Event Player.RanchCare == 1);')
  + block(3, 'Big Message(Event Player, Custom String("소가 통통하게 컸다 — {0}마리 출하 준비 완료", Event Player.RanchReady));',
             'Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 80);')
  + block(2, 'Else;')
  + block(3, 'Big Message(Event Player, Custom String("돌보지 않은 우리 — 야윈 소 {0}마리뿐이다", Event Player.RanchReady));',
             'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 80);')
  + block(2, 'End;')
  + T + '}' + N + '}' + N + N)
sub('rule("[감옥 01] 만기 출소")', RANCH_RULE + 'rule("[감옥 01] 만기 출소")', 1)

# ── 6. 목장·정거장 안내판 ─────────────────────────────────────────
sub('몰이 성공 — 허기 3 · 갈증 2.5 · 피로 5' + RN,
    '몰이 성공 — 허기 3 · 갈증 2.5 · 피로 5' + RN
    + '내 목장 $2000 (명성 30) — 물통 2·육포 1이 하루 만에 소가 된다' + RN, 1)
sub('금괴 호송 — 수배 없는 자만 · 질주 불가 · 악명 높은 자들이 노린다' + RN,
    '금괴 호송 — 수배 없는 자만 · 질주 불가 · 악명 높은 자들이 노린다' + RN
    + '가축 출하 — 목장에서 기른 소, 마리당 $60' + RN, 1)

io.open(P, 'w', encoding='utf-8', newline=N).write(s)
print('내 목장 경영 적용')
