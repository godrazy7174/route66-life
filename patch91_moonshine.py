# -*- coding: utf-8 -*-
"""범죄 대형 콘텐츠 3/3 — 밀주 양조장 (지속 운영형 지하 사업).

  건설  은신처 메뉴, $2,000 + 악명 30 필요 (양조통 1)
  생산  물통 2개 투입 -> 게임 1일(720초) 숙성 -> 밀주 3병 (통 2개면 6병)
  판매  술집 '뒷문 거래' — 병당 $60, 단속 25%(갱단 두목 15%):
        걸리면 전량 몰수 + 현상금 +$150 + 악명 +10 + 전서버 망신
        성공 시 악명 +5, 범죄 수입이라 오늘 목표 제외
  증설  양조통 2개 $5,000 -> 6병/일
  사업은 회차(방) 자산 — 부동산과 같은 원칙으로 세이브 코드 미저장
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

# ── 1. 변수 ────────────────────────────────────────────────────────
sub(T*2 + '105: HasPowder' + N + '}',
    T*2 + '105: HasPowder' + N + T*2 + '106: Brew' + N + T*2 + '107: BrewVats' + N
    + T*2 + '108: BrewEnd' + N + T*2 + '109: BrewReady' + N + '}')

# ── 2. 은신처 메뉴 4 -> 6 (양조장·증설) ────────────────────────────
sub('Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 4, 4, 5, 2, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 6, 4, 5, 2, 2, 1, 1)', 3)
sub('Custom String("뒷골목 은신 $40"), Custom String("승급: 갱단 두목 — Lv.4"), Custom String("-"), Custom String("-")',
    'Custom String("뒷골목 은신 $40"), Custom String("밀주 양조장"), Custom String("양조통 증설 $5000"), Custom String("승급: 갱단 두목 — Lv.4")')

BREW_MENU = (block(3, 'Else If(Event Player.MenuIdx == 3);')
    + block(4, 'If(Event Player.Brew == 0);')
    + block(5, 'If(Event Player.Noto < 30);')
    + block(6, 'Small Message(Event Player, Custom String("양조는 아무나 못 한다 — 악명 30을 쌓아 와라 (현재 {0})", Event Player.Noto));', EFF_RED)
    + block(5, 'Else If(Event Player.Money >= 2000);')
    + block(6, 'Modify Player Variable(Event Player, Money, Subtract, 2000);',
               'Set Player Variable(Event Player, Brew, 1);',
               'Set Player Variable(Event Player, BrewVats, 1);',
               'Big Message(Event Player, Custom String("뒷골목에 양조장을 차렸다 — 물통 2개면 밀주를 담근다"));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 140);')
    + block(5, 'Else;')
    + block(6, 'Small Message(Event Player, Custom String("돈이 부족합니다 ($2000 필요)"));', EFF_RED)
    + block(5, 'End;')
    + block(4, 'Else If(Event Player.BrewReady > 0);')
    + block(5, 'Small Message(Event Player, Custom String("밀주 {0}병 보관 중 — 술집 뒷문에 넘겨라", Event Player.BrewReady));')
    + block(4, 'Else If(Event Player.BrewEnd > Total Time Elapsed());')
    + block(5, 'Small Message(Event Player, Custom String("숙성 중... {0}초 뒤에 익는다", Round To Integer(Subtract(Event Player.BrewEnd, Total Time Elapsed()), Up)));')
    + block(4, 'Else If(Value In Array(Event Player.Inv, 1) >= 2);')
    + block(5, 'Set Player Variable At Index(Event Player, Inv, 1, Subtract(Value In Array(Event Player.Inv, 1), 2));',
               'Set Player Variable(Event Player, BrewEnd, Add(Total Time Elapsed(), 720));',
               'Big Message(Event Player, Custom String("밀주를 담갔다 — 하루 뒤에 익는다"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Purple), Position Of(Event Player), 60);')
    + block(4, 'Else;')
    + block(5, 'Small Message(Event Player, Custom String("물통 2개가 필요하다 (보유 {0})", Value In Array(Event Player.Inv, 1)));', EFF_RED)
    + block(4, 'End;')
    + block(3, 'Else If(Event Player.MenuIdx == 4);')
    + block(4, 'If(Event Player.Brew == 0);')
    + block(5, 'Small Message(Event Player, Custom String("양조장부터 차려라"));', EFF_RED)
    + block(4, 'Else If(Event Player.BrewVats >= 2);')
    + block(5, 'Small Message(Event Player, Custom String("이미 최대 규모다 — 한 번에 6병"));', EFF_RED)
    + block(4, 'Else If(Event Player.Money >= 5000);')
    + block(5, 'Modify Player Variable(Event Player, Money, Subtract, 5000);',
               'Set Player Variable(Event Player, BrewVats, 2);',
               'Big Message(Event Player, Custom String("양조통을 늘렸다 — 이제 한 번에 6병"));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 140);')
    + block(4, 'Else;')
    + block(5, 'Small Message(Event Player, Custom String("돈이 부족합니다 ($5000 필요)"));', EFF_RED)
    + block(4, 'End;'))
sub(T*3 + 'Else;' + N + T*4 + 'If(Event Player.Job != 4);',
    BREW_MENU + T*3 + 'Else;' + N + T*4 + 'If(Event Player.Job != 4);')

# ── 3. 숙성 완료 규칙 ──────────────────────────────────────────────
BREW_RULE = ('rule("[양조 01] 밀주 숙성 완료")' + N + '{' + N
  + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Each Player;' + N + T*2 + 'All;' + N + T*2 + 'All;' + N + T + '}' + N + N
  + T + 'conditions' + N + T + '{' + N
  + T*2 + 'Event Player.Brew == 1;' + N
  + T*2 + 'Event Player.BrewEnd > 0;' + N
  + T*2 + 'Total Time Elapsed() >= Event Player.BrewEnd;' + N
  + T + '}' + N + N
  + T + 'actions' + N + T + '{' + N
  + block(2, 'Set Player Variable(Event Player, BrewEnd, 0);',
             'Set Player Variable(Event Player, BrewReady, Multiply(3, Event Player.BrewVats));',
             'Big Message(Event Player, Custom String("밀주가 익었다 — {0}병. 술집 뒷문이 기다린다", Event Player.BrewReady));',
             'Play Effect(Event Player, Buff Impact Sound, Color(Purple), Position Of(Event Player), 80);')
  + T + '}' + N + '}' + N + N)
sub('rule("[감옥 01] 만기 출소")', BREW_RULE + 'rule("[감옥 01] 만기 출소")')

# ── 4. 술집 뒷문 거래 (메뉴 4 -> 5) ────────────────────────────────
sub('Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 6, 4, 5, 2, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 2, 2, 1, 1)', 3)
sub('Custom String("소문 듣기"), Custom String("불꽃놀이 $5,000")',
    'Custom String("소문 듣기"), Custom String("뒷문 거래 — 밀주 납품"), Custom String("불꽃놀이 $5,000")')
BACKDOOR = (block(3, 'Else If(Event Player.MenuIdx == 3);')
    + block(4, 'If(Event Player.BrewReady <= 0);')
    + block(5, 'Small Message(Event Player, Custom String("넘길 밀주가 없다 — 은신처 양조장에서 담가라"));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Set Player Variable(Event Player, Amt, Value In Array(Event Player.Adv, 4) == 1 ? 15 : 25);')
    + block(5, 'If(Random Integer(1, 100) <= Event Player.Amt);')
    + block(6, 'Set Player Variable(Event Player, SellQty, Event Player.BrewReady);',
               'Set Player Variable(Event Player, BrewReady, 0);',
               'Modify Player Variable(Event Player, Bounty, Add, 150);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 10)));',
               'Big Message(All Players(All Teams), Custom String("{0}의 밀주 {1}병이 단속에 걸렸다 — 전량 몰수!", Event Player, Event Player.SellQty));',
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Event Player), 3);',
               'Play Effect(Event Player, Explosion Sound, Color(Red), Position Of(Event Player), 160);')
    + block(5, 'Else;')
    + block(6, 'Set Player Variable(Event Player, SellQty, Event Player.BrewReady);',
               'Set Player Variable(Event Player, SellSum, Multiply(Event Player.BrewReady, 60));',
               'Set Player Variable(Event Player, BrewReady, 0);',
               'Modify Player Variable(Event Player, Money, Add, Event Player.SellSum);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 5)));',
               'Small Message(Event Player, Custom String("뒷문으로 밀주 {0}병을 넘겼다 — +$ {1} (악명 +5)", Event Player.SellQty, Event Player.SellSum));',
               'Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 120);')
    + block(5, 'End;')
    + block(4, 'End;'))
sub(T*3 + 'Else If(Event Player.MenuIdx == 3);' + N + T*4 + 'If(Event Player.Money >= 5000);',
    BACKDOOR + T*3 + 'Else If(Event Player.MenuIdx == 4);' + N + T*4 + 'If(Event Player.Money >= 5000);')

# ── 5. 간판 갱신 ───────────────────────────────────────────────────
sub('뒷골목 은신 $40 — 추방자도 여기선 먹고 잔다' + RN,
    '뒷골목 은신 $40 — 추방자도 여기선 먹고 잔다' + RN
    + '양조장 $2000 (악명 30) — 물통 2개가 하루 만에 밀주 3병' + RN
    + '밤의 큰 건 — 은행(재건 3단계)과 열차는 간 큰 자를 기다린다' + RN)
sub('불꽃놀이 $5000 — 전 서버에 쏘아 올린다' + RN,
    '불꽃놀이 $5000 — 전 서버에 쏘아 올린다' + RN + '뒷문은 아무것도 묻지 않는다' + RN)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('밀주 양조장 적용')
