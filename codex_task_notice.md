# 작업: Big Message 44곳을 즉시 갱신 알림 줄로 이전 (ROUTE66_LIFE_EN.ow)

대상 파일: `ROUTE66_LIFE_EN.ow` (오버워치 워크샵 스크립트, UTF-8, 들여쓰기는 탭). 이 파일만 수정하라. `ROUTE66_LIFE.ow`는 절대 건드리지 말 것. Python 실행 금지 — 텍스트 편집만 하라. 검증은 의뢰인이 별도로 수행한다.

## A. 전역 변수 4개 선언

`variables` 블록의 `global:` 목록 끝, `\t\t65: WeakFx` 바로 다음 줄에 (같은 들여쓰기로) 추가:

```
		66: NoticeMsg
		67: NoticeEnd
		68: TickerMsg
		69: TickerEnd
```

## B. 새 규칙 삽입

`rule("[세금 01] 징수원 도착")` 줄 **바로 앞**에 아래 규칙을 그대로 삽입 (뒤에 빈 줄 1개 포함, 들여쓰기는 탭):

```
rule("[알림 01] 알림 줄 생성")
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
	}

	actions
	{
		Create HUD Text(Event Player, Total Time Elapsed() < Value In Array(Global Variable(NoticeEnd), Slot Of(Event Player)) ? Value In Array(Global Variable(NoticeMsg), Slot Of(Event Player)) : Null, Null, Null, Top, 2, Color(Orange), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);
		Create HUD Text(Event Player, Total Time Elapsed() < Global Variable(TickerEnd) ? Global Variable(TickerMsg) : Null, Null, Null, Top, 3, Color(White), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);
	}
}
```

## C. 서버 티커 이전 — 22곳

아래 문자열을 포함하는 `Big Message(All Players(All Teams), X);` 한 줄을, **같은 들여쓰기의 두 줄**로 교체하라. `X`는 원래 Big Message의 두 번째 인자 전체(Custom String(...) 표현식)를 **한 글자도 바꾸지 말고** 그대로 옮긴다:

```
Set Global Variable(TickerMsg, X);
Set Global Variable(TickerEnd, Add(Total Time Elapsed(), 6));
```

대상 문자열 (각 1곳):
1. `오늘의 계약 — {0} (달성 시 $150 · 명성 +3)`
2. `{0}일차 — 새 아침. 원석 ${1} / 가죽 ${2}`
3. `해가 졌다 — 마을의 불이 꺼진다`
4. `동이 텄다 — 마을에 다시 불이 들어온다`
5. `{0}의 밀주 {1}병이 단속에 걸렸다 — 전량 몰수!`
6. `{0} — 금맥 발견! $ {1}`
7. `거대한 야수다! 체력 5배 — 가죽도 5배`
8. `{0} — 거대한 야수를 쓰러뜨렸다! 가죽 +{1}장 + $50`
9. `{0} — 큰 놈을 잡았다! 가죽 +{1}장 + $60`
10. `{0}이(가) {1}을(를) 체포했다 — 현상금 $ {2}`
11. `{0}이(가) {1}에게서 $ {2}를 강탈했다`
12. `{0}이(가) {1}의 화물을 가로챘다! (+$ {2})`
13. `{0}이(가) {1}의 밀수 화물을 가로챘다! (+$80)`
14. `{0}이(가) {1}의 금괴 호송을 털었다! (+$120)`
15. `열차가 협곡을 무사히 지나갔다`
16. `열차가 다시 움직인다 — 강도극이 끝났다`
17. `{0}이(가) 열차 금고를 뜯었다! (+$ {1}) — 남은 금고 {2}`
18. `흔적을 찾았다 — 냄새가 짙어진다. 다음 표식으로`
19. `{0}이(가) 수배범 {1}을(를) 처단했다 — $ {2}`
20. `{0}이(가) {1}을(를) 살해했다 — 현상금 $ {2}`
21. `{0}이(가) 금고 마차를 털었다! (+$ {1}, 악명 +10)`
22. `{0} — 보물 상자를 차지했다!  $ {1}`

## D. 개인 알림 줄 이전 — 22곳

아래 문자열을 포함하는 `Big Message(Event Player, X);` 한 줄을, **같은 들여쓰기의 두 줄**로 교체하라 (`X`는 동일하게 그대로 이관):

```
Set Global Variable At Index(NoticeMsg, Slot Of(Event Player), X);
Set Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 5));
```

대상 문자열:
1. `화물 접수 — {0}까지! 기본 보수 $ {1}`
2. `소가 벌판에 있다 — 몸으로 밀어 우리로!`
3. `전직 — {0}`
4. `곡괭이의 박자 — 결을 읽어라`
5. `광산주의 눈 — 이번 수확 2배!`
6. `채굴 {0}회 달성 — 보너스 $25`
7. `오늘의 계약 달성! +$150 · 명성 +3` — **동일 문자열 4곳 전부 교체**
8. `{0}연속 채굴!   +$ {1}`
9. `크아앙! 엄청 무서운 야수가 나타났다!`
10. `잘 잤다 — 피로 {0}`
11. `배달 완료!   +$ {0}`
12. `우리에 몰아넣었다!   +$ {0}   (잡화점 육포 재고 +6)`
13. `장물을 부렸다 — +$ {0}`
14. `밀주가 익었다 — {0}병. 술집 뒷문이 기다린다`
15. `소가 통통하게 컸다 — {0}마리 출하 준비 완료`
16. `돌보지 않은 우리 — 야윈 소 {0}마리뿐이다`
17. `샛길이 보인다 — 7초 안에 빛기둥을 밟아라!`
18. `그림자 강도가 따라붙었다 — 쏴서 떨쳐내라! (붉은 그림자)`
19. `소가 성났다 — 고삐의 때를 노려라!`

(7번이 4곳이라 총 22곳)

## 금지 사항

- `{0}이(가) 당신을 체포하려 한다`와 `{0}이(가) 총을 겨눴다` 가 포함된 Big Message 2곳은 **절대 변경 금지** (Big 유지 결정).
- 위에 명시되지 않은 어떤 줄도 수정·삭제·재정렬하지 말 것. Small Message는 전부 그대로.
- 탭 들여쓰기 유지. 줄 끝 공백 추가 금지.

## 완료 기준 (자체 확인)

- `Set Global Variable(TickerMsg` 정확히 22줄
- `Set Global Variable At Index(NoticeMsg` 정확히 22줄
- `Big Message(` 가 121곳 → 77곳으로 감소
- `rule("` 개수 121 → 122
- 마지막에 위 4개 수치를 보고하라.
