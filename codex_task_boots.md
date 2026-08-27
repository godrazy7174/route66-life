Implement two small improvements in this Overwatch 2 Workshop project via ONE Python patch script patch108_boots.py: (A) a walk-speed boost for gearless newcomers, (B) tutorial lines documenting the three job mini-games. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,200 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch102_tutfix.py (STUDY it - you will reuse its tutorial-body length-check-and-split routine) and patch107_minigames.py. sub() assert-counted, one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch108_boots.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS; a ternary as a WHOLE function argument is fine (used below). Custom String literals hard-cap at 128 rendered characters - after appending tutorial text you MUST re-run the split guard.

# Part A - 낡은 장화 (gearless walk boost)
The line `Set Move Speed(Event Player, 100);` occurs EXACTLY 2 times (needs-recovery path in the world rule, and sprint-end restore). Replace BOTH (cnt=2) with:
`Set Move Speed(Event Player, And(Event Player.HasBag == 0, Event Player.HasHorse == 0) ? 110 : 100);`
(Newcomers with neither the leather bag nor the horse walk at 110%; buying either mobility item returns walking to 100%, which is fine because those items carry their own perks. The hunger/fatigue penalty speeds 70/80 stay untouched.)

# Part B - tutorial mini-game lines
The 18 tutorial page bodies live in the single Create HUD Text line containing `Min(17, Event Player.TutStep)` (assert exactly one such line). Some bodies are already split into `Custom String("{0}{1}", Custom String(...), Custom String(...))` form by an earlier patch - your appends must therefore target the page TEXT, not assume unsplit literals. Append to three pages (RN = the literal backslash-r backslash-n sequence, built as chr(92)+'r'+chr(92)+'n'):
- 광부 page: after the text `쉬지 않고 이어 캐면 연속 보너스가 붙는다.` (cnt=1) append RN + `가끔 광맥이 울린다 — ◆가 ■ 구간에 올 때 [R]이 정타다.`
- 파발꾼 page: after the text `대신 화물을 든 채 털리면 빼앗긴다.` (cnt=1) append RN + `달리다 샛길 빛기둥이 보이면 7초 안에 밟아라 — 웃돈이 붙는다.`
- 목동 page: after the text `접근 각도가 실력이다.` (cnt=1) append RN + `소가 겁먹으면 멈춰 서서 바라봐라 — 진정하면 웃돈이 붙는다.`
THEN re-run the patch102-style guard over the tutorial body array: for every body literal (or part-literal) whose length L (each RN escape counted as 2) exceeds 120, split it into nested `Custom String("{0}{1}", Custom String(part1), Custom String(part2))` at the RN boundary nearest the middle (a part that is already a nested {0}{1} wrapper: re-balance its two parts instead - move whole RN-delimited lines between them so both parts are <= 120). Assert afterwards that no single quoted literal in the body array exceeds 120.

# Deliverables
patch108_boots.py (script alone suffices if execution is blocked). Verification counts for the caller: `? 110 : 100);` = 2, `Set Move Speed(Event Player, 100);` = 0, `[R]이 정타다` = 1, `샛길 빛기둥이 보이면` = 1, `소가 겁먹으면 멈춰 서서` = 1, plus report which pages were (re)split and their lengths. Touch nothing else.
