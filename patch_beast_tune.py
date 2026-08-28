# -*- coding: utf-8 -*-
"""대야수 실기 조정 — 사거리 25 -> 12, 강타 55 -> 28.

실기 제보: 사거리가 너무 길고, 피해는 절반이면 좋겠다.

사거리 25 는 README 8-2 가 "실기 조정 전제값"이라고 못박아 둔 숫자였다.
야수는 `Hero(Jetpack Cat)` 이고 원래 히트박스가 아주 작은 영웅이라,
30배를 해도 몸 반경이 10m 안팎이다. 25m 면 몸 바깥으로 15m 쯤 떨어져 있어도
맞는 셈이라 "닿지도 않았는데 맞는다"는 체감이 된다. 몸집에 붙는 12 로 내린다.
(참고로 전설의 야수가 50배라 대야수 30배보다 크다)

**두 곳을 반드시 같이 고쳐야 한다** — README 7장 8번이 경고한 대로다.
사거리는 강타 판정만이 아니라 끼임 워프의 게이트로도 쓰인다.
강타를 12 로 내리고 워프 게이트를 25 로 두면, 표적이 12~25m 에 있을 때
때리지도 못하고(12 초과) 워프하지도 못해(25 이하) 그 자리에 굳는다.

피해 55 -> 28 (절반). 1.6초 간격은 그대로라 초당 약 17.5 가 된다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)


# ── 강타 판정 사거리 ───────────────────────────────────────────
sub("Distance Between(Position Of(Event Player), Position Of(Global Variable(HuntTgt))) <= 25,"
    " Total Time Elapsed() >= Global Variable(HuntSwing)",
    "Distance Between(Position Of(Event Player), Position Of(Global Variable(HuntTgt))) <= 12,"
    " Total Time Elapsed() >= Global Variable(HuntSwing)")

# ── 강타 피해 ──────────────────────────────────────────────────
sub("				Damage(Global Variable(HuntTgt), Event Player, 55);",
    "				Damage(Global Variable(HuntTgt), Event Player, 28);")

# ── 끼임 워프 게이트 (같은 사거리를 써야 한다) ─────────────────
sub("Distance Between(Position Of(Event Player), Position Of(Global Variable(HuntTgt))) > 25)))",
    "Distance Between(Position Of(Event Player), Position Of(Global Variable(HuntTgt))) > 12)))")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
