# -*- coding: utf-8 -*-
"""열차의 날 안내 강화 — "화약을 심었는데 8시에 아무 일도 없다"의 원인 제거.

실기 제보: 화약을 사고 심어두는 것까지는 알겠는데 그 뒤에 뭘 해야 하는지 모르겠고,
저녁 8시가 되어도 아무 일도 없어 보인다.

[열차 02]의 상태 기계(3·6·9일차 x Clock 1200)와 TrainPos 는 정상이었다.
진짜 원인은 셋이다.

1. [열차 01]은 TrainPos 5m 안에서만 발동하는데, 벗어나 있으면 F 를 눌러도
   아무 반응이 없다 (실패 메시지조차 없다). 철길목에는 가까이 가야 보이는
   작은 간판 하나뿐이라 애초에 찾아가기가 어렵다.
   -> 열차의 날 내내 철길목에 주황 표식 아이콘을 세우고([열차 04]),
      화약을 든 사람의 HUD 에 남은 거리를 미터로 띄운다. 5m 안이면 "지금이다".

2. 화약이 안 심긴 채 8시가 되면 티커 한 줄로만 알려준다 — 놓치기 쉽다.
   -> Big Message 로 올리고, 왜 안 섰는지와 다음에 뭘 해야 하는지를 같이 적는다.
      1분 전(Clock 1080) 예고도 추가한다.

3. 금고를 뜯어도 지갑에 돈이 안 들어온다. 장물 자루에 쌓이고 은신처에서
   정산해야 현금이 되며 죽으면 전액 소실인데, 메시지는 "+$500"이라 이미 받은 것처럼 보인다.
   -> 자루에 담겼다는 것과 은신처 정산이 필요하다는 것을 명시한다.

전역 82: TrainWay (철길목 상시 표식 핸들) 신규.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:60], s.count(old))
    s = s.replace(old, new)


# ── 1. 전역 슬롯 추가 ──────────────────────────────────────────
sub("""		81: PickN
""", """		81: PickN
		82: TrainWay
""")

# ── 2. HUD 안내줄 — 거리와 남은 시간을 보여준다 ────────────────
sub(
    'Global Variable(PowderSet) == 1 ? Custom String("열차의 날 — 저녁 8시, 협곡 철길목에 열차가 선다")'
    ' : Custom String("{0}", Local Player.HasPowder == 1 ?'
    ' Custom String("열차의 날 — 협곡 철길목에 [F] 8초로 화약을 묻어라")'
    ' : Custom String("{0}", Custom String("열차의 날 — 대장간에서 화약 $200을 사라")))',

    'Global Variable(PowderSet) == 1 ?'
    ' Custom String("화약을 심었다 — 저녁 8시까지 {0}분, 철길목을 지켜라",'
    ' Round To Integer(Divide(Subtract(1200, Global Variable(Clock)), 120), Up))'
    ' : Custom String("{0}", Local Player.HasPowder == 1 ?'
    ' Custom String("{0}", Distance Between(Position Of(Local Player), Global Variable(TrainPos)) < 5 ?'
    ' Custom String("열차의 날 — 지금이다! [F]를 8초 누르고 있어라")'
    ' : Custom String("열차의 날 — 철길목까지 {0}m, 주황 표식을 따라가라",'
    ' Round To Integer(Distance Between(Position Of(Local Player), Global Variable(TrainPos)), Down)))'
    ' : Custom String("{0}", Custom String("열차의 날 — 대장간에서 화약 $200을 사라")))')

# ── 3. 화약이 없어 열차가 지나갈 때 — 티커에서 Big Message 로 ──
sub("""		If(Global Variable(PowderSet) == 0);
			Set Global Variable(TickerMsg, Custom String("열차가 협곡을 무사히 지나갔다"));
			Set Global Variable(TickerEnd, Add(Total Time Elapsed(), 3));""",
    """		If(Global Variable(PowderSet) == 0);
			Big Message(All Players(All Teams), Custom String("열차가 그냥 지나갔다 — 철길목에 화약이 없었다"));
			Set Global Variable(TickerMsg, Custom String("다음 열차는 사흘 뒤 — 대장간 화약 $200을 철길목에 묻어야 선다"));
			Set Global Variable(TickerEnd, Add(Total Time Elapsed(), 5));""")

# ── 4. 8시 1분 전 예고 ─────────────────────────────────────────
sub("""		Wait Until(And(Modulo(Global Variable(Day), 3) == 0, Global Variable(Clock) >= 1200), 99999);
		If(Global Variable(PowderSet) == 0);""",
    """		Wait Until(And(Modulo(Global Variable(Day), 3) == 0, Global Variable(Clock) >= 1080), 99999);
		If(Global Variable(PowderSet) == 1);
			Big Message(All Players(All Teams), Custom String("1분 뒤 열차가 선다 — 철길목으로 모여라"));
		Else;
			Big Message(All Players(All Teams), Custom String("1분 뒤 열차 — 아직 화약이 없다! 대장간 $200, 철길목에서 [F] 8초"));
		End;
		Wait Until(And(Modulo(Global Variable(Day), 3) == 0, Global Variable(Clock) >= 1200), 99999);
		If(Global Variable(PowderSet) == 0);""")

# ── 5. 열차가 떠날 때 자루 정산을 상기시킨다 ───────────────────
sub("""			Set Global Variable(TickerMsg, Custom String("열차가 다시 움직인다 — 강도극이 끝났다"));""",
    """			Set Global Variable(TickerMsg, Custom String("열차가 다시 움직인다 — 자루를 진 자는 은신처에서 정산해라"));""")

# ── 6. 금고 보상이 '자루'라는 것을 명시 ────────────────────────
sub("""			Set Global Variable(TickerMsg, Custom String("{0}이(가) 열차 금고를 뜯었다! (+$ {1}) — 남은 금고 {2}", Event Player, Event Player.Loot, Global Variable(TrainVault)));""",
    """			Set Global Variable(TickerMsg, Custom String("{0}이(가) 열차 금고를 뜯었다! 자루에 $ {1} — 남은 금고 {2}", Event Player, Event Player.Loot, Global Variable(TrainVault)));
			Big Message(Event Player, Custom String("금고를 뜯었다 — 자루에 $ {0}. 은신처에서 부려야 돈이 된다", Event Player.Loot));""")

# ── 7. [열차 04] 철길목 상시 표식 ──────────────────────────────
sub("""rule("[열차 03] 금고 개방 (F 5초)")""",
    """rule("[열차 04] 철길목 표식 — 열차의 날 내내")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Global Variable(Ready) == 1;
		Modulo(Global Variable(Day), 3) == 0;
	}

	actions
	{
		Destroy Icon(Global Variable(TrainWay));
		Create Icon(All Players(All Teams), Add(Global Variable(TrainPos), Vector(0, 3.5, 0)), Bolt, Visible To and Position, Color(Orange), True);
		Set Global Variable(TrainWay, Last Created Entity());
		Set Global Variable(TickerMsg, Custom String("철길목에 주황 표식이 섰다 — 저녁 8시, 열차"));
		Set Global Variable(TickerEnd, Add(Total Time Elapsed(), 4));
		Wait Until(Modulo(Global Variable(Day), 3) != 0, 99999);
		Destroy Icon(Global Variable(TrainWay));
	}
}

rule("[열차 03] 금고 개방 (F 5초)")""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
