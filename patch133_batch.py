# -*- coding: utf-8 -*-
"""patch133: 5건 배치.
1) 공격팀 스폰 근처(18m) 이벤트 좌표 금지 — SpawnPos 캡처 + 6개 생성기 클램프(32m 밀어내기)
2) 계약 HUD를 Left 4 -> Left 2 (경험치 바와 분리)
3) 역마차 습격 전면 리디자인 — 달리는 마차 추격 + 근접 약탈 게이지 + 호위 반격
4) 밀수/금괴 호송/금고 마차 시작 시 전 서버 공지
5) 가죽 배낭 $2800 -> $4800, 말 $5500 -> $11000
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

def insert_after_line(anchor, block, cnt):
    """anchor를 포함한 각 줄 끝에 block(들여쓰기 자동)을 삽입."""
    global src
    n = src.count(anchor)
    assert n == cnt, "anchor expected %d, found %d: %r" % (cnt, n, anchor[:70])
    out = []
    pos = 0
    while True:
        i = src.find(anchor, pos)
        if i < 0:
            out.append(src[pos:])
            break
        eol = src.index("\n", i)
        ls = src.rfind("\n", 0, i) + 1
        indent = src[ls:ls + (len(src[ls:i]) - len(src[ls:i].lstrip("\t")))]
        out.append(src[pos:eol + 1])
        out.append(block.replace("@", indent))
        pos = eol + 1
    src = "".join(out)

def clamp_global(name):
    return ("@If(Distance Between(Global Variable(%s), Global Variable(SpawnPos)) < 18);\n"
            "@\tSet Global Variable(%s, Nearest Walkable Position(Add(Global Variable(SpawnPos), Multiply(Direction Towards(Global Variable(SpawnPos), Global Variable(%s)), 32))));\n"
            "@End;\n") % (name, name, name)

def clamp_player(name):
    return ("@If(Distance Between(Event Player.%s, Global Variable(SpawnPos)) < 18);\n"
            "@\tSet Player Variable(Event Player, %s, Nearest Walkable Position(Add(Global Variable(SpawnPos), Multiply(Direction Towards(Global Variable(SpawnPos), Event Player.%s), 32))));\n"
            "@End;\n") % (name, name, name)

# ---------- 1) SpawnPos ----------
sub("\t\t59: FundTier\n", "\t\t59: FundTier\n\t\t60: SpawnPos\n", 1)

insert_after_line("Set Player Variable(Event Player, Init, 1);",
    "@If(Is Dummy Bot(Event Player) == False);\n"
    "@\tSet Global Variable(SpawnPos, Position Of(Event Player));\n"
    "@End;\n", 1)

insert_after_line("Set Global Variable(WagonPos, Add(Nearest Walkable", clamp_global("WagonPos"), 1)
insert_after_line("Set Global Variable(TreasurePos, Add(Nearest Walkable", clamp_global("TreasurePos"), 1)
insert_after_line("Set Global Variable(HuntTrackPos, Nearest Walkable", clamp_global("HuntTrackPos"), 2)
insert_after_line("Set Player Variable(Event Player, SmugglePos, Nearest Walkable", clamp_player("SmugglePos"), 1)
insert_after_line("Set Player Variable(Event Player, EscortPos, Nearest Walkable", clamp_player("EscortPos"), 1)
insert_after_line("Set Player Variable(Event Player, DialTgt, Nearest Walkable", clamp_player("DialTgt"), 1)

# ---------- 2) 계약 HUD 위치 ----------
sub('Custom String(""), Null, Left, 4, Color(White), Color(Aqua), Color(White)',
    'Custom String(""), Null, Left, 2, Color(White), Color(Aqua), Color(White)', 1)

# ---------- 4) 시작 공지 ----------
insert_after_line('Big Message(Event Player, Custom String("금괴 상자를 실었다 — 노란 표식까지 (보수 $ {0})", Event Player.EscortPay));',
    '@Small Message(All Players(All Teams), Custom String("{0} — 금괴 호송을 시작했다", Event Player));\n', 1)
insert_after_line('Big Message(Event Player, Custom String("밀수 화물을 받았다 — 접선지로 (보수 $ {0})", Event Player.SmugglePay));',
    '@Small Message(All Players(All Teams), Custom String("누군가 밀수 화물을 실었다 — 자주색 표식을 노려라"));\n', 1)

WAGON_ANCHOR = '\t\tCreate Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("금고를 터는 중..."),'
n = src.count(WAGON_ANCHOR)
assert n == 1, "wagon anchor found %d" % n
src = src.replace(WAGON_ANCHOR,
    '\t\tSmall Message(All Players(All Teams), Custom String("누군가 금고 마차에 손을 댔다!"));\n' + WAGON_ANCHOR, 1)

# ---------- 5) 가격 인상 ----------
assert src.count("2800") == 6 and src.count("5500") == 6
src = src.replace("2800", "4800")
src = src.replace("5500", "11000")

# ---------- 3) 역마차 습격 리디자인 ----------
OLD_DOPLAN = '''	actions
	{
		If(Event Player.Energy < 6);
			Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
			Abort;
		End;
		Set Player Variable(Event Player, Busy, 1);
		Set Player Variable(Event Player, WorkProg, 0);
		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Set Player Variable(Event Player, JobArg, 4);
		Call Subroutine(BecomeJob);
		Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("습격 계획 중..."), Top, 0, Color(Purple), Color(White), Visible To Values and Color, Default Visibility);
		Set Player Variable(Event Player, WorkBar, Last Text ID());
		Chase Player Variable Over Time(Event Player, WorkProg, 100, 2.5, Destination and Duration);
		Wait(2.5, Ignore Condition);
		Stop Chasing Player Variable(Event Player, WorkProg);
		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Modify Player Variable(Event Player, Plan, Add, 1);
		Set Player Variable At Index(Event Player, JobXP, 4, Add(Value In Array(Event Player.JobXP, 4), 15));
		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 8)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 3)));
		Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 3)));
		If(Event Player.Plan >= Subtract(3, Value In Array(Event Player.Adv, 4)));
			Set Player Variable(Event Player, Plan, 0);
			Set Player Variable(Event Player, PlanPay, Random Integer(52, 100));
			If(Global Variable(TodayJob) == 4);
				Set Player Variable(Event Player, PlanPay, Round To Integer(Multiply(Player Variable(Event Player, PlanPay), Global Variable(FundTier) >= 3 ? 1.75 : 1.5), To Nearest));
			End;
			Modify Player Variable(Event Player, Money, Add, Event Player.PlanPay);
			Modify Player Variable(Event Player, Earned, Add, Event Player.PlanPay);
			Modify Player Variable(Event Player, Bounty, Add, 200);
			Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 15)));
			Small Message(Event Player, Custom String("역마차를 털었다 — +$ {0}", Event Player.PlanPay));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Purple), Position Of(Event Player), 4);
			Wait(2, Ignore Condition);
			Small Message(Event Player, Custom String("현상금 $ {0} — 이제 쫓기는 몸이다", Event Player.Bounty));
		Else;
			Set Player Variable(Event Player, PlanPay, Random Integer(6, 12));
			If(Global Variable(TodayJob) == 4);
				Set Player Variable(Event Player, PlanPay, Round To Integer(Multiply(Player Variable(Event Player, PlanPay), Global Variable(FundTier) >= 3 ? 1.75 : 1.5), To Nearest));
			End;
			Modify Player Variable(Event Player, Money, Add, Event Player.PlanPay);
			Small Message(Event Player, Custom String("계획 {0}/{1} — 정찰비 $ {2}", Event Player.Plan, Subtract(3, Value In Array(Event Player.Adv, 4)), Event Player.PlanPay));
			Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 50);
		End;
		Set Player Variable(Event Player, Busy, 0);
	}
}
'''

NEW_DOPLAN = '''	actions
	{
		If(Event Player.Energy < 6);
			Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
			Abort;
		End;
		If(Event Player.Plan >= 1);
			Small Message(Event Player, Custom String("이미 역마차를 쫓고 있다 — 보라 구슬을 따라잡아라"));
			Abort;
		End;
		If(Event Player.CowOn >= 1);
			Small Message(Event Player, Custom String("소를 몰면서 습격은 못 한다"));
			Abort;
		End;
		Set Player Variable(Event Player, JobArg, 4);
		Call Subroutine(BecomeJob);
		Set Player Variable At Index(Event Player, JobXP, 4, Add(Value In Array(Event Player.JobXP, 4), 15));
		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 8)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 3)));
		Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 3)));
		Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Value In Array(Global Variable(LocPos), 11)));
		Destroy Effect(Event Player.CowFx);
		Create Effect(All Players(All Teams), Sphere, Color(Purple), Event Player.CowPos, 1.1, Visible To Position Radius and Color);
		Set Player Variable(Event Player, CowFx, Last Created Entity());
		Destroy Icon(Event Player.CowIco);
		Create Icon(All Players(All Teams), Add(Event Player.CowPos, Vector(0, 2.4, 0)), Diamond, Visible To and Position, Color(Purple), True);
		Set Player Variable(Event Player, CowIco, Last Created Entity());
		Destroy Progress Bar HUD Text(Event Player.WorkBar);
		Create Progress Bar HUD Text(Event Player, Min(100, Subtract(Event Player.Plan, 1)), Custom String("역마차 약탈 — 마차에 붙어라"), Top, 0, Color(Purple), Color(White), Visible To Values and Color, Default Visibility);
		Set Player Variable(Event Player, WorkBar, Last Text ID());
		Set Player Variable(Event Player, Plan, 1);
		Big Message(Event Player, Custom String("역마차가 정거장을 떠났다 — 따라붙어서 털어라!"));
		Small Message(Event Player, Custom String("7m 안에 붙어 있으면 약탈이 차오른다 · 호위가 반격한다 · 마을에 닿으면 실패"));
		Play Effect(Event Player, Buff Impact Sound, Color(Purple), Position Of(Event Player), 60);
	}
}

rule("[습격 01] 역마차 추격")
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
		Event Player.Plan >= 1;
	}

	actions
	{
		If(Not(Is Alive(Event Player)));
			Set Player Variable(Event Player, Plan, 0);
			Destroy Effect(Event Player.CowFx);
			Destroy Icon(Event Player.CowIco);
			Destroy Progress Bar HUD Text(Event Player.WorkBar);
			Small Message(Event Player, Custom String("쓰러졌다 — 역마차는 유유히 사라졌다"));
			Abort;
		End;
		If(Distance Between(Event Player.CowPos, Value In Array(Global Variable(LocPos), 0)) < 8);
			Set Player Variable(Event Player, Plan, 0);
			Destroy Effect(Event Player.CowFx);
			Destroy Icon(Event Player.CowIco);
			Destroy Progress Bar HUD Text(Event Player.WorkBar);
			Small Message(Event Player, Custom String("역마차가 마을 경비 안으로 달아났다 — 습격 실패"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 60);
			Abort;
		End;
		Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Event Player.CowPos, Multiply(Direction Towards(Event Player.CowPos, Value In Array(Global Variable(LocPos), 0)), 2.25))));
		If(Distance Between(Position Of(Event Player), Event Player.CowPos) < 7);
			Modify Player Variable(Event Player, Plan, Add, Add(4, Multiply(2, Value In Array(Event Player.Adv, 4))));
			If(Random Integer(1, 100) <= 12);
				Damage(Event Player, Null, 22);
				Small Message(Event Player, Custom String("호위가 쏜다! 떨어지지 마라"));
				Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
			End;
		End;
		If(Event Player.Plan >= 101);
			Set Player Variable(Event Player, Plan, 0);
			Destroy Effect(Event Player.CowFx);
			Destroy Icon(Event Player.CowIco);
			Destroy Progress Bar HUD Text(Event Player.WorkBar);
			Set Player Variable At Index(Event Player, JobXP, 4, Add(Value In Array(Event Player.JobXP, 4), 30));
			Set Player Variable(Event Player, PlanPay, Random Integer(80, 140));
			If(Global Variable(TodayJob) == 4);
				Set Player Variable(Event Player, PlanPay, Round To Integer(Multiply(Player Variable(Event Player, PlanPay), Global Variable(FundTier) >= 3 ? 1.75 : 1.5), To Nearest));
			End;
			Modify Player Variable(Event Player, Money, Add, Event Player.PlanPay);
			Modify Player Variable(Event Player, Earned, Add, Event Player.PlanPay);
			Modify Player Variable(Event Player, Bounty, Add, 200);
			Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 15)));
			Big Message(Event Player, Custom String("역마차를 털었다! +$ {0}", Event Player.PlanPay));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Purple), Position Of(Event Player), 4);
			Wait(2, Ignore Condition);
			Small Message(Event Player, Custom String("현상금 $ {0} — 이제 쫓기는 몸이다", Event Player.Bounty));
			Abort;
		End;
		Wait(0.5, Ignore Condition);
		Loop If(Event Player.Plan >= 1);
	}
}
'''

sub(OLD_DOPLAN, NEW_DOPLAN, 1)

# (소몰이 가드·문구 3종은 별도 수동 적용됨)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)

print("patch133 OK")
