Replace the three reaction-tap micro-events (채굴 정타 / 배달 흔들리는 화물 / 소몰이 날뛰는 소) with a proper sweeping skill-check bar (a bar with a highlighted hit zone; a cursor sweeps back and forth; the player presses the key while the cursor is inside the zone), via ONE Python patch script patch105_skillbar.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,109 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted, block() assembly, rule-scoped index scanning where noted, one write, UTF-8 header, Korean docstring.
- Player variables are FULL: NO new variables. The bar reuses `WorkProg` (cursor position, chased 0..16), `KeyHud` (the bar HUD text id), and `Roll` (result: -1 pending / 0 miss / 1 hit) - all free in these contexts because Busy gating prevents overlap.
- Validation (run if possible): python patch105_skillbar.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens. Custom String max 3 args. HUD texts re-evaluate their values live (that is what animates the bar). Korean as-is.

# Design - the shared bar
17 cells, indices 0..16. Hit zone = cells 6..10. Cell glyphs: track `□`, zone `■`, cursor `◆` (cursor replaces whatever cell it is on). The bar HUD shows one of 17 precomputed Custom String literals selected by the cursor variable, e.g. cursor at 0: `◆□□□□□■■■■■□□□□□□`, cursor at 8: `□□□□□□■■◆■■□□□□□□`. Build the 17 literals programmatically in Python.
Sweep: WorkProg chased 0->16 in 0.9s, then 16->0 in 0.9s, up to 4 half-sweeps (~3.6s max). Pressing [R] (Button(Reload)) at any moment evaluates: hit if the rounded cursor is 6..10. Holding [R] in advance just evaluates instantly at the edge = natural miss, so no separate anti-mash logic is needed.

## Edit 1 - subroutine declaration
Replace (cnt=1) `	1: SetupPlayer` with `	1: SetupPlayer` + newline + `	2: DoSkillBar` (index 2 is free).

## Edit 2 - subroutine rule
Insert directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor):
rule("[스킬바 01] DoSkillBar")
event: Subroutine; DoSkillBar.
Actions:
- Set Player Variable(Event Player, Roll, -1);
- Set Player Variable(Event Player, WorkProg, 0);
- Destroy HUD Text(Event Player.KeyHud);
- Create HUD Text(Event Player, Null, Value In Array(Array(<the 17 bar literals>), Min(16, Max(0, Round To Integer(Event Player.WorkProg, To Nearest)))), Custom String("◆가 ■ 구간에 올 때 [{0}]", Input Binding String(Button(Reload))), Top, 1, Color(White), Color(Orange), Color(Gray), Visible To Sort Order String and Color, Default Visibility);
- Set Player Variable(Event Player, KeyHud, Last Text ID());
- then FOUR half-sweep blocks; odd blocks chase to 16, even blocks chase to 0. Each half-sweep block is:
  If(Event Player.Roll == -1);
  	Chase Player Variable Over Time(Event Player, WorkProg, <16 or 0>, 0.9, Destination and Duration);
  	Wait Until(Is Button Held(Event Player, Button(Reload)), 0.9);
  	If(Is Button Held(Event Player, Button(Reload)));
  		Stop Chasing Player Variable(Event Player, WorkProg);
  		Set Player Variable(Event Player, Roll, 0);
  		If(And(Round To Integer(Event Player.WorkProg, To Nearest) >= 6, Round To Integer(Event Player.WorkProg, To Nearest) <= 10));
  			Set Player Variable(Event Player, Roll, 1);
  		End;
  	End;
  End;
- after the four blocks:
- Stop Chasing Player Variable(Event Player, WorkProg);
- Destroy HUD Text(Event Player.KeyHud);
- Set Player Variable(Event Player, WorkProg, 0);
- If(Event Player.Roll == -1);
- 	Set Player Variable(Event Player, Roll, 0);
- End;
(Caller reads Roll: 1 = hit, 0 = miss/timeout. Caller shows all flavor messages.)

## Edit 3 - mining rewire
In rule "[직업 01] DoMine", locate the span from the line `		Wait(Random Real(0.3, 0.8), Ignore Condition);` (cnt=1) through the matching `		End;` that closes the QTE chain, i.e. everything up to but NOT including the line `		If(Modulo(Event Player.MineCount, 10) == 0);`. Assert the span contains `광맥이 울렸다` and `If(Random Integer(1, 100) > 30);` before deleting it. Replace the whole span with (depth 2 base):
- If(Random Integer(1, 100) <= 30);
  - Small Message(Event Player, Custom String("광맥이 울렸다 — 결을 노려라!"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 45);
  - Call Subroutine(DoSkillBar);
  - If(Event Player.Roll == 1);
    - Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 2));
    - Small Message(Event Player, Custom String("정타! 원석 +2 (보유 {0})", Value In Array(Event Player.Inv, 2)));
    - Play Effect(Event Player, Ring Explosion, Color(Orange), Position Of(Event Player), 1.2);
  - Else;
    - Small Message(Event Player, Custom String("빗나갔다 — 곡괭이가 헛돌았다"));
  - End;
- End;
(Busy is already 1 for all of DoMine, so no Busy handling here.)

## Edit 4 - delivery rewire
Replace the ENTIRE body of rule "[파발 02] 흔들리는 화물" (locate from its unique header to the rule's closing brace; keep the header, event block, and conditions - ADD one condition line `Event Player.Busy == 0;` after `Event Player.Init == 1;` - and replace the actions with):
- Wait(Random Real(7, 14), Ignore Condition);
- If(And(And(Event Player.HasParcel == 1, Event Player.Busy == 0), Is Alive(Event Player)));
  - Set Player Variable(Event Player, Busy, 1);
  - Small Message(Event Player, Custom String("화물 끈이 풀린다 — 잡아라!"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 45);
  - Call Subroutine(DoSkillBar);
  - If(Event Player.Roll == 1);
    - Modify Player Variable(Event Player, Money, Add, 12);
    - Modify Player Variable(Event Player, Earned, Add, 12);
    - Small Message(Event Player, Custom String("끈을 다시 묶었다 +$12"));
    - Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1);
  - Else;
    - Small Message(Event Player, Custom String("빗나갔다 — 끈이 덜렁거린다"));
  - End;
  - Set Player Variable(Event Player, Busy, 0);
- End;
- Wait(2, Ignore Condition);
- Loop If(Event Player.HasParcel == 1);

## Edit 5 - cattle rewire
Same surgery on rule "[목동 02] 날뛰는 소": add condition `Event Player.Busy == 0;` after Init, replace actions with the same structure but: outer If checks CowOn == 1 instead of HasParcel; prompt `소가 날뛴다 — 고삐를 잡아라!`; success message `고삐를 잡아챘다 +$12` with Color(White) effects; miss message `빗나갔다 — 소가 콧김을 뿜는다`; initial Wait(Random Real(6, 12), Ignore Condition); final Loop If(Event Player.CowOn == 1).

# Deliverables
patch105_skillbar.py (script alone suffices if execution is blocked). Verification counts for the caller: `2: DoSkillBar` = 1, `rule("[스킬바 01] DoSkillBar")` = 1, `Call Subroutine(DoSkillBar);` = 3, `◆가 ■ 구간에 올 때` = 1, `빗나갔다` = 3, `If(Random Integer(1, 100) <= 30);` = 1, `If(Random Integer(1, 100) > 30);` = 0, `손이 앞섰다` = 0, `Chase Player Variable Over Time(Event Player, WorkProg, 16, 0.9` = 2. Touch nothing else.
