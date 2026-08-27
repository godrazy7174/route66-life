Two changes in this Overwatch 2 Workshop project via ONE Python patch script patch119_subdue.py: beasts get even easier (stage 4), and arrests gain a SUBDUE mechanic - you can only cuff a criminal whose health is below half. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,341 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted (occurrence counts via str.count), one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch119_subdue.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens. Korean as-is.

# Part A - beast wander stage 4
- `Random Integer(1, 100) <= 25);` -> `<= 15);` (cnt=1, jump chance)
- `Random Integer(1, 100) <= 3);` -> `<= 0);` (cnt=1, blink-teleport effectively disabled)
- `Else If(Random Integer(1, 100) <= 12);` -> `<= 8);` (cnt=1, erratic dash)
- `Random Integer(210, 250)` -> `Random Integer(190, 230)` (cnt=2, dash speeds)
- `Random Integer(140, 200)` -> `Random Integer(130, 180)` (cnt=1, base speed)

# Part B - subdue-before-cuff (mechanism change in rule "[범죄 01] 황야에서 강도 / 체포 (F)")
Inside the arrest setup, right after the non-hunter gate block - which reads (locate this exact sequence, cnt=1):
(3 tabs)`If(Event Player.Job != 3);`(newline)
(4 tabs)`Set Player Variable(Event Player, Busy, 0);`(newline)
(4 tabs)`Small Message(Event Player, Custom String("체포는 현상금 사냥꾼의 일이다 — 보안관 초소에서 전직할 수 있다"));`(newline)
(4 tabs)`Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);`(newline)
(4 tabs)`Abort;`(newline)
(3 tabs)`End;`(newline)
- insert immediately AFTER that final `End;` line a second gate block:
(3 tabs)`If(Health(Event Player.Target) >= Multiply(Max Health(Event Player.Target), 0.5));`(newline)
(4 tabs)`Set Player Variable(Event Player, Busy, 0);`(newline)
(4 tabs)`Small Message(Event Player, Custom String("아직 팔팔하다 — 쏴서 제압해라 (체력 절반 미만이어야 수갑을 채운다)"));`(newline)
(4 tabs)`Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);`(newline)
(4 tabs)`Abort;`(newline)
(3 tabs)`End;`(newline)

Also update the two texts that describe arrests:
- Tutorial (cnt=1): `전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 전직은 보안관 초소에서.` -> `전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 쏴서 제압한 뒤 수갑을 채운다.`
  Then re-run the patch102-style tutorial length guard (RN escape = 2 chars; literals > 120 split / nested pairs re-balanced).
- Sheriff-post signboard line (cnt=1): `배지 — 체포는 현상금 사냥꾼의 일, 전직은 여기서` -> `배지 — 체포는 현상금 사냥꾼의 일, 제압(체력 절반)이 먼저다`

# Deliverables
patch119_subdue.py (script alone suffices if execution is blocked). Verification counts for the caller: `<= 15);` inside the file = 1 for the exact string `Random Integer(1, 100) <= 15);`, `Random Integer(1, 100) <= 0);` = 1, `Random Integer(190, 230)` = 2, `Random Integer(130, 180)` = 1, `아직 팔팔하다` = 1, `Multiply(Max Health(Event Player.Target), 0.5)` = 1, `쏴서 제압한 뒤 수갑을 채운다` = 1, `제압(체력 절반)이 먼저다` = 1. Touch nothing else.
