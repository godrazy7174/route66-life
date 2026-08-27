Rebalance the robbery/arrest channel in this Overwatch 2 Workshop script project by writing ONE Python patch script. All edits are inside rule "[범죄 01] 황야에서 강도 / 체포 (F)". Work non-interactively: never ask questions, decide within this spec, and print a final summary report at the end.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,749 lines). ROUTE66_LIFE.ow is the Korean build generated from it.
- Changes go through an atomic Python patch script: write patch98_robnerf.py with `# -*- coding: utf-8 -*-` header, a Korean docstring, a sub(old, new, cnt) helper with assert-counted occurrences (copy the helper from patch96_varfix.py), and ONE file write at the end.
- IMPORTANT: player variables are FULL (128/128). Declare NO new variables. The health snapshot reuses the existing player variable `Take` (it is only written later in the same rule, after the channel, so the reuse is safe).
- Your sandbox may block running Python (`CreateProcessAsUserW failed: 5`). If Python runs, run the validation pipeline below. If it does not, apply the patch to ROUTE66_LIFE_EN.ow by hand-editing it to EXACTLY what the patch script would produce, verify by careful re-reading, and say clearly in your report that validation must be re-run by the caller. Do NOT edit ROUTE66_LIFE.ow.
- Validation pipeline: python patch98_robnerf.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow
  (the pre-existing "possibly undeclared player vars" warning listing bare numbers is noise.)

# Design intent
Robbing/arresting is currently too easy: a 1.8-second channel, the victim's only counter is running 12m away, and a failed attempt costs just 6s. Changes: channel 1.8s -> 3s (advanced-sheriff arrest 1.2s -> 2s); ANY damage taken by the channeler breaks the grab (so victims can shoot to resist - left-click combat already exists); failed-attempt cooldown 6s -> 10s. Victim warnings now tell them they can shoot back.

# Exact substitutions (all inside rule "[범죄 01]"; tabs are real tab characters)

1. Health snapshot (cnt=1). Replace the anchor
(2 tabs)`Set Player Variable(Event Player, Busy, 1);`(newline)(2 tabs)`Set Player Variable(Event Player, WorkProg, 0);`(newline)(2 tabs)`If(Player Variable(Event Player.Target, Bounty) > 0);`
with the same three lines but with a new line inserted after the WorkProg line, same 2-tab indent:
`Set Player Variable(Event Player, Take, Health(Event Player));`
(This anchor is unique because only [범죄 01] follows the Busy/WorkProg pair with the Target-Bounty If.)

2. Channel duration (cnt=1). In the line
`Chase Player Variable Over Time(Event Player, WorkProg, 100, And(And(Event Player.Job == 3, Value In Array(Event Player.Adv, Event Player.Job) == 1), Player Variable(Event Player.Target, Bounty) > 0) ? 1.2 : 1.8, Destination and Duration);`
replace `? 1.2 : 1.8,` with `? 2 : 3,` (sub on the whole line or on the unique fragment `? 1.2 : 1.8, Destination and Duration` - your choice, assert-counted).

3. Break-on-damage in the wait (cnt=1). Replace
`Wait Until(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3);`
with
`Wait Until(Or(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3.5);`

4. Break-on-damage in the failure check (cnt=1). Replace
`If(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Not(Is Alive(Event Player))));`
with
`If(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))));`
(Without this the damage-break would fall through into the success branch - this edit is what makes edit 3 correct.)

5. Victim warnings (cnt=1 each):
- `{0}이(가) 당신을 체포하려 한다 — 도망쳐라` -> `{0}이(가) 당신을 체포하려 한다 — 도망치거나 쏴서 뿌리쳐라`
- `{0}이(가) 총을 겨눴다 — 도망쳐라` -> `{0}이(가) 총을 겨눴다 — 도망치거나 쏴서 뿌리쳐라`

6. Failed-attempt cooldown (cnt=2). Replace both occurrences of
`Set Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 6));`
with
`Set Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 10));`
(One is the "놓쳤다" miss branch, one is the "빈털터리다" empty-pockets branch. The success cooldown line with `Subtract(45, ...)` must NOT change.)

# Deliverables
- patch98_robnerf.py in the project dir, every sub() assert-counted.
- Apply it (via Python if the sandbox allows, otherwise exact hand-application to ROUTE66_LIFE_EN.ow only).
- Verify in ROUTE66_LIFE_EN.ow (count occurrences) and print in your final report: `Set Player Variable(Event Player, Take, Health(Event Player));` = 1, `? 2 : 3, Destination and Duration` = 1, `Health(Event Player) < Event Player.Take` = 2, `도망치거나 쏴서 뿌리쳐라` = 2, `RobCd, Add(Total Time Elapsed(), 10)` = 2, `RobCd, Add(Total Time Elapsed(), 6)` = 0, `? 1.2 : 1.8` = 0, `Subtract(45, Multiply(15,` = 1 (unchanged).
- Final report: what you changed, whether validation actually ran, and the occurrence counts. Do not modify anything outside rule "[범죄 01]". Do not reformat existing code. Do not edit ROUTE66_LIFE.ow.
