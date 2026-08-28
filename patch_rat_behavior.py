# -*- coding: utf-8 -*-
"""쥐 행동 개편 (README 8-3) — 육포 우선 · 지속 · 인원 비례 난이도.

사용자 결정: 「쥐떼는 육포를 먼저 털고, 육포가 없으면 죽거나 사람을 잡을 때까지
안 사라진다. 솔로 소프트락을 막기 위해 인원수만큼 약해지게.」

개편 전 동작의 문제:

- [쥐 02] 가 사람을 먼저 쫓았다. 잡화점(LocPos[2]) 9m 안에 우연히 있을 때만 육포를 털어서,
  "쥐가 육포를 노린다"는 습격 문구가 실제 행동과 어긋났다.
- [쥐 01] 이 45초 뒤 무조건 철수했다. 아무도 대응하지 않아도 시간만 지나면 끝나서
  습격이 사건이 아니라 배경음이었다.
- [쥐 05] 의 Set Damage Received 가 타격자 수(RatHitters)에만 반응해서,
  혼자 있는 사람은 영원히 18% 벽을 때렸다 (3명 이상 조건을 혼자서는 못 만든다).

고친 것 — README 8-3 의 1~6 항목:

1. 육포 우선 ([쥐 02]).
   If(JerkyStock > 0) 이면 잡화점으로 직행하고, 가는 길에 3.5m 안에 있는 사람만 문다.
   Else If(표적 40m 안) 추격. Else 잡화점으로. 세 분기 어디도 비어 있지 않다
   (빈 Else 뒤 Else If 는 4장 4번 — 그 뒤가 영영 실행되지 않는다).
   같이 고친 것 둘:
   - 표적 필터에 Has Status(Current Array Element, Phased Out) == False 를 넣었다.
     4장 5번 정면 위반이었다 — Phased Out 은 무기 피해만 막고 스크립트 Damage() 는
     그대로 통과하므로, JailOn/TutOn 만으로는 취침 중인 사람이 물렸다.
   - 잡화점 복귀 순간이동과 약탈 이펙트를 JerkyStock > 0 으로 묶었다.
     안 묶으면 육포가 0 이 된 뒤에도 12틱마다 쥐가 잡화점으로 끌려가 사람 사냥이 끊기고,
     털 것이 없는데 주황 폭발만 매 초 터진다.

2. 지속 ([쥐 01]).
   Wait(45) 뒤에 If(And(And(RatOn == 1, JerkyStock == 0), RatKill == 0)) 게이트를 두고
   Wait Until(Or(RatOn == 0, RatKill == 1), 99999) 로 죽거나 사람을 잡을 때까지 남긴다.
   물러나지 않는다는 것을 Big Message 로 알린다.
   기존 45초 철수 경로는 JerkyStock > 0 일 때만 탄다.
   게이트에 RatKill == 0 을 넣은 이유: 쥐가 45초 이전에 이미 사람을 잡았으면
   Wait Until 이 즉시 반환되어 "물러나지 않는다" 와 철수 메시지가 같은 프레임에 겹친다.
   ref/actions.ts 의 waitUntil 은 "The rule conditions are ignored during this wait" 라
   룰 조건 재평가로 중단되지 않는다. Wait 과 달리 Ignore Condition 인자를 받지 않는다(2인자).

3. 중복 방지 — 코드 변경 없음. 확인만 하고 여기 문서로 남긴다.
   [쥐 01] 의 조건은 RatOn == 0 이고, 액션의 첫 줄이 Set Global Variable(RatOn, 1) 이다.
   RatOn 에 쓰는 곳은 파일 전체에 정확히 셋뿐이다 — [쥐 01] 시작(=1), [쥐 01] 철수(=0),
   [쥐 04] 퇴치(=0). 습격 중에는 조건이 항상 거짓이고 Ongoing 룰은 대기열이 없으므로
   다음 일정(RatNext)이 지나가도 그냥 건너뛴다. 지속 개편으로 습격이 몇 분씩 이어져도
   같은 이유로 두 번째 인스턴스는 뜨지 않는다.
   **다만 그것이 성립하는 진짜 이유는 타이밍이다.** RatOn 을 0 으로 되돌리는 두 지점 모두
   바로 다음 줄에서 RatNext 를 미래로 민다. 그 사이에 Wait 이 하나도 없기 때문에
   조건이 다시 참이 되는 프레임에는 이미 RatNext 가 미래다.
   아래 6번으로 죽은 RatNext 줄을 지운 뒤에도 이 불변식은 유지된다 —
   철수 블록의 End; 와 꼬리의 RatNext 사이에 Wait 을 끼우면 같은 프레임에 [쥐 01] 이
   재발동한다. 이 구간에는 절대 Wait 을 넣지 마라.

4. 인원 비례 난이도 ([쥐 05]).
   Set Damage Received 를
   Max(Count Of(RatHitters) >= 3 ? 70 : 18, Divide(54, Max(1, 접속 인원))) 로 바꾼다.
   1명 54% / 2명 27% / 3명 이상 18%(기존값 유지).
   README 8-3 은 이 공식을 "[쥐 03] 의 값" 이라고 적었지만 실제 Set Damage Received 는
   [쥐 05] 쥐떼의 가죽에 있다 — README 의 번호가 오기이고, 의도(피해 배율 공식)대로 [쥐 05] 를 고쳤다.
   접속 인원 표기는 이 파일의 기존 필터 표기(L1405/L3515/L6490)를 따랐다.
   README 의 축약형 And(Is Alive, Init == 1) 을 그대로 쓰면 임포트가 거부된다 —
   And 는 항상 2인자이고 Is Alive / Init 는 Current Array Element 를 명시해야 한다.

5. 신규 전역 87: RatKill, 신규 룰 [쥐 06] 쥐가 사람을 잡았다.
   Player Died / Team 1 이고 공격자가 Team 2 슬롯 3(쥐 봇)이면 RatKill = 1.
   습격 시작([쥐 01])에서 0 으로 초기화한다.
   Victim 에 Init == 1 을 요구해 더미 봇의 죽음은 세지 않는다 (4장 6번 — 봇은 Init 0,
   make_test_build.py 가 Team 1 슬롯 5~7 에 봇을 넣는다).
   공격자 판별을 Slot Of(Attacker) == 3 이 아니라
   Attacker == Players In Slot(3, Team 2) 로 쓴 것도 같은 이유다 —
   팀 구분 없는 슬롯 비교는 그 더미 봇들과 부딪힐 수 있다.

6. 죽은 코드 제거 ([쥐 01]).
   Set Global Variable(RatNext, Add(Total Time Elapsed(), 240)); 는 바로 아래에서
   Random Real(240, 600) 으로 덮어써지므로 지운다. 3번의 개편과 같은 앵커에서 처리한다.

전역 앵커는 8-2(대야수) 패치가 넣는 "86: HuntSwing" 이다. 8-2 를 먼저 적용해야 한다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:60], s.count(old))
    s = s.replace(old, new)


# ── 1. 전역 87: RatKill ────────────────────────────────────────
# 앵커는 8-2 패치가 넣는 마지막 슬롯이다. 중간 빈 슬롯(8/11/14/60/64)은 쓰지 않는다 —
# ArchOn(13) 재사용 금지와 같은 이유로 제거된 기능의 흔적일 가능성이 있다 (4-1장).
sub("""		86: HuntSwing
""", """		86: HuntSwing
		87: RatKill
""")

# ── 2. [쥐 01] 습격 시작 시 RatKill 초기화 ─────────────────────
sub("""		Set Global Variable(RatHitters, Empty Array);
""", """		Set Global Variable(RatHitters, Empty Array);
		Set Global Variable(RatKill, 0);
""")

# ── 3. [쥐 01] 지속 + 죽은 RatNext 240 제거 ────────────────────
# 세 갈래로 갈린다.
#  A. t+45 에 육포가 남아 있다 -> 기존 45초 철수 (육포 -15).
#  B. 육포가 0 이고 아직 아무도 못 잡았다 -> 경고 후 죽거나 사람을 잡을 때까지 버틴다.
#  C. 육포가 0 인데 이미 사람을 잡았다 -> 게이트를 건너뛰고 바로 철수. 메시지가 겹치지 않는다.
# 철수 문구는 어느 경로로 왔는지에 맞춘다. lint 의 fact_check 는 문구/행동 불일치를 못 잡는다.
sub("""		Wait(45, Ignore Condition);
		If(Global Variable(RatOn) == 1);
			Set Global Variable(RatOn, 0);
			Set Global Variable(RatNext, Add(Total Time Elapsed(), 240));
			Destroy Icon(Global Variable(RatFx));
			Set Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 15)));
			Big Message(All Players(All Teams), Custom String("쥐떼가 육포를 물고 달아났다 — 잡화점이 텅 비었다"));
			Destroy Dummy Bot(Team 2, 3);
		End;
""", """		Wait(45, Ignore Condition);
		If(And(And(Global Variable(RatOn) == 1, Global Variable(JerkyStock) == 0), Global Variable(RatKill) == 0));
			Big Message(All Players(All Teams), Custom String("육포가 바닥났다 — 쥐떼가 물러나지 않는다! 죽여야 끝난다"));
			Wait Until(Or(Global Variable(RatOn) == 0, Global Variable(RatKill) == 1), 99999);
		End;
		If(Global Variable(RatOn) == 1);
			Set Global Variable(RatOn, 0);
			Destroy Icon(Global Variable(RatFx));
			If(Global Variable(RatKill) == 1);
				Big Message(All Players(All Teams), Custom String("쥐떼가 사람을 물어 죽이고 물러갔다"));
			Else;
				Set Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 15)));
				Big Message(All Players(All Teams), Custom String("쥐떼가 육포를 물고 달아났다 — 잡화점에 육포 {0} 남았다", Global Variable(JerkyStock)));
			End;
			Destroy Dummy Bot(Team 2, 3);
		End;
""")

# ── 4. [쥐 02] 표적 필터에 Phased Out 제외 ─────────────────────
sub("""		Set Global Variable(RatTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Player Variable(Current Array Element, JailOn) == 0, Player Variable(Current Array Element, TutOn) == 0))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
""", """		Set Global Variable(RatTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Has Status(Current Array Element, Phased Out) == False, And(Player Variable(Current Array Element, JailOn) == 0, Player Variable(Current Array Element, TutOn) == 0)))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
""")

# ── 5. [쥐 02] 우선순위 역전 — 육포가 먼저다 ───────────────────
sub("""		If(And(Entity Exists(Global Variable(RatTgt)), Distance Between(Position Of(Global Variable(RatTgt)), Position Of(Event Player)) < 40));
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(RatTgt))), 1, To World, Replace existing throttle, None);
			If(Distance Between(Position Of(Event Player), Position Of(Global Variable(RatTgt))) < 3.5);
				Damage(Global Variable(RatTgt), Event Player, 20);
				Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1.5);
			End;
		Else;
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)), 1, To World, Replace existing throttle, None);
		End;
""", """		If(Global Variable(JerkyStock) > 0);
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
		End;
""")

# ── 6. [쥐 02] 약탈 판정과 잡화점 복귀를 육포가 남아 있을 때로 한정 ──
# 육포가 0 인데도 순간이동이 살아 있으면 12틱마다 쥐가 잡화점으로 끌려가 사람 사냥이 끊긴다.
sub("""		If(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) < 9);
			Set Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 2)));
			Play Effect(All Players(All Teams), Bad Explosion, Color(Orange), Position Of(Event Player), 1);
		End;
""", """		If(And(Global Variable(JerkyStock) > 0, Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) < 9));
			Set Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 2)));
			Play Effect(All Players(All Teams), Bad Explosion, Color(Orange), Position Of(Event Player), 1);
		End;
""")

sub("""		If(And(Modulo(Event Player.Roll, 12) == 0, Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) > 34));
""", """		If(And(Global Variable(JerkyStock) > 0, And(Modulo(Event Player.Roll, 12) == 0, Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) > 34)));
""")

# ── 7. [쥐 05] 인원 비례 피해 배율 ─────────────────────────────
sub("""		Set Damage Received(Event Player, Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18);
""", """		Set Damage Received(Event Player, Max(Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18, Divide(54, Max(1, Count Of(Filtered Array(All Players(Team 1), And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1)))))));
""")

# ── 8. [쥐 06] 쥐가 사람을 잡았다 ──────────────────────────────
sub("""rule("[쥐 04] 쥐떼 퇴치")""", """rule("[쥐 06] 쥐가 사람을 잡았다")
{
	event
	{
		Player Died;
		Team 1;
		All;
	}

	conditions
	{
		Global Variable(RatOn) == 1;
		Event Player.Init == 1;
		Entity Exists(Attacker) == True;
		Attacker == Players In Slot(3, Team 2);
	}

	actions
	{
		Set Global Variable(RatKill, 1);
	}
}

rule("[쥐 04] 쥐떼 퇴치")""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
