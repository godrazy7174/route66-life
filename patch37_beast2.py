# -*- coding: utf-8 -*-
"""[1] 야수 아이콘이 안 뜨는 문제
    BuildWorld의 Create Icon 3개가 조건부 표시였다.
        Create Icon(BeastTimer[n] > Total Time Elapsed() ? All Players : False, ...)
    광기둥·하늘 조명을 죽였던 그 패턴이다. 벽 너머 표시가 원래 있긴 했는데
    한 번도 화면에 뜬 적이 없었을 것이다.
    -> 드러날 때 만들고 숨거나 죽을 때 부순다.

[2] 제트팩 캣을 더 역동적으로
    기존: 1~2.5초마다 방향 전환, 속도 75%, 전력 직진
    수정: 0.3~1.1초마다 전환, 속도 115~165%를 매번 다시 뽑고,
          추력도 0.55~1로 흔들어 가다 서다를 만든다. 30% 확률로 점프.
          개활지 중심에서 25m를 넘어가면 되돌아온다 (사냥터 이탈 방지).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
C6 = 'Value In Array(Global Variable(LocPos), 6)'
LIVE = 'Value In Array(Global Variable(BeastTimer), Slot Of(Event Player)) > Total Time Elapsed()'

# ── 전용 변수 ──────────────────────────────────────────────────────
assert 'IcoId' not in s
s = s.replace('\t\t23: Idx\n', '\t\t22: IcoId\n\t\t23: Idx\n', 1)

# ── 1) 깨진 아이콘 3개 제거 ────────────────────────────────────────
L = s.split(chr(10))
L = [x for x in L if not ('Create Icon(Value In Array(Global Variable(BeastTimer)' in x)]
s = chr(10).join(L)
assert 'Create Icon(Value In Array(Global Variable(BeastTimer)' not in s

# ── 2) 배회 룰 교체 ────────────────────────────────────────────────
a = s.index('rule("[직업 03-3] 야수 배회")')
b = s.index('rule("[직업 03-2] 야수 처치")')
NEW = '''rule("[직업 03-3] 야수 배회")
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
		%(live)s;
	}

	actions
	{
		Set Move Speed(Event Player, Random Integer(115, 165));
		If(Distance Between(Position Of(Event Player), %(c6)s) > 25);
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), %(c6)s), 1, To World, Replace existing throttle, Direction and Magnitude);
		Else;
			Start Throttle In Direction(Event Player, Vector(Random Real(-1, 1), 0, Random Real(-1, 1)), Random Real(0.55, 1), To World, Replace existing throttle, Direction and Magnitude);
			If(Random Integer(1, 100) <= 30);
				Press Button(Event Player, Button(Jump));
			End;
		End;
		Wait(Random Real(0.3, 1.1), Ignore Condition);
		Loop If(%(live)s);
		Stop Throttle In Direction(Event Player);
	}
}

rule("[직업 03-4] 야수 위치 표시")
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
		Is Alive(Event Player) == True;
		%(live)s;
	}

	actions
	{
		Destroy Icon(Event Player.IcoId);
		Create Icon(All Players(All Teams), Event Player, Eye, Visible To and Position, Color(Orange), True);
		Set Player Variable(Event Player, IcoId, Last Created Entity());
		Wait Until(Or(Not(%(live)s), Not(Is Alive(Event Player))), 99999);
		Destroy Icon(Event Player.IcoId);
		Set Player Variable(Event Player, IcoId, 0);
	}
}

''' % {'live': LIVE, 'c6': C6}
s = s[:a] + NEW + s[b:]

# ── 3) 숨을 때 / 죽을 때 아이콘 정리 (룰 중단으로 위 파괴가 안 돌 수 있음) ──
OLD = '\t\tStop Throttle In Direction(Event Player);\n\t\tSet Move Speed(Event Player, 0);'
assert s.count(OLD) == 1
s = s.replace(OLD, '\t\tDestroy Icon(Event Player.IcoId);\n'
                   '\t\tSet Player Variable(Event Player, IcoId, 0);\n' + OLD, 1)

OLD2 = '\t\tSet Global Variable At Index(BeastTimer, Slot Of(Victim), 0);'
assert s.count(OLD2) == 1
s = s.replace(OLD2, '\t\tDestroy Icon(Player Variable(Victim, IcoId));\n'
                    '\t\tSet Player Variable(Victim, IcoId, 0);\n' + OLD2, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  아이콘 : 조건부 표시 폐기 -> 드러날 때 생성, 숨거나 죽을 때 파괴 (벽 너머 표시 유지)')
print('  이동   : 0.3~1.1초 전환 / 속도 115~165%% / 추력 0.55~1 / 점프 30%% / 25m 리시')
