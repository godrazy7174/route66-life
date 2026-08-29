# -*- coding: utf-8 -*-
"""패치노트 2·5·6 — 벌금·세금 인상, 식당 2배, 열차 금고 시각 동기화.

## 2. 벌금 및 세금 인상

경제 시뮬레이터 기준 지속 수입이 분당 $117~$861 인데 비해 소모처가 약했다.
수치는 지정받지 않아 아래로 잡았다 — 체감이 다르면 여기만 고치면 된다.

- 벌금: `Max(명성70+ ? 50 : 100, 현상금 x (명성70+ ? 0.15 : 0.3))`
     -> `Max(명성70+ ? 100 : 200, 현상금 x (명성70+ ? 0.25 : 0.5))`
     최소액 2배, 비율 약 1.67배. 명성 70+ 의 감면(절반)은 그대로 유지.
- 재산세: 5% -> 8% (명성 70+ 는 2.5% -> 4%). '절반' 구조 유지.

## 5. 식당 2배

$18 -> $36. 명성/악명 할인식 `x (1 - (명성-악명) x 0.002)` 은 그대로다.

## 6. 열차 금고 시각 동기화

금고를 하나 털어도 주황 구체 3개가 그대로 남아, 전부 털어야 한꺼번에 사라졌다.
`[열차 02]` 가 `TrainFx` 에 구체 3개를 담고 종료 시점에만 일괄 파괴했기 때문이다.
`[열차 03]` 에서 금고를 딸 때마다 `TrainFx[TrainVault]` 를 파괴한다 —
`TrainVault` 를 먼저 1 줄이므로 3->2 면 인덱스 2, 2->1 이면 1, 1->0 이면 0 이 사라져
**남은 금고 개수와 구체 개수가 정확히 일치한다.**
종료 시점의 일괄 파괴는 그대로 둔다 (이미 파괴된 핸들을 다시 파괴해도 무동작이고,
시간 초과로 남은 금고가 있을 때 필요하다).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:70], s.count(old))
    s = s.replace(old, new)


# ── 2. 벌금 ────────────────────────────────────────────────────
sub("Set Player Variable(Event Player, Amt, Max(Event Player.Fame >= 70 ? 50 : 100,"
    " Round To Integer(Multiply(Event Player.Bounty, Event Player.Fame >= 70 ? 0.15 : 0.3), To Nearest)));",
    "Set Player Variable(Event Player, Amt, Max(Event Player.Fame >= 70 ? 100 : 200,"
    " Round To Integer(Multiply(Event Player.Bounty, Event Player.Fame >= 70 ? 0.25 : 0.5), To Nearest)));")
sub("벌금 = 현상금의 30% · 최소 $100 (명성 70+ 절반)",
    "벌금 = 현상금의 50% · 최소 $200 (명성 70+ 절반)")
sub("벌금 납부 — 현상금의 30% (최소 $100)",
    "벌금 납부 — 현상금의 50% (최소 $200)")

# ── 2. 재산세 ──────────────────────────────────────────────────
sub("Event Player.Fame >= 70 ? 0.025 : 0.05), Down));",
    "Event Player.Fame >= 70 ? 0.04 : 0.08), Down));")
sub("재산의 5% — 예금도 재산이다 (명성 70+는 절반). 떼먹으면 10%가 현상금으로 붙는다",
    "재산의 8% — 예금도 재산이다 (명성 70+는 절반). 떼먹으면 10%가 현상금으로 붙는다")
sub("보안관 초소에서 재산세를 내라 (재산의 5%)",
    "보안관 초소에서 재산세를 내라 (재산의 8%)")

# ── 5. 식당 2배 ────────────────────────────────────────────────
sub("Set Player Variable(Event Player, Amt, Round To Integer(Multiply(18,"
    " Subtract(1, Multiply(Subtract(Event Player.Fame, Event Player.Noto), 0.002))), To Nearest));",
    "Set Player Variable(Event Player, Amt, Round To Integer(Multiply(36,"
    " Subtract(1, Multiply(Subtract(Event Player.Fame, Event Player.Noto), 0.002))), To Nearest));")
sub("식사 $18 — 허기와 갈증을 한 번에 채운다", "식사 $36 — 허기와 갈증을 한 번에 채운다", 3)
sub("식사 $18 — 허기·갈증 회복", "식사 $36 — 허기·갈증 회복", 3)

# ── 6. 금고를 딸 때마다 구체 하나씩 ────────────────────────────
sub("""			Modify Global Variable(TrainVault, Subtract, 1);
			Set Player Variable(Event Player, Loot, Random Integer(300, 500));""",
    """			Modify Global Variable(TrainVault, Subtract, 1);
			Destroy Effect(Value In Array(Global Variable(TrainFx), Global Variable(TrainVault)));
			Set Player Variable(Event Player, Loot, Random Integer(300, 500));""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
