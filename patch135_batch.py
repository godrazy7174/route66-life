# -*- coding: utf-8 -*-
"""patch135: HUD 재배치 + 가스 리듬 + 사냥꾼 급소.
1) 육포/물 키 안내를 메뉴 HUD([R] 다음 오른쪽)로 이동, 조작 HUD에서 제거
2) [광산 02] 가스 분출 주기 — 전조 2초 후 1.8초 분출, 분출 중 스윙 = 피해+연속 끊김
3) 사냥꾼: 급소 주기(2.5초 점멸, 점등 시 피해 250%/소등 60%), 야수 속도 -8%,
   도약 15%->12%, 거대 2.2%->4.4%(승급 6.4%), 전설 0.2%->0.4%
"""
import io

PATH = "ROUTE66_LIFE_EN.ow"
with io.open(PATH, "r", encoding="utf-8") as f:
    src = f.read()

def sub(old, new, cnt):
    global src
    n = src.count(old)
    assert n == cnt, "expected %d, found %d: %r" % (cnt, n, old[:70])
    src = src.replace(old, new)

# ---- 전역 변수 ----
sub("\t\t61: RaidPath\n", "\t\t61: RaidPath\n\t\t62: GasOn\n\t\t63: GasFx\n\t\t64: WeakOn\n\t\t65: WeakFx\n", 1)

# ---- 1) HUD 재배치 ----
TAIL = 'Custom String("      [{0}] 육포 · [{1}] 물", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate)))'
sub('Value In Array(Array(Custom String("[{0}] 실행", Input Binding String(Button(Interact))), Custom String("[{0}] 실행      [{1}] 다음", Input Binding String(Button(Interact)), Input Binding String(Button(Reload))))',
    'Value In Array(Array(Custom String("{0}{1}", Custom String("[{0}] 실행", Input Binding String(Button(Interact))), ' + TAIL + '), Custom String("{0}{1}", Custom String("[{0}] 실행      [{1}] 다음", Input Binding String(Button(Interact)), Input Binding String(Button(Reload))), ' + TAIL + '))', 1)

sub('Custom String("{0}   {1}   {2}", Custom String("[{0}] 육포  [{1}] 물", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate))), Custom String("[{0}] 달리기", Input Binding String(Button(Ability 1))), Custom String("[{0}] 강도/체포 · 앉아서 [{0}] 송금 · 가만히 웅크리면 피로 회복", Input Binding String(Button(Melee))))',
    'Custom String("{0}   {1}", Custom String("[{0}] 달리기", Input Binding String(Button(Ability 1))), Custom String("[{0}] 강도/체포 · 앉아서 [{0}] 송금 · 가만히 웅크리면 피로 회복", Input Binding String(Button(Melee))))', 1)

# ---- 2) 가스 분출 — DoMine 훅 ----
sub('''				Stop Chasing Player Variable(Event Player, WorkProg);
				If(And(Round To Integer(Event Player.WorkProg, To Nearest) >= 7, Round To Integer(Event Player.WorkProg, To Nearest) <= 9));''',
    '''				Stop Chasing Player Variable(Event Player, WorkProg);
				If(Global Variable(GasOn) == 1);
					Set Player Variable(Event Player, Streak, 0);
					Damage(Event Player, Null, 30);
					Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 2.5)));
					Small Message(Event Player, Custom String("분출 속에 곡괭이를 휘둘렀다! — 전조가 오르면 손을 멈춰라"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 60);
					Wait(0.8, Ignore Condition);
				Else If(And(Round To Integer(Event Player.WorkProg, To Nearest) >= 7, Round To Integer(Event Player.WorkProg, To Nearest) <= 9));''', 1)

# ---- 가스 분출 주기 규칙 + 급소 규칙 ----
NEW_RULES = '''rule("[광산 02] 가스 분출 주기")
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
		Wait(Random Real(8, 13), Ignore Condition);
		Destroy Effect(Global Variable(GasFx));
		Create Effect(All Players(All Teams), Light Shaft, Color(Yellow), Value In Array(Global Variable(LocPos), 1), 2.2, Visible To Position Radius and Color);
		Set Global Variable(GasFx, Last Created Entity());
		Small Message(Players Within Radius(Value In Array(Global Variable(LocPos), 1), 16, All Teams, Off), Custom String("광산이 부글거린다 — 분출 전조다, 손을 멈춰라!"));
		Play Effect(Players Within Radius(Value In Array(Global Variable(LocPos), 1), 16, All Teams, Off), Debuff Impact Sound, Color(Yellow), Value In Array(Global Variable(LocPos), 1), 60);
		Wait(2, Ignore Condition);
		Destroy Effect(Global Variable(GasFx));
		Set Global Variable(GasOn, 1);
		Create Effect(All Players(All Teams), Sphere, Color(Yellow), Value In Array(Global Variable(LocPos), 1), 9, Visible To Position Radius and Color);
		Set Global Variable(GasFx, Last Created Entity());
		Play Effect(All Players(All Teams), Bad Explosion, Color(Yellow), Value In Array(Global Variable(LocPos), 1), 6);
		Wait(1.8, Ignore Condition);
		Set Global Variable(GasOn, 0);
		Destroy Effect(Global Variable(GasFx));
		Loop();
	}
}

rule("[야수 06] 급소의 빛")
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
		Wait(2.5, Ignore Condition);
		Set Global Variable(WeakOn, 1);
		Set Damage Received(Players On Team(Team 2), 250);
		Set Global Variable(WeakFx, Empty Array);
		Create Effect(Player Variable(Value In Array(Players On Team(Team 2), 0), RevealEnd) > Total Time Elapsed() ? All Players(All Teams) : Null, Sphere, Color(Red), Add(Position Of(Value In Array(Players On Team(Team 2), 0)), Vector(0, 1.6, 0)), 0.55, Visible To Position Radius and Color);
		Modify Global Variable(WeakFx, Append To Array, Last Created Entity());
		Create Effect(Player Variable(Value In Array(Players On Team(Team 2), 1), RevealEnd) > Total Time Elapsed() ? All Players(All Teams) : Null, Sphere, Color(Red), Add(Position Of(Value In Array(Players On Team(Team 2), 1)), Vector(0, 1.6, 0)), 0.55, Visible To Position Radius and Color);
		Modify Global Variable(WeakFx, Append To Array, Last Created Entity());
		Create Effect(Player Variable(Value In Array(Players On Team(Team 2), 2), RevealEnd) > Total Time Elapsed() ? All Players(All Teams) : Null, Sphere, Color(Red), Add(Position Of(Value In Array(Players On Team(Team 2), 2)), Vector(0, 1.6, 0)), 0.55, Visible To Position Radius and Color);
		Modify Global Variable(WeakFx, Append To Array, Last Created Entity());
		Wait(2.5, Ignore Condition);
		Set Global Variable(WeakOn, 0);
		Set Damage Received(Players On Team(Team 2), 60);
		Destroy Effect(Value In Array(Global Variable(WeakFx), 0));
		Destroy Effect(Value In Array(Global Variable(WeakFx), 1));
		Destroy Effect(Value In Array(Global Variable(WeakFx), 2));
		Loop();
	}
}

'''
sub('rule("[디버그 01] 경로 측량 좌표")', NEW_RULES + 'rule("[디버그 01] 경로 측량 좌표")', 1)

# ---- 3) 사냥꾼 확률·속도·안내 ----
sub("Add(22, Multiply(10, Event Player.Roll)) ? 1 : 0", "Add(44, Multiply(20, Event Player.Roll)) ? 1 : 0", 1)
sub(", Roll) <= 2);", ", Roll) <= 4);", 1)
sub("Random Integer(190, 230)", "Random Integer(175, 215)", 2)
sub("Random Integer(120, 160)", "Random Integer(110, 148)", 1)
sub('Big Message(Event Player, Custom String("크아앙! 엄청 무서운 야수가 나타났다!"));',
    '''Big Message(Event Player, Custom String("크아앙! 엄청 무서운 야수가 나타났다!"));
		Small Message(Event Player, Custom String("붉은 급소가 빛날 때 쏴라 — 세 배로 아프다"));''', 1)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)

print("patch135 OK")
