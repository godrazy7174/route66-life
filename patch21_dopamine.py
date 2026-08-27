# -*- coding: utf-8 -*-
"""도파민 주기 보강.

기존은 '금맥' 같은 큰 한 방에 몰려 있고 중간 리듬이 비어 있었다.
서로 다른 주기로 터지도록 다섯 갈래를 추가한다.

  초 단위   : 연속 채굴 콤보 (5연속마다 보너스가 커짐)
  십초~분   : 길 위의 발견 (황야를 걷다 무작위로 줍는다)
  2~4분     : 보물 상자 (전체 공지 + 선착순 경쟁)
  세션      : 칭호 승급 전체 공지
  2~4분     : 월드 이벤트 3종 -> 6종
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

TIER_IDX = ('Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), '
            'Event Player.Money >= 2500), Event Player.Money >= 6000), Event Player.Money >= 15000)')
TIER_NAME = ('Value In Array(Array(Custom String("떠돌이"), Custom String("일꾼"), Custom String("정착민"), '
             'Custom String("유지"), Custom String("거상"), Custom String("66번 국도의 주인")), %s)' % TIER_IDX)

# ── 변수 ────────────────────────────────────────────────────────────
s = s.replace("\t\t26: BeastTimer\n",
              "\t\t26: BeastTimer\n\t\t27: TreasurePos\n\t\t28: TreasureOn\n\t\t29: TreasureIco\n\t\t30: TreasureFx\n\t\t31: SellMult\n")
s = s.replace("\t\t17: Streak\n", "\t\t15: Tier\n\t\t16: LastMine\n\t\t17: Streak\n")
s = s.replace("\t\tSet Global Variable(BeastTimer, Array(0, 0, 0));",
              "\t\tSet Global Variable(BeastTimer, Array(0, 0, 0));\n\t\tSet Global Variable(TreasureOn, 0);\n\t\tSet Global Variable(SellMult, 1);")

# ── 1) 연속 채굴 콤보 ──────────────────────────────────────────────
s = s.replace('''		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 5)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 2)));
		Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2.5)));
		Set Player Variable(Event Player, Busy, 0);''',
'''		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 5)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 2)));
		Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2.5)));
		If(Subtract(Total Time Elapsed(), Event Player.LastMine) > 25);
			Set Player Variable(Event Player, Streak, 0);
		End;
		Set Player Variable(Event Player, LastMine, Total Time Elapsed());
		Modify Player Variable(Event Player, Streak, Add, 1);
		If(Modulo(Event Player.Streak, 5) == 0);
			Set Player Variable(Event Player, Roll, Multiply(Event Player.Streak, 6));
			Modify Player Variable(Event Player, Money, Add, Event Player.Roll);
			Modify Player Variable(Event Player, Earned, Add, Event Player.Roll);
			Big Message(Event Player, Custom String("{0}연속 채굴!   +$ {1}", Event Player.Streak, Event Player.Roll));
			Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1.5);
		End;
		Set Player Variable(Event Player, Busy, 0);''')

# ── 2~4) 신규 규칙 ─────────────────────────────────────────────────
NEW = '''
rule("[도파민 01] 길 위의 발견")
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
		Event Player.Zone == -1;
		Is Alive(Event Player) == True;
		Is Moving(Event Player) == True;
	}

	actions
	{
		Wait(18, Ignore Condition);
		If(Random Integer(1, 100) <= 12);
			Set Player Variable(Event Player, Roll, Random Integer(1, 100));
			If(Event Player.Roll <= 55);
				Set Player Variable(Event Player, Amt, Random Integer(20, 70));
				Modify Player Variable(Event Player, Money, Add, Event Player.Amt);
				Modify Player Variable(Event Player, Earned, Add, Event Player.Amt);
				Small Message(Event Player, Custom String("길바닥에서 낡은 지갑을 주웠다 — $ {0}", Event Player.Amt));
			Else If(Event Player.Roll <= 85);
				Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 2));
				Small Message(Event Player, Custom String("버려진 보급품을 찾았다 — 육포 +2"));
			Else;
				Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 6));
				Small Message(Event Player, Custom String("드러난 광맥 조각 — 원석 +6"));
			End;
			Play Effect(Event Player, Good Pickup Effect, Color(Yellow), Position Of(Event Player), 1.5);
		End;
		Loop();
	}
}

rule("[도파민 02] 보물 상자 출현")
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
		Wait(Random Integer(150, 240), Ignore Condition);
		Set Global Variable(TreasurePos, Add(Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 10)), Vector(Random Real(-14, 14), 0, Random Real(-14, 14)))), Vector(0, 1, 0)));
		Set Global Variable(TreasureOn, 1);
		Create Effect(All Players(All Teams), Sphere, Color(Yellow), Global Variable(TreasurePos), 1.2, Visible To Position Radius and Color);
		Set Global Variable(TreasureFx, Last Created Entity());
		Create Icon(All Players(All Teams), Global Variable(TreasurePos), Diamond, Visible To and Position, Color(Yellow), True);
		Set Global Variable(TreasureIco, Last Created Entity());
		Big Message(All Players(All Teams), Custom String("어딘가에 보물 상자가 떨어졌다 — 먼저 닿는 사람이 임자"));
		Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Global Variable(TreasurePos), 200);
		Wait Until(Global Variable(TreasureOn) == 0, 90);
		Set Global Variable(TreasureOn, 0);
		Destroy Effect(Global Variable(TreasureFx));
		Destroy Icon(Global Variable(TreasureIco));
		Loop();
	}
}

rule("[도파민 03] 보물 획득")
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
		Global Variable(TreasureOn) == 1;
		Is Alive(Event Player) == True;
		Distance Between(Position Of(Event Player), Global Variable(TreasurePos)) <= 3;
	}

	actions
	{
		Set Global Variable(TreasureOn, 0);
		Set Player Variable(Event Player, Amt, Random Integer(200, 500));
		Modify Player Variable(Event Player, Money, Add, Event Player.Amt);
		Modify Player Variable(Event Player, Earned, Add, Event Player.Amt);
		Big Message(All Players(All Teams), Custom String("{0} — 보물 상자를 차지했다!  $ {1}", Event Player, Event Player.Amt));
		Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 4);
	}
}

rule("[도파민 04] 칭호 승급")
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
		TIERIDX > Event Player.Tier;
	}

	actions
	{
		Wait(1, Ignore Condition);
		Set Player Variable(Event Player, Tier, TIERIDX);
		Big Message(All Players(All Teams), Custom String("{0} — 이제 『 {1} 』", Event Player, TIERNAME));
		Play Effect(All Players(All Teams), Ring Explosion, Color(Lime Green), Position Of(Event Player), 4);
		Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 200);
	}
}
'''.replace('TIERIDX', TIER_IDX).replace('TIERNAME', TIER_NAME)
s = s.replace('\nrule("[이벤트 01] 주기적 사건 발생")', NEW + '\nrule("[이벤트 01] 주기적 사건 발생")')

# ── 5) 월드 이벤트 3종 -> 6종 ──────────────────────────────────────
s = s.replace('Set Global Variable(EventKind, Random Integer(1, 3));', 'Set Global Variable(EventKind, Random Integer(1, 6));')
s = s.replace('''		Else;
			Set Global Variable(BotBounty, 40);
			Big Message(All Players(All Teams), Custom String("무법자 습격! 현상금 3배"));
		End;''',
'''		Else If(Global Variable(EventKind) == 3);
			Set Global Variable(BotBounty, 40);
			Big Message(All Players(All Teams), Custom String("무법자 습격! 현상금 3배"));
		Else If(Global Variable(EventKind) == 4);
			Set Global Variable(SellMult, 2);
			Big Message(All Players(All Teams), Custom String("역마차 도착! 90초 동안 원석·가죽이 두 배 값에 팔린다"));
		Else If(Global Variable(EventKind) == 5);
			Set Global Variable(Tmp, Random Value In Array(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Init) == 1)));
			If(Entity Exists(Global Variable(Tmp)));
				Modify Player Variable(Global Variable(Tmp), Bounty, Add, 300);
				Big Message(All Players(All Teams), Custom String("{0}에게 누명이 씌워졌다 — 현상금 $300", Global Variable(Tmp)));
				Small Message(Global Variable(Tmp), Custom String("억울하지만 쫓기게 됐다. 보안관 초소에서 벌금을 내면 지워진다"));
			End;
		Else;
			Big Message(All Players(All Teams), Custom String("금광이 무너진다! 채굴 수확 3배, 대신 다칠 각오를 해라"));
		End;''')
s = s.replace('''		Wait(90, Ignore Condition);
		Set Global Variable(EventKind, 0);
		Set Global Variable(BotBounty, 12);''',
'''		Wait(90, Ignore Condition);
		Set Global Variable(EventKind, 0);
		Set Global Variable(SellMult, 1);
		Set Global Variable(BotBounty, 12);''')

# 금광 붕괴: 채굴 수확 3배 + 피해
s = s.replace('''			If(Global Variable(EventKind) == 1);
				Modify Player Variable(Event Player, Roll, Multiply, 2);
			End;''',
'''			If(Global Variable(EventKind) == 1);
				Modify Player Variable(Event Player, Roll, Multiply, 2);
			End;
			If(Global Variable(EventKind) == 6);
				Modify Player Variable(Event Player, Roll, Multiply, 3);
				Damage(Event Player, Null, 15);
			End;''')

# 역마차: 판매액에 배율 적용
s = s.replace('Set Player Variable(Event Player, Roll, Multiply(Event Player.Amt, Global Variable(OrePrice)));',
              'Set Player Variable(Event Player, Roll, Multiply(Multiply(Event Player.Amt, Global Variable(OrePrice)), Global Variable(SellMult)));')
s = s.replace('Set Player Variable(Event Player, Roll, Multiply(Event Player.Amt, Global Variable(HidePrice)));',
              'Set Player Variable(Event Player, Roll, Multiply(Multiply(Event Player.Amt, Global Variable(HidePrice)), Global Variable(SellMult)));')

# 소문 듣기 문구 확장
s = s.replace('Value In Array(Array(Custom String("소문 — 오늘은 조용하다"), Custom String("소문 — 금맥 소동이 벌어졌다!"), Custom String("소문 — 모래폭풍이 온다"), Custom String("소문 — 무법자들이 몰려왔다")), Global Variable(EventKind))',
              'Value In Array(Array(Custom String("소문 — 오늘은 조용하다"), Custom String("소문 — 금맥 소동이 벌어졌다!"), Custom String("소문 — 모래폭풍이 온다"), Custom String("소문 — 무법자들이 몰려왔다"), Custom String("소문 — 역마차가 들어왔다"), Custom String("소문 — 누군가 누명을 썼다"), Custom String("소문 — 금광이 무너지고 있다")), Global Variable(EventKind))')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
for k, label in [('연속 채굴!', '콤보'), ('길바닥에서 낡은 지갑', '길 위의 발견'),
                 ('보물 상자를 차지했다', '보물 상자'), ('이제 『 {1} 』', '칭호 승급'),
                 ('역마차 도착!', '역마차'), ('누명이 씌워졌다', '현상수배'), ('금광이 무너진다', '금광 붕괴')]:
    print('  %-12s %s' % (label, '추가됨' if k in s else '!! 실패'))
