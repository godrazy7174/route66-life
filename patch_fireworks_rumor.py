# -*- coding: utf-8 -*-
"""패치노트 3·4 — 불꽃놀이를 실제로 보이는 쇼로, 술집 소문을 오늘의 판에 맞게.

## 3. 불꽃놀이 (구매해도 아무것도 안 보였다)

원인 둘.

1. `Play Effect` 는 **한 번 터지고 끝나는 순간 효과**다. 지속 시간이 없다.
   구매하는 순간 3발이 동시에 터지고 사라지므로, 술집 밖으로 나가 하늘을 볼 때는
   이미 끝나 있다.
2. 터지는 위치가 **구매자 머리 위**(+18~30m)였다. 구매자는 술집 **안**에 있어
   천장에 가린다.

그래서 즉발 3발을 **[축제 02] 라는 별도 룰의 20발짜리 쇼**로 바꾼다.
구매는 `FireEnd` 에 시작 시각(4초 뒤)만 찍고 즉시 끝나므로 상점 조작을 막지 않는다.
4초는 밖으로 나갈 시간이다. 쇼는 술집(LocPos[5]) **상공 34~48m** 에서 터져
마을 어디서나 올려다보인다.

`While` 로 돌린다 — `Loop If` 는 액션 목록을 처음부터 다시 돌아(4장 17번)
준비 구간이 매 발 반복된다.

**하얀색은 쓰지 않는다** (지시). 낮 하늘에 묻힌다. 노랑·주황·빨강·장미·보라·하늘·연두
일곱 색에서 뽑는다.

## 4. 술집 소문 — 화약을 심었는데 "오늘은 조용하다"

버그는 아니었다. 소문은 `Global Variable(EventKind)`(주기적 세계 이벤트: 금맥 소동,
모래폭풍 등) 하나만 읽었고, 그 0번이 "오늘은 조용하다"다. 열차·대사냥·쥐 같은
**오늘의 큰 판을 아예 보지 않았다.**

우선순위를 두어 실제로 벌어지는 일을 알려준다:
열차 발파 준비됨 > 열차의 날 > 대사냥 > 쥐떼 > 주기 이벤트 > 조용하다.
화약을 심어둔 사람에게는 "누가 철길목에 손을 댔다"가 뜬다 — 심은 본인만 아는 정보가
아니라 술집에서 살 수 있는 정보가 되어, 금고 앞 눈치 싸움의 재료가 된다.

전역 89: FireEnd (쇼 시작 시각), 90: FireN (발수 카운터), 91: FirePos (터지는 자리).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


# ── 전역 ───────────────────────────────────────────────────────
sub("""		88: RatPop
""", """		88: RatPop
		89: FireEnd
		90: FireN
		91: FirePos
""")
sub("""		Set Global Variable(JerkyStock, 15);
""", """		Set Global Variable(JerkyStock, 15);
		Set Global Variable(FireEnd, 0);
""")

# ── 3. 구매는 예약만 한다 ──────────────────────────────────────
sub("""				Big Message(All Players(All Teams), Custom String("{0}이(가) 하늘에 불꽃을 쏘아 올렸다!!", Event Player));
					Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Position Of(Event Player), Vector(0, 18, 0)), 8);
					Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Add(Position Of(Event Player), Vector(-6, 24, 4)), 6);
					Play Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Add(Position Of(Event Player), Vector(5, 30, -5)), 7);
					Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 250);""",
    """				Set Global Variable(FireEnd, Add(Total Time Elapsed(), 4));
					Big Message(All Players(All Teams), Custom String("{0}이(가) 불꽃을 사들였다 — 밖으로 나가 하늘을 봐라!", Event Player));
					Play Effect(All Players(All Teams), Buff Impact Sound, Color(Yellow), Position Of(Event Player), 200);""")

# ── 3. 쇼 룰 ───────────────────────────────────────────────────
sub("""rule("[열차 04] 철길목 표식 — 열차의 날 내내")""",
    """rule("[축제 02] 불꽃놀이")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Global Variable(FireEnd) > 0;
		Total Time Elapsed() >= Global Variable(FireEnd);
	}

	actions
	{
		Set Global Variable(FireEnd, 0);
		Set Global Variable(FireN, 0);
		Big Message(All Players(All Teams), Custom String("하늘이 열린다 — 불꽃놀이!"));
		While(Global Variable(FireN) < 20);
			Set Global Variable(FirePos, Add(Value In Array(Global Variable(LocPos), 5), Vector(Random Real(-14, 14), Random Real(34, 48), Random Real(-14, 14))));
			Play Effect(All Players(All Teams), Ring Explosion, Random Value In Array(Array(Color(Yellow), Color(Orange), Color(Red), Color(Rose), Color(Purple), Color(Sky Blue), Color(Lime Green))), Global Variable(FirePos), Random Real(7, 13));
			Play Effect(All Players(All Teams), Good Explosion, Random Value In Array(Array(Color(Yellow), Color(Orange), Color(Rose), Color(Sky Blue))), Global Variable(FirePos), Random Real(4, 8));
			Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Global Variable(FirePos), 200);
			Modify Global Variable(FireN, Add, 1);
			Wait(Random Real(0.45, 0.85), Ignore Condition);
		End;
		Set Global Variable(TickerMsg, Custom String("불꽃이 사그라들었다"));
		Set Global Variable(TickerEnd, Add(Total Time Elapsed(), 3));
	}
}

rule("[열차 04] 철길목 표식 — 열차의 날 내내")""")

# ── 4. 소문이 오늘의 판을 본다 ─────────────────────────────────
sub("""				Small Message(Event Player, Value In Array(Array(Custom String("소문 — 오늘은 조용하다"), Custom String("소문 — 금맥 소동이 벌어졌다!"), Custom String("소문 — 모래폭풍이 온다"), Custom String("소문 — 야수들이 사납게 날뛴다"), Custom String("소문 — 역마차가 들어왔다"), Custom String("소문 — 누군가 누명을 썼다"), Custom String("소문 — 금광이 무너지고 있다")), Global Variable(EventKind)));""",
    """				Small Message(Event Player, Global Variable(PowderSet) == 1 ? Custom String("소문 — 누가 철길목에 손을 댔다더군. 저녁 8시를 노려라") : Custom String("{0}", And(Modulo(Global Variable(Day), 3) == 0, Global Variable(IsNight) == 0) ? Custom String("소문 — 오늘 저녁 8시 열차가 선다. 대장간 화약이 동날 게다") : Custom String("{0}", Global Variable(HuntPhase) >= 1 ? Custom String("소문 — 큰 놈이 돌아다닌다. 주황 흔적을 쫓아라") : Custom String("{0}", Global Variable(RatOn) == 1 ? Custom String("소문 — 쥐떼가 잡화점을 털고 있다!") : Value In Array(Array(Custom String("소문 — 오늘은 조용하다"), Custom String("소문 — 금맥 소동이 벌어졌다!"), Custom String("소문 — 모래폭풍이 온다"), Custom String("소문 — 야수들이 사납게 날뛴다"), Custom String("소문 — 역마차가 들어왔다"), Custom String("소문 — 누군가 누명을 썼다"), Custom String("소문 — 금광이 무너지고 있다")), Global Variable(EventKind))))));""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
