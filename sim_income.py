# -*- coding: utf-8 -*-
"""직업별 수익 몬테카를로 시뮬레이션 — 코드 실측 파라미터 기반.

전제 (모든 직업 공통):
  - 1일 = 720초(12분) 순수 노동, 솔로 기준 (PvP 피탈·체포당함 없음)
  - 월드 이벤트(2배 등) 제외, 오늘 목표 보너스 제외 (전 직업 동일 조건)
  - 스탯 자연 감소: 10초당 허기 -1.2 / 갈증 -1.5 / 피로 -0.5
  - 회복 최적 플레이: 식사 $18(+60/+60), 위스키 $38(피로+30·갈증+10)
    회복 방문 시간 = 일터-가게 거리 실측 기반 왕복
  - 이동: 걷기 5.5m/s, 질주 9.08m/s(165%), 질주 3초당 피로 1
  - 판매: 원석·가죽은 정비소 시세 100%로 일괄 판매 (시세는 일별 랜덤)
  - 메뉴 조작 오버헤드 0.8초/회
시나리오: 신입 / 숙련. v2026-08-27 동기화: -20% 경제·QTE(정타55%/샛길75%/고삐55% 가정)·확률2배·소몰이 49~77m
"""
import random, math

DAY = 720.0
WALK, SPRINT = 5.5, 9.08
LOC = {0:(44.29,62.28), 1:(21.71,17.81), 2:(31.96,-2.84), 3:(-11.17,-4.93),
       4:(-16.24,-46.07), 5:(-34.83,-17.51), 6:(58.16,23.4), 7:(-75.34,21.36),
       8:(7.66,-41.28), 9:(44.29,58.28), 10:(-10.24,-46.07), 11:(-82.36,-15.2),
       12:(-92.09,-30.0), 13:(-30.13,-21.18), 14:(-90.02,19.68)}

def dist(a, b):
    return math.hypot(LOC[a][0]-LOC[b][0], LOC[a][1]-LOC[b][1])

def nearest(frm, targets):
    return min(dist(frm, t) for t in targets)

MEALS = [0, 13, 14]   # 식당들
BAR = 5               # 술집 (위스키)

class P:
    def __init__(self, xp, adv, pick=0, bag=0):
        self.h = self.t = self.e = 100.0
        self.money = 0.0
        self.xp = xp; self.adv = adv; self.pick = pick; self.bag = bag
        self.time = 0.0; self.spent = 0.0
        self.ore = 0; self.hide = 0
    @property
    def lv(self): return int(self.xp // 250)

def decay(p, sec):
    p.h = max(0, p.h - 1.2 * sec / 10)
    p.t = max(0, p.t - 1.5 * sec / 10)
    p.e = max(0, p.e - 0.5 * sec / 10)
    p.time += sec

def travel(p, meters, sprint=True):
    if sprint and p.e > 15:
        sec = meters / SPRINT
        p.e = max(0, p.e - sec / (6 if p.bag else 3))
    else:
        sec = meters / WALK
    decay(p, sec)

def upkeep(p, workzone, need_e):
    # 갈증·허기: 30 밑이면 식사 (가장 가까운 식당 왕복)
    if p.h < 30 or p.t < 30:
        d = nearest(workzone, MEALS)
        travel(p, d * 2); decay(p, 3)
        p.money -= 18; p.spent += 18
        p.h = min(100, p.h + 60); p.t = min(100, p.t + 60)
    # 피로: 작업 요구치 밑이면 위스키 (술집 왕복, 필요한 만큼 연속 구매)
    if p.e < need_e:
        d = dist(workzone, BAR)
        travel(p, d * 2)
        while p.e < 70:
            decay(p, 2)
            p.money -= 38; p.spent += 38
            p.e = min(100, p.e + 30); p.t = min(100, p.t + 10)

def sim_miner(pro):
    p = P(1000 if pro else 0, 1 if pro else 0, pick=2 if pro else 0)
    streak = 0; count = 0; prospect = 0
    while p.time < DAY:
        upkeep(p, 1, 5)
        if pro and prospect == 0:          # 광산주는 정밀 탐사 무료
            decay(p, 0.8); prospect = 3
        decay(p, 4.0)                       # 채굴 3.2s + 조작
        p.e = max(0, p.e - 5); p.h = max(0, p.h - 2); p.t = max(0, p.t - 2.5)
        roll = random.randint(1, 100) - 2 - min(4, p.lv)
        if prospect > 0: roll -= 8; prospect -= 1
        count += 1
        if roll <= 3:
            p.money += random.randint(40, 105); p.xp += 40
        else:
            gain = random.randint(1, 2) + 1 + p.pick
            if pro and random.random() < 0.10: gain *= 2
            p.ore += gain; p.xp += 12
        if random.random() < 0.30:          # 정타 QTE (30%)
            decay(p, 2.1)
            if random.random() < 0.55: p.ore += 3
        if count % 10 == 0: p.money += 20
        streak += 1
        if streak % 5 == 0: p.money += min(streak, 25) * 3
    p.money += p.ore * ORE_PRICE
    return p

def sim_hunter(pro):
    p = P(1000 if pro else 0, 1 if pro else 0)
    giant_c = 32 if pro else 22
    leg_c = 2
    while p.time < DAY:
        upkeep(p, 6, 4)
        decay(p, 2.6)                       # 추적 1.8s + 조작
        p.e = max(0, p.e - 4); p.h = max(0, p.h - 1.5); p.t = max(0, p.t - 2)
        for _ in range(3):                  # 야수 3마리 처치
            r = random.randint(1, 1000)
            leg = r <= leg_c; giant = (not leg) and r <= giant_c
            decay(p, 24 if leg else (5 if giant else 3))
            y = random.randint(1, 3) + min(2, p.lv) + (1 if pro else 0)
            if leg:   y *= 50; p.money += 200
            elif giant: y *= 5; p.money += 40
            elif random.random() < 0.10: p.money += 48
            p.hide += y; p.xp += 15
    p.money += p.hide * HIDE_PRICE
    return p

def sim_courier(pro):
    p = P(1000 if pro else 0, 1 if pro else 0)
    while p.time < DAY:
        upkeep(p, 11, 4)
        decay(p, 1.6)                       # 수주 조작
        dest = random.randint(0, 10)
        d = dist(11, dest)
        travel(p, d); travel(p, d)          # 왕복
        pay = round(12 + d * 1.05)
        pay = round(pay * (1 + 0.05 * min(10, p.lv)))
        if pro:
            pay = round(pay * 1.3); p.e = min(100, p.e + 5)
        p.e = max(0, p.e - 4); p.h = max(0, p.h - 2); p.t = max(0, p.t - 3)
        n_prompt = int((2 * d / SPRINT) // 11)
        for _ in range(n_prompt):           # 샛길 QTE
            decay(p, 3)
            if random.random() < 0.75: p.money += 12
        p.money += pay; p.xp += 25
    return p

def sim_herder(pro):
    p = P(1000 if pro else 0, 1 if pro else 0)
    while p.time < DAY:
        upkeep(p, 12, 5)
        decay(p, 1.6)
        cow_d = random.uniform(49, 77)
        travel(p, cow_d)                    # 소까지 이동
        rate = 1.04 if pro else 0.90        # 밀기 실효 속도(구버전 실측 역산)
        drive = 8 + cow_d / rate
        n_prompt = int(drive // 13)
        for _ in range(n_prompt):           # 고삐 QTE (스킬바)
            if random.random() < 0.55: p.money += 10
        decay(p, drive)
        p.e = max(0, p.e - 5); p.h = max(0, p.h - 3); p.t = max(0, p.t - 2.5)
        pay = 220 + 4 * min(10, p.lv)
        if pro: pay = round(pay * 1.15)
        p.money += pay; p.xp += 25
    return p

def sim_outlaw(pro):
    p = P(1000 if pro else 0, 1 if pro else 0)
    plan = 0
    while p.time < DAY:
        upkeep(p, 8, 6)
        decay(p, 3.3)                       # 습격 계획 2.5s + 조작
        p.e = max(0, p.e - 8); p.h = max(0, p.h - 3); p.t = max(0, p.t - 3)
        p.money += random.randint(6, 12); p.xp += 15
        plan += 1
        if plan >= (2 if pro else 3):
            plan = 0
            p.money += random.randint(52, 100)
    return p

JOBS = [('광부', sim_miner), ('사냥꾼', sim_hunter), ('파발꾼', sim_courier),
        ('목동', sim_herder), ('무법자(습격)', sim_outlaw)]

N = 3000
random.seed(66)
print('직업            | 시나리오 | 총수입/일     | 유지비/일   | 순수익/일     | 분당')
print('-' * 88)
results = {}
for name, fn in JOBS:
    for pro in (False, True):
        g = []; c = []
        for _ in range(N):
            global ORE_PRICE, HIDE_PRICE
            ORE_PRICE = random.randint(2, 5)
            HIDE_PRICE = random.randint(3, 6)
            p = fn(pro)
            g.append(p.money + p.spent); c.append(p.spent)
        gross = sum(g) / N; cost = sum(c) / N; net = gross - cost
        sd = (sum((x - c2) ** 2 for x, c2 in zip(g, [gross] * N)) / N) ** 0.5
        tag = '숙련·승급' if pro else '신입    '
        results[(name, pro)] = (gross, cost, net, sd)
        print('%-14s | %s | $%6.0f ±%4.0f | $%9.0f | $%11.0f | $%5.1f'
              % (name, tag, gross, sd, cost, net, net / 12))
