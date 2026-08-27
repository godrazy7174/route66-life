# -*- coding: utf-8 -*-
"""수정안 검증용 시뮬레이션.

수정 골자
 1) 위스키 하루 2잔 제한 + 회복 40->30  (무한 피로 보충 차단)
 2) 피로 효율 보정: 피로가 낮으면 채굴 수확이 줄어든다
    -> 피로가 '할 수 있냐/없냐'가 아니라 '얼마나 잘 버냐'가 되어
       하루 시간이 남지도, 무한 반복이 되지도 않는다
 3) 보급 회복량 45->55 (상점 왕복 빈도 감소)
"""
import random, sys

DAY = 720.0
MINE_T = 3.5
MINE_EN, MINE_HU, MINE_TH = 5, 2, 2.5
PASSIVE = (1.2, 1.5, 0.5)
JERKY, CANTEEN = 15, 10
FOOD_V = 55
SLEEP_COST = 60
WHISKY_COST, WHISKY_V, WHISKY_MAX = 25, 30, 2
TRAVEL = 12.0
SHOP = 16.0


def fatigue_penalty(en):
    if en >= 60:
        return 0
    if en >= 30:
        return 1
    return 2


def sim(pick=0, joblv=1, has_home=False, has_horse=False, seed=0,
        price_lo=2, price_hi=5, jack_base=0.06, jack_lo=60, jack_hi=140, bonus10=30):
    rnd = random.Random(seed)
    t = money = 0.0
    hu = th = en = 100.0
    ore = 0; mines = 0; whisky_used = 0; slept = False
    jerky = canteen = 0
    spent = {'식량': 0, '숙박': 0, '위스키': 0}
    tu = {'채굴': 0.0, '이동': 0.0, '보급': 0.0}
    price = rnd.randint(price_lo, price_hi)
    jack = min(jack_base + 0.01 * (joblv - 1), 0.18)
    travel = TRAVEL * (0.8 if has_horse else 1.0)
    shop = SHOP * (0.8 if has_horse else 1.0)

    def tick(sec, bucket):
        nonlocal hu, th, en, t
        t += sec; tu[bucket] += sec
        hu = max(0, hu - PASSIVE[0] * sec / 10)
        th = max(0, th - PASSIVE[1] * sec / 10)
        en = max(0, en - PASSIVE[2] * sec / 10)

    while t < DAY:
        # 현장 보급
        if hu < 30 and jerky > 0:
            jerky -= 1; hu = min(100, hu + FOOD_V); tick(1, '보급'); continue
        if th < 30 and canteen > 0:
            canteen -= 1; th = min(100, th + FOOD_V); tick(1, '보급'); continue
        # 상점 왕복 (한 번에 5개씩 비축)
        if (hu < 30 and jerky == 0) or (th < 30 and canteen == 0):
            money -= 65; spent['식량'] += 65; jerky += 5
            money -= 50; spent['식량'] += 50; canteen += 5
            tick(shop + 6, '보급'); continue
        # 피로
        if en < 15:
            if not slept or has_home:
                cost = 0 if has_home else SLEEP_COST
                money -= cost; spent['숙박'] += cost
                en = 100; slept = True; tick(6 + shop, '보급'); continue
            elif whisky_used < WHISKY_MAX:
                money -= WHISKY_COST; spent['위스키'] += WHISKY_COST
                en = min(100, en + WHISKY_V); whisky_used += 1
                tick(shop, '보급'); continue
        # 채굴 (피로 0이어도 가능하지만 수확이 급감)
        tick(MINE_T, '채굴')
        hu = max(0, hu - MINE_HU); th = max(0, th - MINE_TH)
        en_before = en; en = max(0, en - MINE_EN)
        mines += 1
        if rnd.random() < jack:
            money += rnd.randint(jack_lo, jack_hi)
        else:
            yield_ = rnd.randint(1, 2) + 1 + pick - fatigue_penalty(en_before)
            ore += max(0, yield_)
        if mines % 10 == 0:
            money += bonus10
        if ore >= 20:
            tick(travel, '이동'); money += ore * price; ore = 0
    money += ore * price
    return dict(money=money, mines=mines, spent=spent, time=tu, whisky=whisky_used)


def report(label, n=40, **kw):
    rows = [sim(seed=i, **kw) for i in range(n)]
    m = sum(r['money'] for r in rows) / n
    mi = sum(r['mines'] for r in rows) / n
    tu = {k: sum(r['time'][k] for r in rows) / n for k in rows[0]['time']}
    print('  %-26s 순이익 $%-6.0f  채굴 %3.0f회  |  채굴 %2.0f%% 이동 %2.0f%% 보급 %2.0f%%'
          % (label, m, mi, tu['채굴'] / DAY * 100, tu['이동'] / DAY * 100, tu['보급'] / DAY * 100))
    return m


tune = dict(price_lo=2, price_hi=4, jack_base=0.05, jack_lo=50, jack_hi=110, bonus10=25)
if '--tuned' in sys.argv:
    print('=== 수정 + 수치 조정 후 ===')
    kw = tune
else:
    print('=== 수정만 (수치는 현재 값) ===')
    kw = {}

base = report('기본 (곡괭이0, 직업Lv1)', **kw)
report('곡괭이 Lv2', pick=2, **kw)
report('곡괭이 Lv4 + 직업 Lv10', pick=4, joblv=10, **kw)
report('완전 장비 (내방+말+곡4)', pick=4, joblv=10, has_home=True, has_horse=True, **kw)

print('\n=== 진행 사다리 (기본 수입 $%.0f/일 기준) ===' % base)
cum = 0
for name, cost in [('곡괭이 Lv1', 250), ('곡괭이 Lv2', 600), ('가죽 배낭', 800),
                   ('곡괭이 Lv3', 1400), ('말', 2000), ('곡괭이 Lv4', 3000), ('내 방', 3500)]:
    cum += cost
    print('  %-12s 누적 $%-6d → %5.1f일 (%3.0f분)' % (name, cum, cum / base, cum / base * 12))
