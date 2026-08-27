"""더미 봇 무법자를 스크립트 표적으로 교체한다.

이유: 오버워치 로비 총원 상한이 12명이라 '12인 + 봇 5기'(17)가
"유효하지 않은 팀 설정"으로 거부됐다. 봇이 슬롯을 먹지 않게 하여
사람 12명(6대6)을 온전히 확보한다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# --- 1) 전역 변수 추가 -------------------------------------------------
s = s.replace("\t\t17: Tmp\n", "\t\t17: Tmp\n\t\t18: OutPos\n\t\t19: OutHP\n\t\t20: OutResp\n\t\t21: OutFx\n\t\t22: OutIco\n")

# --- 2) 설정: 6대6 ------------------------------------------------------
s = s.replace("\t\tMax Team 1 Players: 12\n\t\tMax Team 2 Players: 5\n",
              "\t\tMax Team 1 Players: 6\n\t\tMax Team 2 Players: 6\n")

# --- 3) 초기화에 무법자 배열 추가 --------------------------------------
s = s.replace("\t\tSet Global Variable(SignIds, Empty Array);\n",
              "\t\tSet Global Variable(SignIds, Empty Array);\n"
              "\t\tSet Global Variable(OutPos, Array(Vector(0, 0, 0), Vector(0, 0, 0), Vector(0, 0, 0)));\n"
              "\t\tSet Global Variable(OutHP, Array(0, 0, 0));\n"
              "\t\tSet Global Variable(OutResp, Array(0, 0, 0));\n"
              "\t\tSet Global Variable(OutFx, Array(0, 0, 0));\n"
              "\t\tSet Global Variable(OutIco, Array(0, 0, 0));\n")

# --- 4) 더미 봇 생성 루프 제거 -----------------------------------------
s = s.replace("""		For Global Variable(Idx, 0, 5, 1);
			Create Dummy Bot(Hero(Ashe), Team 2, Global Variable(Idx), Global Variable(BotHome), Vector(1, 0, 0));
			Wait(0.25, Ignore Condition);
		End;
""", "")

# --- 5) 봇 룰 3개를 스크립트 무법자 룰로 교체 --------------------------
a = s.index('rule("[무법자 01]')
b = s.index('rule("[범죄 01]')

NEW = '''rule("[무법자 01] 무법자 스폰 관리")
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
		For Global Variable(Idx, 0, 3, 1);
			If(And(Value In Array(Global Variable(OutHP), Global Variable(Idx)) <= 0, Total Time Elapsed() >= Value In Array(Global Variable(OutResp), Global Variable(Idx))));
				Set Global Variable At Index(OutPos, Global Variable(Idx), Add(Nearest Walkable Position(Add(Global Variable(BotHome), Vector(Random Real(-9, 9), 0, Random Real(-9, 9)))), Vector(0, 1.1, 0)));
				Set Global Variable At Index(OutHP, Global Variable(Idx), 100);
				Create Effect(All Players(All Teams), Sphere, Color(Red), Value In Array(Global Variable(OutPos), Global Variable(Idx)), 1, Visible To Position Radius and Color);
				Set Global Variable At Index(OutFx, Global Variable(Idx), Last Created Entity());
				Create Icon(All Players(All Teams), Add(Value In Array(Global Variable(OutPos), Global Variable(Idx)), Vector(0, 1.6, 0)), Skull, Visible To and Position, Color(Red), True);
				Set Global Variable At Index(OutIco, Global Variable(Idx), Last Created Entity());
			End;
		End;
		Wait(2, Ignore Condition);
		Loop();
	}
}

rule("[무법자 02] 무법자 사격 판정")
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
		For Player Variable(Event Player, Idx, 0, 3, 1);
			If(And(Value In Array(Global Variable(OutHP), Event Player.Idx) > 0, And(Distance Between(Eye Position(Event Player), Value In Array(Global Variable(OutPos), Event Player.Idx)) <= 45, And(Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Value In Array(Global Variable(OutPos), Event Player.Idx))) >= 0.985, Is In Line of Sight(Eye Position(Event Player), Value In Array(Global Variable(OutPos), Event Player.Idx), Barriers Do Not Block LOS)))));
				Set Global Variable At Index(OutHP, Event Player.Idx, Subtract(Value In Array(Global Variable(OutHP), Event Player.Idx), 34));
				Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Value In Array(Global Variable(OutPos), Event Player.Idx), 0.6);
				If(Value In Array(Global Variable(OutHP), Event Player.Idx) <= 0);
					Destroy Effect(Value In Array(Global Variable(OutFx), Event Player.Idx));
					Destroy Icon(Value In Array(Global Variable(OutIco), Event Player.Idx));
					Set Global Variable At Index(OutResp, Event Player.Idx, Add(Total Time Elapsed(), 14));
					Set Player Variable(Event Player, Roll, Multiply(Global Variable(BotBounty), Add(1, Global Variable(IsNight))));
					If(Event Player.Job == 3);
						Modify Player Variable(Event Player, Roll, Add, 40);
						Set Player Variable At Index(Event Player, JobXP, 3, Add(Value In Array(Event Player.JobXP, 3), 20));
					End;
					Modify Player Variable(Event Player, Money, Add, Event Player.Roll);
					Modify Player Variable(Event Player, Earned, Add, Event Player.Roll);
					Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 2)));
					Small Message(Event Player, Custom String("무법자 처치 — 현상금 $ {0}", Event Player.Roll));
					Play Effect(Event Player, Good Pickup Effect, Color(Lime Green), Position Of(Event Player), 1.5);
				End;
				Break;
			End;
		End;
		Wait(0.3, Ignore Condition);
		Loop If(Is Firing Primary(Event Player));
	}
}

rule("[무법자 03] 무법자 반격")
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
		For Global Variable(Idx, 0, 3, 1);
			If(Value In Array(Global Variable(OutHP), Global Variable(Idx)) > 0);
				Set Global Variable(Tmp, First Of(Sorted Array(Filtered Array(Players Within Radius(Value In Array(Global Variable(OutPos), Global Variable(Idx)), 20, All Teams, Surfaces), And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1)), Distance Between(Value In Array(Global Variable(OutPos), Global Variable(Idx)), Position Of(Current Array Element)))));
				If(Entity Exists(Global Variable(Tmp)));
					Damage(Global Variable(Tmp), Null, 13);
					Play Effect(All Players(All Teams), Bad Explosion, Color(Red), Value In Array(Global Variable(OutPos), Global Variable(Idx)), 0.35);
				End;
			End;
		End;
		Wait(1.8, Ignore Condition);
		Loop();
	}
}

'''
s = s[:a] + NEW + s[b:]

# --- 6) 강도 대상 탐색: 같은 팀만 -> 전체 팀 ---------------------------
s = s.replace("Players Within Radius(Eye Position(Event Player), 9, Team 1, Surfaces)",
              "Players Within Radius(Eye Position(Event Player), 9, All Teams, Surfaces)")

# --- 7) 플레이어 살해/처단 규칙 추가 -----------------------------------
MURDER = '''
rule("[범죄 02] 살해와 처단")
{
	event
	{
		Player Died;
		All;
		All;
	}

	conditions
	{
		Event Player.Init == 1;
		Entity Exists(Attacker) == True;
		Attacker != Victim;
		Player Variable(Attacker, Init) == 1;
	}

	actions
	{
		If(Player Variable(Victim, Bounty) > 0);
			Set Player Variable(Attacker, Roll, Player Variable(Victim, Bounty));
			Modify Player Variable(Attacker, Money, Add, Player Variable(Attacker, Roll));
			Modify Player Variable(Attacker, Earned, Add, Player Variable(Attacker, Roll));
			Set Player Variable(Victim, Bounty, 0);
			Set Player Variable(Attacker, Rep, Min(100, Add(Player Variable(Attacker, Rep), 8)));
			Big Message(All Players(All Teams), Custom String("{0}이(가) 수배범 {1}을(를) 처단했다 — $ {2}", Attacker, Victim, Player Variable(Attacker, Roll)));
		Else;
			Modify Player Variable(Attacker, Bounty, Add, 120);
			Set Player Variable(Attacker, Rep, Max(-100, Subtract(Player Variable(Attacker, Rep), 20)));
			Big Message(All Players(All Teams), Custom String("{0}이(가) {1}을(를) 살해했다 — 현상금 $ {2}", Attacker, Victim, Player Variable(Attacker, Bounty)));
		End;
	}
}
'''
s = s.replace('\nrule("[생활 02] 사망 처리")', MURDER + '\nrule("[생활 02] 사망 처리")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
for probe in ('Create Dummy Bot', 'Is Dummy Bot', 'OutPos', 'Max Team 1 Players: 6', '[범죄 02]'):
    print('  %-24s %d회' % (probe, s.count(probe)))
