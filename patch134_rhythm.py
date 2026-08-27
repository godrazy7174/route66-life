# -*- coding: utf-8 -*-
"""patch134: 리듬 채굴 + 호송 매복.
1) DoMine 전면 재작성 — 연속 스윕 박자 세션 (While 루프), 정타/회심/헛스윙
2) [호송 03] 길목의 매복 — 예고 후 15초 위험지대 (Cow* 변수 차용)
3) 상호 배타 가드: 호송↔소몰이↔습격 (Cow*/CowEnd 차용 안전)
"""
import io

PATH = "ROUTE66_LIFE_EN.ow"
with io.open(PATH, "r", encoding="utf-8") as f:
    src = f.read()

def sub(old, new, cnt):
    global src
    n = src.count(old)
    assert n == cnt, "expected %d, found %d: %r" % (cnt, n, old[:60])
    src = src.replace(old, new)

BAR = 'Value In Array(Array(Custom String("◆□□□□□□■■■□□□□□□□"), Custom String("□◆□□□□□■■■□□□□□□□"), Custom String("□□◆□□□□■■■□□□□□□□"), Custom String("□□□◆□□□■■■□□□□□□□"), Custom String("□□□□◆□□■■■□□□□□□□"), Custom String("□□□□□◆□■■■□□□□□□□"), Custom String("□□□□□□◆■■■□□□□□□□"), Custom String("□□□□□□□◆■■□□□□□□□"), Custom String("□□□□□□□■◆■□□□□□□□"), Custom String("□□□□□□□■■◆□□□□□□□"), Custom String("□□□□□□□■■■◆□□□□□□"), Custom String("□□□□□□□■■■□◆□□□□□"), Custom String("□□□□□□□■■■□□◆□□□□"), Custom String("□□□□□□□■■■□□□◆□□□"), Custom String("□□□□□□□■■■□□□□◆□□"), Custom String("□□□□□□□■■■□□□□□◆□"), Custom String("□□□□□□□■■■□□□□□□◆")), Min(16, Max(0, Round To Integer(Event Player.WorkProg, To Nearest))))'

SWEEP_T = 'Max(0.5, Subtract(0.85, Multiply(0.012, Min(25, Event Player.Streak))))'

NEW_DOMINE = '''rule("[직업 01] DoMine")
{
	event
	{
		Subroutine;
		DoMine;
	}

	actions
	{
		If(Event Player.Energy < 5);
			Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
			Abort;
		End;
		Set Player Variable(Event Player, Busy, 1);
		Set Player Variable(Event Player, JobArg, 1);
		Call Subroutine(BecomeJob);
		Set Player Variable(Event Player, WorkProg, 0);
		Destroy HUD Text(Event Player.KeyHud);
		Create HUD Text(Event Player, Null, %(BAR)s, Custom String("◆가 ■일 때 [{0}] — 한가운데면 회심   ·   [웅크리기] 마침", Input Binding String(Button(Interact))), Top, 1, Color(White), Color(Yellow), Color(Gray), Visible To Sort Order String and Color, Default Visibility);
		Set Player Variable(Event Player, KeyHud, Last Text ID());
		Big Message(Event Player, Custom String("곡괭이의 박자 — 결을 읽어라"));
		Wait Until(Not(Is Button Held(Event Player, Button(Interact))), 1.5);
		While(And(And(Event Player.Zone == 1, Is Alive(Event Player)), And(And(Event Player.Energy > 0, Event Player.Hunger > 0), Is Button Held(Event Player, Button(Crouch)) == False)));
			Chase Player Variable Over Time(Event Player, WorkProg, Round To Integer(Event Player.WorkProg, To Nearest) >= 8 ? 0 : 16, %(SWEEP_T)s, Destination and Duration);
			Wait Until(Or(Is Button Held(Event Player, Button(Interact)), Is Button Held(Event Player, Button(Crouch))), %(SWEEP_T)s);
			If(And(Is Button Held(Event Player, Button(Interact)), Is Button Held(Event Player, Button(Crouch)) == False));
				Stop Chasing Player Variable(Event Player, WorkProg);
				If(And(Round To Integer(Event Player.WorkProg, To Nearest) >= 7, Round To Integer(Event Player.WorkProg, To Nearest) <= 9));
					Set Player Variable(Event Player, Roll, Random Integer(1, 100));
					Modify Player Variable(Event Player, MineCount, Add, 1);
					If(Event Player.Prospect > 0);
						Modify Player Variable(Event Player, Prospect, Subtract, 1);
						Modify Player Variable(Event Player, Roll, Subtract, 8);
					End;
					If(Event Player.Job == 1);
						Modify Player Variable(Event Player, Roll, Subtract, 2);
						Modify Player Variable(Event Player, Roll, Subtract, Min(4, Round To Integer(Divide(Value In Array(Event Player.JobXP, 1), 250), Down)));
					End;
					If(Event Player.Roll <= 3);
						Set Player Variable(Event Player, MineGain, Random Integer(40, 105));
						If(Global Variable(TodayJob) == 1);
							Set Player Variable(Event Player, MineGain, Round To Integer(Multiply(Player Variable(Event Player, MineGain), Global Variable(FundTier) >= 3 ? 1.75 : 1.5), To Nearest));
						End;
						Modify Player Variable(Event Player, Money, Add, Event Player.MineGain);
						Modify Player Variable(Event Player, Earned, Add, Event Player.MineGain);
						Set Player Variable At Index(Event Player, JobXP, 1, Add(Value In Array(Event Player.JobXP, 1), 40));
						Big Message(All Players(All Teams), Custom String("{0} — 금맥 발견! $ {1}", Event Player, Event Player.MineGain));
						Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 4);
					Else;
						Set Player Variable(Event Player, MineGain, Random Integer(1, 2));
						If(Event Player.Job == 1);
							Modify Player Variable(Event Player, MineGain, Add, 1);
							Set Player Variable At Index(Event Player, JobXP, 1, Add(Value In Array(Event Player.JobXP, 1), 12));
						End;
						Modify Player Variable(Event Player, MineGain, Add, Event Player.Pick);
						If(Round To Integer(Event Player.WorkProg, To Nearest) == 8);
							Modify Player Variable(Event Player, MineGain, Add, 2);
							Small Message(Event Player, Custom String("회심의 정타!"));
							Play Effect(Event Player, Ring Explosion, Color(Orange), Position Of(Event Player), 1.2);
						End;
						If(And(And(Event Player.Job == 1, Value In Array(Event Player.Adv, Event Player.Job) == 1), Random Integer(1, 100) <= 10));
							Modify Player Variable(Event Player, MineGain, Multiply, 2);
							Big Message(Event Player, Custom String("광산주의 눈 — 이번 수확 2배!"));
							Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1.5);
						End;
						If(Global Variable(EventKind) == 1);
							Modify Player Variable(Event Player, MineGain, Multiply, 2);
						End;
						If(Global Variable(EventKind) == 6);
							Modify Player Variable(Event Player, MineGain, Multiply, 3);
							Damage(Event Player, Null, 15);
						End;
						If(Global Variable(TodayJob) == 1);
							Set Player Variable(Event Player, MineGain, Round To Integer(Multiply(Player Variable(Event Player, MineGain), Global Variable(FundTier) >= 3 ? 1.75 : 1.5), To Nearest));
						End;
						Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), Event Player.MineGain));
						Small Message(Event Player, Custom String("원석 +{0}   (보유 {1})", Event Player.MineGain, Value In Array(Event Player.Inv, 2)));
						Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 50);
					End;
					Play Effect(All Players(All Teams), Bad Explosion, Color(Gray), Position Of(Event Player), 0.5);
					If(Modulo(Event Player.MineCount, 10) == 0);
						Modify Player Variable(Event Player, Money, Add, 20);
						Big Message(Event Player, Custom String("채굴 {0}회 달성 — 보너스 $25", Event Player.MineCount));
						Play Effect(Event Player, Good Explosion, Color(Lime Green), Position Of(Event Player), 2);
					End;
					Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 5)));
					Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 2)));
					Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2.5)));
					If(Subtract(Total Time Elapsed(), Event Player.LastMine) > 25);
						Set Player Variable(Event Player, Streak, 0);
					End;
					Set Player Variable(Event Player, LastMine, Total Time Elapsed());
					If(And(Global Variable(ContractKind) == 1, Modulo(Player Variable(Event Player, Giant), 10) < 8));
						Modify Player Variable(Event Player, Giant, Add, 1);
						If(Modulo(Player Variable(Event Player, Giant), 10) == 8);
							Modify Player Variable(Event Player, Giant, Add, Subtract(9, 8));
							Modify Player Variable(Event Player, Money, Add, 150);
							Modify Player Variable(Event Player, Earned, Add, 150);
							Set Player Variable(Event Player, Fame, Min(100, Add(Player Variable(Event Player, Fame), 3)));
							Big Message(Event Player, Custom String("오늘의 계약 달성! +$150 · 명성 +3"));
							Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 120);
						Else;
							Small Message(Event Player, Custom String("오늘의 계약 — 진행 {0} / {1}", Modulo(Player Variable(Event Player, Giant), 10), 8));
						End;
					End;
					Modify Player Variable(Event Player, Streak, Add, 1);
					If(Modulo(Event Player.Streak, 5) == 0);
						Set Player Variable(Event Player, StreakPay, Multiply(Min(Event Player.Streak, 25), 3));
						Modify Player Variable(Event Player, Money, Add, Event Player.StreakPay);
						Modify Player Variable(Event Player, Earned, Add, Event Player.StreakPay);
						Big Message(Event Player, Custom String("{0}연속 채굴!   +$ {1}", Event Player.Streak, Event Player.StreakPay));
						Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1.5);
					End;
					Wait(1.1, Ignore Condition);
				Else;
					Set Player Variable(Event Player, Streak, 0);
					Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 2.5)));
					Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1)));
					Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 1.2)));
					Small Message(Event Player, Custom String("헛스윙 — 결을 놓쳤다 (연속 끊김)"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 40);
					Wait(0.6, Ignore Condition);
				End;
				Wait Until(Not(Is Button Held(Event Player, Button(Interact))), 1);
			End;
		End;
		Stop Chasing Player Variable(Event Player, WorkProg);
		Destroy HUD Text(Event Player.KeyHud);
		Set Player Variable(Event Player, WorkProg, 0);
		Set Player Variable(Event Player, Busy, 0);
		Small Message(Event Player, Custom String("곡괭이를 내려놓았다"));
	}
}''' % {"BAR": BAR, "SWEEP_T": SWEEP_T}

# ---- 1) DoMine 교체 (마커 슬라이스) ----
start = src.index('rule("[직업 01] DoMine")')
end_marker = src.index('\n}\n', start)
old_rule = src[start:end_marker + 3]
assert "채굴 중..." in old_rule and "DoSkillBar" in old_rule, "DoMine slice sanity failed"
src = src[:start] + NEW_DOMINE + "\n" + src[end_marker + 3:]

# ---- 2) [호송 03] 매복 ----
AMBUSH = '''rule("[호송 03] 길목의 매복")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Is Dummy Bot(Event Player) == False;
		Event Player.Init == 1;
		Event Player.Escort == 1;
		Is Alive(Event Player) == True;
	}

	actions
	{
		Wait(Random Real(10, 16), Ignore Condition);
		If(And(And(Event Player.Escort == 1, Is Alive(Event Player)), Random Integer(1, 100) <= 45));
			Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Direction Towards(Position Of(Event Player), Event Player.EscortPos), 14))));
			Set Player Variable(Event Player, CowEnd, Add(Total Time Elapsed(), 15));
			Destroy Effect(Event Player.CowFx);
			Create Effect(All Players(All Teams), Sphere, Color(Red), Event Player.CowPos, 6, Visible To Position Radius and Color);
			Set Player Variable(Event Player, CowFx, Last Created Entity());
			Small Message(Event Player, Custom String("길목에 매복이다! 붉은 원을 밟지 마라 — 15초"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 70);
			While(And(Total Time Elapsed() < Event Player.CowEnd, And(Event Player.Escort == 1, Is Alive(Event Player))));
				If(Distance Between(Position Of(Event Player), Event Player.CowPos) < 6);
					Damage(Event Player, Null, 30);
					Small Message(Event Player, Custom String("매복 사격에 당하고 있다!"));
					Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Event Player.CowPos, 100);
				End;
				Wait(0.5, Ignore Condition);
			End;
			Destroy Effect(Event Player.CowFx);
			If(And(Event Player.Escort == 1, Is Alive(Event Player)));
				Small Message(Event Player, Custom String("매복이 물러갔다 — 길이 열렸다"));
			End;
		End;
		Wait(2, Ignore Condition);
		Loop If(Event Player.Escort == 1);
	}
}

'''
sub('rule("[대사냥 01] 대야수의 흔적")', AMBUSH + 'rule("[대사냥 01] 대야수의 흔적")', 1)

# ---- 3) 상호 배타 가드 ----
# 3a) 소몰이 시작: 호송 중 차단
sub('''				Else If(Event Player.Plan >= 1);
					Small Message(Event Player, Custom String("역마차를 쫓는 중에는 소를 몰 수 없다"));''',
    '''				Else If(Event Player.Escort == 1);
					Small Message(Event Player, Custom String("금괴를 나르는 중에는 소를 몰 수 없다"));
				Else If(Event Player.Plan >= 1);
					Small Message(Event Player, Custom String("역마차를 쫓는 중에는 소를 몰 수 없다"));''', 1)

# 3b) 습격 시작: 호송 중 차단
sub('''		If(Event Player.CowOn >= 1);
			Small Message(Event Player, Custom String("소를 몰면서 습격은 못 한다"));
			Abort;
		End;''',
    '''		If(Event Player.CowOn >= 1);
			Small Message(Event Player, Custom String("소를 몰면서 습격은 못 한다"));
			Abort;
		End;
		If(Event Player.Escort == 1);
			Small Message(Event Player, Custom String("금괴를 진 채 습격은 못 한다"));
			Abort;
		End;''', 1)

# 3c) 호송 계약: 소몰이/습격 중 차단
ESC_ANCHOR = '''				Else If(Event Player.Energy < 4);
					Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else;'''
sub(ESC_ANCHOR,
    '''				Else If(Event Player.CowOn >= 1);
					Small Message(Event Player, Custom String("소를 몰면서 금괴는 못 나른다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.Plan >= 1);
					Small Message(Event Player, Custom String("역마차를 쫓는 중에는 금괴를 맡을 수 없다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
''' + ESC_ANCHOR, 1)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)

print("patch134 OK")
