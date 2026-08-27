"""레퍼런스('헬조선에서 살아남기' 실제 동작 코드)에서 확인한 사실을 반영한다.

1. 호위(5대5)는 팀당 최대 5명이라 6대6도 12대0도 거부된다.
   -> 연습 전투(Skirmish) + 1팀 12 / 2팀 0. 레퍼런스가 쓰는 검증된 구성.
2. 연습 전투에는 목표물이 없으므로 Objective Position을 앵커로 쓸 수 없다.
   -> 호스트 위치 기준 링 배치 + 설계자 모드로 확정.
3. HUD는 Local Player를 쓰면 텍스트 1개가 보는 사람마다 자기 값으로 렌더된다.
   -> 3개 x 12명 = 36개였던 것이 3개로. 128개 상한에 여유가 크게 생긴다.
4. Input Binding String(Button(...))으로 실제 키 표시.
5. 같은 팀이면 무기 피해가 안 들어가므로 PvP 총격은 조준각 판정 + Damage 액션으로.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 플레이어 변수 추가 (총격 대상) ────────────────────────────────
s = s.replace("\t\t28: Target\n", "\t\t28: Target\n\t\t29: ShotTgt\n")

# ── 2) 설정: 연습 전투 12대0 ─────────────────────────────────────────
s = s.replace("\t\tMax Team 1 Players: 6\n\t\tMax Team 2 Players: 6\n",
              "\t\tMax Team 1 Players: 12\n\t\tMax Team 2 Players: 0\n")
s = s.replace("\t\tEscort\n\t\t{\n\t\t\tEnable Perks: Off\n",
              "\t\tSkirmish\n\t\t{\n\t\t\tEnable Perks: Off\n")

# ── 3) 매치 타임 조작 제거 (연습 전투는 원래 무제한) ─────────────────
s = s.replace("""		Set Match Time(1);
		Wait Until(Is Game In Progress(), 60);
		Set Match Time(3600);
		Pause Match Time();
		Call Subroutine(BuildWorld);""",
"""		Wait Until(Is Game In Progress(), 30);
		Wait(2, Ignore Condition);
		Call Subroutine(BuildWorld);""")

# ── 4) 앵커: 목표물 -> 호스트 위치 기준 링 배치 ──────────────────────
old_anchor = s[s.index("\t\tSet Global Variable(Anchor, Array("):s.index("\t\tSet Global Variable(LocRad,")]
new_anchor = """		Set Global Variable(Anchor, Nearest Walkable Position(Position Of(Host Player())));
		Set Global Variable(LocPos, Empty Array);
		For Global Variable(Idx, 0, 8, 1);
			Modify Global Variable(LocPos, Append To Array, Nearest Walkable Position(Add(Global Variable(Anchor), Vector(Multiply(24, Cosine From Degrees(Multiply(Global Variable(Idx), 45))), 0, Multiply(24, Sine From Degrees(Multiply(Global Variable(Idx), 45)))))));
		End;
"""
s = s.replace(old_anchor, new_anchor)

# ── 5) HUD: Local Player 방식으로 전면 교체 ─────────────────────────
a = s.index('rule("[코어 08] BuildHud")')
b = s.index('rule("[월드 01] 시간 흐름")')
NEW_HUD = '''rule("[코어 08] 공용 HUD 생성")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Global Variable(Ready) == 1;
	}

	actions
	{
		Create HUD Text(Local Player, Custom String("{0}일차   {1}시   {2}", Global Variable(Day), Round To Integer(Divide(Global Variable(Clock), 60), Down), Value In Array(Array(Custom String("낮"), Custom String("밤")), Global Variable(IsNight))), Custom String("소지금   $ {0}", Local Player.Money), Custom String("{0}   Lv.{1}   평판 {2}", Value In Array(Array(Custom String("떠돌이"), Custom String("광부"), Custom String("사냥꾼"), Custom String("현상금 사냥꾼")), Local Player.Job), Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 100), Down)), Local Player.Rep), Left, 1, Color(Yellow), Color(Lime Green), Color(White), Visible To Sort Order String and Color, Default Visibility);
		Create HUD Text(Local Player, Custom String("허기 {0}   갈증 {1}   피로 {2}", Round To Integer(Local Player.Hunger, Down), Round To Integer(Local Player.Thirst, Down), Round To Integer(Local Player.Energy, Down)), Custom String("{0}      {1}", Custom String("육포 {0}", Value In Array(Local Player.Inv, 0)), Custom String("물통 {0}", Value In Array(Local Player.Inv, 1))), Custom String("{0}      {1}      {2}", Custom String("원석 {0}", Value In Array(Local Player.Inv, 2)), Custom String("가죽 {0}", Value In Array(Local Player.Inv, 3)), Custom String("현상금 $ {0}", Local Player.Bounty)), Left, 2, Color(Orange), Color(White), Color(Sky Blue), Visible To Sort Order String and Color, Default Visibility);
		Create HUD Text(Local Player, Value In Array(Array(Custom String("황야"), Custom String("시청 · 직업소개소"), Custom String("광산"), Custom String("식료품점"), Custom String("여관"), Custom String("잡화상"), Custom String("술집"), Custom String("사냥터"), Custom String("무법자 캠프")), Add(Local Player.Zone, 1)), Value In Array(Array(Custom String("행동 없음 — 마을로 이동하세요"), Custom String("-"), Custom String("-"), Custom String("-"), Custom String("전직: 광부"), Custom String("전직: 사냥꾼"), Custom String("전직: 현상금 사냥꾼"), Custom String("벌금 납부 $100 (현상금 제거)"), Custom String("채굴하기"), Custom String("정밀 탐사 $30"), Custom String("-"), Custom String("-"), Custom String("육포 구매 $15"), Custom String("물통 구매 $10"), Custom String("육포 5개 묶음 $65"), Custom String("-"), Custom String("숙박 $40 — 피로 완전 회복"), Custom String("-"), Custom String("-"), Custom String("-"), Custom String("원석 전량 판매"), Custom String("가죽 전량 판매"), Custom String("오늘의 시세 확인"), Custom String("-"), Custom String("위스키 $20 — 피로 회복"), Custom String("카드 도박 $50"), Custom String("소문 듣기"), Custom String("-"), Custom String("흔적 추적 — 사냥감 출현"), Custom String("-"), Custom String("-"), Custom String("-"), Custom String("현상금 게시판"), Custom String("-"), Custom String("-"), Custom String("-")), Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx)), Custom String("[{0}] 행동 선택    [{1}] 실행    [{2}] 보급품", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)), Input Binding String(Button(Melee))), Right, 1, Color(Aqua), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);
	}
}

'''
s = s[:a] + NEW_HUD + s[b:]

# BuildHud 호출과 퇴장 정리 규칙 제거
s = s.replace("\t\tCall Subroutine(BuildHud);\n", "")
s = s.replace("\t\tSet Player Variable(Event Player, HudIds, Empty Array);\n", "")
s = s.replace("\t\t2: BuildHud\n", "")

# ── 6) 키 안내를 실제 키 바인딩으로 ─────────────────────────────────
s = s.replace('Small Message(Event Player, Custom String("시청에서 직업을 고르세요.  [R] 선택  [F] 실행"));',
              'Small Message(Event Player, Custom String("시청에서 직업을 고르세요.  [{0}] 선택  [{1}] 실행", Input Binding String(Button(Reload)), Input Binding String(Button(Interact))));')
s = s.replace('Small Message(Event Player, Custom String("대상 없음 — 9m 안의 상대를 조준하세요"));',
              'Small Message(Event Player, Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Interact))));')

# ── 7) PvP 총격 (같은 팀이라 무기 피해가 안 들어감) ─────────────────
PVP = '''
rule("[범죄 03] 총격 판정 (플레이어)")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Event Player.Init == 1;
		Is Alive(Event Player) == True;
		Is Firing Primary(Event Player) == True;
	}

	actions
	{
		Set Player Variable(Event Player, ShotTgt, First Of(Sorted Array(Filtered Array(Players Within Radius(Eye Position(Event Player), 45, All Teams, Surfaces), And(Current Array Element != Event Player, And(Is Alive(Current Array Element), And(Player Variable(Current Array Element, Init) == 1, Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Eye Position(Current Array Element))) >= 0.995)))), Distance Between(Eye Position(Event Player), Eye Position(Current Array Element)))));
		If(Entity Exists(Event Player.ShotTgt));
			Damage(Event Player.ShotTgt, Event Player, 50);
			Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Eye Position(Event Player.ShotTgt), 0.4);
			Small Message(Event Player.ShotTgt, Custom String("{0}이(가) 당신을 쏘고 있다!", Event Player));
		End;
		Wait(0.5, Ignore Condition);
		Loop If(Is Firing Primary(Event Player));
	}
}

rule("[코어 10] 서버 부하 보호")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Server Load() > 230;
	}

	actions
	{
		Wait(2, Abort When False);
		Small Message(All Players(All Teams), Custom String("서버 부하가 높습니다 — 일부 처리를 늦춥니다"));
		Set Slow Motion(85);
		Wait Until(Server Load() < 190, 120);
		Set Slow Motion(100);
	}
}
'''
s = s.replace('\nrule("[생활 02] 사망 처리")', PVP + '\nrule("[생활 02] 사망 처리")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
for probe in ('Local Player', 'Input Binding String', 'Objective Position', 'BuildHud', 'ShotTgt', 'Skirmish'):
    print('  %-24s %d회' % (probe, s.count(probe)))
