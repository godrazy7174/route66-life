# -*- coding: utf-8 -*-
"""점검 승인분 1·가·나 — 튜토리얼 쥐 문구, 금괴 호송·목동 상향.

## 1. 튜토리얼 「사건」 장의 쥐 서술이 낡았다 (버그급)

게임 내 텍스트가 아직 "쥐떼가 몰려오면 사람부터 문다 — 셋은 붙어야 하고"인데,
개편 후 실제로는 육포부터 털고, 육포가 0이면 버티며, 1~2인에서는 무르다.
위키는 고쳤지만 게임 안 문구를 놓쳤었다.

## 가. 금괴 호송 거리 계수 2 -> 2.6

sim_economy 기준 금괴 호송이 지속 $124/분으로 안전한 배달($258)의 절반 —
매복·위치 노출·강탈 위험을 지는 옵션이 더 가난한 역전 상태였다.
계수 2.6 이면 평균 거리 80m 기준 건당 약 $268, 지속 약 $150/분(CALC).
기본 60·명성 +8·쿨타임 60초는 그대로.

## 나. 목동 상향 — 완주 $220 -> $250, 완주 피로 5 -> 4

지속 $117/분 꼴찌인데 가축 출하로 육포 재고를 채우는 공공재 직업이다.
-> 지속 약 $140/분(CALC). 목장 간판의 "피로 5"도 4 로 맞춘다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


# ── 1. 튜토리얼 쥐 문구 ────────────────────────────────────────
sub("쥐떼가 몰려오면 사람부터 문다 — 셋은 붙어야 하고, 사냥 솜씨가 있으면 더 낫다.",
    "쥐떼는 육포부터 턴다 — 바닥나면 잡을 때까지 안 떠난다. 인원이 적을수록 무르다.")

# ── 가. 금괴 호송 계수 ─────────────────────────────────────────
sub("Set Player Variable(Event Player, EscortPay, Round To Integer(Add(60,"
    " Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2)), To Nearest));",
    "Set Player Variable(Event Player, EscortPay, Round To Integer(Add(60,"
    " Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2.6)), To Nearest));")

# ── 나. 목동 완주 보수·피로 ────────────────────────────────────
sub("Set Player Variable(Event Player, RunPay, Add(220, Multiply(4,"
    " Min(10, Round To Integer(Divide(Value In Array(Event Player.JobXP, 6), 250), Down)))));",
    "Set Player Variable(Event Player, RunPay, Add(250, Multiply(4,"
    " Min(10, Round To Integer(Divide(Value In Array(Event Player.JobXP, 6), 250), Down)))));")
sub("""			Set Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 6)));
			Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 5)));""",
    """			Set Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 6)));
			Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 4)));""")
sub("몰이 성공 — 허기 3 · 갈증 2.5 · 피로 5",
    "몰이 성공 — 허기 3 · 갈증 2.5 · 피로 4")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
