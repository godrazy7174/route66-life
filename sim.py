# -*- coding: utf-8 -*-
"""66번 국도 인생게임 하루 시뮬레이션.

목적: 실제 플레이 양상을 초 단위로 굴려보고
      (1) 하루 순이익 (2) 무엇이 병목인지 (3) 시간이 어디로 가는지
      (4) 진행 사다리 도달 시점을 확인한다.
"""
import random

DAY = 720.0          # 1일 = 12분

# 현재 코드 값
MINE_T = 3.5
MINE_EN, MINE_HU, MINE_TH = 5, 2, 2.5
PASSIVE = (1.2, 1.5, 0.5)     # 10초당 허기/갈증/피로
ORE_MIN, ORE_MAX = 1, 2
JOB_ORE_BONUS = 1
PRICE_MIN, PRICE_MAX = 2, 5
JACK_BASE = 0.06              # 광부
JACK_MIN, JACK_MAX = 60, 140
BONUS10 = 30
JERKY, CANTEEN = 15, 10
JERKY_V, CANTEEN_V = 45, 45
SLEEP_COST = 60
WHISKY_COST, WHISKY_V = 25, 40
TRAVEL_MINE_TRADER = 12.0     # 광산<->정비소 왕복(달리기)
TRAVEL_SHOP = 16.0            # 잡화점/술집 왕복


def simulate_day(pick=0, joblv=1, has_home=False, has_horse=False, seed=0, verbose=False):
    rnd = random.Random(seed)
    t = 0.0
    money = 0.0
    hu = th = en = 100.0
    ore = 0
    mines = 0
    spent = {'식량': 0, '숙박': 0, '위스키': 0}
    time_use = {'채굴': 0.0, '이동': 0.0, '보급': 0.0, '판매': 0.0}
    price = rnd.randint(PRICE_MIN, PRICE_MAX)
    jack = min(JACK_BASE + 0.01 * (joblv - 1), 0.18)
    travel = TRAVEL_MINE_TRADER * (0.8 if has_horse else 1.0)
    shop = TRAVEL_SHOP * (0.8 if has_horse else 1.0)
    slept = False

    def tick(sec):
        nonlocal hu, th, en, t
        t += sec
        hu = max(0, hu - PASSIVE[0] * sec / 10)
        th = max(0, th - PASSIVE[1] * sec / 10)
        en = max(0, en - PASSIVE[2] * sec / 10)

    while t < DAY:
        # 보급 판단
        if hu < 25:
            money -= JERKY; spent['식량'] += JERKY
            hu = min(100, hu + JERKY_V)
            tick(shop); time_use['보급'] += shop
            continue
        if th < 25:
            money -= CANTEEN; spent['식량'] += CANTEEN
            th = min(100, th + CANTEEN_V)
            tick(shop); time_use['보급'] += shop
            continue
        if en < MINE_EN:
            if not slept or has_home:
                cost = 0 if has_home else SLEEP_COST
                money -= cost; spent['숙박'] += cost
                en = 100; slept = True
                tick(6 + shop); time_use['보급'] += 6 + shop
            else:
                money -= WHISKY_COST; spent['위스키'] += WHISKY_COST
                en = min(100, en + WHISKY_V)
                tick(shop); time_use['보급'] += shop
            continue
        # 채굴
        tick(MINE_T); time_use['채굴'] += MINE_T
        hu = max(0, hu - MINE_HU); th = max(0, th - MINE_TH); en = max(0, en - MINE_EN)
        mines += 1
        if rnd.random() < jack:
            money += rnd.randint(JACK_MIN, JACK_MAX)
        else:
            ore += rnd.randint(ORE_MIN, ORE_MAX) + JOB_ORE_BONUS + pick
        if mines % 10 == 0:
            money += BONUS10
        # 20개 모이면 팔러 감
        if ore >= 20:
            tick(travel); time_use['이동'] += travel
            money += ore * price; ore = 0
            time_use['판매'] += 1.0; tick(1.0)

    money += ore * price
    return dict(money=money, mines=mines, spent=spent, time=time_use,
                end=(hu, th, en), slept=slept)


def avg(rows, key):
    return sum(r[key] for r in rows) / len(rows)


print('=' * 62)
print('하루(12분) 시뮬레이션 — 광부, 30회 평균')
print('=' * 62)
for label, kw in [('기본 (곡괭이0, Lv1)', {}),
                  ('곡괭이 Lv2', dict(pick=2)),
                  ('곡괭이 Lv4 + 직업 Lv10', dict(pick=4, joblv=10)),
                  ('내 방 + 말 + 곡괭이4', dict(pick=4, joblv=10, has_home=True, has_horse=True))]:
    rows = [simulate_day(seed=i, **kw) for i in range(30)]
    m = avg(rows, 'money')
    mi = avg(rows, 'mines')
    tu = {k: sum(r['time'][k] for r in rows) / len(rows) for k in rows[0]['time']}
    sp = {k: sum(r['spent'][k] for r in rows) / len(rows) for k in rows[0]['spent']}
    print('\n[%s]' % label)
    print('  순이익 $%-7.0f  채굴 %.0f회' % (m, mi))
    print('  지출  식량 $%.0f / 숙박 $%.0f / 위스키 $%.0f' % (sp['식량'], sp['숙박'], sp['위스키']))
    print('  시간  채굴 %.0f초(%.0f%%) · 이동 %.0f초 · 보급 %.0f초' %
          (tu['채굴'], tu['채굴'] / DAY * 100, tu['이동'], tu['보급']))

print('\n' + '=' * 62)
print('진행 사다리 도달 시점 (기본 수입 기준)')
print('=' * 62)
base = avg([simulate_day(seed=i) for i in range(30)], 'money')
cum = 0
for name, cost in [('곡괭이 Lv1', 250), ('곡괭이 Lv2', 600), ('가죽 배낭', 800),
                   ('곡괭이 Lv3', 1400), ('말', 2000), ('곡괭이 Lv4', 3000), ('내 방', 3500)]:
    cum += cost
    print('  %-12s 누적 $%-6d  →  %5.1f일  (%.0f분)' % (name, cum, cum / base, cum / base * 12))
