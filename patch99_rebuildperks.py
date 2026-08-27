# -*- coding: utf-8 -*-
"""재건 단계별 언락 — 우물·전신국·은행·오페라 하우스 기능 추가.

플레이어 변수 슬롯은 Brew 소유 플래그를 BrewVats로 통합해 확보하고
같은 106번 슬롯을 Deposit으로 재사용한다. 5단계 환생 기능은 포함하지 않는다.
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
    return ''.join(T * depth + line + N for line in lines)


EFF_RED = 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);'

# ── 1. Brew 소유 플래그 통합, Deposit 슬롯 확보 ───────────────────
sub(T * 2 + '106: Brew' + N, T * 2 + '106: Deposit' + N, 1)
sub('If(Event Player.Brew == 0);', 'If(Event Player.BrewVats == 0);', 2)
sub('Event Player.Brew == 1;', 'Event Player.BrewVats >= 1;', 1)
sub(T * 6 + 'Set Player Variable(Event Player, Brew, 1);' + N, '', 1)

# ── 2. 재건 1단계 — 마을 우물 ─────────────────────────────────────
WELL_BRANCH = (block(2, 'If(And(Event Player.Rebuild >= 1, Event Player.Zone == 9));')
    + block(3, 'Set Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 20)));',
               'Heal(Event Player, Null, 10);',
               'Small Message(Event Player, Custom String("마을 우물의 물 — 물통이 축나지 않았다 (갈증 {0})", Round To Integer(Event Player.Thirst, Down)));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 50);')
    + block(2, 'Else If(Value In Array(Event Player.Inv, 1) >= 1);'))
sub(block(2, 'If(Value In Array(Event Player.Inv, 1) >= 1);'), WELL_BRANCH, 1)

# ── 3. 재건 2단계 — 전신국 사건 예고 ──────────────────────────────
sub(block(2, 'Wait(Random Integer(220, 360), Ignore Condition);'),
    block(2, 'Wait(Random Integer(190, 330), Ignore Condition);',
             'Small Message(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Rebuild) >= 2), Custom String("전신국 타전 — 곧 무슨 일이 벌어진다"));',
             'Play Effect(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Rebuild) >= 2), Buff Impact Sound, Color(Yellow), Vector(0, 0, 0), 9999);',
             'Wait(30, Ignore Condition);'), 1)

# ── 4. 재건 3단계 — 마을 은행 ─────────────────────────────────────
OLD_MENU_COUNTS = 'Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 4, 4, 1, 1)'
NEW_MENU_COUNTS = 'Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 4, 4, 1, 1)'
sub(OLD_MENU_COUNTS, NEW_MENU_COUNTS, 3)
sub('Custom String("마을 재건"), Custom String("-"), Custom String("-")',
    'Custom String("마을 재건"), Custom String("은행 예금 — 전액 맡기기"), Custom String("은행 출금 — 전액 찾기")', 1)

sub(block(3, 'Else;') + block(4, 'If(Event Player.Rebuild >= 5);'),
    block(3, 'Else If(Event Player.MenuIdx == 3);') + block(4, 'If(Event Player.Rebuild >= 5);'), 1)

BANK_BRANCHES = (block(3, 'Else If(Event Player.MenuIdx == 4);')
    + block(4, 'If(Global Variable(RebuildMax) < 3);')
    + block(5, 'Small Message(Event Player, Custom String("은행이 아직 재건되지 않았다 — 재건 3단계부터"));', EFF_RED)
    + block(4, 'Else If(Event Player.Money < 1);')
    + block(5, 'Small Message(Event Player, Custom String("맡길 돈이 없다"));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Modify Player Variable(Event Player, Deposit, Add, Event Player.Money);',
               'Set Player Variable(Event Player, Money, 0);',
               'Small Message(Event Player, Custom String("전액을 맡겼다 — 예금 $ {0} (강탈과 죽음이 닿지 않는다)", Event Player.Deposit));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);')
    + block(4, 'End;')
    + block(3, 'Else;')
    + block(4, 'If(Event Player.Deposit < 1);')
    + block(5, 'Small Message(Event Player, Custom String("예금이 비어 있다"));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Modify Player Variable(Event Player, Money, Add, Event Player.Deposit);',
               'Set Player Variable(Event Player, Deposit, 0);',
               'Small Message(Event Player, Custom String("전액을 찾았다 — 소지금 $ {0}", Event Player.Money));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);')
    + block(4, 'End;'))

ZONE9_END = block(4, 'End;') + block(3, 'End;') + block(2, 'Else If(Event Player.Zone == 10);')
sub(ZONE9_END,
    block(4, 'End;') + BANK_BRANCHES + block(3, 'End;') + block(2, 'Else If(Event Player.Zone == 10);'), 1)

INTEREST = (block(2, 'If(Event Player.Deposit >= 100);')
    + block(3, 'Set Player Variable(Event Player, Amt, Min(200, Round To Integer(Multiply(Event Player.Deposit, 0.01), Down)));',
               'Modify Player Variable(Event Player, Deposit, Add, Event Player.Amt);',
               'Small Message(Event Player, Custom String("은행 이자 +$ {0} (예금 $ {1})", Event Player.Amt, Event Player.Deposit));')
    + block(2, 'End;'))
sub(block(2, 'Set Player Variable(Event Player, DayStart, Event Player.Earned);'),
    INTEREST + block(2, 'Set Player Variable(Event Player, DayStart, Event Player.Earned);'), 1)

sub('Subtract(0, Player Variable(Current Array Element, Money))',
    'Subtract(0, Add(Player Variable(Current Array Element, Money), Player Variable(Current Array Element, Deposit)))', 1)
sub('Custom String("소지금   $ {0}", Local Player.Money)',
    'Custom String("소지금   $ {0}   예금 $ {1}", Local Player.Money, Local Player.Deposit)', 1)
sub('Min(9999, Round To Integer(Divide(Event Player.Money, 100), Down))',
    'Min(9999, Round To Integer(Divide(Add(Event Player.Money, Event Player.Deposit), 100), Down))', 1)

# ── 5. 재건 4단계 — 오페라의 밤 ──────────────────────────────────
OPERA_RULE = ('rule("[재건 02] 오페라의 밤")' + N + '{' + N
    + T + 'event' + N + T + '{' + N
    + block(2, 'Ongoing - Each Player;', 'All;', 'All;')
    + T + '}' + N + N
    + T + 'conditions' + N + T + '{' + N
    + block(2, 'Is Dummy Bot(Event Player) == False;',
             'Event Player.Init == 1;',
             'Event Player.Rebuild >= 4;',
             'Global Variable(IsNight) == 1;',
             'Event Player.Zone == 5;',
             'Is Alive(Event Player) == True;')
    + T + '}' + N + N
    + T + 'actions' + N + T + '{' + N
    + block(2, 'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 15)));',
             'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 1)));',
             'Small Message(Event Player, Custom String("오페라의 밤 — 무대의 노래가 피로를 씻는다 (피로 +15 · 명성 +1)"));',
             'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 80);',
             'Wait Until(Global Variable(IsNight) == 0, 99999);')
    + T + '}' + N + '}' + N + N)
sub('rule("[감옥 01] 만기 출소")', OPERA_RULE + 'rule("[감옥 01] 만기 출소")', 1)

# ── 6. 안내소 표지판 ───────────────────────────────────────────────
sub('마을 재건 — 우물에서 기차역까지 다섯 단계, 총 $1,000,000' + RN,
    '마을 재건 — 우물에서 기차역까지 다섯 단계, 총 $1,000,000' + RN
    + '재건은 기능을 연다 — 우물 물 · 전신국 예고 · 은행 예금 · 오페라의 밤' + RN, 1)

# ── 결과 검증과 단일 쓰기 ─────────────────────────────────────────
EXPECTED = (
    ('106: Deposit', 1),
    ('Event Player.BrewVats == 0', 2),
    ('Event Player.BrewVats >= 1;', 1),
    ('Set Player Variable(Event Player, Brew, 1);', 0),
    ('마을 우물의 물', 1),
    ('전신국 타전', 1),
    ('은행 예금 — 전액 맡기기', 1),
    ('전액을 맡겼다', 1),
    ('은행 이자', 1),
    ('Player Variable(Current Array Element, Deposit)', 1),
    ('예금 $ {1}', 2),
    ('rule("[재건 02] 오페라의 밤")', 1),
    ('재건은 기능을 연다', 1),
    (NEW_MENU_COUNTS, 3),
)
for needle, expected in EXPECTED:
    assert s.count(needle) == expected, (needle, s.count(needle), expected)

io.open(P, 'w', encoding='utf-8', newline=N).write(s)

print('재건 단계별 언락 적용 완료')
print('변경: Brew 슬롯을 Deposit으로 재사용; 1단계 우물, 2단계 전신국, 3단계 은행, 4단계 오페라 기능 추가')
print('검증 카운트:')
for needle, expected in EXPECTED:
    print('  {0} = {1}'.format(needle, expected))
