# -*- coding: utf-8 -*-
"""점검 승인분 다 — 호송 경비 계약.

금괴 호송자가 웅크린 채 [V](근접 공격 키)로 곁 6m 안의 사람을 경비로 지정한다.
인계에 성공할 때 경비가 12m 안에 있으면 경비 $80·명성 +3, 호송자 +$60.
강탈당하거나 죽으면 둘 다 빈손 — 위험을 같이 지는 계약이다.

목적 둘: 현상금 사냥꾼의 평시 일감 부재(수배자가 없으면 할 일이 없는 유일한
직업)와 금괴 호송의 외로움을 한 고리로 푼다. 물론 아무 직업이나 경비를 설 수 있다.

## 설계 결정

- 경비 저장은 `DialTgt` 겸용. 호송 중에는 DialTgt 를 쓰는 다른 활동이 전부 막혀
  있어 안전하다 — 급행(HasParcel 필요), 늑대(CowOn 필요)는 병행 불가이고,
  은행 다이얼은 이번에 짐 게이트에 Escort 를 추가해 막는다(아래).
  수주 시 0 으로 초기화하므로 낡은 급행 마감시각(숫자)이 남아 있어도
  `Entity Exists(숫자) == False` 라 오지급이 없다.
- **은행 짐 게이트에 Escort == 1 추가.** "짐을 진 채로는 금고를 못 딴다"가
  배달·소몰이만 막고 금괴는 안 막고 있었다 — 금괴도 짐이다. 설계 일관성 수정이자
  DialTgt 충돌 차단이다.
- **[거래 01] 송금에 Escort == 0 추가.** 같은 키(웅크리기+V)라 호송 중에는
  경비 지정이 우선한다. 호송 60~90초 동안 송금이 막히는 대가는 감수한다.
- 성공 지급에 12m 거리 조건 — 멀리서 이름만 올린 경비는 못 받는다.
  "함께 걷는" 계약이어야 공짜 돈 버그가 안 된다.

## 영상(서버부하) 준수

새 룰 [경비 01]의 조건은 전부 싼 비교이고, 드물게 참인 `Escort == 1` 을 맨 위에
뒀다(4장 함정·영상 04:33). 배열 함수(Sorted/Filtered)는 버튼을 눌렀을 때만
액션에서 1회 돈다. 지속 엔티티 생성 없음(메시지·소리뿐). 버튼 룰이므로
끝에 Wait Until 디바운스(4장 3번).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old[:70], s.count(old))
    s = s.replace(old, new)


# ── 은행 짐 게이트에 Escort 추가 ───────────────────────────────
sub("				If(Or(Event Player.HasParcel >= 1, Event Player.CowOn >= 1));",
    "				If(Or(Event Player.HasParcel >= 1, Or(Event Player.CowOn >= 1, Event Player.Escort == 1)));")

# ── [거래 01] 송금은 호송 중이 아닐 때만 ───────────────────────
sub("""		Is Button Held(Event Player, Button(Crouch)) == True;
		Is Button Held(Event Player, Button(Melee)) == True;
	}""",
    """		Event Player.Escort == 0;
		Is Button Held(Event Player, Button(Crouch)) == True;
		Is Button Held(Event Player, Button(Melee)) == True;
	}""")

# ── 수주 시 경비 슬롯 초기화 ───────────────────────────────────
sub("""					Set Player Variable(Event Player, Escort, 1);""",
    """					Set Player Variable(Event Player, Escort, 1);
					Set Player Variable(Event Player, DialTgt, 0);""")

# ── [경비 01] 경비 지정 룰 ─────────────────────────────────────
sub("""rule("[호송 02] 금괴 인계 (F 3초)")""",
    """rule("[경비 01] 호송 경비 지정 (웅크리기+V)")
{
	event
	{
		Ongoing - Each Player;
		Team 1;
		All;
	}

	conditions
	{
		Event Player.Escort == 1;
		Is Button Held(Event Player, Button(Crouch)) == True;
		Is Button Held(Event Player, Button(Melee)) == True;
		Is Dummy Bot(Event Player) == False;
		Event Player.Init == 1;
		Event Player.Busy == 0;
		Is Alive(Event Player) == True;
	}

	actions
	{
		If(Or(Event Player.Escort != 1, Not(Is Alive(Event Player))));
			Abort;
		End;
		Set Player Variable(Event Player, Amt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(And(Current Array Element != Event Player, Is Dummy Bot(Current Array Element) == False), And(And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1), And(Player Variable(Current Array Element, TutOn) == 0, Distance Between(Position Of(Current Array Element), Position Of(Event Player)) < 6)))), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
		If(Not(Entity Exists(Event Player.Amt)));
			Small Message(Event Player, Custom String("곁 6m 안에 경비로 세울 사람이 없다"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
		Else;
			Set Player Variable(Event Player, DialTgt, Event Player.Amt);
			Small Message(Event Player, Custom String("{0}을(를) 경비로 세웠다 — 함께 인계 지점에 닿으면 +$60", Event Player.DialTgt));
			Small Message(Event Player.DialTgt, Custom String("{0}의 금괴 호송 경비를 맡았다 — 곁을 지켜라 (성공 시 $80 · 명성 +3)", Event Player));
			Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 70);
		End;
		Wait Until(Or(Not(Is Button Held(Event Player, Button(Crouch))), Not(Is Button Held(Event Player, Button(Melee)))), 3);
	}
}

rule("[호송 02] 금괴 인계 (F 3초)")""")

# ── 성공 지급 ──────────────────────────────────────────────────
sub("""			Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 8)));
			Set Player Variable(Event Player, Escort, 0);""",
    """			Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 8)));
			If(And(Entity Exists(Event Player.DialTgt), And(Is Alive(Event Player.DialTgt), Distance Between(Position Of(Event Player.DialTgt), Position Of(Event Player)) <= 12)));
				Modify Player Variable(Event Player.DialTgt, Money, Add, 80);
				Modify Player Variable(Event Player.DialTgt, Earned, Add, 80);
				Set Player Variable(Event Player.DialTgt, Fame, Min(100, Add(Player Variable(Event Player.DialTgt, Fame), 3)));
				Modify Player Variable(Event Player, Money, Add, 60);
				Modify Player Variable(Event Player, Earned, Add, 60);
				Small Message(Event Player.DialTgt, Custom String("경비 삯을 받았다 — +$80 (명성 +3)"));
				Small Message(Event Player, Custom String("경비 덕에 든든했다 — +$60"));
			End;
			Set Player Variable(Event Player, DialTgt, 0);
			Set Player Variable(Event Player, Escort, 0);""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
