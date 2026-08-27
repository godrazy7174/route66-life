# -*- coding: utf-8 -*-
"""최종안 검증: 피로 하드 게이트 + 수치 조정."""
import random

DAY = 720.0
MINE_T = 4.5
MINE_EN, MINE_HU, MINE_TH = 5, 2, 2.5
PASSIVE = (1.2, 1.5, 0.5)
FOOD_V = 55
SLEEP_COST = 60
WHISKY_COST, WHISKY_V, WHISKY_MAX = 25, 30, 2
TRAVEL, SHOP = 12.0, 16.0
PRICE_LO, PRICE_HI = 3, 6
JACK_LO, JACK_HI = 50, 130
BONUS10 = 25


def sim(pick=0, joblv=1, has_home=False, has_horse=False, seed=0):
    rnd = random.Random(seed)
    t = money = 0.0
    hu = th = en = 100.0
    ore = mines = whisky = 0
    jerky = canteen = 0
    sleeps = 0
    idle = 0.0
    tu = {'채굴': 0.0, '이동': 0.0, '보급': 0.0, '유휴': 0.0}
    price = rnd.randint(PRICE_LO, PRICE_HI)
    jack = (3 + (2 if True else 0) + min(12, joblv - 1)) / 100.0
    travel = TRAVEL * (0.8 if has_horse else 1.0)
    shop = SHOP * (0.8 if has_horse else 1.0)

    def tick(sec, b):
        nonlocal hu, th, en, t
        t += sec; tu[b] += sec
        hu = max(0, hu - PASSIVE[0] * sec / 10)
        th = max(0, th - PASSIVE[1] * sec / 10)
        en = max(0, en - PASSIVE[2] * sec / 10)

    while t < DAY:
        if hu < 30 and jerky > 0:
            jerky -= 1; hu = min(100, hu + FOOD_V); tick(1, '보급'); continue
        if th < 30 and canteen > 0:
            canteen -= 1; th = min(100, th + FOOD_V); tick(1, '보급'); continue
        if (hu < 30 and jerky == 0) or (th < 30 and canteen == 0):
            money -= 115; jerky += 5; canteen += 5
            tick(shop + 6, '보급'); continue
        if en < MINE_EN:                       # ← 하드 게이트
            cap = 2 if has_home else 1
            if sleeps < cap:
                money -= (0 if has_home else SLEEP_COST)
                en = 100; sleeps += 1; tick(6 + shop, '보급'); continue
            if whisky < WHISKY_MAX:
                money -= WHISKY_COST; en = min(100, en + WHISKY_V)
                whisky += 1; tick(shop, '보급'); continue
            tick(8, '유휴'); idle += 8; money += 25; continue   # 피로 없이 가능한 현상금 사냥
        tick(MINE_T, '채굴')
        hu = max(0, hu - MINE_HU); th = max(0, th - MINE_TH); en = max(0, en - MINE_EN)
        mines += 1
        if rnd.random() < jack:
            money += rnd.randint(JACK_LO, JACK_HI)
        else:
            ore += rnd.randint(1, 2) + 1 + pick
        if mines % 10 == 0:
            money += BONUS10
        if ore >= 20:
            tick(travel, '이동'); money += ore * price; ore = 0
    money += ore * price
    return dict(money=money, mines=mines, time=tu, idle=idle)


def report(label, n=40, **kw):
    rows = [sim(seed=i, **kw) for i in range(n)]
    m = sum(r['money'] for r in rows) / n
    mi = sum(r['mines'] for r in rows) / n
    tu = {k: sum(r['time'][k] for r in rows) / n for k in rows[0]['time']}
    print('  %-24s 순이익 $%-5.0f 채굴 %3.0f회 | 채굴 %2.0f%% 이동 %2.0f%% 보급 %2.0f%% 현상금사냥 %2.0f%%'
          % (label, m, mi, tu['채굴'] / DAY * 100, tu['이동'] / DAY * 100,
             tu['보급'] / DAY * 100, tu['유휴'] / DAY * 100))
    return m


print('=== 피로 하드 게이트 + 조정 수치 ===')
base = report('기본 (곡괭이0, Lv1)')
report('곡괭이 Lv2, 직업 Lv4', pick=2, joblv=4)
report('곡괭이 Lv4, 직업 Lv10', pick=4, joblv=10)
full = report('완전 장비 (내방+말)', pick=4, joblv=13, has_home=True, has_horse=True)

LADDER = [('곡괭이 Lv1', 500), ('곡괭이 Lv2', 1200), ('가죽 배낭', 1800),
          ('곡괭이 Lv3', 2500), ('말', 3500), ('곡괭이 Lv4', 5000), ('내 방', 7000)]
print('\n=== 진행 사다리 ===')
cum = 0
# 장비를 살수록 수입이 오르므로 구간별 수입을 보간
for i, (name, cost) in enumerate(LADDER):
    cum += cost
    rate = base + (full - base) * (i / max(1, len(LADDER) - 1)) * 0.6
    print('  %-12s 누적 $%-5d  수입 $%-5.0f/일  →  %4.1f일 (%3.0f분)'
          % (name, cum, rate, cum / rate, cum / rate * 12))
print('\n  사다리 총액 $%d,  체감 도달 시간 약 %.0f분' % (cum, cum / ((base + full) / 2) * 12))
