Implement a new game feature in this Overwatch 2 Workshop script project by writing and running a Python patch script. Work non-interactively: never ask questions, decide within this spec, and print a final summary report at the end.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,199 lines, a western life-sim Workshop gamemode). ROUTE66_LIFE.ow is the Korean build generated from it.
- All changes are made via atomic Python patch scripts (patchNN_name.py) that read ROUTE66_LIFE_EN.ow, perform exact-string substitutions with assert-counted occurrences, and write the file ONCE at the end. STUDY patch89_bankheist.py first - it is the style reference: its sub(), block(), insert_into() helpers, mkrule() rule builder, chr(9)/chr(10) tab/newline assembly (never raw backslash escapes in generated content), and its edit of the "[범죄 01]" no-target branch are all patterns you must reuse.
- Validation pipeline (all must pass, run from the project dir):
  python patch92_smuggle.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python to_korean.py ROUTE66_LIFE_EN.ow ROUTE66_LIFE.ow
  lint prints Korean check names; a pre-existing "possibly undeclared player vars" warning listing bare numbers is noise - ignore it. Any NEW warning or error is a failure you must fix before finishing.

# Workshop scripting rules you MUST follow (hard-won project doctrine)
1. Never place a ternary inside a comparison right-hand side and never use bare grouping parentheses like `X <= (a ? b : c)` - precompute into a variable first. A ternary as a whole function argument is fine.
2. Custom String takes max 3 format args; nest Custom Strings for more.
3. Messages re-evaluate while displayed: any value shown in a message must come from a variable that will not change during display.
4. Icons/effects are created and destroyed on state transitions - never rely on conditional visible-to with global state.
5. Menu labels are a flat 84-entry array with 6 slots per zone - zone 8 (은신처) is FULL (6/6), which is why this feature starts with the V key, not a menu.
6. Korean text goes inside Custom String("...") literals as-is (files are UTF-8). The literal two-character sequences backslash-r and backslash-n inside signboard Custom Strings represent newlines; build them in Python as chr(92)+'r'+chr(92)+'n'.
7. Write the patch file in UTF-8 with a `# -*- coding: utf-8 -*-` header and a Korean docstring summarizing the change, matching patch89's format.

# Feature spec - 밀수 호송 (smuggling run)
A courier-of-crime loop: accept contraband at the hideout with the V key, deliver it to a secret drop point, get paid in notoriety-tainted money.

New player variables (append to the player variable declaration block, right after the line `109: BrewReady`):
110 Contraband, 111 SmugglePos, 112 SmuggleIco, 113 SmugglePay, 114 SmuggleCd, 115 SmuggleFlash

1. ACCEPT - extend the no-target branch inside rule "[범죄 01] 황야에서 강도 / 체포 (F)". That branch currently reads: If (zone 9 bank conditions) -> bank dial start; Else -> "대상 없음" message. Insert a new Else If BETWEEN them with condition:
   And(And(Event Player.Zone == 8, Event Player.Contraband == 0), Total Time Elapsed() >= Event Player.SmuggleCd)
   actions:
   - Set SmugglePos = Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-15, 15), 0, Random Real(-15, 15))))
   - Set SmugglePay = Round To Integer(Add(30, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 8), Event Player.SmugglePos), 2.5)), To Nearest)
   - Set Contraband = 1
   - Destroy Icon(Event Player.SmuggleIco); Create Icon(Event Player, Add(Event Player.SmugglePos, Vector(0, 3, 0)), Diamond, Visible To and Position, Color(Purple), True); Set SmuggleIco = Last Created Entity()   [icon visible ONLY to the smuggler - first arg Event Player]
   - Big Message(Event Player, Custom String("밀수 화물을 받았다 — 접선지로 (보수 $ {0})", Event Player.SmugglePay))
   - Small Message(Event Player, Custom String("화물을 진 동안 질주할 수 없고, 죽으면 끝이다 — 자주색 표식을 따라가라"))
   - Play Effect(Event Player, Buff Impact Sound, Color(Purple), Position Of(Event Player), 60)

2. SPRINT BLOCK - rule "[조작 04] 달리기 (Shift)" conditions already contain the line `Event Player.Sack == 0;` (inserted by patch89 via its insert_into helper). Add `Event Player.Contraband == 0;` the same way.

3. PERIODIC EXPOSURE - new rule "[밀수 01] 화물 냄새" modeled exactly on the existing rule "[수배 01] 전단 노출" (find it in the file): conditions Is Dummy Bot False / Init == 1 / Contraband == 1 / Is Alive True. Actions: Create Icon(All Players(All Teams), Add(Position Of(Event Player), Vector(0, 2.6, 0)), Circle, Visible To and Position, Color(Purple), True) stored in SmuggleFlash; Wait(3); Destroy Icon(Event Player.SmuggleFlash); Wait(17); Loop If(And(Event Player.Contraband == 1, Is Alive(Event Player))).

4. HANDOVER - new rule "[밀수 02] 접선 인계 (F 3초)" modeled exactly on rule "[밤 02] 금고 마차 털기 (F 5초)" (find it; copy its condition set and channel/interrupt structure): conditions include Is Dummy Bot False, Init == 1, Busy == 0, ArchOn == 0, Contraband == 1, Is Alive True, Distance Between(Position Of(Event Player), Event Player.SmugglePos) < 4, crouch not held, Interact held. Channel 3 seconds with progress bar text "화물 인계 중..." (interrupt if distance > 6 or dead, using the wagon rule's exact structure with Busy=1 at start and Busy=0 at end). On success: Modify Money Add SmugglePay (do NOT touch Earned - crime income is excluded from daily goals), Set Noto = Min(100, Add(Noto, 8)), Set Contraband = 0, Destroy Icon(Event Player.SmuggleIco), Set SmuggleCd = Add(Total Time Elapsed(), 60), Small Message(Event Player, Custom String("화물을 넘겼다 — +$ {0} (악명 +8)", Event Player.SmugglePay)), Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 120).
   Insert both new rules directly before rule("[감옥 01] 만기 출소") the way patch89 does.

5. DEATH LOSS - the death cleanup rule contains this block added by patch89: If(Event Player.Sack > 0); ... "장물 자루를 흘렸다" ... End;
   Insert immediately after that End a parallel block: If(Event Player.Contraband == 1); Set Contraband = 0; Destroy Icon(Event Player.SmuggleIco); Small Message(Event Player, Custom String("밀수 화물을 잃었다 — 접선은 없던 일이 됐다")); End;

6. ROBBERY INTERCEPT - in the rob-success branch of "[범죄 01]" there is a block: If(Player Variable(Event Player.Target, HasParcel) == 1); ... End; (courier parcel intercept, +$60). Insert right after that End an analogous block: If(Player Variable(Event Player.Target, Contraband) == 1); Set Player Variable(Event Player.Target, Contraband, 0); Destroy Icon(Player Variable(Event Player.Target, SmuggleIco)); Modify Player Variable(Event Player, Money, Add, 80); Big Message(All Players(All Teams), Custom String("{0}이(가) {1}의 밀수 화물을 가로챘다! (+$80)", Event Player, Event Player.Target)); End;

7. SIGNBOARD - the hideout in-world signboard contains the line `밤의 큰 건 — 은행(재건 3단계)과 열차는 간 큰 자를 기다린다` followed by the literal backslash-r backslash-n sequence. Append after that line and its newline sequence: `밀수 — [V]로 화물 수주, 접선지 인계 (질주 불가·죽으면 소실)` plus the same literal newline sequence.

# Deliverables
- patch92_smuggle.py in the project dir, following patch89's structure, every sub() assert-counted.
- Run the full validation pipeline; all checks pass; to_korean produces ROUTE66_LIFE.ow with no new warnings.
- Verify in ROUTE66_LIFE.ow (count occurrences) and print the counts in your final report: "밀수 화물을 받았다" = 1, "화물 인계 중" = 1, "밀수 화물을 잃었다" = 1, "밀수 화물을 가로챘다" = 1, rule("[밀수 0 = 2, the signboard line = 1.
- Final report: what you changed, validator output summary, and the final rule/line counts that lint prints. Do not modify anything outside this feature. Do not reformat existing code.
