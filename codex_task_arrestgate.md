Rework arrests in this Overwatch 2 Workshop project via ONE Python patch script patch115_arrestgate.py: only bounty hunters may arrest, the bounty-hunter job is picked up at the sheriff post, and getting arrested becomes harder for the hunter (threshold + longer channel). Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,273 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted (counts below are OCCURRENCE counts via str.count), block() assembly, one write, UTF-8 header, Korean docstring. NO new variables (the precomputed channel duration reuses `Amt`, which is unused inside this rule).
- Validation (run if possible): python patch115_arrestgate.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens; whole-function-argument ternary fine. Custom String literals <= 120 chars (tutorial edit must re-run the split guard). Korean as-is.

# Design summary
- Arrest now requires the arrester's Job == 3 (현상금 사냥꾼) AND the target's Bounty >= 300 (전단 단계). A wanted player below $300 falls through to the ROB branch like any citizen (petty criminals lose arrest-protection - intended).
- Arrest channel: 3s -> 4s (sheriff advancement: 2s -> 2.5s). Rob channel stays 3s. Escape radius stays 12m; the damage-break stays.
- The arrest-based auto-conversion to Job 3 is removed; instead the sheriff post gets a 5th menu item "전직: 현상금 사냥꾼" that converts for free.

# Edits - all in rule "[범죄 01] 황야에서 강도 / 체포 (F)" unless stated

## Edit 1 - setup branch gate (two-line anchor, cnt=1)
Replace
(2 tabs)`If(Player Variable(Event Player.Target, Bounty) > 0);`(newline)(3 tabs)`Set Player Variable(Event Player, JobArg, 3);`(newline)(3 tabs)`Call Subroutine(BecomeJob);`(newline)
with
(2 tabs)`If(Player Variable(Event Player.Target, Bounty) >= 300);`(newline)
(3 tabs)`If(Event Player.Job != 3);`(newline)
(4 tabs)`Set Player Variable(Event Player, Busy, 0);`(newline)
(4 tabs)`Small Message(Event Player, Custom String("체포는 현상금 사냥꾼의 일이다 — 보안관 초소에서 전직할 수 있다"));`(newline)
(4 tabs)`Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);`(newline)
(4 tabs)`Abort;`(newline)
(3 tabs)`End;`(newline)
(The Busy reset before Abort is mandatory. The old JobArg/BecomeJob auto-conversion lines are deleted by this replacement.)

## Edit 2 - channel duration precomputed (cnt=1 each)
2a. Replace the line
`		Chase Player Variable Over Time(Event Player, WorkProg, 100, And(And(Event Player.Job == 3, Value In Array(Event Player.Adv, Event Player.Job) == 1), Player Variable(Event Player.Target, Bounty) > 0) ? 2 : 3, Destination and Duration);`
with two lines (2-tab indent):
`		Set Player Variable(Event Player, Amt, 3);`
`		If(Player Variable(Event Player.Target, Bounty) >= 300);`
`			Set Player Variable(Event Player, Amt, Value In Array(Event Player.Adv, 3) == 1 ? 2.5 : 4);`
`		End;`
`		Chase Player Variable Over Time(Event Player, WorkProg, 100, Event Player.Amt, Destination and Duration);`
2b. The Wait Until timeout on the next line is `), 3);` at the end of the Wait Until line containing `Event Player.WorkProg >= 99` inside this rule (locate the exact line `		Wait Until(Or(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3);`, cnt=1): replace its trailing `), 3);` with `), 4.5);`.

## Edit 3 - result branch threshold (cnt=1)
Replace `Else If(Player Variable(Event Player.Target, Bounty) > 0);` with `Else If(Player Variable(Event Player.Target, Bounty) >= 300);`

## Edit 4 - sheriff post gets the job-change menu
4a. Menu counts: `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 6, 4, 1, 1)` occurs EXACTLY 3 times (str.count); replace all 3 with `Array(1, 1, 3, 4, 2, 3, 5, 2, 5, 6, 6, 5, 6, 4, 1, 1)` (index 8, zone 7 초소, 4 -> 5).
4b. Label (cnt=1): replace `Custom String("재산세 납부 — 징수 기간만"), Custom String("-")` with `Custom String("재산세 납부 — 징수 기간만"), Custom String("전직: 현상금 사냥꾼")`.
4c. Zone-7 chain in rule "[조작 03b]": replace the anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Global Variable(TaxOn) == 0);` with (3 tabs)`Else If(Event Player.MenuIdx == 3);`(newline)(4 tabs)`If(Global Variable(TaxOn) == 0);` (cnt=1). Then at the zone-7 chain close - the sequence (4 tabs)`End;`(newline)(3 tabs)`End;`(newline)(2 tabs)`Else If(Event Player.Zone == 8);` (cnt=1) - insert between the first End; and the second a new depth-3 `Else;` branch:
- If(Event Player.Job == 3);
  - Small Message(Event Player, Custom String("이미 현상금 사냥꾼이다")); plus Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- Else;
  - Set Player Variable(Event Player, JobArg, 3);
  - Call Subroutine(BecomeJob);
  - Big Message(Event Player, Custom String("배지를 받았다 — 현상금 사냥꾼. 전단이 붙은 자($300+)를 산 채로 잡아라"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 80);
- End;

## Edit 5 - sheriff post signboard (cnt=1)
After the signboard line beginning `체포 시도 — 허기` (append after that full line's literal backslash-r backslash-n escape, chr(92)+'r'+chr(92)+'n'): add `배지 — 체포는 현상금 사냥꾼의 일, 전직은 여기서` plus the same RN escape.

## Edit 6 - tutorial bounty-hunter page (cnt=1)
Replace the tutorial body text `현상금이 붙은 자는 누구든 잡을 수 있다.` with `전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 전직은 보안관 초소에서.`
Then re-run the patch102-style length guard over the tutorial body array (each RN escape counted as 2; any literal > 120 gets split / any nested {0}{1} pair re-balanced).

# Deliverables
patch115_arrestgate.py (script alone suffices if execution is blocked). Verification counts for the caller: `Bounty) >= 300` = 3, `체포는 현상금 사냥꾼의 일이다` = 1, `전직: 현상금 사냥꾼` = 1, `배지를 받았다` = 1, `? 2.5 : 4);` = 1, `? 2 : 3, Destination and Duration` = 0, `Set Player Variable(Event Player, JobArg, 3);` = 1 (only the new menu branch), `전단이 붙은 자($300+)` = 2 (tutorial + menu message), `Array(1, 1, 3, 4, 2, 3, 5, 2, 5, 6, 6, 5, 6, 4, 1, 1)` = 3, `배지 — 체포는` = 1. Touch nothing else.
