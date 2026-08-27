"""실기 5차 피드백.

1. 수비팀으로 스폰되어 공격 스폰(식당 내부)에 못 들어감
   -> Move Player to Team(Event Player, Team 1)로 전원을 1팀으로 강제 이동.
      1팀이 되면 공격 스폰 문이 열려 식당 안으로 들어갈 수 있다.
      혹시 슬롯이 안 잡히는 경우를 대비해, 식당 반경 안에서는
      환경 충돌을 꺼서 문을 통과할 수 있게 보조 장치도 둔다(바닥은 유지).

3. 달리기 추가 (Shift). 이동속도 165%, 피로를 3초당 1 소모.
   봉인된 Ability 1 버튼을 입력으로 사용(E/Q와 같은 방식).
   결핍 패널티 규칙이 매 5초 이동속도를 덮어쓰므로 달리는 중엔 건드리지 않게 한다.

4. 협곡 사냥터 -> 협곡 개활지 (되돌림)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 4) 이름 되돌리기 ────────────────────────────────────────────────
s = s.replace('협곡 사냥터', '협곡 개활지')

# ── 변수 추가 ───────────────────────────────────────────────────────
s = s.replace("\t\t30: Plan\n", "\t\t30: Plan\n\t\t31: Sprinting\n")

# ── 1) 전원 1팀으로 이동 ────────────────────────────────────────────
s = s.replace("\t\tSet Player Variable(Event Player, Init, 1);\n",
              "\t\tSet Player Variable(Event Player, Init, 1);\n"
              "\t\tSet Player Variable(Event Player, Sprinting, 0);\n"
              "\t\tIf(Team Of(Event Player) != Team 1);\n"
              "\t\t\tMove Player to Team(Event Player, Team 1, -1);\n"
              "\t\t\tWait(1, Ignore Condition);\n"
              "\t\tEnd;\n")

# ── 3) 결핍 패널티가 달리는 중엔 속도를 덮지 않게 ───────────────────
old_pen = """		If(Or(Event Player.Hunger <= 0, Event Player.Thirst <= 0));
			Damage(Event Player, Null, 8);
			Set Move Speed(Event Player, 70);
			Small Message(Event Player, Custom String("탈진 — 음식이나 물이 필요합니다"));
		Else If(Event Player.Energy <= 0);
			Set Move Speed(Event Player, 80);
			Set Aim Speed(Event Player, 70);
		Else;
			Set Move Speed(Event Player, 100);
			Set Aim Speed(Event Player, 100);"""
new_pen = """		If(Or(Event Player.Hunger <= 0, Event Player.Thirst <= 0));
			Damage(Event Player, Null, 8);
			If(Event Player.Sprinting == 0);
				Set Move Speed(Event Player, 70);
			End;
			Small Message(Event Player, Custom String("탈진 — 음식이나 물이 필요합니다"));
		Else If(Event Player.Energy <= 0);
			If(Event Player.Sprinting == 0);
				Set Move Speed(Event Player, 80);
			End;
			Set Aim Speed(Event Player, 70);
		Else;
			If(Event Player.Sprinting == 0);
				Set Move Speed(Event Player, 100);
			End;
			Set Aim Speed(Event Player, 100);"""
assert s.count(old_pen) == 1, '결핍 패널티 구간을 찾지 못함'
s = s.replace(old_pen, new_pen)

# ── 3) 달리기 + 1) 식당 출입 보조 ──────────────────────────────────
NEW_RULES = '''
rule("[조작 04] 달리기 (Shift)")
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
		Event Player.Busy == 0;
		Event Player.Energy > 0;
		Is Moving(Event Player) == True;
		Is Button Held(Event Player, Button(Ability 1)) == True;
	}

	actions
	{
		Set Player Variable(Event Player, Sprinting, 1);
		Set Move Speed(Event Player, 165);
		Wait(3, Ignore Condition);
		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 1)));
		Loop If(And(Is Button Held(Event Player, Button(Ability 1)), And(Is Moving(Event Player), And(Event Player.Energy > 0, And(Event Player.Busy == 0, Is Alive(Event Player))))));
		Set Player Variable(Event Player, Sprinting, 0);
		If(Or(Event Player.Hunger <= 0, Event Player.Thirst <= 0));
			Set Move Speed(Event Player, 70);
		Else If(Event Player.Energy <= 0);
			Set Move Speed(Event Player, 80);
		Else;
			Set Move Speed(Event Player, 100);
		End;
	}
}

rule("[코어 11] 식당 출입 보조")
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
		Global Variable(Ready) == 1;
		Is Alive(Event Player) == True;
		Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 0)) <= 10;
	}

	actions
	{
		Disable Movement Collision With Environment(Event Player, False);
		Wait Until(Or(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 0)) > 10, Not(Is Alive(Event Player))), 99999);
		Enable Movement Collision With Environment(Event Player);
	}
}
'''
s = s.replace('\nrule("[조작 03] 행동 실행 (F)")', NEW_RULES + '\nrule("[조작 03] 행동 실행 (F)")')

# ── HUD 키 안내에 달리기 추가 ───────────────────────────────────────
s = s.replace('Custom String("[{0}] 육포   [{1}] 물", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate)))',
              'Custom String("[{0}] 육포  [{1}] 물  [{2}] 달리기", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate)), Input Binding String(Button(Ability 1)))')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  1팀 강제 이동 : %d' % s.count('Move Player to Team(Event Player, Team 1, -1)'))
print('  달리기 규칙   : %d' % s.count('[조작 04] 달리기'))
print('  식당 출입 보조: %d' % s.count('[코어 11] 식당 출입 보조'))
print('  협곡 개활지   : %d' % s.count('협곡 개활지'))
print('  협곡 사냥터 잔존: %d' % s.count('협곡 사냥터'))
