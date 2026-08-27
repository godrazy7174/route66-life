Remove the architect mode and slightly soften beast movement in this Overwatch 2 Workshop project via ONE Python patch script patch114_architect.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,356 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub()/assert style, one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch114_architect.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Part A - remove architect mode
The last three rules of the file are, in order: rule("[설계자 01] 모드 토글 (호스트: Ctrl 2초)"), rule("[설계자 02] 다음 장소 (R)"), rule("[설계자 03] 이 자리로 지정 (F)"), and nothing follows them. Delete everything from the line containing `rule("[설계자 01] 모드 토글 (호스트: Ctrl 2초)")` to the end of the file, then ensure the file still ends with exactly one trailing newline after the previous rule's closing `}`.
Assertions: before deleting, assert each of the three rule headers occurs exactly once and that [설계자 01]'s header index is greater than every other `rule("` occurrence except 02/03. After deleting, assert the file contains zero occurrences of `설계자` and zero occurrences of `ArchHud`.
Do NOT touch anything else related: the many `Global Variable(ArchOn) == 0;` condition lines and the ArchOn/ArchIdx/ArchHud global declarations stay exactly as they are (ArchOn is never set to 1 anymore, so those conditions are permanently true and harmless).

# Part B - beast wander slightly easier to hit (rule "[직업 03-3] 야수 배회")
B1. Replace `Set Jump Vertical Speed(Event Player, Random Integer(120, 380));` with `Set Jump Vertical Speed(Event Player, Random Integer(120, 320));` (cnt=2 - both occurrences are in the wander rule; lower hop ceiling).
B2. Replace `If(Random Integer(1, 100) <= 60);` with `If(Random Integer(1, 100) <= 50);` (cnt=1; jump less often).
B3. The blink-teleport: the two-line anchor (cnt=1)
(3 tabs)`If(Random Integer(1, 100) <= 10);`(newline)(4 tabs)`Teleport(Event Player, Nearest Walkable Position(Add(Position Of(Event Player), Vector(Random Real(-5, 5)`
- replace only the `<= 10` in the first line with `<= 8`, keeping everything else byte-identical.

# Deliverables
patch114_architect.py (script alone suffices if execution is blocked). Verification counts for the caller: `설계자` = 0, `ArchHud` = 0, `Random Integer(120, 320)` = 2, `Random Integer(120, 380)` = 0, `Random Integer(1, 100) <= 50);` = 1, and the blink line now reads `<= 8` (report true/false). Touch nothing else.
