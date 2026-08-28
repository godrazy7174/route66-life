# -*- coding: utf-8 -*-
"""쥐 솔로 난이도 재조정 — 8-4가 남긴 "솔로 체감이 여전히 무겁다"의 해결.

## 왜 고치는가

사용자가 고른 안전장치는 「인원수만큼 약해지게」였고, 의도는
"혼자서도 오래 버티면 잡을 수 있게" 였다. 그런데 실제 수치가 그렇지 않다.

`Set Max Health` 가 백분율이라 쥐 체력은 약 4,000 이다(8-4). 현재 공식
`Max(RatHitters >= 3 ? 70 : 18, Divide(54, N))` 로 솔로는 54% 를 받으므로
필요한 총 피해량이 4000 / 0.54 = 7,411 이다. 캐서디 지속 화력을 약 120/초로
잡으면 **약 62초를 계속 맞혀야** 한다. 반면 쥐는 3.5m 안에서 초당 20 을 물고
이동 속도가 130 이라 걷기(100)보다 빠르다 — 플레이어 체력이 200대이므로
붙으면 10초 남짓에 죽는다. 즉 솔로에서는 사실상 못 잡는다.

## 왜 분자만 키우면 안 되는가

`X / N` 꼴은 **TTK 가 인원수와 무관하다**. TTK = 체력 x 100 / (X x 1인당 화력)
이라 N 이 약분된다. 그래서 분자를 키우면 모든 인원수에서 같은 비율로 쉬워지고,
3인 이상 구간의 설계(기본 18%, 타격자 3명이면 70%)가 함께 무너진다.
X=110 이면 18% 바닥은 N>=7 에서야 걸려, 3~6인 서버에서 "셋은 붙어야 한다"는
긴장이 사라진다.

## 그래서 완화를 3인 미만으로 가둔다

    Max(RatHitters >= 3 ? 70 : 18, RatPop >= 3 ? 0 : Divide(110, Max(1, RatPop)))

- 1명 -> 110% : 4000 / 1.10 = 3,636 -> 약 30초
- 2명 -> 55%  : 4000 / 0.55 = 7,273 을 둘이 나눠 -> 약 30초
- 3명 이상    -> 둘째 인자가 0 이 되어 **기존 설계 그대로** (18%, 타격자 3명이면 70% = 약 16초)

솔로·듀오는 30초짜리 카이팅 숙제가 되고(질주 165 로 쥐 130 을 뿌리치되 기력을 쓴다),
3인 이상은 손대지 않았다. 타격자 게이트의 보상(약 2배)도 그대로다.

## 인원 집계에 TutOn == 0 을 추가한다

기존 집계는 `Is Alive` 와 `Init == 1` 만 봤다. 튜토리얼 중인 사람은 싸울 수 없고
`[쥐 02]` 의 표적 필터도 `TutOn == 0` 을 요구하므로, 집계에 넣으면 쥐만 단단해진다.
표적 필터와 같은 기준으로 맞춘다.

전역 88: RatPop 신규 (집계식을 두 번 쓰지 않기 위해).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


# ── 전역 슬롯 ──────────────────────────────────────────────────
sub("""		87: RatKill
""", """		87: RatKill
		88: RatPop
""")

# ── 피해 배율 ──────────────────────────────────────────────────
sub(
    "		Set Damage Received(Event Player, Max(Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18,"
    " Divide(54, Max(1, Count Of(Filtered Array(All Players(Team 1),"
    " And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1)))))));",

    "		Set Global Variable(RatPop, Count Of(Filtered Array(All Players(Team 1),"
    " And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1),"
    " Player Variable(Current Array Element, TutOn) == 0))));\n"
    "		Set Damage Received(Event Player, Max(Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18,"
    " Global Variable(RatPop) >= 3 ? 0 : Divide(110, Max(1, Global Variable(RatPop)))));")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
