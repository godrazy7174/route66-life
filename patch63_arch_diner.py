# -*- coding: utf-8 -*-
"""[1] 설계자 모드 확장 — 13곳 전부 지정 가능
    지금까지 순환이 9곳(0~8)까지라 안내소·대장간·역마차 정거장·목장은
    지정할 수 없었다. 순환을 13으로 넓히고 좌표 목록에도 4곳을 추가.

[2] 식당에서 파발꾼·목동 전직 가능
    구역당 메뉴 슬롯이 4개라 식당(전직3+식사)이 꽉 차 있었다.
    라벨 격자를 4칸 -> 6칸으로 넓혀(전 구역 공통) 슬롯을 확보하고,
    식당 메뉴를 [광부/사냥꾼/현상금/파발꾼/목동/식사] 6개로 재구성.
    일터(정거장·목장)에서의 전직도 그대로 유지 — 두 곳 다 된다.
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

# ══ [2a] 라벨 격자 재생성 (4칸 -> 6칸) ════════════════════════════
CS = lambda t: 'Custom String("%s")' % t
PICK = ('Local Player.Pick >= 4 ? Custom String("곡괭이 — 최고 등급") : '
        'Custom String("곡괭이 강화 $ {0}", Value In Array(Array(500, 1200, 2500, 5000), Local Player.Pick))')
TABLE = [
    ['행동 없음 — 마을로 이동하세요'],
    ['전직: 광부', '전직: 사냥꾼', '전직: 현상금 사냥꾼', '전직: 파발꾼', '전직: 목동', '식사 $12 — 허기 회복'],
    ['채굴하기', '정밀 탐사 $30', '승급: 광산주 — Lv.4'],
    ['육포 구매 $15', '물통 구매 $10', '육포 5개 묶음 $65', '원석·가죽 전량 판매 — 시세 90%'],
    ['숙박 $60 — 피로 회복', '내 방 마련 $7000'],
    ['원석 전량 판매', '가죽 전량 판매', '오늘의 시세'],
    ['위스키 $25 — 피로 회복', '카드 도박 $50', '소문 듣기', '불꽃놀이 $3,000'],
    ['흔적 추적 — 야수 몰아내기', '승급: 맹수 사냥꾼 — Lv.4'],
    ['벌금 납부 $100 — 현상금 말소', '현상금 게시판', '승급: 보안관 — Lv.4'],
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
s = s[:i2] + NEWARR + s[e2:]        # 뒤(미리보기)부터 바꿔야 앞 인덱스가 안 밀린다
s = s[:i1] + NEWARR + s[e1:]

sub('Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx)',
    'Add(Multiply(Add(Local Player.Zone, 1), 6), Local Player.MenuIdx)')
sub('Add(Multiply(Add(Local Player.Zone, 1), 4), Modulo(Add(Local Player.MenuIdx, 1)',
    'Add(Multiply(Add(Local Player.Zone, 1), 6), Modulo(Add(Local Player.MenuIdx, 1)')
sub('Array(1, 4, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4, 3, 3)', 'Array(1, 6, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4, 3, 3)', 4)

# ══ [2b] 식당 메뉴 6개로 ══════════════════════════════════════════
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

MEAL_ANCHOR = '\t\t\tElse;\n\t\t\t\tSet Player Variable(Event Player, Amt, Round To Integer(Multiply(12, Subtract(1, Multiply(Event Player.Rep, 0.002))), To Nearest));'
assert s.count(MEAL_ANCHOR) == 1
s = s.replace(MEAL_ANCHOR,
    '\t\t\tElse If(Event Player.MenuIdx == 3);\n' + hirejob(5, '파발꾼')
  + '\t\t\tElse If(Event Player.MenuIdx == 4);\n' + hirejob(6, '목동')
  + MEAL_ANCHOR, 1)

# ══ [1] 설계자 모드 13곳 ══════════════════════════════════════════
ARCH_OLD = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), Custom String("모텔"), '
            'Custom String("정비소 고물상"), Custom String("술집"), Custom String("협곡 개활지"), Custom String("보안관 초소"), '
            'Custom String("무법자 은신처"), Custom String("안내소"))')
ARCH_NEW = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), Custom String("모텔"), '
            'Custom String("정비소 고물상"), Custom String("술집"), Custom String("협곡 개활지"), Custom String("보안관 초소"), '
            'Custom String("무법자 은신처"), Custom String("안내소"), Custom String("대장간"), Custom String("역마차 정거장"), Custom String("목장"))')
n = s.count(ARCH_OLD)
assert n == 2, n
s = s.replace(ARCH_OLD, ARCH_NEW)
sub('Set Global Variable(ArchIdx, Modulo(Add(Global Variable(ArchIdx), 1), 9));', 'Set Global Variable(ArchIdx, Modulo(Add(Global Variable(ArchIdx), 1), 13));', 2)

ROWS = ''
for idx, name, sort in ((9, '9 안내소', 19), (10, '10 대장간', 20), (11, '11 역마차 정거장', 21), (12, '12 목장', 22)):
    ROWS += (T*3 + 'Create HUD Text(Host Player(), Null, Custom String("{0}   {1}", Custom String("%s"), '
             'Custom String("X {0}   Y {1}   Z {2}", X Component Of(Value In Array(Global Variable(LocPos), %d)), '
             'Y Component Of(Value In Array(Global Variable(LocPos), %d)), Z Component Of(Value In Array(Global Variable(LocPos), %d)))), '
             'Null, Left, %d, Color(White), Color(Aqua), Color(White), Visible To Sort Order String and Color, Default Visibility);' % (name, idx, idx, idx, sort) + NLC
           + T*3 + 'Modify Global Variable(ArchHud, Append To Array, Last Text ID());' + NLC)
K8 = 'Custom String("8 무법자 은신처")'
i = s.index(K8)
j = s.index('Modify Global Variable(ArchHud, Append To Array, Last Text ID());', i) + len('Modify Global Variable(ArchHud, Append To Array, Last Text ID());') + 1
s = s[:j] + ROWS + s[j:]
sub('Custom String("설계자 모드 ON — 8곳 좌표가 왼쪽에 표시됩니다")', 'Custom String("설계자 모드 ON — 13곳 좌표가 왼쪽에 표시됩니다")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('설계자 13곳 + 식당 6슬롯(파발꾼·목동 전직) 완료')
