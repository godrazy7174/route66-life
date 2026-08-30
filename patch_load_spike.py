# -*- coding: utf-8 -*-
"""서버 강제 종료 재발 — 경고 없이 죽은 이유와 두 갈래 대책.

## 왜 경고문이 안 떴는가 — [코어 10] 은 이 크래시 유형을 구조적으로 못 잡는다

기존 [코어 10]:

    conditions:  Server Load() > 230;
    actions:     Wait(2, Abort When False);        <- 2초 내내 230 을 유지해야
                 Small Message("서버가 버겁다...")  <- 그제서야 자막

두 겹으로 못 잡는다.

1. `Server Load()` 는 **현재 순간값**이다. "과도하게 불러와" 강제 종료는
   프레임 하나가 스크립트 예산을 터뜨리는 **순간 스파이크**로도 일어나는데,
   그 프레임과 조건 평가 프레임이 겹칠 확률은 낮다.
2. 설령 걸려도 `Wait(2, Abort When False)` 가 2초 지속을 요구한다.
   스파이크로 즉사하는 서버는 그 2초를 채우기 전에 죽는다.

즉 "경고 없이 죽었다" 는 경고가 고장난 게 아니라 **크래시가 지속형이 아니라
스파이크형이라는 증거**다.

## 대책 1 — 스파이크의 가장 유력한 원인 제거: 전설의 야수 50배

`ref/actions.ts` 의 `startScalingSize`:

    "large players placed into complex environments will severely impact
     server load, so consider also applying the Disable Movement Collision
     With Environment action."

대야수(30배)에는 이미 걸었지만, **전설의 야수(50배)는 벽 충돌을 켠 채였다.**
50배 히트박스가 [직업 03-3] 배회의 무작위 throttle·점프·임펄스로 협곡 벽을
매 프레임 긁는다 — ref 가 명시한 바로 그 부하다. 발현 확률이 낮아(리롤당 0.4%)
"이따금, 경고 없이" 라는 재현 양상과도 맞는다.

50배를 세우는 곳에 `Disable Movement Collision With Environment(_, False)` 를 걸고
(includeFloors 는 False — 바닥까지 끄면 맵 아래로 떨어진다. 8-2 와 동일),
크기를 되돌리는 세 곳(리롤 Else · 은신 · 처치) 모두에서 Enable 로 복원한다.
2.4배 거대 야수는 그대로 둔다 — 그 크기는 문제 규모가 아니다.

## 대책 2 — 경고를 스파이크 감지형으로

`Server Load Peak()` 은 **최근 구간의 최고치**라 순간 스파이크가 지나간 뒤에도
값이 남는다. 조건을 Peak > 200 으로 바꾸고 2초 확인 대기를 없애 즉시 띄운다.
해제는 Peak < 170.

한계도 적어 둔다: 프레임 하나로 즉사하는 최악의 스파이크는 어떤 스크립트도
자막을 못 띄운다 (서버가 먼저 죽는다). 경고는 "죽기 직전까지 갔다 온" 스파이크를
잡는 조기 신호이고, 근본 대책은 위의 원인 제거다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:80], s.count(old))
    s = s.replace(old, new)


# ── 대책 1: 전설의 야수(50배) 벽 충돌 해제 ─────────────────────
sub("""				Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 50, False);""",
    """				Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 50, False);
				Disable Movement Collision With Environment(Value In Array(Event Player.Target, Event Player.Idx), False);""")

# 리롤에서 일반으로 돌아갈 때
sub("""				Set Max Health(Value In Array(Event Player.Target, Event Player.Idx), 35);
				Stop Scaling Player(Value In Array(Event Player.Target, Event Player.Idx));""",
    """				Set Max Health(Value In Array(Event Player.Target, Event Player.Idx), 35);
				Stop Scaling Player(Value In Array(Event Player.Target, Event Player.Idx));
				Enable Movement Collision With Environment(Value In Array(Event Player.Target, Event Player.Idx));""")

# 은신으로 돌아갈 때
sub("""			Set Respawn Max Time(Event Player, 4);
			Stop Scaling Player(Event Player);""",
    """			Set Respawn Max Time(Event Player, 4);
			Stop Scaling Player(Event Player);
			Enable Movement Collision With Environment(Event Player);""")

# 처치될 때
sub("""		Stop Scaling Player(Victim);""",
    """		Stop Scaling Player(Victim);
		Enable Movement Collision With Environment(Victim);""")

# ── 대책 2: 경고를 스파이크 감지형으로 ─────────────────────────
sub("""	conditions
	{
		Server Load() > 230;
	}

	actions
	{
		Wait(2, Abort When False);
		Small Message(All Players(All Teams), Custom String("서버가 버겁다 — 구역 감지를 잠시 늦춘다"));
		Wait Until(Server Load() < 190, 120);
		Small Message(All Players(All Teams), Custom String("서버가 다시 안정됐다"));
	}""",
    """	conditions
	{
		Server Load Peak() > 200;
	}

	actions
	{
		Small Message(All Players(All Teams), Custom String("서버가 버겁다 — 구역 감지를 잠시 늦춘다"));
		Wait Until(Server Load Peak() < 170, 120);
		Small Message(All Players(All Teams), Custom String("서버가 다시 안정됐다"));
		Wait(5, Ignore Condition);
	}""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
