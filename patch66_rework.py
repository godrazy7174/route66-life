# -*- coding: utf-8 -*-
"""[1] 소몰이 완화: 밀림 반경 4->4.5m, 보폭 1.8->2.2(+0.9 승급),
    미는 방향에 우리 쪽 40% 보정(자석 우리), 완료 판정 5->6m, 제한 90->120초.

[2] 전직 전면 이동: 식당 폐지 -> 각 일터 1번 게시판에서.
    광산/개활지/초소/정거장/목장에 '전직' 슬롯 추가, 은신처는 기존 유지.
    식당 메뉴는 식사 하나만 남는다.

[3] 식당 재정의: 식사 $12 = 허기 +60 · 갈증 +60 · 체력 60 (한 끼가 답).
    육포 허기 +55 -> +20 (회복 40->15), 물 갈증 +55 -> +20 (회복 25->10).
    시온 자동 취식도 동일 너프.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)
L12CENTER = 'Value In Array(Global Variable(LocPos), 12)'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

def span(src, start):
    d, j = 0, start
    while True:
        c = src[j]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return j + 1
        j += 1

# ══ [1] 소몰이 완화 ═══════════════════════════════════════════════
sub('If(Distance Between(Position Of(Event Player), Event Player.CowPos) < 4);',
    'If(Distance Between(Position Of(Event Player), Event Player.CowPos) < 4.5);')
AWAY = 'Direction Towards(Position Of(Event Player), Event Player.CowPos)'
TOPEN = 'Direction Towards(Event Player.CowPos, %s)' % L12CENTER
BLEND = 'Add(Multiply(%s, 0.6), Multiply(%s, 0.4))' % (AWAY, TOPEN)
FLAT = 'Normalize(Vector(X Component Of(%s), 0, Z Component Of(%s)))' % (BLEND, BLEND)
sub('Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Event Player.CowPos, Multiply(Vector(X Component Of(Direction Towards(Position Of(Event Player), Event Player.CowPos)), 0, Z Component Of(Direction Towards(Position Of(Event Player), Event Player.CowPos))), Add(1.8, Multiply(0.8, Event Player.Adv))))));',
    'Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Event Player.CowPos, Multiply(%s, Add(2.2, Multiply(0.9, Event Player.Adv))))));' % FLAT)
sub('If(Distance Between(Event Player.CowPos, %s) < 5);' % L12CENTER,
    'If(Distance Between(Event Player.CowPos, %s) < 6);' % L12CENTER)
sub('Set Player Variable(Event Player, CowEnd, Add(Total Time Elapsed(), 90));',
    'Set Player Variable(Event Player, CowEnd, Add(Total Time Elapsed(), 120));')
sub('소는 네가 다가간 반대쪽으로 도망친다 · 90초 제한', '소는 네가 다가간 반대쪽으로 밀린다 · 120초 제한')

# ══ [3] 육포·물 너프 ══════════════════════════════════════════════
sub('\t\t\tSet Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 55)));\n\t\t\tHeal(Event Player, Null, 40);',
    '\t\t\tSet Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 20)));\n\t\t\tHeal(Event Player, Null, 15);')
sub('\t\t\tSet Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 55)));\n\t\t\tHeal(Event Player, Null, 25);',
    '\t\t\tSet Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 20)));\n\t\t\tHeal(Event Player, Null, 10);')
sub('\t\tSet Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 55)));\n\t\tHeal(Event Player, Null, 40);',
    '\t\tSet Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 20)));\n\t\tHeal(Event Player, Null, 15);')

# ══ [2]+[3] 식당 = 식사 전용 ══════════════════════════════════════
BUY12 = 'Round To Integer(Multiply(12, Subtract(1, Multiply(Event Player.Rep, 0.002))), To Nearest)'
OWNER0 = 'Value In Array(Global Variable(BldOwner), 0)'
LEVY0 = (T*4 + 'If(And(Entity Exists(%s), %s != Event Player));' % (OWNER0, OWNER0) + NLC
       + T*5 + 'Set Player Variable(%s, Rent, Max(1, Round To Integer(Multiply(Event Player.Amt, 0.1), To Nearest)));' % OWNER0 + NLC
       + T*5 + 'Modify Player Variable(%s, Money, Add, Player Variable(%s, Rent));' % (OWNER0, OWNER0) + NLC
       + T*5 + 'Small Message(%s, Custom String("임대 수입 +$ {0}", Player Variable(%s, Rent)));' % (OWNER0, OWNER0) + NLC
       + T*4 + 'End;' + NLC)
ZONE0 = ('\t\tIf(Event Player.Zone == 0);' + NLC
 + T*3 + 'Set Player Variable(Event Player, Amt, %s);' % BUY12 + NLC
 + T*3 + 'If(Event Player.Money >= Event Player.Amt);' + NLC
 + T*4 + 'Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);' + NLC
 + LEVY0
 + T*4 + 'Set Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 60)));' + NLC
 + T*4 + 'Set Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 60)));' + NLC
 + T*4 + 'Heal(Event Player, Null, 60);' + NLC
 + T*4 + 'Small Message(Event Player, Custom String("따뜻한 식사 — 허기 {0} · 갈증 {1}", Round To Integer(Event Player.Hunger, Down), Round To Integer(Event Player.Thirst, Down)));' + NLC
 + T*4 + 'Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);' + NLC
 + T*3 + 'Else;' + NLC
 + T*4 + 'Small Message(Event Player, Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt));' + NLC
 + T*4 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
 + T*3 + 'End;' + NLC)
z0 = s.index('\t\tIf(Event Player.Zone == 0);')
z1 = s.index('\t\tElse If(Event Player.Zone == 1);')
s = s[:z0] + ZONE0 + s[z1:]

# ══ [2] 일터 전직 슬롯 ════════════════════════════════════════════
def hirejob(j, name, already):
    L4, L5 = T*4, T*5
    return (L4 + 'If(Event Player.Job == %d);' % j + NLC
          + L5 + 'Small Message(Event Player, Custom String("%s"));' % already + NLC
          + L5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + NLC
          + L4 + 'Else;' + NLC
          + L5 + 'Set Player Variable(Event Player, Job, %d);' % j + NLC
          + L5 + 'Set Player Variable(Event Player, Adv, 0);' + NLC
          + L5 + 'Big Message(Event Player, Custom String("전직 완료 — %s"));' % name + NLC
          + L5 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Position Of(Event Player), 2.5);' + NLC
          + L5 + 'Play Effect(Event Player, Buff Explosion Sound, Color(Sky Blue), Position Of(Event Player), 160);' + NLC
          + L4 + 'End;' + NLC)

# 광산: 0 전직 / 1 채굴 / 2 탐사 / 3 승급
sub('\t\t\tIf(Event Player.MenuIdx == 0);\n\t\t\t\tCall Subroutine(DoMine);\n',
    '\t\t\tIf(Event Player.MenuIdx == 0);\n' + hirejob(1, '광부', '이미 광부다')
  + '\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tCall Subroutine(DoMine);\n')
sub('\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tSet Player Variable(Event Player, Amt, And(Event Player.Job == 1, Event Player.Adv == 1) ? 0 : 30);',
    '\t\t\tElse If(Event Player.MenuIdx == 2);\n\t\t\t\tSet Player Variable(Event Player, Amt, And(Event Player.Job == 1, Event Player.Adv == 1) ? 0 : 30);')

# 개활지: 0 전직 / 1 추적 / 2 승급
sub('\t\t\tIf(Event Player.MenuIdx == 0);\n\t\t\t\tCall Subroutine(DoHunt);\n\t\t\tElse;\n',
    '\t\t\tIf(Event Player.MenuIdx == 0);\n' + hirejob(2, '사냥꾼', '이미 사냥꾼이다')
  + '\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tCall Subroutine(DoHunt);\n\t\t\tElse;\n')

# 초소: 0 전직 / 1 벌금 / 2 게시판 / 3 승급
sub('\t\t\tIf(Event Player.MenuIdx == 0);\n\t\t\t\tIf(Event Player.Bounty <= 0);',
    '\t\t\tIf(Event Player.MenuIdx == 0);\n' + hirejob(3, '현상금 사냥꾼', '이미 현상금 사냥꾼이다')
  + '\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tIf(Event Player.Bounty <= 0);')
sub('\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tSmall Message(Event Player, Custom String("현상금 게시판 —',
    '\t\t\tElse If(Event Player.MenuIdx == 2);\n\t\t\t\tSmall Message(Event Player, Custom String("현상금 게시판 —')

# 정거장: 0 전직 / 1 수주 / 2 승급
sub('\t\t\tIf(Event Player.MenuIdx == 0);\n\t\t\t\tIf(Event Player.Job != 5);',
    '\t\t\tIf(Event Player.MenuIdx == 0);\n' + hirejob(5, '파발꾼', '이미 파발꾼이다')
  + '\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tIf(Event Player.Job != 5);')

# 목장: 0 전직 / 1 소몰기 / 2 승급
sub('\t\t\tIf(Event Player.MenuIdx == 0);\n\t\t\t\tIf(Event Player.Job != 6);',
    '\t\t\tIf(Event Player.MenuIdx == 0);\n' + hirejob(6, '목동', '이미 목동이다')
  + '\t\t\tElse If(Event Player.MenuIdx == 1);\n\t\t\t\tIf(Event Player.Job != 6);')

# ══ 라벨 격자 재생성 ══════════════════════════════════════════════
CS = lambda t: 'Custom String("%s")' % t
PICK = ('Local Player.Pick >= 4 ? Custom String("곡괭이 — 최고 등급") : '
        'Custom String("곡괭이 강화 $ {0}", Value In Array(Array(500, 1200, 2500, 5000), Local Player.Pick))')
TABLE = [
    ['행동 없음 — 마을로 이동하세요'],
    ['식사 $12 — 허기·갈증 회복'],
    ['전직: 광부', '채굴하기', '정밀 탐사 $30', '승급: 광산주 — Lv.4'],
    ['육포 구매 $15', '물통 구매 $10', '육포 5개 묶음 $65', '원석·가죽 전량 판매 — 시세 90%'],
    ['숙박 $60 — 피로 회복', '내 방 마련 $7000'],
    ['원석 전량 판매', '가죽 전량 판매', '오늘의 시세'],
    ['위스키 $25 — 피로 회복', '카드 도박 $50', '소문 듣기', '불꽃놀이 $3,000'],
    ['전직: 사냥꾼', '흔적 추적 — 야수 몰아내기', '승급: 맹수 사냥꾼 — Lv.4'],
    ['전직: 현상금 사냥꾼', '벌금 납부 $100 — 현상금 말소', '현상금 게시판', '승급: 보안관 — Lv.4'],
    ['무법자 합류', '장물 거래', '습격 계획 (무법자 전용)', '승급: 갱단 두목 — Lv.4'],
    ['튜토리얼 보기'],
    [PICK, '가죽 배낭 $1800', '말 $3500', '황금 동상 $25,000'],
    ['전직: 파발꾼', '배달 수주', '승급: 역마차장 — Lv.4'],
    ['전직: 목동', '소 몰기 시작', '승급: 목장주 — Lv.4'],
]
cells = []
for row in TABLE:
    padded = row + ['-'] * (6 - len(row))
    for c in padded:
        cells.append(c if c.startswith('Local Player.Pick') else CS(c))
NEWARR = 'Array(' + ', '.join(cells) + ')'
KEY = 'Array(Custom String("행동 없음 — 마을로 이동하세요")'
i1 = s.index(KEY)
e1 = span(s, i1 + 5)
i2 = s.index(KEY, e1)
e2 = span(s, i2 + 5)
s = s[:i2] + NEWARR + s[e2:]
s = s[:i1] + NEWARR + s[e1:]

sub('Array(1, 6, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4, 2, 2)', 'Array(1, 1, 4, 4, 2, 3, 4, 3, 4, 4, 1, 4, 3, 3)', 4)

# ══ 안내 문구 정리 ════════════════════════════════════════════════
sub('전직  광부 · 사냥꾼 · 현상금 사냥꾼' + NL + '파발꾼은 역마차 정거장에서, 목동은 목장에서 뽑는다' + NL
  + '일할수록 레벨이 오르고 그 직업의 수입이 늘어난다' + NL + 'Lv.4가 되면 자기 일터에서 승급할 수 있다' + NL + '식사 $12' + NL,
    '따뜻한 식사 $12 — 허기와 갈증을 한 번에 채운다' + NL
  + '직업은 각자의 일터 게시판에서 구한다' + NL
  + '일할수록 레벨이 오르고, Lv.4면 그 일터에서 승급한다' + NL)
s = s.replace('전직은 식당에서', '전직은 여기 1번 게시판에서')
sub('Custom String("허기와 갈증은 쉬지 않고 줄어든다. 여기서 육포와 물통을 사서' + NL + '[E]로 먹고 [Q]로 마신다. 0이 되면 피를 흘린다.")',
    'Custom String("허기와 갈증은 쉬지 않고 줄어든다. 육포는 [E], 물은 [Q] — 하지만 요기일 뿐이다.' + NL + '제대로 채우려면 식당에서 한 끼를 먹어라. 0이 되면 피를 흘린다.")')
sub('Custom String("광부 · 사냥꾼 · 현상금 사냥꾼 · 파발꾼 · 목동, 그리고 무법자.' + NL + '여기 게시판에서 언제든 바꾼다 — 무법자만 은신처에서 합류한다.")',
    'Custom String("광부 · 사냥꾼 · 현상금 사냥꾼 · 파발꾼 · 목동 · 무법자 — 일곱 갈래 인생.' + NL + '직업은 각자의 일터 게시판에서 구한다. 가서 문을 두드려라.")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1] 소몰이 완화 / [2] 전직 일터 이관 / [3] 식당 한 끼 · 육포/물 너프')
