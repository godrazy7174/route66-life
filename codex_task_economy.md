Three changes in this Overwatch 2 Workshop project via ONE Python patch script patch116_economy.py: remove the price line from bar rumors, remove the redundant wanted-position icon rule, and scale down labor income ~20% across the board. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,291 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted (occurrence counts via str.count), one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch116_economy.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Part A - bar rumor no longer repeats market prices (the scrapyard already sells "오늘의 시세")
Delete these three consecutive lines (anchor on all three together with their indents, cnt=1):
(3 tabs)`Small Message(Event Player, Custom String("소문 — 원석 $ {0}, 가죽 $ {1}", Global Variable(OrePrice), Global Variable(HidePrice)));`(newline)
(3 tabs)`Play Effect(Event Player, Debuff Impact Sound, Color(Sky Blue), Position Of(Event Player), 25);`(newline)
(3 tabs)`Wait(2, Ignore Condition);`(newline)
(The event-rumor message that follows becomes the sole output of 소문 듣기.)

# Part B - remove rule "[수배 01] 전단 노출"
All players share Team 1, so ally outlines already reveal everyone's position - the periodic skull icon is redundant. Delete the ENTIRE rule from its header line `rule("[수배 01] 전단 노출")` through its closing `}` (up to but not including the next rule header `rule("[수배 02] 전단 경고")`; assert both headers occur exactly once before deleting). After deletion assert: `수배 01` occurs 0 times and `WantedIco` occurs exactly 1 time (the variable declaration stays). Rules [수배 02/03/04] stay untouched.

# Part C - labor income scaled down ~20% (dopamine events, transfers, robbery/arrest, contract/mastery payouts stay as they are)
Each replacement cnt=1 unless stated:
1. `Set Global Variable(OrePrice, Random Integer(3, 6));` -> `Set Global Variable(OrePrice, Random Integer(2, 5));`
2. `Set Global Variable(HidePrice, Random Integer(4, 7));` -> `Set Global Variable(HidePrice, Random Integer(3, 6));`
3. `Set Global Variable(OrePrice, 3);` -> `Set Global Variable(OrePrice, 2);` (init)
4. `Set Global Variable(HidePrice, 6);` -> `Set Global Variable(HidePrice, 5);` (init)
5. 금맥: `Random Integer(50, 130)` -> `Random Integer(40, 105)`
6. 연속 채굴: `Multiply(Min(Event Player.Streak, 25), 4)` -> `Multiply(Min(Event Player.Streak, 25), 3)`
7. 채굴 10회 보너스: `Modify Player Variable(Event Player, Money, Add, 25);` -> `..., Add, 20);` (cnt=1)
8. 사냥 고정 보너스 (each pair cnt=1): `Modify Player Variable(Attacker, Money, Add, 250);` -> `Add, 200);` and `Modify Player Variable(Attacker, Earned, Add, 250);` -> `Add, 200);`; `Money, Add, 50);` -> `Add, 40);` and `Earned, Add, 50);` -> `Add, 40);` (the Attacker lines); `Money, Add, 60);` -> `Add, 48);` and `Earned, Add, 60);` -> `Add, 48);` (the Attacker lines)
9. 배달 기본: the fragment `Add(15, Multiply(Distance Between` occurs 2 times (수주 고지 + 정산 재계산): in BOTH, replace `Add(15,` with `Add(12,` and the `, 1.3)` multiplier in those same two lines with `, 1.05)` (each cnt=2; note `, 1.3)` also appears in the 역마차장 +30% line as `, 1.3), To Nearest` - do NOT touch that one; scope the 1.3 replacement to the two Distance-Between lines by replacing the longer fragment `Value In Array(Global Variable(LocPos), Event Player.DelDest)), 1.3)` cnt=2)
10. 소몰이: `Add(165, Multiply(3,` -> `Add(132, Multiply(2.4,`
11. 습격: `Random Integer(65, 125)` -> `Random Integer(52, 100)`; `Random Integer(8, 15)` -> `Random Integer(6, 12)`
12. 금괴 호송: in the line containing `Add(40, Multiply(Distance Between` replace `Add(40,` with `Add(32,` and its trailing `, 2.5)),` with `, 2)),` (scope to that single line, cnt=1)
13. 밀수: in the line containing `Add(30, Multiply(Distance Between` replace `Add(30,` with `Add(24,` and its trailing `, 2.5)),` with `, 2)),` (cnt=1)
14. 목장 출하: `? 70 : 60` -> `? 56 : 48`
15. 밀주 뒷문: `Multiply(Event Player.BrewReady, 60)` -> `Multiply(Event Player.BrewReady, 48)`
16. 미니게임 보상: `Money, Add, 12);` -> `Add, 10);` and `Earned, Add, 12);` -> `Add, 10);` (each cnt=1, the 눈싸움 pair); `Money, Add, 15);` -> `Add, 12);` and `Earned, Add, 15);` -> `Add, 12);` (each cnt=1, the 샛길 pair)
17. 일일 목표: `Set Global Variable(DailyGoal, 480);` -> `..., 384);` and `Set Global Variable(DailyGoal, Add(400, Multiply(Global Variable(Day), 80)));` -> `..., Add(320, Multiply(Global Variable(Day), 64)));`
Also update two signboard/tutorial price mentions if they exist verbatim: `가축 출하 — 마리당 $60` -> `가축 출하 — 마리당 $48` (this text appears 2 times: menu label + signboard; replace both, cnt=2) and `병당 $60` if present (check count; if 0, skip silently - do not assert).

# Deliverables
patch116_economy.py (script alone suffices if execution is blocked). Verification counts for the caller: `소문 — 원석` = 0, `rule("[수배 01]` = 0, `WantedIco` = 1, `Random Integer(2, 5)` = 1, `Random Integer(40, 105)` = 1, `Add(132, Multiply(2.4,` = 1, `? 56 : 48` = 1, `Multiply(Event Player.BrewReady, 48)` = 1, `DailyGoal, 384` = 1, `Add(320, Multiply(Global Variable(Day), 64))` = 1, `가축 출하 — 마리당 $48` = 2. Touch nothing else.
