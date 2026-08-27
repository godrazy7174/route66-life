# -*- coding: utf-8 -*-
"""식당 분점 2곳 (zone 13 = 2호점, zone 14 = 3호점).

    기본 위치: 2호점 (-70, 6.5, 5) — 초소·정거장·목장 서쪽 생활권
              3호점 (-22, 3.5, -33) — 정비소·대장간 남쪽 생활권
    (둘 다 설계자 모드로 재배치 가능 — 순환 15곳으로 확장)

    기능은 본점과 동일한 식사 $12. 임대 징수는 프랜차이즈:
    본점(식당) 소유주가 분점 매출의 10%도 걷는다.
    분점 자체는 매매 대상이 아니다.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)
L13 = 'Value In Array(Global Variable(LocPos), 13)'
L14 = 'Value In Array(Global Variable(LocPos), 14)'

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

# ══ 좌표·반경·구역 감지 ═══════════════════════════════════════════
sub('\t\tModify Global Variable(LocPos, Append To Array, Vector(-92.09, 6.5, -30));\n',
    '\t\tModify Global Variable(LocPos, Append To Array, Vector(-92.09, 6.5, -30));\n'
    '\t\tModify Global Variable(LocPos, Append To Array, Vector(-70, 6.5, 5));\n'
    '\t\tModify Global Variable(LocPos, Append To Array, Vector(-22, 3.5, -33));\n')
sub('Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6, 6, 7));',
    'Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6, 6, 7, 5, 5));')
sub('For Player Variable(Event Player, Idx, 0, 13, 1);', 'For Player Variable(Event Player, Idx, 0, 15, 1);')
sub('\t\tSet Global Variable At Index(LocPos, 12, Nearest Walkable Position(Value In Array(Global Variable(LocPos), 12)));\n',
    '\t\tSet Global Variable At Index(LocPos, 12, Nearest Walkable Position(Value In Array(Global Variable(LocPos), 12)));\n'
    '\t\tSet Global Variable At Index(LocPos, 13, Nearest Walkable Position(%s));\n' % L13
  + '\t\tSet Global Variable At Index(LocPos, 14, Nearest Walkable Position(%s));\n' % L14)

# ══ 구역 이름·메뉴 수·라벨 ════════════════════════════════════════
sub('Custom String("역마차 정거장"), Custom String("목장")), Add(Local Player.Zone, 1))',
    'Custom String("역마차 정거장"), Custom String("목장"), Custom String("식당 2호점"), Custom String("식당 3호점")), Add(Local Player.Zone, 1))')
sub('Array(1, 1, 4, 4, 2, 3, 4, 3, 4, 4, 1, 4, 3, 3)', 'Array(1, 1, 4, 4, 2, 3, 4, 3, 4, 4, 1, 4, 3, 3, 1, 1)', 4)
TAILROW = (', ' + ', '.join(['Custom String("식사 $12 — 허기·갈증 회복")'] + ['Custom String("-")'] * 5) * 2)
sub('Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("-"), Custom String("-"), Custom String("-"))',
    'Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("-"), Custom String("-"), Custom String("-")' + TAILROW + ')', 2)

# ══ 식사 핸들러: 세 지점 공용 ═════════════════════════════════════
sub('\t\tIf(Event Player.Zone == 0);\n',
    '\t\tIf(Or(Or(Event Player.Zone == 0, Event Player.Zone == 13), Event Player.Zone == 14));\n')

# ══ BuildWorld: 표지판·패널 ═══════════════════════════════════════
def diner_sign(L, name):
    return (T*2 + 'Create In-World Text(All Players(All Teams), Custom String("%s"), Add(%s, Vector(0, 2.6, 0)), 1.7, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);' % (name, L) + NLC
          + T*2 + 'Create In-World Text(And(Distance Between(Local Player, %s) < 13, Local Player.TutOn == 0) ? Local Player : False, Custom String("{0}{1}", Custom String("따뜻한 식사 $12 — 허기와 갈증을 한 번에 채운다' % L + NL + '본점 주인이 자릿세를 걷는다' + NL + '"), Custom String("[{0}] 실행", Input Binding String(Button(Interact)))), Add(%s, Vector(0, 1.5, 0)), 0.95, Do Not Clip, Visible To Position and String, Color(White), Default Visibility);' % L + NLC)
anchor = '\t\tCreate Dummy Bot(Hero(Jetpack Cat), Team 2, 0,'
i = s.index(anchor)
s = s[:i] + diner_sign(L13, '식당 2호점') + diner_sign(L14, '식당 3호점') + s[i:]

# ══ 광기둥 (낮/밤) ════════════════════════════════════════════════
sub('\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 16));\n',
    '\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 16));\n'
    '\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 17));\n'
    '\t\tDestroy Effect(Value In Array(Global Variable(SignIds), 18));\n', 2)
DAYADD = (T*2 + 'Create Effect(All Players(All Teams), Light Shaft, Color(White), %s, 1.2, Visible To Position Radius and Color);' % L13 + NLC
        + T*2 + 'Modify Global Variable(SignIds, Append To Array, Last Created Entity());' + NLC
        + T*2 + 'Create Effect(All Players(All Teams), Light Shaft, Color(White), %s, 1.2, Visible To Position Radius and Color);' % L14 + NLC
        + T*2 + 'Modify Global Variable(SignIds, Append To Array, Last Created Entity());' + NLC)
k = s.index('Create Effect(All Players(All Teams), Light Shaft, Color(White), Value In Array(Global Variable(LocPos), 12), 1.2, Visible To Position Radius and Color);')
k = s.index('Modify Global Variable(SignIds, Append To Array, Last Created Entity());', k) + len('Modify Global Variable(SignIds, Append To Array, Last Created Entity());') + 1
s = s[:k] + DAYADD + s[k:]

# ══ 설계자 모드 15곳 ══════════════════════════════════════════════
ARCH_OLD = 'Custom String("안내소"), Custom String("대장간"), Custom String("역마차 정거장"), Custom String("목장"))'
ARCH_NEW = 'Custom String("안내소"), Custom String("대장간"), Custom String("역마차 정거장"), Custom String("목장"), Custom String("식당 2호점"), Custom String("식당 3호점"))'
n = s.count(ARCH_OLD)
assert n == 2, n
s = s.replace(ARCH_OLD, ARCH_NEW)
sub('Set Global Variable(ArchIdx, Modulo(Add(Global Variable(ArchIdx), 1), 13));', 'Set Global Variable(ArchIdx, Modulo(Add(Global Variable(ArchIdx), 1), 15));', 2)
ROWS = ''
for idx, name, sort in ((13, '13 식당 2호점', 23), (14, '14 식당 3호점', 24)):
    ROWS += (T*3 + 'Create HUD Text(Host Player(), Null, Custom String("{0}   {1}", Custom String("%s"), '
             'Custom String("X {0}   Y {1}   Z {2}", X Component Of(Value In Array(Global Variable(LocPos), %d)), '
             'Y Component Of(Value In Array(Global Variable(LocPos), %d)), Z Component Of(Value In Array(Global Variable(LocPos), %d)))), '
             'Null, Left, %d, Color(White), Color(Aqua), Color(White), Visible To Sort Order String and Color, Default Visibility);' % (name, idx, idx, idx, sort) + NLC
           + T*3 + 'Modify Global Variable(ArchHud, Append To Array, Last Text ID());' + NLC)
K12 = 'Custom String("12 목장")'
i = s.index(K12)
j = s.index('Modify Global Variable(ArchHud, Append To Array, Last Text ID());', i) + len('Modify Global Variable(ArchHud, Append To Array, Last Text ID());') + 1
s = s[:j] + ROWS + s[j:]
sub('Custom String("설계자 모드 ON — 13곳 좌표가 왼쪽에 표시됩니다")', 'Custom String("설계자 모드 ON — 15곳 좌표가 왼쪽에 표시됩니다")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('식당 2호점·3호점 추가 (프랜차이즈 징수 · 설계자 15곳)')
