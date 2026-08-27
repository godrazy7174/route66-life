# -*- coding: utf-8 -*-
"""[1] 소가 안 보이는 문제
    (a) 소 이펙트 재평가가 Position 포함이라 Event Player 컨텍스트가
        날아가면 원점으로 사라진다 -> 어차피 이동마다 재생성하므로 None.
    (b) 목장이 실내다. 산포 12~22m 는 벽 밖 -> 7~12m 로 축소.

[2] 배달 보수: 거리 x1.5 -> 15 + 거리 x2.0 (수주 시 기본 보수 표시)

[3] 전직 창구 일원화: 다른 직업들처럼 파발꾼·목동도 식당에서만.
    정거장·목장의 '전직' 메뉴 제거 (남는 메뉴: 일 + 승급 2개).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)
L11 = 'Value In Array(Global Variable(LocPos), 11)'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ [1] 소 소환 ═══════════════════════════════════════════════════
sub('Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, Visible To Position Radius and Color);',
    'Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, None);', 2)
sub('Vector(Multiply(Random Real(12, 22), Random Integer(0, 1) == 1 ? 1 : -1), 0, Multiply(Random Real(12, 22), Random Integer(0, 1) == 1 ? 1 : -1))',
    'Vector(Multiply(Random Real(7, 12), Random Integer(0, 1) == 1 ? 1 : -1), 0, Multiply(Random Real(7, 12), Random Integer(0, 1) == 1 ? 1 : -1))')

# ══ [2] 배달 보수 ═════════════════════════════════════════════════
FEE = 'Round To Integer(Add(15, Multiply(Distance Between(%s, Value In Array(Global Variable(LocPos), Event Player.DelDest)), 2)), To Nearest)' % L11
sub('Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Distance Between(%s, Value In Array(Global Variable(LocPos), Event Player.DelDest)), 1.5), To Nearest));' % L11,
    'Set Player Variable(Event Player, RunPay, %s);' % FEE)
ZONE_NAMES = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), Custom String("모텔"), '
              'Custom String("정비소 고물상"), Custom String("술집"), Custom String("협곡 개활지"), Custom String("보안관 초소"), '
              'Custom String("무법자 은신처"), Custom String("안내소"), Custom String("대장간"))')
sub('Big Message(Event Player, Custom String("화물 접수 — {0}까지 달려라!", Value In Array(%s, Event Player.DelDest)));' % ZONE_NAMES,
    'Big Message(Event Player, Custom String("화물 접수 — {0}까지! 기본 보수 $ {1}", Value In Array(%s, Event Player.DelDest), %s));' % (ZONE_NAMES, FEE))

# ══ [3] 일터 전직 제거 ════════════════════════════════════════════
for zone, jobname in ((11, '파발꾼'), (12, '목동')):
    zkey = 'Else If(Event Player.Zone == %d);' % zone
    zi = s.index(zkey)
    ei = s.index('Else If(Event Player.MenuIdx == 1);', zi)
    seg_old = s[zi:ei + len('Else If(Event Player.MenuIdx == 1);')]
    assert ('이미 %s이다' % jobname) in seg_old        # 전직 분기가 맞는지 확인
    s = s[:zi] + zkey + NLC + T*3 + 'If(Event Player.MenuIdx == 0);' + s[ei + len('Else If(Event Player.MenuIdx == 1);'):]

# 메뉴 수: 정거장·목장 3 -> 2
sub('Array(1, 6, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4, 3, 3)', 'Array(1, 6, 3, 4, 2, 3, 4, 2, 3, 4, 1, 4, 2, 2)', 4)

# 라벨 격자 마지막 12칸 (정거장·목장 행) 재배치
OLDTAIL = ('Custom String("전직: 파발꾼"), Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), '
           'Custom String("-"), Custom String("-"), Custom String("-"), '
           'Custom String("전직: 목동"), Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), '
           'Custom String("-"), Custom String("-"), Custom String("-"))')
NEWTAIL = ('Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("-"), '
           'Custom String("-"), Custom String("-"), Custom String("-"), '
           'Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("-"), '
           'Custom String("-"), Custom String("-"), Custom String("-"))')
sub(OLDTAIL, NEWTAIL, 2)

# 가드 문구에 전직 창구 안내
sub('Custom String("파발꾼만 수주할 수 있다")', 'Custom String("파발꾼만 수주할 수 있다 — 전직은 식당에서")')
sub('Custom String("목동만 소를 몰 수 있다")', 'Custom String("목동만 소를 몰 수 있다 — 전직은 식당에서")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1] 소 재평가 None + 산포 7~12m / [2] 보수 15+거리x2 / [3] 전직은 식당 전용')
