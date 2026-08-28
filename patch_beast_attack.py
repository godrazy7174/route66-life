# -*- coding: utf-8 -*-
"""대야수가 플레이어를 공격하게 한다 (README 8-2) — "깨워도 아무것도 안 한다"의 제거.

현재 `[대사냥 02]` 는 Team 2 슬롯 0~2 봇 하나를 `HuntBeast` 로 잡아 8000 체력 풀을 붙이고
`Start Scaling Player(..., 30, False)` 로 30배 크기를 만들지만, **공격 수단이 전혀 없다.**
움직임은 `[직업 03-3] 야수 배회` 의 무작위 배회뿐이라, 대야수는 개활지를 어슬렁거리는
거대한 과녁일 뿐이다. 사용자의 요청은 「추격 + 근접 강타」와 「장애물에 걸릴 때의 해결책」이다.

고친 것은 다섯이다.

1. **`[직업 03-3]` 조건에 `Event Player != Global Variable(HuntBeast);` 추가.**
   안 하면 배회 룰과 새 추격 룰이 같은 봇에 throttle 을 걸고 싸우며,
   11m 리쉬 때문에 대야수가 개활지 밖으로 한 발도 못 나간다.
   사냥이 끝나면 `HuntBeast` 는 Null 이 되므로 평소 야수 3마리는 영향이 없다.

2. **`[대사냥 06] 대야수의 추격과 강타`** 신규 룰.
   `All Players(Team 1)` 중 살아 있고 `Init == 1` · `TutOn == 0` 이며
   **`Has Status(..., Phased Out) == False`** 인 사람 중 최근접을 `HuntTgt` 로 잡는다.
   Phased Out 제외는 README 4장 5번 — 스크립트 `Damage` 는 Phased Out 을 뚫으므로
   빼먹으면 튜토리얼·유치장·취침 중인 사람이 55 씩 맞는다.
   `Start Throttle In Direction` + `Set Facing` 으로 쫓고 `Set Move Speed` 115
   (걷기 100 보다 빠르고 질주 165 보다 느리다 — 질주로 도망칠 여지를 남긴다).
   사거리 안이면 `Damage(HuntTgt, Event Player, 55)`, `HuntSwing` 타임스탬프로 1.6초 간격.
   **사거리 25m 는 30배 크기를 감안한 시작값이고 실기 조정 전제다** — 모델이 거대해
   발밑에 서 있어도 중심까지의 거리가 멀다. 같은 25 가 강타 판정과 끼임 순간이동 조건
   양쪽에 들어가므로 조정할 때는 두 곳을 같이 고쳐야 한다 (정적 검사로는 안 잡힌다).

3. **장애물 해법 — 두 겹.**
   (a) `ref/actions.ts` 의 `startScalingSize` 설명이 못박고 있다:
       "large players placed into complex environments will severely impact server load,
        so consider also applying the Disable Movement Collision With Environment action."
       그래서 각성 시 `Disable Movement Collision With Environment(HuntBeast, False)`,
       토벌(`[대사냥 04]`)과 밤 종료(`[대사냥 05]`)에서 `Enable ...` 로 되돌린다.
       **2번째 인자 includeFloors 는 반드시 False** — True 면 바닥까지 뚫려 맵 아래로 떨어진다.
       `[대사냥 05]` 의 복구는 `Set Global Variable(HuntBeast, Null)` 보다 **위**,
       `If(HuntPhase == 4)` 분기 안에 둔다. 아래에 두면 Null 에 액션을 거는 셈이라
       조용히 아무 일도 안 일어나고 봇이 벽을 통과한 채 다음 사냥까지 남는다.
   (b) 끼임 감지 — 0.5초마다 위치를 `HuntLast` 에 적어 1.5m 미만 이동이 6틱(3초) 이어지고
       표적이 사거리 밖이면, **표적에서 가장 가까운 `SpotPos` 검증 지점**으로 순간이동시킨다.
       좌표를 계산하지 않는다는 README 4장 1번 원칙을 지키는 유일한 방법이다
       (오프셋을 더하면 협곡에서는 허공이나 절벽 안으로 간다).
       붉은 Ring Explosion + 티커 「대야수가 길을 질러 나타났다」로 덮어 글리치로 안 보이게 한다.

4. **`Loop If` 는 액션 목록을 처음부터 다시 돌린다.**
   그래서 `HuntStuck` · `HuntLast` 초기화를 액션 맨 위에 두면 매 틱 리셋되어
   끼임 감지가 통째로 죽는다. 초기화는 전부 `[대사냥 02]` 의 각성 블록에 둔다.
   그 안에서도 **Teleport 다음**이어야 한다 — `Set Global Variable(HuntPhase, 4)` 줄 옆에
   두면 순간이동 전 좌표가 `HuntLast` 에 박혀 발현 직후 3초 동안 끼임으로 오판하고
   곧바로 SpotPos 순간이동이 터진다.

5. 신규 전역 4개: 83: HuntTgt · 84: HuntLast · 85: HuntStuck · 86: HuntSwing.
   플레이어 변수 128칸은 꽉 찼지만 대야수는 하나뿐이라 전역으로 충분하다.
   `82: TrainWay` 뒤에 append 한다 — 빈 인덱스(8·11·14·60·64)나 `ArchOn` 옆을
   재활용하지 않는다 (README 4-1장).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:60], s.count(old))
    s = s.replace(old, new)


# ── 1. 전역 슬롯 4개 추가 ──────────────────────────────────────
sub("""		82: TrainWay
""", """		82: TrainWay
		83: HuntTgt
		84: HuntLast
		85: HuntStuck
		86: HuntSwing
""")

# ── 2. [직업 03-3] 배회에서 대야수를 뺀다 ──────────────────────
# 룰 이름까지 붙여야 유일해진다 — [직업 03-4] 야수 위치 표시의 event·conditions
# 블록이 바이트 단위로 완전히 같아서, conditions 꼬리만으로는 2회 잡힌다.
sub("""rule("[직업 03-3] 야수 배회")
{
	event
	{
		Ongoing - Each Player;
		Team 2;
		All;
	}

	conditions
	{
		Is Dummy Bot(Event Player) == True;
		Global Variable(Ready) == 1;
		Is Alive(Event Player) == True;
		Event Player.RevealEnd > Total Time Elapsed();
		Slot Of(Event Player) <= 2;
	}
""", """rule("[직업 03-3] 야수 배회")
{
	event
	{
		Ongoing - Each Player;
		Team 2;
		All;
	}

	conditions
	{
		Is Dummy Bot(Event Player) == True;
		Global Variable(Ready) == 1;
		Is Alive(Event Player) == True;
		Event Player.RevealEnd > Total Time Elapsed();
		Slot Of(Event Player) <= 2;
		Event Player != Global Variable(HuntBeast);
	}
""")

# 조건만으로는 이미 돌고 있던 배회 인스턴스를 못 끊는다.
# ref/actions.ts 의 __loopIf__ 는 "Restarts the action list from the beginning if
# **this action's condition** evaluates to true" — 룰 조건 목록을 다시 보지 않는다
# (재평가하는 것은 별개 액션 __loopIfConditionIsTrue__ 다). 게다가 이 룰의 대기는
# 전부 Ignore Condition 이라 "the wait will not be interrupted" 다.
#
# 도달 경로가 실제로 있다: [직업 02] DoHunt 의 Abort 가드는 HuntPhase == 4 일 때만
# 걸리므로 흔적 조사 단계(1~3)에서는 정상 사냥이 되고, 그때 슬롯 0~2 봇 전부에
# RevealEnd = +50 이 붙어 배회 루프가 돈다. 그 50초 안에 3번째 흔적을 조사하면
# [대사냥 02] 가 RevealEnd 를 보지 않고 그 봇을 HuntBeast 로 집고, 곧바로
# RevealEnd 를 +9999 로 덮으므로 배회 루프가 영원히 산다.
# 그러면 배회의 11m 리쉬 Teleport 와 무작위 throttle 이 [대사냥 06] 의 추격과
# 매 틱 싸운다 — 8-2 1번이 막으려던 바로 그 증상이다.
sub("""		Loop If(Event Player.RevealEnd > Total Time Elapsed());
		Stop Throttle In Direction(Event Player);""",
    """		Loop If(And(Event Player.RevealEnd > Total Time Elapsed(), Event Player != Global Variable(HuntBeast)));
		Stop Throttle In Direction(Event Player);""")

# ── 3. [대사냥 02] 각성 — 충돌 해제 + 추격 상태 초기화 ─────────
# 각성 블록의 마지막 줄(Explosion Sound) 뒤. Teleport 다음이라
# HuntLast 에 실제 발현 좌표가 들어간다 (docstring 4번).
sub("""				Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(Global Variable(HuntBeast)), 300);
""", """				Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(Global Variable(HuntBeast)), 300);
				Disable Movement Collision With Environment(Global Variable(HuntBeast), False);
				Set Global Variable(HuntTgt, Null);
				Set Global Variable(HuntLast, Position Of(Global Variable(HuntBeast)));
				Set Global Variable(HuntStuck, 0);
				Set Global Variable(HuntSwing, Total Time Elapsed());
""")

# ── 4. [대사냥 04] 토벌 — 충돌 복구 ────────────────────────────
# 꼬리 3줄 + 닫는 '}' 까지 붙여야 유일하다. 각 줄은 단독으로는 2회씩 등장한다
# ([직업 03-2] 야수 처치의 RevealEnd 0, [대사냥 05] 의 HuntBeast Null).
sub("""		Set Player Variable(Victim, RevealEnd, 0);
		Set Player Variable(All Players(All Teams), HuntDmg, 0);
		Set Global Variable(HuntBeast, Null);
	}
""", """		Enable Movement Collision With Environment(Victim);
		Set Player Variable(Victim, RevealEnd, 0);
		Set Player Variable(All Players(All Teams), HuntDmg, 0);
		Set Global Variable(HuntBeast, Null);
	}
""")

# ── 5. [대사냥 05] 밤 정리 — 충돌 복구 ─────────────────────────
# 반드시 If(HuntPhase == 4) 분기 안. 아래쪽 HuntBeast Null 뒤에 넣으면
# Null 에 액션을 거는 셈이 되어 조용히 무효가 된다.
sub("""		If(Global Variable(HuntPhase) == 4);
			Set Player Variable(Global Variable(HuntBeast), RevealEnd, 0);
		Else;
""", """		If(Global Variable(HuntPhase) == 4);
			Set Player Variable(Global Variable(HuntBeast), RevealEnd, 0);
			Enable Movement Collision With Environment(Global Variable(HuntBeast));
		Else;
""")

# ── 6. [대사냥 06] 추격과 강타 신규 룰 ─────────────────────────
# [대사냥 05] 바로 다음 룰([목장 02]) 앞에 끼워 대사냥 01~06 을 한 덩어리로 둔다.
sub("""rule("[목장 02] 소가 다 컸다")""",
    """rule("[대사냥 06] 대야수의 추격과 강타")
{
	event
	{
		Ongoing - Each Player;
		Team 2;
		All;
	}

	conditions
	{
		Global Variable(HuntPhase) == 4;
		Event Player == Global Variable(HuntBeast);
		Is Alive(Event Player) == True;
	}

	actions
	{
		Set Global Variable(HuntTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Player Variable(Current Array Element, TutOn) == 0, Has Status(Current Array Element, Phased Out) == False))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
		Set Move Speed(Event Player, 115);
		If(Entity Exists(Global Variable(HuntTgt)));
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(HuntTgt))), 1, To World, Replace existing throttle, None);
			Set Facing(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(HuntTgt))), To World);
			If(And(Distance Between(Position Of(Event Player), Position Of(Global Variable(HuntTgt))) <= 25, Total Time Elapsed() >= Global Variable(HuntSwing)));
				Damage(Global Variable(HuntTgt), Event Player, 55);
				Set Global Variable(HuntSwing, Add(Total Time Elapsed(), 1.6));
				Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Global Variable(HuntTgt)), 3);
				Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(Global Variable(HuntTgt)), 120);
			End;
		Else;
			Stop Throttle In Direction(Event Player);
		End;
		If(And(Entity Exists(Global Variable(HuntTgt)), Distance Between(Position Of(Event Player), Global Variable(HuntLast)) < 1.5));
			Modify Global Variable(HuntStuck, Add, 1);
		Else;
			Set Global Variable(HuntStuck, 0);
		End;
		Set Global Variable(HuntLast, Position Of(Event Player));
		If(And(Global Variable(HuntStuck) >= 6, And(Entity Exists(Global Variable(HuntTgt)), Distance Between(Position Of(Event Player), Position Of(Global Variable(HuntTgt))) > 25)));
			Teleport(Event Player, First Of(Sorted Array(Global Variable(SpotPos), Distance Between(Current Array Element, Position Of(Global Variable(HuntTgt))))));
			Set Global Variable(HuntStuck, 0);
			Set Global Variable(HuntLast, Position Of(Event Player));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Event Player), 12);
			Set Global Variable(TickerMsg, Custom String("대야수가 길을 질러 나타났다"));
			Set Global Variable(TickerEnd, Add(Total Time Elapsed(), 3));
		End;
		Wait(0.5, Ignore Condition);
		Loop If(And(Global Variable(HuntPhase) == 4, And(Is Alive(Event Player), Event Player == Global Variable(HuntBeast))));
		Stop Throttle In Direction(Event Player);
	}
}

rule("[목장 02] 소가 다 컸다")""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
