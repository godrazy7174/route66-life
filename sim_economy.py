# -*- coding: utf-8 -*-
"""경제·일정을 실제로 돌려 구조적 결함을 찾는다.

정적 분석(코드 읽기)으로는 "일일 목표가 언젠가 달성 불가해지는가" 같은
누적·시간 의존 결함이 안 보인다. 상수를 .ow 에서 직접 뽑아 굴려 본다.

가정은 전부 아래 ASSUME 에 모아 두고 결과와 함께 출력한다.
가정이 틀리면 결론도 틀리므로, 실기에서 한 번 재보고 숫자를 고치면 된다.
"""
import io
import math
import re

SRC = 'ROUTE66_LIFE_EN.ow'
s = io.open(SRC, encoding='utf-8').read()

# ── .ow 에서 상수 뽑기 ────────────────────────────────────────────
def one(pat, cast=float):
    m = re.search(pat, s)
    assert m, '못 찾음: %s' % pat
    return cast(m.group(1))


CLOCK_STEP = one(r'Modify Global Variable\(Clock, Add, (\d+)\)')
TICK = one(r'rule\("\[월드 01\][^"]*"\)[\s\S]{0,400}?Wait\(([\d.]+),')
DAY_SEC = 1440 / CLOCK_STEP * TICK

GOAL_BASE = one(r'Set Global Variable\(DailyGoal, Add\((\d+), Multiply')
GOAL_PER_DAY = one(r'Set Global Variable\(DailyGoal, Add\(\d+, Multiply\(Global Variable\(Day\), (\d+)\)')

DELIV_BASE = one(r'RunPay, Round To Integer\(Add\((12), Multiply')
DELIV_RATE = one(r'Event Player\.DelDest\)\), ([\d.]+)\)')
ESCORT_BASE = one(r'EscortPay, Round To Integer\(Add\((60), Multiply')
ESCORT_RATE = one(r'Event Player\.EscortPos\), ([\d.]+)\)\), To Nearest')
SMUG_BASE = one(r'SmugglePay, Round To Integer\(Add\((24), Multiply')
SMUG_RATE = one(r'Event Player\.SmugglePos\), ([\d.]+)\)\), To Nearest')
HERD_BASE = one(r'RunPay, Add\((\d+), Multiply\(4,')
RAID_LO = one(r'PlanPay, Random Integer\((\d+), \d+\)')
RAID_HI = one(r'PlanPay, Random Integer\(\d+, (\d+)\)')
ESCORT_CD = one(r'EscortCd, Add\(Total Time Elapsed\(\), (\d+)\)')
SMUG_CD = one(r'SmuggleCd, Add\(Total Time Elapsed\(\), (\d+)\)')
GOAL_BONUS = one(r'Money, Add, Event Player\.Rebuild >= 2 \? \d+ : (\d+)')
FUND_STEP = one(r'Modify Global Variable\(Fund, Add, (\d+)\)')
FUND_GOAL = one(r'Array\(8000, 23000, 48000, 88000, 148000, 233000, 348000, (\d+)\)')

# 좌표 (배치 풀) — 거리 분포를 실제로 계산한다
raid = [(-91, 7, -14), (-80, 7, 7), (-61, 7, 16), (-51, 3, -6), (-46, 3, -11), (-47, 3, -22),
        (-40, 3, -34), (-27, 3, -38), (-17, 3, -22), (-4, 3, -14), (16, 2, -7), (29, 2, 13), (32, 2, -2)]
loc = [(44.29, 2.39, 62.28), (21.71, 2.07, 17.81), (31.96, 2.14, -2.84), (-11.17, 3.02, -4.93),
       (-16.24, 3.49, -46.07), (-34.83, 3.43, -17.51), (58.16, 1.39, 23.4), (-75.34, 6.5, 21.36),
       (7.66, 8.99, -41.28)]
loc += [(loc[0][0], loc[0][1], loc[0][2] - 4), (loc[4][0] + 6, loc[4][1], loc[4][2]),
        (-82.36, 6.5, -15.2), (-92.09, 6.5, -30), (-30.13, 8.43, -21.18), (-90.02, 6.5, 19.68)]
spot = raid + loc
d = lambda a, b: math.dist(a, b)

# ── 가정 (실기에서 재보고 고칠 값) ────────────────────────────────
ASSUME = {
    '기본 이동 속도(m/s)': 5.5 * 1.10,
    '질주 속도(m/s)': 5.5 * 1.65,
    '실제 경로 / 직선 비율': 1.3,
    '메뉴 조작 1회(초)': 2.0,
    '하루 중 실제 노동 비율': 0.85,
    '소몰이 1회 소요(초)': 90.0,
    '채굴 1타(초)': 0.95,
}
WALK = ASSUME['기본 이동 속도(m/s)']
RUN = ASSUME['질주 속도(m/s)']
PATH = ASSUME['실제 경로 / 직선 비율']
MENU = ASSUME['메뉴 조작 1회(초)']


def travel(dist, sprint=True):
    return dist * PATH / (RUN if sprint else WALK)


# ── 직업별 사이클 ($/분) ─────────────────────────────────────────
def job_rates():
    out = {}

    # 파발꾼 — 정거장(LocPos 11) -> 목적지(0~10) 왕복
    dists = [d(loc[11], loc[i]) for i in range(11)]
    md = sum(dists) / len(dists)
    pay = DELIV_BASE + md * DELIV_RATE
    pay *= 0.75 * 1 + 0.25 * 2.5          # 25% 확률 값진 화물 2.5배
    t = travel(md) * 2 + MENU
    out['파발꾼(배달)'] = (pay, t)

    # 금괴 호송 — 정거장에서 35m 이상, 질주 불가, 쿨타임
    cand = [x for x in (d(loc[11], p) for p in spot) if x >= 35]
    md = sum(cand) / len(cand)
    out['파발꾼(금괴 호송)'] = (ESCORT_BASE + md * ESCORT_RATE,
                          travel(md, sprint=False) * 2 + MENU + ESCORT_CD)

    # 밀수 — 은신처에서 40m 이상, 질주 불가, 쿨타임
    cand = [x for x in (d(loc[8], p) for p in spot) if x >= 40]
    md = sum(cand) / len(cand)
    out['무법자(밀수)'] = (SMUG_BASE + md * SMUG_RATE,
                       travel(md, sprint=False) * 2 + MENU + SMUG_CD)

    # 목동 — 소몰이
    out['목동(소몰이)'] = (HERD_BASE, ASSUME['소몰이 1회 소요(초)'] + MENU)

    # 무법자 — 역마차 습격 (게이지 4/0.5초 -> 100까지 약 13초 + 접근)
    out['무법자(역마차 습격)'] = ((RAID_LO + RAID_HI) / 2, 13 + travel(40) + MENU)

    # 광부 — 원석 평균 2개 × 시세 평균 3.5 + 10타마다 20
    ore = 2.0 * 3.5 + 20 / 10.0
    out['광부(채굴)'] = (ore, ASSUME['채굴 1타(초)'])
    return out


rates = job_rates()
print('=== 가정 ===')
for k, v in ASSUME.items():
    print('  %-22s %s' % (k, v))
print('\n=== .ow 에서 뽑은 상수 ===')
print('  하루 %.0f초 (%.0f분) · 일일 목표 = %.0f + 일차×%.0f · 목표 보너스 $%.0f'
      % (DAY_SEC, DAY_SEC / 60, GOAL_BASE, GOAL_PER_DAY, GOAL_BONUS))
print('  배달 %.0f+거리×%.2f · 호송 %.0f+거리×%.0f(쿨%.0f) · 밀수 %.0f+거리×%.0f(쿨%.0f)'
      % (DELIV_BASE, DELIV_RATE, ESCORT_BASE, ESCORT_RATE, ESCORT_CD, SMUG_BASE, SMUG_RATE, SMUG_CD))

print('\n=== 직업별 벌이 ===')
best = 0
for k, (pay, t) in sorted(rates.items(), key=lambda kv: -kv[1][0] / kv[1][1]):
    per_min = pay / t * 60
    best = max(best, per_min)
    print('  %-20s 1회 $%-7.0f %5.1f초  ->  $%.0f/분' % (k, pay, t, per_min))

work = DAY_SEC * ASSUME['하루 중 실제 노동 비율']
day_income = best * work / 60
print('\n  최고 효율 직업으로 하루 종일: $%.0f/분 × %.0f초(노동) = 하루 $%.0f' % (best, work, day_income))

print('\n=== 일일 목표 달성 가능성 ===')
print('  %-6s %-10s %-10s %s' % ('일차', '목표', '가능 수입', '판정'))
fail_day = None
for day in [1, 5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100]:
    goal = GOAL_BASE + day * GOAL_PER_DAY
    ok = goal <= day_income
    if not ok and fail_day is None:
        fail_day = day
    print('  %-6d $%-9.0f $%-9.0f %s' % (day, goal, day_income, '가능' if ok else '불가'))
exact = (day_income - GOAL_BASE) / GOAL_PER_DAY
print('\n  이론상 마지막 달성 가능일: %d일차 (그 뒤로는 하루 종일 최고 효율로 일해도 불가)' % int(exact))
print('  현실 플레이(효율 60%%) 기준: %d일차' % int((day_income * 0.6 - GOAL_BASE) / GOAL_PER_DAY))
print('  실시간으로는 %.1f시간째' % (int(exact) * DAY_SEC / 3600))

print('\n=== 마을 금고 8단계까지 ===')
for players in (1, 4, 8):
    per_day = day_income * 0.6 * players
    donate = min(per_day * 0.5, per_day)
    days = FUND_GOAL / donate
    print('  %d인 서버: 하루 총수입 $%.0f · 절반을 갹출하면 %.0f일 (실시간 %.1f시간)'
          % (players, per_day, days, days * DAY_SEC / 3600))


# ── 피로를 제약으로 넣은 지속 가능 시급 ─────────────────────────
# 시간당 벌이만 보면 틀린다. 피로는 숙박으로만 실질 회복되고,
# 숙박은 돈과 시간을 둘 다 쓴다. 그 비용을 각 직업에 배분해야
# "계속 굴릴 수 있는" 진짜 시급이 나온다.
SLEEP_COST = one(r'Multiply\((90), Subtract\(1')
SLEEP_GAIN = one(r'HasHome == 1 \? 80 : (\d+)')
SLEEP_SEC = 4.5
rest_price = SLEEP_COST / SLEEP_GAIN      # 피로 1 회복에 드는 돈
rest_time = SLEEP_SEC / SLEEP_GAIN        # 피로 1 회복에 드는 시간
AMBIENT = 0.5 / 10.0                      # 상시 감소 (초당)
SPRINT = 1 / 3.0                          # 질주 중 초당

# 이름: (1회 보수, 사이클 초, 직업 피로 소모, 사이클 중 질주 초)
JOBS = {
    '광부(채굴)': (2.0 * 3.5 + 2.0, 0.95, 2.5, 0),
    '파발꾼(배달)': (rates['파발꾼(배달)'][0], rates['파발꾼(배달)'][1],
                 4, rates['파발꾼(배달)'][1] * 0.5),
    '파발꾼(배달·역마차장)': (rates['파발꾼(배달)'][0] * 1.3, rates['파발꾼(배달)'][1], -1, 0),
    '파발꾼(금괴 호송)': (rates['파발꾼(금괴 호송)'][0], rates['파발꾼(금괴 호송)'][1], 4, 0),
    '무법자(밀수)': (rates['무법자(밀수)'][0], rates['무법자(밀수)'][1], 3, 0),
    '무법자(역마차 습격)': (rates['무법자(역마차 습격)'][0], rates['무법자(역마차 습격)'][1], 8, 6),
    '목동(소몰이)': (rates['목동(소몰이)'][0], rates['목동(소몰이)'][1], 5, 20),
}

print('')
print('=== 피로를 제약으로 넣은 지속 가능 시급 ===')
print('  숙박 $%.0f 에 피로 +%.0f → 피로 1 = $%.2f · %.2f초' % (SLEEP_COST, SLEEP_GAIN, rest_price, rest_time))
print('  %-22s %-11s %-11s %-9s %s' % ('직업', '$/분(순진)', '피로/사이클', '$/피로', '지속 $/분'))
rows = []
for k, (pay, t, ejob, sprint_s) in JOBS.items():
    e = ejob + AMBIENT * t + SPRINT * sprint_s
    naive = pay / t * 60
    if e <= 0:
        rows.append((k, naive, e, None, naive))
        continue
    net = pay - rest_price * e
    sustain = net / (t + rest_time * e) * 60
    rows.append((k, naive, e, pay / e, sustain))
for k, naive, e, per_e, sustain in sorted(rows, key=lambda r: -r[4]):
    print('  %-22s $%-10.0f %-11.1f %-9s $%.0f'
          % (k, naive, e, '무한' if per_e is None else '$%.0f' % per_e, sustain))

fin = [r for r in rows if r[3] is not None]
lo = min(r[4] for r in fin)
hi = max(r[4] for r in fin)
print('')
print('  지속 시급 격차: $%.0f/분 ~ $%.0f/분 = %.1f배' % (lo, hi, hi / lo))
inf = [r[0] for r in rows if r[3] is None]
if inf:
    print('  피로가 순증해 쉬지 않아도 되는 직업: %s' % ', '.join(inf))
print('  ※ 습격은 1회마다 현상금 +200 · 악명 +15 가 붙어 $800 에서 상점이 막힌다 —')
print('     4회면 추방이므로 위 수치를 오래 유지할 수 없다 (자체 제동이 걸려 있다)')
