# -*- coding: utf-8 -*-
"""사냥감을 구체 이펙트 -> 리퍼 더미봇으로 교체.

이점: 실제 적팀 유닛이라 진짜 총으로 쏘고 명중/헤드샷/처치 판정을 게임이 해준다.
      직접 만든 조준각 판정(내적 0.985)을 걷어낼 수 있다.

비용: 더미봇도 슬롯을 먹는다. 로비 총원 12명 상한이라
      1팀 9명(사람) + 2팀 3기(야수) 구성으로 간다.

추적 방식 변경: 야수가 3기뿐이므로 '내 전용 사냥감 생성'이 아니라
      '흔적 추적 -> 가장 가까운 야수를 내 앞으로 몰아낸다'로 바꾼다.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) BuildWorld 에 야수 3기 생성 ─────────────────────────────────
SPAWN = ('\t\tFor Global Variable(Idx, 0, 3, 1);\n'
         '\t\t\tCreate Dummy Bot(Hero(Reaper), Team 2, Global Variable(Idx), Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-10, 10), 0, Random Real(-10, 10)))), Vector(1, 0, 0));\n'
         '\t\t\tWait(0.25, Ignore Condition);\n'
         '\t\tEnd;\n')
_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + SPAWN + s[b:]

# ── 2) DoHunt 재작성 ───────────────────────────────────────────────
a = s.index('rule("[직업 02] DoHunt")')
b = s.index('\nrule("[직업 03] 사냥감 사격 판정")')
c = s.index('\nrule(', s.index('rule("[직업 03] 사냥감 사격 판정")') + 5)
NEW = '''rule("[직업 02] DoHunt")
{
	event
	{
		Subroutine;
		DoHunt;
	}

	actions
	{
		If(Event Player.Energy < 4);
			Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));
			Abort;
		End;
		Set Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))), Distance Between(Position Of(Event Player), Position Of(Current Array Element)))));
		If(Not(Entity Exists(Event Player.Target)));
			Small Message(Event Player, Custom String("흔적이 끊겼다 — 잠시 뒤 다시 시도해라"));
			Abort;
		End;
		Set Player Variable(Event Player, Busy, 1);
		Set Player Variable(Event Player, WorkProg, 0);
		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("흔적 추적 중..."), Top, 0, Color(Orange), Color(White), Visible To Values and Color, Default Visibility);
		Set Player Variable(Event Player, WorkBar, Last Text ID());
		Chase Player Variable Over Time(Event Player, WorkProg, 100, 2.5, Destination and Duration);
		Wait(2.5, Ignore Condition);
		Stop Chasing Player Variable(Event Player, WorkProg);
		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 4)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.5)));
		Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2)));
		Teleport(Event Player.Target, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Facing Direction Of(Event Player), 16))));
		Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player.Target), 2);
		Big Message(Event Player, Custom String("야수를 몰아냈다 — 쏴라"));
	}
}

rule("[직업 03] 야수 관리")
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
		Global Variable(Ready) == 1;
	}

	actions
	{
		Set Max Health(Event Player, 40);
		Set Ability 1 Enabled(Event Player, False);
		Set Ability 2 Enabled(Event Player, False);
		Set Ultimate Ability Enabled(Event Player, False);
		Set Primary Fire Enabled(Event Player, False);
		Set Secondary Fire Enabled(Event Player, False);
		Set Move Speed(Event Player, 0);
		Create Icon(All Players(All Teams), Event Player, Eye, Visible To and Position, Color(Orange), True);
		Wait(1, Ignore Condition);
		Teleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-12, 12), 0, Random Real(-12, 12)))));
	}
}

rule("[직업 03-2] 야수 처치")
{
	event
	{
		Player Died;
		Team 2;
		All;
	}

	conditions
	{
		Is Dummy Bot(Victim) == True;
		Entity Exists(Attacker) == True;
		Player Variable(Attacker, Init) == 1;
	}

	actions
	{
		Set Player Variable(Attacker, Roll, Random Integer(2, 4));
		If(Player Variable(Attacker, Job) == 2);
			Modify Player Variable(Attacker, Roll, Add, 2);
			Set Player Variable At Index(Attacker, JobXP, 2, Add(Value In Array(Player Variable(Attacker, JobXP), 2), 15));
		End;
		Set Player Variable At Index(Attacker, Inv, 3, Add(Value In Array(Player Variable(Attacker, Inv), 3), Player Variable(Attacker, Roll)));
		If(Random Integer(1, 100) <= 15);
			Modify Player Variable(Attacker, Money, Add, 70);
			Modify Player Variable(Attacker, Earned, Add, 70);
			Big Message(All Players(All Teams), Custom String("{0} — 큰 놈을 잡았다! 가죽 {1}장 + $70", Attacker, Player Variable(Attacker, Roll)));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Attacker), 3);
		Else;
			Small Message(Attacker, Custom String("사냥 성공 — 가죽 +{0}", Player Variable(Attacker, Roll)));
		End;
		Wait(25, Ignore Condition);
		Teleport(Victim, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-12, 12), 0, Random Real(-12, 12)))));
	}
}
'''
s = s[:a] + NEW + s[c + 1:]

# ── 3) 옛 구체 시스템 잔재 제거 ────────────────────────────────────
s = s.replace('''		If(Event Player.HuntHP > 0);
			Destroy Effect(Event Player.HuntFx);
			Destroy Icon(Event Player.HuntIco);
			Set Player Variable(Event Player, HuntHP, 0);
		End;
''', '')
for v in ('15: HuntPos', '16: HuntHP', '19: HuntFx', '22: HuntKind', '27: HuntIco'):
    s = s.replace('\t\t%s\n' % v, '')
s = re.sub(r'\t\tSet Player Variable\(Event Player, (HuntHP|HuntKind), 0\);\n', '', s)

# ── 4) 사냥터 패널 문구 ────────────────────────────────────────────
s = s.replace('Custom String("흔적 추적 → 사냥감 출현\\r\\n좌클릭으로 직접 쏴서 잡는다\\r\\n")',
              'Custom String("흔적 추적 — 야수를 앞으로 몰아낸다\\r\\n좌클릭으로 직접 쏴서 잡는다\\r\\n")')
s = s.replace('Custom String("흔적 추적 — 사냥감 출현")', 'Custom String("흔적 추적 — 야수 몰아내기")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  야수 봇 생성   : %d' % s.count('Create Dummy Bot(Hero(Reaper)'))
print('  구체 잔재      : %d' % (s.count('HuntPos') + s.count('HuntHP') + s.count('HuntFx') + s.count('HuntIco') + s.count('HuntKind')))
print('  야수 처치 보상 : %d' % s.count('[직업 03-2] 야수 처치'))
