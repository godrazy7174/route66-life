Implement "재건 단계별 언락" (per-stage rebuild perks) in this Overwatch 2 Workshop project by writing ONE Python patch script, patch99_rebuildperks.py. Work non-interactively: never ask questions, decide within this spec, print a final summary report.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,750 lines). ROUTE66_LIFE.ow is the Korean build - do NOT edit it.
- STUDY patch95_ranch.py and patch96_varfix.py for the sub()/block() helpers, chr(9)/chr(10) assembly, assert-counted substitutions, single file write. `# -*- coding: utf-8 -*-` header + Korean docstring.
- Player variables are FULL (128/128): declare NO new player variable. This patch frees one slot by eliminating `Brew` (ownership is equivalent to `BrewVats >= 1`, the exact pattern patch96 used for Ranch/RanchPens) and reuses that slot as `Deposit`.
- Sandbox may block Python (`CreateProcessAsUserW failed: 5`) - if so, hand-apply the patch's exact output to ROUTE66_LIFE_EN.ow only and say validation must be re-run by the caller.
- Validation: python patch99_rebuildperks.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow ("possibly undeclared player vars" warning with bare numbers is pre-existing noise).

# Doctrine
No ternary inside comparison RHS; whole-argument ternary fine. Custom String max 3 args, nest for more. Values shown in Small/Big Messages must be stable during display. Korean inside Custom String as-is (UTF-8).

# Design
Rebuild (player var `Rebuild`, 0-5) currently gives stat perks only. Add one small FEATURE per stage. Stage 5's feature (rebirth) ships in a later patch - nothing to do here.

## Edit 1 - free the slot: Brew -> Deposit
- Declaration (cnt=1): replace `		106: Brew` with `		106: Deposit`.
- `If(Event Player.Brew == 0);` occurs 2 times (brewery build check, vat expansion check): replace both (cnt=2) with `If(Event Player.BrewVats == 0);`.
- `Event Player.Brew == 1;` occurs once (the [양조 01] maturity rule condition): replace (cnt=1) with `Event Player.BrewVats >= 1;`.
- Remove the line `Set Player Variable(Event Player, Brew, 1);` with its indent and newline (cnt=1); the adjacent `Set Player Variable(Event Player, BrewVats, 1);` remains the ownership marker.

## Edit 2 - stage 1 (마을 우물): free water at the village
In rule "[조작 02-2] 물 마시기 (Q)", replace the opening branch line (cnt=1)
`		If(Value In Array(Event Player.Inv, 1) >= 1);`
with an inserted branch BEFORE it, so the chain becomes:
`		If(And(Event Player.Rebuild >= 1, Event Player.Zone == 9));`
(3 tabs body:)
- Set Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 20)));
- Heal(Event Player, Null, 10);
- Small Message(Event Player, Custom String("마을 우물의 물 — 물통이 축나지 않았다 (갈증 {0})", Round To Integer(Event Player.Thirst, Down)));
- Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 50);
then `		Else If(Value In Array(Event Player.Inv, 1) >= 1);` followed by the original body unchanged.
(So: the original If line turns into Else If; everything else in the rule stays.)

## Edit 3 - stage 2 (전신국): 30-second event warning
In rule "[이벤트 01] 주기적 사건 발생", replace (cnt=1)
`		Wait(Random Integer(220, 360), Ignore Condition);`
with
`		Wait(Random Integer(190, 330), Ignore Condition);`
plus, on the following lines (same 2-tab indent):
- Small Message(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Rebuild) >= 2), Custom String("전신국 타전 — 곧 무슨 일이 벌어진다"));
- Play Effect(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Rebuild) >= 2), Buff Impact Sound, Color(Yellow), Vector(0, 0, 0), 9999);
- Wait(30, Ignore Condition);
(Total delay stays 220-360.)

## Edit 4 - stage 3 (마을 은행): deposits
4a. Menu count: `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 4, 4, 1, 1)` occurs EXACTLY 3 times; replace all 3 (cnt=3) with `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 4, 4, 1, 1)` (index 10, zone 9 안내소, 4 -> 6).
4b. Labels (cnt=1): replace `Custom String("마을 재건"), Custom String("-"), Custom String("-")` with `Custom String("마을 재건"), Custom String("은행 예금 — 전액 맡기기"), Custom String("은행 출금 — 전액 찾기")`.
4c. Zone-9 action chain in rule "[조작 03c] 행동 실행 — 안내소·대장간·정거장·목장": the chain currently ends with a bare `Else;` branch (the 마을 재건 logic, starting `				If(Event Player.Rebuild >= 5);`). Replace the anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Event Player.Rebuild >= 5);` with (3 tabs)`Else If(Event Player.MenuIdx == 3);`(newline)(4 tabs)`If(Event Player.Rebuild >= 5);` (cnt=1). Then find the sequence that closes that rebuild branch and opens zone 10: (4 tabs)`End;`(newline)(3 tabs)`End;`(newline)(2 tabs)`Else If(Event Player.Zone == 10);` (cnt=1) and insert between the first End; and the second two new depth-3 branches:
`Else If(Event Player.MenuIdx == 4);` (예금)
- If(Global Variable(RebuildMax) < 3);
  - Small Message(Event Player, Custom String("은행이 아직 재건되지 않았다 — 재건 3단계부터")); plus Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- Else If(Event Player.Money < 1);
  - Small Message(Event Player, Custom String("맡길 돈이 없다")); plus the red debuff sound;
- Else;
  - Modify Player Variable(Event Player, Deposit, Add, Event Player.Money);
  - Set Player Variable(Event Player, Money, 0);
  - Small Message(Event Player, Custom String("전액을 맡겼다 — 예금 $ {0} (강탈과 죽음이 닿지 않는다)", Event Player.Deposit));
  - Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);
- End;
`Else;` (출금, MenuIdx 5)
- If(Event Player.Deposit < 1);
  - Small Message(Event Player, Custom String("예금이 비어 있다")); plus the red debuff sound;
- Else;
  - Modify Player Variable(Event Player, Money, Add, Event Player.Deposit);
  - Set Player Variable(Event Player, Deposit, 0);
  - Small Message(Event Player, Custom String("전액을 찾았다 — 소지금 $ {0}", Event Player.Money));
  - Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);
- End;
4d. Interest - in rule "[월드 05] 아침 정산", insert immediately BEFORE the line `		Set Player Variable(Event Player, DayStart, Event Player.Earned);` (cnt=1):
- If(Event Player.Deposit >= 100);
  - Set Player Variable(Event Player, Amt, Min(200, Round To Integer(Multiply(Event Player.Deposit, 0.01), Down)));
  - Modify Player Variable(Event Player, Deposit, Add, Event Player.Amt);
  - Small Message(Event Player, Custom String("은행 이자 +$ {0} (예금 $ {1})", Event Player.Amt, Event Player.Deposit));
- End;
4e. Wealth rank includes deposits (cnt=1): replace `Subtract(0, Player Variable(Current Array Element, Money))` with `Subtract(0, Add(Player Variable(Current Array Element, Money), Player Variable(Current Array Element, Deposit)))`.
4f. HUD shows deposit (cnt=1): replace `Custom String("소지금   $ {0}", Local Player.Money)` with `Custom String("소지금   $ {0}   예금 $ {1}", Local Player.Money, Local Player.Deposit)`.
4g. Save code includes deposit (cnt=1): replace `Min(9999, Round To Integer(Divide(Event Player.Money, 100), Down))` with `Min(9999, Round To Integer(Divide(Add(Event Player.Money, Event Player.Deposit), 100), Down))` (on restore the sum returns as wallet cash - nothing else to change).

## Edit 5 - stage 4 (오페라 하우스): nightly show at the saloon
Insert a new rule directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor):
rule("[재건 02] 오페라의 밤")
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.Rebuild >= 4; Global Variable(IsNight) == 1; Event Player.Zone == 5; Is Alive(Event Player) == True.
Actions:
- Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 15)));
- Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 1)));
- Small Message(Event Player, Custom String("오페라의 밤 — 무대의 노래가 피로를 씻는다 (피로 +15 · 명성 +1)"));
- Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 80);
- Wait Until(Global Variable(IsNight) == 0, 99999);
(The Wait Until holds the instance until morning so it fires at most once per night.)

## Edit 6 - signboard
The 안내소 signboard contains the line `마을 재건 — 우물에서 기차역까지 다섯 단계, 총 $1,000,000` followed by the literal backslash-r backslash-n sequence (build as chr(92)+'r'+chr(92)+'n'). Append after it (cnt=1): `재건은 기능을 연다 — 우물 물 · 전신국 예고 · 은행 예금 · 오페라의 밤` plus the same newline sequence.

# Deliverables
patch99_rebuildperks.py, applied. Verify and print counts: `106: Deposit` = 1, `Event Player.BrewVats == 0` = 2, `Event Player.BrewVats >= 1;` = 1, `Set Player Variable(Event Player, Brew, 1);` = 0, `마을 우물의 물` = 1, `전신국 타전` = 1, `은행 예금 — 전액 맡기기` = 1, `전액을 맡겼다` = 1, `은행 이자` = 1, `Player Variable(Current Array Element, Deposit)` = 1, `예금 $ {1}` = 2, `rule("[재건 02] 오페라의 밤")` = 1, `재건은 기능을 연다` = 1, `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 4, 4, 1, 1)` = 3. Report what changed, whether validation ran, and the counts. Touch nothing else.
