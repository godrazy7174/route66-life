# -*- coding: utf-8 -*-
"""깨꾸 「서버부하 줄이기」(youtu.be/X5dPpNwlOaQ) 대조 적용 — 크래시 대책 2차.

영상의 핵심 주장 (자막 전문 검토, 시각은 영상 기준):

  * 03:03 — "서버 로드율이 높다고 꼭 터지는 것도, 낮다고 안 터지는 것도 아니다.
    로드율에 영향을 주는 건 액션·시각 효과고, **과부하는 주로 컨디션에서 발생한다**
    (컨디션은 지속적으로 값을 비교하므로)."
    -> 우리 [코어 10] 경고(Server Load Peak 기반)는 조기 신호일 뿐, 컨디션 쪽
       과부하는 측정으로 안 보인다. 측정 대기를 풀고 컨디션 쪽을 지금 고친다.
  * 04:33 — 조건은 위에서부터 검사하고, 위가 거짓이면 아래는 계산조차 안 한다.
    싸고 드물게 참인 조건을 위로.
  * 05:06 — Ray Cast·Entity Exists·배열 함수(Filtered/Sorted/Value In Array...)는
    비싸다. 특히 매 프레임 값이 변하는 피연산자(Position Of)가 든 조건이 문제.
  * 09:23 — Start Throttle In Direction 을 수시로 재호출하지 마라. "자동차도 출발할
    때 기름이 많이 든다." 방향 인자에 변수를 넣고 재평가(Direction and Magnitude)로
    한 번만 걸어라. 더미 봇 이동의 대표적 함정.

## 이번에 고치는 것

### 1. [기금 02] 모닥불 곁 — 조건에서 Nearest Walkable Position 이 매 프레임 돌았다

조건의 `Distance(pos, NWP(고정 좌표 중점)) < 8` 은 **상수 좌표에 대한 경로 탐색을
플레이어마다 매 프레임** 수행한다 (FundTier >= 1 이후 영구히, 액션에서도 2번 더).
솔로·평상시에도 도는 비용이라 "아무 일도 없을 때 터진다"와 정합한다.
월드 구축 때 `CampPos` 로 한 번만 계산하고 전부 치환한다. TrainPos 와 같은 패턴.

### 2. Start Throttle 재호출 3곳 -> 재평가 1회 호출

- [직업 03-3] 야수 배회: 0.35~0.9초마다 재호출 x 드러난 야수 최대 3 — **두 크래시
  모두 사냥이 진행 중이었다**는 제보와 정합하는 유일한 활동 코드다.
- [쥐 02]: 1초마다 재호출.
- [대사냥 06]: 0.5초마다 재호출 + 표적 없으면 Stop, 다시 Start 반복.

세 곳 모두: 목표 좌표 변수(HuntGoal/RatGoal/DialTgt)를 향한 방향을
`Direction and Magnitude` 재평가로 **한 번만** 걸고, 틱마다 좌표 변수만 갱신한다.
루프는 Loop If(액션 목록 전체 재실행) 대신 While 로 바꿔 Start 가 루프 밖에 있게 한다.
[대사냥 06]의 Set Move Speed(115)도 틱마다 -> 진입 시 1회로 옮긴다.

배회의 목표 변수는 DialTgt 겸용 — 인간 전용 변수라 2팀 봇에서는 비어 있다(4장 16번).
배회 텔레포트 직후에는 DialTgt 를 제 위치로 되돌려 낡은 목표로 튀어나가지 않게 한다.

### 3. 조건 순서 — 버튼(싸고 드물게 참)을 Distance(매 프레임 재평가) 위로

- [조작 03a~f]: Or(Distance...) 3줄이 버튼 검사보다 위에 있어, F 를 안 눌러도
  매 프레임 거리 3개를 계산했다. 버튼 2줄을 위로 (같은 조건 블록 6곳).
- F 홀드 룰 6곳([열차 01/03]·[밀수 02]·[호송 02]·[대사냥 02]·[밤 02]):
  Distance 줄과 버튼 2줄의 순서를 맞바꾼다.

조건은 전부 AND 라 순서는 발동 의미에 영향이 없다 — 계산량만 줄어든다.

전역 95: HuntGoal, 96: CampPos.
"""
import io
import re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:80], s.count(old))
    s = s.replace(old, new)


# ── 전역 ───────────────────────────────────────────────────────
sub("""		94: RatStuck
""", """		94: RatStuck
		95: HuntGoal
		96: CampPos
""")

# ── 1. CampPos 승격 ────────────────────────────────────────────
NWP_CAMP = ("Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 0),"
            " Value In Array(Global Variable(LocPos), 11)), 0.5))")
sub(NWP_CAMP, "Global Variable(CampPos)", 8)
sub("		Set Global Variable(TrainPos, Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 11), Value In Array(Global Variable(LocPos), 6)), 0.5)));\n",
    "		Set Global Variable(TrainPos, Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 11), Value In Array(Global Variable(LocPos), 6)), 0.5)));\n"
    "		Set Global Variable(CampPos, " + NWP_CAMP + ");\n")

# ── 2-1. [직업 03-3] 배회 — While + 재평가 스로틀 ──────────────
sub("""		If(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 6)) > 11);
			Teleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-4, 4), 0, Random Real(-4, 4)))));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 1);
			Wait(0.2, Ignore Condition);
		Else;
			Set Move Speed(Event Player, Random Integer(1, 100) <= 35 ? Random Integer(175, 215) : Random Integer(110, 148));
			Set Jump Vertical Speed(Event Player, Random Integer(100, 250));
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-7, 7), 0, Random Real(-7, 7))))), 1, To World, Replace existing throttle, None);
			Set Facing(Event Player, Vector(Random Real(-1, 1), Random Real(-0.6, 0.6), Random Real(-1, 1)), To World);
			If(Random Integer(1, 100) <= 8);
				Press Button(Event Player, Button(Jump));
			End;
			If(Random Integer(1, 100) <= 12);
				Apply Impulse(Event Player, Vector(Random Real(-1, 1), Random Real(0.8, 1.5), Random Real(-1, 1)), Random Real(9, 16), To World, Cancel Contrary Motion);
			End;
			Wait(Random Real(0.35, 0.9), Ignore Condition);
		End;
		Loop If(And(Event Player.RevealEnd > Total Time Elapsed(), Event Player != Global Variable(HuntBeast)));
		Stop Throttle In Direction(Event Player);""",
    """		Set Player Variable(Event Player, DialTgt, Position Of(Event Player));
		Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Event Player.DialTgt), 1, To World, Replace existing throttle, Direction and Magnitude);
		While(And(Event Player.RevealEnd > Total Time Elapsed(), Event Player != Global Variable(HuntBeast)));
			If(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 6)) > 11);
				Teleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-4, 4), 0, Random Real(-4, 4)))));
				Set Player Variable(Event Player, DialTgt, Position Of(Event Player));
				Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 1);
				Wait(0.2, Ignore Condition);
			Else;
				Set Move Speed(Event Player, Random Integer(1, 100) <= 35 ? Random Integer(175, 215) : Random Integer(110, 148));
				Set Jump Vertical Speed(Event Player, Random Integer(100, 250));
				Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-7, 7), 0, Random Real(-7, 7)))));
				Set Facing(Event Player, Vector(Random Real(-1, 1), Random Real(-0.6, 0.6), Random Real(-1, 1)), To World);
				If(Random Integer(1, 100) <= 8);
					Press Button(Event Player, Button(Jump));
				End;
				If(Random Integer(1, 100) <= 12);
					Apply Impulse(Event Player, Vector(Random Real(-1, 1), Random Real(0.8, 1.5), Random Real(-1, 1)), Random Real(9, 16), To World, Cancel Contrary Motion);
				End;
				Wait(Random Real(0.35, 0.9), Ignore Condition);
			End;
		End;
		Stop Throttle In Direction(Event Player);""")

# ── 2-2. [쥐 02] — While + 재평가 스로틀 ───────────────────────
sub("""		Set Global Variable(RatTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Has Status(Current Array Element, Phased Out) == False, And(Player Variable(Current Array Element, JailOn) == 0, Player Variable(Current Array Element, TutOn) == 0)))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));""",
    """		Set Global Variable(RatGoal, Position Of(Event Player));
		Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Global Variable(RatGoal)), 1, To World, Replace existing throttle, Direction and Magnitude);
		While(And(Global Variable(RatOn) == 1, Is Alive(Event Player)));
		Set Global Variable(RatTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Has Status(Current Array Element, Phased Out) == False, And(Player Variable(Current Array Element, JailOn) == 0, Player Variable(Current Array Element, TutOn) == 0)))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));""")
sub("""		Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Global Variable(RatGoal)), 1, To World, Replace existing throttle, None);
""", "")
sub("""		Wait(1, Ignore Condition);
		Loop If(And(Global Variable(RatOn) == 1, Is Alive(Event Player)));
	}""",
    """		Wait(1, Ignore Condition);
		End;
		Stop Throttle In Direction(Event Player);
	}""")

# ── 2-3. [대사냥 06] — While + 재평가 스로틀 + 속도 1회 ────────
sub("""		Set Global Variable(HuntTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Player Variable(Current Array Element, TutOn) == 0, Has Status(Current Array Element, Phased Out) == False))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
		Set Move Speed(Event Player, 115);
		If(Entity Exists(Global Variable(HuntTgt)));
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(HuntTgt))), 1, To World, Replace existing throttle, None);
			Set Facing(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(HuntTgt))), To World);""",
    """		Set Global Variable(HuntGoal, Position Of(Event Player));
		Set Move Speed(Event Player, 115);
		Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Global Variable(HuntGoal)), 1, To World, Replace existing throttle, Direction and Magnitude);
		While(And(Global Variable(HuntPhase) == 4, And(Is Alive(Event Player), Event Player == Global Variable(HuntBeast))));
		Set Global Variable(HuntTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Player Variable(Current Array Element, TutOn) == 0, Has Status(Current Array Element, Phased Out) == False))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
		If(Entity Exists(Global Variable(HuntTgt)));
			Set Global Variable(HuntGoal, Position Of(Global Variable(HuntTgt)));
			Set Facing(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(HuntTgt))), To World);""")
sub("""		Else;
			Stop Throttle In Direction(Event Player);
		End;
		If(And(Entity Exists(Global Variable(HuntTgt)), Distance Between(Position Of(Event Player), Global Variable(HuntLast)) < 1.5));""",
    """		Else;
			Set Global Variable(HuntGoal, Position Of(Event Player));
		End;
		If(And(Entity Exists(Global Variable(HuntTgt)), Distance Between(Position Of(Event Player), Global Variable(HuntLast)) < 1.5));""")
sub("""		Wait(0.5, Ignore Condition);
		Loop If(And(Global Variable(HuntPhase) == 4, And(Is Alive(Event Player), Event Player == Global Variable(HuntBeast))));
		Stop Throttle In Direction(Event Player);""",
    """		Wait(0.5, Ignore Condition);
		End;
		Stop Throttle In Direction(Event Player);""")

# ── 3-1. [조작 03a~f] 조건 순서 (동일 블록 6곳) ────────────────
sub("""		Is Alive(Event Player) == True;
		Global Variable(ArchOn) == 0;
		Or(Event Player.Escort == 0, Distance Between(Position Of(Event Player), Event Player.EscortPos) >= 4) == True;
		Or(Global Variable(WagonOn) == 0, Distance Between(Position Of(Event Player), Global Variable(WagonPos)) >= 4) == True;
		Or(Global Variable(HuntPhase) != 1, Distance Between(Position Of(Event Player), Global Variable(HuntTrackPos)) >= 5) == True;
		Is Button Held(Event Player, Button(Crouch)) == False;
		Is Button Held(Event Player, Button(Interact)) == True;""",
    """		Is Alive(Event Player) == True;
		Is Button Held(Event Player, Button(Interact)) == True;
		Is Button Held(Event Player, Button(Crouch)) == False;
		Global Variable(ArchOn) == 0;
		Or(Event Player.Escort == 0, Distance Between(Position Of(Event Player), Event Player.EscortPos) >= 4) == True;
		Or(Global Variable(WagonOn) == 0, Distance Between(Position Of(Event Player), Global Variable(WagonPos)) >= 4) == True;
		Or(Global Variable(HuntPhase) != 1, Distance Between(Position Of(Event Player), Global Variable(HuntTrackPos)) >= 5) == True;""", 6)

# ── 3-2. F 홀드 룰 — Distance 와 버튼 2줄 맞바꿈 ───────────────
pat = re.compile(
    r'(\t\tDistance Between\(Position Of\(Event Player\)[^\n]*;\n)'
    r'(\t\tIs Button Held\(Event Player, Button\(Crouch\)\) == False;\n'
    r'\t\tIs Button Held\(Event Player, Button\(Interact\)\) == True;\n)')
s, n = pat.subn(lambda m: m.group(2) + m.group(1), s)
assert n == 6, n  # 열차 01/03, 밀수 02, 호송 02, 대사냥 02, 밤 02

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok (조건 교환 %d곳)' % n)
