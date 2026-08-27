# -*- coding: utf-8 -*-
"""patch136: 목동 (가)총성 폭주 + (나)늑대의 습격.
- [목동 03] 타인의 총성(소 25m 안)에 소가 놀라 목장 반대쪽으로 내달림
- [목동 04] 늑대(회색 구체)가 소에게 접근, 조준 사격 누적 3틱으로 격퇴,
  물리면 소가 15~20m 후퇴 (DialTgt/DialPin/DialCur·EscortFlash 차용)
- 상호 배타: 배달 수주 <-> 소몰이 (샛길 Dial 변수 충돌 방지)
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

P = "Value In Array(All Players(Team 1), Event Player.Idx)"

NEW_RULES = '''rule("[목동 03] 총성에 놀란 소")
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
		Is Button Held(Event Player, Button(Primary Fire)) == True;
	}

	actions
	{
		For Player Variable(Event Player, Idx, 0, Count Of(All Players(Team 1)), 1);
			If(And(And(Player Variable(%(P)s, CowOn) >= 1, %(P)s != Event Player), Distance Between(Position Of(Event Player), Player Variable(%(P)s, CowPos)) < 25));
				Set Player Variable(%(P)s, CowPos, Nearest Walkable Position(Add(Player Variable(%(P)s, CowPos), Add(Multiply(Direction Towards(Value In Array(Global Variable(LocPos), 12), Player Variable(%(P)s, CowPos)), Random Real(8, 12)), Vector(Random Real(-6, 6), 0, Random Real(-6, 6))))));
				Destroy Effect(Player Variable(%(P)s, CowFx));
				Create Effect(All Players(All Teams), Sphere, Color(White), Player Variable(%(P)s, CowPos), 0.7, None);
				Set Player Variable(%(P)s, CowFx, Last Created Entity());
				Destroy Icon(Player Variable(%(P)s, CowIco));
				Create Icon(All Players(All Teams), Add(Player Variable(%(P)s, CowPos), Vector(0, 1.6, 0)), Circle, Visible To and Position, Color(White), True);
				Set Player Variable(%(P)s, CowIco, Last Created Entity());
				Small Message(%(P)s, Custom String("총성에 소가 놀라 내달렸다!"));
				Play Effect(%(P)s, Debuff Impact Sound, Color(White), Player Variable(%(P)s, CowPos), 60);
			End;
		End;
		Wait(1.5, Ignore Condition);
	}
}

rule("[목동 04] 늑대의 습격")
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
		Event Player.CowOn >= 1;
		Is Alive(Event Player) == True;
	}

	actions
	{
		Wait(Random Real(18, 30), Ignore Condition);
		If(And(And(Event Player.CowOn >= 1, Is Alive(Event Player)), Random Integer(1, 100) <= 45));
			Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Event Player.CowPos, Multiply(Direction From Angles(Random Real(-180, 180), 0), 20))));
			Set Player Variable(Event Player, DialPin, 0);
			Set Player Variable(Event Player, DialCur, 0);
			Destroy Effect(Event Player.EscortFlash);
			Create Effect(All Players(All Teams), Sphere, Color(Gray), Event Player.DialTgt, 0.9, Visible To Position Radius and Color);
			Set Player Variable(Event Player, EscortFlash, Last Created Entity());
			Small Message(Event Player, Custom String("늑대다! 소에게 달려든다 — 쏴서 쫓아내라 (회색 그림자)"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 80);
			While(And(And(Event Player.CowOn >= 1, Is Alive(Event Player)), And(Event Player.DialCur < 12, Event Player.DialPin < 3)));
				Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Event Player.DialTgt, Multiply(Direction Towards(Event Player.DialTgt, Event Player.CowPos), 1.4))));
				If(And(Is Button Held(Event Player, Button(Primary Fire)), And(Distance Between(Position Of(Event Player), Event Player.DialTgt) < 30, Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Event Player.DialTgt)) >= 0.96)));
					Modify Player Variable(Event Player, DialPin, Add, 1);
					Play Effect(Event Player, Buff Impact Sound, Color(Orange), Event Player.DialTgt, 40);
				End;
				If(Distance Between(Event Player.DialTgt, Event Player.CowPos) < 2.5);
					Set Player Variable(Event Player, DialCur, 99);
					Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Event Player.CowPos, Add(Multiply(Direction Towards(Value In Array(Global Variable(LocPos), 12), Event Player.CowPos), Random Real(15, 20)), Vector(Random Real(-5, 5), 0, Random Real(-5, 5))))));
					Destroy Effect(Event Player.CowFx);
					Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, None);
					Set Player Variable(Event Player, CowFx, Last Created Entity());
					Destroy Icon(Event Player.CowIco);
					Create Icon(All Players(All Teams), Add(Event Player.CowPos, Vector(0, 1.6, 0)), Circle, Visible To and Position, Color(White), True);
					Set Player Variable(Event Player, CowIco, Last Created Entity());
					Small Message(Event Player, Custom String("늑대가 소를 물었다 — 소가 멀리 달아났다!"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Event Player.CowPos, 90);
				End;
				Modify Player Variable(Event Player, DialCur, Add, 0.3);
				Wait(0.3, Ignore Condition);
			End;
			Destroy Effect(Event Player.EscortFlash);
			If(Event Player.DialPin >= 3);
				Small Message(Event Player, Custom String("늑대를 쫓아냈다!"));
				Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);
			End;
		End;
		Wait(2, Ignore Condition);
		Loop If(Event Player.CowOn >= 1);
	}
}

''' % {"P": P}

sub('rule("[스킬바 01] DoSkillBar")', NEW_RULES + 'rule("[스킬바 01] DoSkillBar")', 1)

# ---- 상호 배타: 배달 <-> 소몰이 ----
sub('''				Else If(Event Player.HasParcel == 2);
					Small Message(Event Player, Custom String("이미 값진 화물이다 — 온 서버가 너를 안다, 목적지로 달려라"));''',
    '''				Else If(Event Player.CowOn >= 1);
					Small Message(Event Player, Custom String("소를 몰면서 화물은 못 든다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else If(Event Player.HasParcel == 2);
					Small Message(Event Player, Custom String("이미 값진 화물이다 — 온 서버가 너를 안다, 목적지로 달려라"));''', 1)

sub('''				Else If(Event Player.Escort == 1);
					Small Message(Event Player, Custom String("금괴를 나르는 중에는 소를 몰 수 없다"));''',
    '''				Else If(Event Player.HasParcel >= 1);
					Small Message(Event Player, Custom String("화물을 든 채 소를 몰 수는 없다"));
				Else If(Event Player.Escort == 1);
					Small Message(Event Player, Custom String("금괴를 나르는 중에는 소를 몰 수 없다"));''', 1)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)

print("patch136 OK")
