Implement a new game feature in this Overwatch 2 Workshop script project by writing a Python patch script. Work non-interactively: never ask questions, decide within this spec, and print a final summary report at the end.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,303 lines, a western life-sim Workshop gamemode). ROUTE66_LIFE.ow is the Korean build generated from it.
- All changes are made via atomic Python patch scripts (patchNN_name.py) that read ROUTE66_LIFE_EN.ow, perform exact-string substitutions with assert-counted occurrences, and write the file ONCE at the end. STUDY patch92_smuggle.py and patch91_moonshine.py first - they are the style references: their sub() helper, block()-style chr(9)/chr(10) tab/newline assembly (never raw backslash escapes in generated content), and patch91's menu-branch insertion pattern are all patterns you must reuse.
- Your sandbox may block running Python (`CreateProcessAsUserW failed: 5`). If Python runs, run the validation pipeline below. If it does not, apply the patch to ROUTE66_LIFE_EN.ow by hand-editing it to EXACTLY what the patch script would produce, verify by careful re-reading, and say clearly in your report that validation must be re-run by the caller. Do NOT edit ROUTE66_LIFE.ow (the Korean build) - the caller regenerates it.
- Validation pipeline (all must pass, run from the project dir):
  python patch93_escort.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow
  lint prints Korean check names; a pre-existing "possibly undeclared player vars" warning listing bare numbers is noise - ignore it. Any NEW warning or error is a failure you must fix before finishing.

# Workshop scripting rules you MUST follow (hard-won project doctrine)
1. Never place a ternary inside a comparison right-hand side and never use bare grouping parentheses like `X <= (a ? b : c)` - precompute into a variable first. A ternary as a whole function argument is fine.
2. Custom String takes max 3 format args; nest Custom Strings for more.
3. Messages re-evaluate while displayed: any value shown in a message must come from a variable that will not change during display.
4. Icons/effects are created and destroyed on state transitions - never rely on conditional visible-to with global state.
5. Korean text goes inside Custom String("...") literals as-is (files are UTF-8). The literal two-character sequences backslash-r and backslash-n inside signboard Custom Strings represent newlines; build them in Python as chr(92)+'r'+chr(92)+'n'.
6. Write the patch file as patch93_escort.py in UTF-8 with a `# -*- coding: utf-8 -*-` header and a Korean docstring summarizing the change, matching patch91's format. Every sub() must be assert-counted with the counts given below.

# Feature spec - 금괴 호송 계약 (gold escort contract)
The lawful mirror of the smuggling run: accept a gold strongbox at the stagecoach station (zone 11) via a NEW third menu slot, walk it (no sprinting) to a random drop point marked with a gold diamond only the escort sees, and hand it over for money + Fame. While escorting, the gold's position leaks periodically to CRIMINAL players only (Noto >= 30 or Bounty > 0), inviting robbery; being robbed or dying ends the contract.

New player variables (append to the player variable declaration block, right after the line `		115: SmuggleFlash` and before the closing `}`):
116 Escort, 117 EscortPos, 118 EscortIco, 119 EscortPay, 120 EscortCd, 121 EscortFlash, 122 EscortFx

## Edit 1 - station menu grows from 2 to 3 slots
The menu-count literal `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 2, 2, 1, 1)` occurs EXACTLY 3 times. Replace all 3 (cnt=3) with `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 3, 2, 1, 1)` (index 12, the station zone 11 slot, 2 -> 3).

## Edit 2 - menu label
In the flat menu-label array (one occurrence), replace
`Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("-")`
with
`Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("금괴 호송 계약")`
(cnt=1; this consumes the first "-" filler of the station's 6-slot label segment).

## Edit 3 - station action branch (rule "[조작 03c] 행동 실행 — 안내소·대장간·정거장·목장", zone 11 chain)
The zone-11 chain currently is: `If(Event Player.MenuIdx == 0);` (delivery accept) ... then a bare `Else;` whose body starts with `If(Event Player.Job != 5);` (the 역마차장 promotion). Two sub-edits:

3a. Replace the anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Event Player.Job != 5);` with (3 tabs)`Else If(Event Player.MenuIdx == 1);`(newline)(4 tabs)`If(Event Player.Job != 5);` (cnt=1).

3b. The zone-11 chain closes with this exact sequence: (4 tabs)`End;`(newline)(3 tabs)`End;`(newline)(2 tabs)`Else If(Event Player.Zone == 12);` (cnt=1). Insert a new Else branch between the first `End;` and the second: after (4 tabs)`End;`(newline), insert at depth 3 `Else;` then the accept logic below, so the result reads (4 tabs)End; / (3 tabs)Else; / [accept body] / (3 tabs)End-chain continues with the original (3 tabs)End;.

Accept body (depth 4 unless nested deeper):
- `If(Event Player.Escort == 1);` -> Small Message(Event Player, Custom String("이미 금괴를 호송 중이다 — 노란 표식으로 가라")); plus Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- `Else If(Event Player.Bounty > 0);` -> Small Message(Event Player, Custom String("현상금 붙은 자에게 금괴를 맡길 수는 없다")); plus the same red debuff sound;
- `Else If(Total Time Elapsed() < Event Player.EscortCd);` -> Small Message(Event Player, Custom String("다음 금괴 마차가 아직이다 — {0}초 뒤에 다시", Round To Integer(Subtract(Event Player.EscortCd, Total Time Elapsed()), Up))); plus the red debuff sound;
- `Else If(Event Player.Energy < 4);` -> Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다")); plus the red debuff sound;
- `Else;` ->
  - Set Player Variable(Event Player, EscortPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-15, 15), 0, Random Real(-15, 15)))));
  - Set Player Variable(Event Player, EscortPay, Round To Integer(Add(40, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2.5)), To Nearest));
  - Set Player Variable(Event Player, Escort, 1);
  - Destroy Icon(Event Player.EscortIco); Create Icon(Event Player, Add(Event Player.EscortPos, Vector(0, 3, 0)), Diamond, Visible To and Position, Color(Yellow), True); Set Player Variable(Event Player, EscortIco, Last Created Entity());  [destination marker visible ONLY to the escort - first arg Event Player]
  - Destroy Effect(Event Player.EscortFx); Create Effect(All Players(All Teams), Sphere, Color(Yellow), Add(Position Of(Event Player), Vector(0, 2.4, 0)), 0.3, Visible To Position Radius and Color); Set Player Variable(Event Player, EscortFx, Last Created Entity());  [the gold strongbox glow that follows the escort, visible to everyone nearby]
  - Big Message(Event Player, Custom String("금괴 상자를 실었다 — 노란 표식까지 (보수 $ {0})", Event Player.EscortPay));
  - Small Message(Event Player, Custom String("질주할 수 없다 · 죽거나 털리면 끝 — 악명 높은 자들이 냄새를 맡는다"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);
- `End;`
Do NOT call BecomeJob and do NOT touch JobXP - the escort is a contract, not a job.

## Edit 4 - sprint block
The sprint rule's conditions contain the line (2 tabs)`Event Player.Sack == 0;` (cnt=1). Insert after it, same indent: `Event Player.Escort == 0;`

## Edit 5 - new rule "[호송 01] 금괴의 소문" (periodic leak to criminals)
Modeled EXACTLY on the existing rule "[밀수 01] 화물 냄새" (find it in the file): event Ongoing - Each Player / All / All; conditions Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.Escort == 1; Is Alive(Event Player) == True. Actions:
- Create Icon(Filtered Array(All Players(All Teams), Or(Player Variable(Current Array Element, Noto) >= 30, Player Variable(Current Array Element, Bounty) > 0)), Add(Position Of(Event Player), Vector(0, 2.6, 0)), Circle, Visible To and Position, Color(Yellow), True);
- Set Player Variable(Event Player, EscortFlash, Last Created Entity());
- Wait(3, Ignore Condition); Destroy Icon(Event Player.EscortFlash); Wait(17, Ignore Condition);
- Loop If(And(Event Player.Escort == 1, Is Alive(Event Player)));

## Edit 6 - new rule "[호송 02] 금괴 인계 (F 3초)"
Modeled EXACTLY on rule "[밀수 02] 접선 인계 (F 3초)" (find it; copy its condition set and channel/interrupt structure, replacing Contraband with Escort and SmugglePos with EscortPos): conditions Is Dummy Bot False, Init == 1, Busy == 0, ArchOn == 0, Escort == 1, Is Alive True, Distance Between(Position Of(Event Player), Event Player.EscortPos) < 4, crouch not held, Interact held. Channel 3 seconds with progress bar text "금괴 인계 중..." in Color(Yellow) (interrupt if distance > 6 or dead, same Wait Until / abort structure with Busy=1 at start and Busy=0 at end, and the same "손을 뗐다" failure message). On success:
- Modify Player Variable(Event Player, Money, Add, Event Player.EscortPay);
- Modify Player Variable(Event Player, Earned, Add, Event Player.EscortPay);   [lawful income DOES count toward the daily goal - unlike smuggling]
- Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 8)));
- Set Player Variable(Event Player, Escort, 0);
- Destroy Icon(Event Player.EscortIco); Destroy Effect(Event Player.EscortFx);
- Set Player Variable(Event Player, EscortCd, Add(Total Time Elapsed(), 60));
- Small Message(Event Player, Custom String("금괴를 지켜냈다 — +$ {0} (명성 +8)", Event Player.EscortPay));
- Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 120);
Insert both new rules directly before rule("[감옥 01] 만기 출소") the way patch92 does, order: [호송 01] then [호송 02].

## Edit 7 - death loss
The death cleanup rule contains this block: If(Event Player.Contraband == 1); ... Custom String("밀수 화물을 잃었다 — 접선은 없던 일이 됐다")); ... End;
Insert immediately after that End a parallel block:
If(Event Player.Escort == 1); Set Player Variable(Event Player, Escort, 0); Destroy Icon(Event Player.EscortIco); Destroy Effect(Event Player.EscortFx); Small Message(Event Player, Custom String("금괴를 잃었다 — 호송은 실패로 끝났다")); End;

## Edit 8 - robbery intercept
In the rob-success branch of "[범죄 01] 황야에서 강도 / 체포 (F)" there is a block: If(Player Variable(Event Player.Target, Contraband) == 1); ... (+$80) ... End;
Insert right after that End an analogous block:
If(Player Variable(Event Player.Target, Escort) == 1); Set Player Variable(Event Player.Target, Escort, 0); Destroy Icon(Player Variable(Event Player.Target, EscortIco)); Destroy Effect(Player Variable(Event Player.Target, EscortFx)); Modify Player Variable(Event Player, Money, Add, 120); Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 금괴 호송을 털었다! (+$120)", Event Player, Event Player.Target)); Small Message(Player Variable(Event Player.Target, Escort) == 0 ? Event Player.Target : Event Player.Target, Custom String("금괴를 빼앗겼다 — 호송 실패")); End;
(For that Small Message just use Small Message(Event Player.Target, Custom String("금괴를 빼앗겼다 — 호송 실패")); - no ternary needed.)

## Edit 9 - station signboard
The station in-world signboard contains the line `배달 완료 — 허기 2 · 갈증 3 · 피로 4` followed by the literal backslash-r backslash-n sequence. Append after that line and its newline sequence: `금괴 호송 — 수배 없는 자만 · 질주 불가 · 악명 높은 자들이 노린다` plus the same literal newline sequence (cnt=1).

# Deliverables
- patch93_escort.py in the project dir, following patch91/patch92's structure, every sub() assert-counted with the counts stated above.
- Apply it (via Python if the sandbox allows, otherwise by exact hand-application to ROUTE66_LIFE_EN.ow only).
- Verify in ROUTE66_LIFE_EN.ow (count occurrences) and print the counts in your final report: "금괴 상자를 실었다" = 1, "금괴 인계 중" = 1, "금괴를 잃었다" = 1, "금괴를 빼앗겼다" = 1, "금괴 호송을 털었다" = 1, rule("[호송 0 = 2, "Event Player.Escort == 0;" in the sprint rule = 1, the signboard line = 1, "Earned, Add, Event Player.EscortPay" = 1.
- Final report: what you changed, whether validation actually ran, and the occurrence counts. Do not modify anything outside this feature. Do not reformat existing code. Do not edit ROUTE66_LIFE.ow.
