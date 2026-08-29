# -*- coding: utf-8 -*-
"""패치노트 1 — 쥐가 벽에 갈려 멈추고, 막힌 방향으로 계속 밀어붙이는 문제.

## 원인

`Start Throttle In Direction` 은 **길찾기가 없는 직선 돌진**이다. 벽이 있으면
그대로 밀어붙여 마찰로 속도가 죽고 사실상 정지한다. 왔다갔다 해야 닿는
복잡한 길에서는 영영 못 간다.

끼임 탈출이 있긴 했지만 `JerkyStock > 0` 일 때만, 그것도 12틱마다 잡화점에서
34m 넘게 떨어져 있을 때만 걸렸다. **플레이어를 쫓는 동안에는 탈출 수단이 아예 없었다.**

## 두 갈래로 고친다 (지시: "이동 메커니즘 개선 또는 스폰 지점 변경")

**1) 스폰 지점을 협곡 개활지에서 잡화점으로 옮긴다.**
쥐의 목적지는 잡화점(`LocPos[2]`)인데 스폰은 맵 반대편 협곡 개활지(`LocPos[6]`)였다.
그 횡단 구간이 끼임의 대부분이다. 털러 온 곳에서 시작하게 하면 원인 자체가 줄고,
"쥐떼가 잡화점에 몰려왔다"가 연출로도 자연스럽다.

**2) 끼임 감지를 대야수와 같은 방식으로, 두 갈래 모두에 넣는다.**
1초마다 위치를 `RatLast` 와 비교해 1m 미만 이동이 3틱(3초) 이어지고 목적지가
6m 밖이면, **목적지에서 가장 가까운 `SpotPos` 검증 지점**으로 순간이동시킨다.
좌표를 계산하지 않는다는 4장 1번을 지키는 방법이고, `[대사냥 06]` 과 같은 패턴이다.

목적지를 `RatGoal` 하나로 모아 이동·끼임 판정이 같은 값을 보게 했다.
기존에는 세 갈래(육포/추격/기본)가 각자 `Start Throttle` 을 불러 중복이 많았다.

## 정리한 것

`Roll` 을 쓰던 12틱 순간이동은 새 끼임 감지가 대체하므로 지웠다.
그러면 `[쥐 01]` 의 `Roll = 0` 초기화도 고아가 되어 함께 지운다
(`Roll` 은 다른 활동과 겸용이라 슬롯 자체는 그대로 둔다 — 4장 16번).

## 함정

`RatLast`·`RatStuck` 초기화는 **`[쥐 01]` 스폰 블록에** 둔다.
`Loop If` 는 액션 목록을 처음부터 다시 돌기 때문에(4장 17번) 루프 안에 두면 매 틱 리셋된다.

전역 92: RatGoal, 93: RatLast, 94: RatStuck.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


# ── 전역 ───────────────────────────────────────────────────────
sub("""		91: FirePos
""", """		91: FirePos
		92: RatGoal
		93: RatLast
		94: RatStuck
""")

# ── 1) 스폰을 잡화점으로 + 끼임 카운터 초기화 ──────────────────
sub("		Create Dummy Bot(Hero(Wrecking Ball), Team 2, 3,"
    " Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6),"
    " Vector(Random Real(-6, 6), 0, Random Real(-6, 6)))), Vector(1, 0, 0));",
    "		Create Dummy Bot(Hero(Wrecking Ball), Team 2, 3,"
    " Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 2),"
    " Vector(Random Real(-7, 7), 0, Random Real(-7, 7)))), Vector(1, 0, 0));")

sub("		Set Player Variable(Players In Slot(3, Team 2), Roll, 0);\n",
    "		Set Global Variable(RatLast, Position Of(Players In Slot(3, Team 2)));\n"
    "		Set Global Variable(RatStuck, 0);\n")

# ── 2) 이동을 목적지 하나로 모으고 끼임 감지를 붙인다 ──────────
old_move = """		If(Global Variable(JerkyStock) > 0);
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)), 1, To World, Replace existing throttle, None);
			If(And(Entity Exists(Global Variable(RatTgt)), Distance Between(Position Of(Event Player), Position Of(Global Variable(RatTgt))) < 3.5));
				Damage(Global Variable(RatTgt), Event Player, 20);
				Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1.5);
			End;
		Else If(And(Entity Exists(Global Variable(RatTgt)), Distance Between(Position Of(Global Variable(RatTgt)), Position Of(Event Player)) < 40));
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(RatTgt))), 1, To World, Replace existing throttle, None);
			If(Distance Between(Position Of(Event Player), Position Of(Global Variable(RatTgt))) < 3.5);
				Damage(Global Variable(RatTgt), Event Player, 20);
				Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1.5);
			End;
		Else;
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)), 1, To World, Replace existing throttle, None);
		End;"""

new_move = """		If(Or(Global Variable(JerkyStock) > 0, Not(Entity Exists(Global Variable(RatTgt)))));
			Set Global Variable(RatGoal, Value In Array(Global Variable(LocPos), 2));
		Else;
			Set Global Variable(RatGoal, Position Of(Global Variable(RatTgt)));
		End;
		Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Global Variable(RatGoal)), 1, To World, Replace existing throttle, None);
		If(And(Entity Exists(Global Variable(RatTgt)), Distance Between(Position Of(Event Player), Position Of(Global Variable(RatTgt))) < 3.5));
			Damage(Global Variable(RatTgt), Event Player, 20);
			Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1.5);
		End;"""

sub(old_move, new_move)

# ── 낡은 12틱 순간이동을 끼임 감지로 교체 ──────────────────────
sub("""		Modify Player Variable(Event Player, Roll, Add, 1);
		If(And(Global Variable(JerkyStock) > 0, And(Modulo(Event Player.Roll, 12) == 0, Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) > 34)));
			Teleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 2), Vector(Random Real(-5, 5), 0, Random Real(-5, 5)))));
		End;""",
    """		If(Distance Between(Position Of(Event Player), Global Variable(RatLast)) < 1);
			Modify Global Variable(RatStuck, Add, 1);
		Else;
			Set Global Variable(RatStuck, 0);
		End;
		Set Global Variable(RatLast, Position Of(Event Player));
		If(And(Global Variable(RatStuck) >= 3, Distance Between(Position Of(Event Player), Global Variable(RatGoal)) > 6));
			Set Global Variable(RatStuck, 0);
			Teleport(Event Player, First Of(Sorted Array(Global Variable(SpotPos), Distance Between(Current Array Element, Global Variable(RatGoal)))));
			Set Global Variable(RatLast, Position Of(Event Player));
			Play Effect(All Players(All Teams), Bad Explosion, Color(Orange), Position Of(Event Player), 2);
		End;""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
