Three changes in this Overwatch 2 Workshop project via ONE Python patch script patch118_freja.py: the bounty hunter plays Freja, beasts get easier and rarer variants twice as likely, and arrests get much harder to land. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,260 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted (occurrence counts via str.count), block()/mkrule assembly, one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch118_freja.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow
  If lint's element-name check flags the hero name `Freja` as unknown, that is EXPECTED (new hero, not yet in the dictionary) - report it and do NOT edit lint.py; the caller handles dictionaries.

# Doctrine
No ternary in comparison RHS, no bare grouping parens; whole-function-argument ternary fine. Korean as-is.

# Part A - bounty hunter plays Freja (while Job == 3)
A1. New rule "[코어 20] 프레야 스킬 봉인 (조준 허용)" - model it EXACTLY on the existing rule "[코어 06] 애쉬 스킬 봉인 (조준경 허용)" (find it and copy its full structure and action list verbatim), changing only: the rule name, and the hero condition to `Hero Of(Event Player) == Hero(Freja);`. Insert it directly after the [코어 06] rule (i.e. before whatever follows [코어 06]).
A2. New rule "[코어 21] 현상금 사냥꾼은 프레야" inserted directly before rule("[코어 07] 궁극기 게이지 상시 제거") (cnt=1 anchor):
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.Job == 3.
Actions:
- Start Forcing Player To Be Hero(Event Player, Hero(Freja));
A3. New rule "[코어 22] 배지를 반납하면" inserted directly after [코어 21]:
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.Job != 3; Hero Of(Event Player) == Hero(Freja).
Actions:
- If(Event Player.HasHorse == 1);
  - Start Forcing Player To Be Hero(Event Player, Hero(Shion));
- Else If(Event Player.HasBag == 1);
  - Start Forcing Player To Be Hero(Event Player, Hero(Tracer));
- Else;
  - Stop Forcing Player To Be Hero(Event Player);
- End;
A4. Badge message (cnt=1): replace `배지를 받았다 — 현상금 사냥꾼. 전단이 붙은 자($300+)를 산 채로 잡아라` with `배지를 받았다 — 석궁의 프레야가 된다. 전단이 붙은 자($300+)를 산 채로 잡아라`

# Part B - beasts easier + variants twice as likely
B1. Variant odds x2 (giant 1%->2%, legendary 0.1%->0.2%):
- `Add(11, Multiply(5, Event Player.Roll))` -> `Add(22, Multiply(10, Event Player.Roll))` (cnt=1)
- `Idx), Roll) <= 1);` -> `Idx), Roll) <= 2);` (cnt=1)
B2. Reveal window 30s -> 40s: `RevealEnd, Add(Total Time Elapsed(), 30)` -> `RevealEnd, Add(Total Time Elapsed(), 40)` (cnt=1)
B3. Wander stage-3 softening:
- `Random Integer(1, 100) <= 35);` -> `<= 25);` (cnt=1, jump chance)
- `Random Integer(1, 100) <= 5);` -> `<= 3);` (cnt=1, blink)
- `Else If(Random Integer(1, 100) <= 18);` -> `<= 12);` (cnt=1, erratic dash)
- `Random Integer(230, 270)` -> `Random Integer(210, 250)` (cnt=2, dash speeds)
- `Random Integer(150, 220)` -> `Random Integer(140, 200)` (cnt=1, base speed)

# Part C - arrests much harder to land
- `? 2.5 : 4);` -> `? 3 : 5);` (cnt=1, arrest channel; rob stays 3s)
- `), 4.5);` -> `), 5.5);` (cnt=1, the channel Wait Until timeout)
- `Position Of(Event Player.Target)) > 12` -> `> 10` (cnt=2, escape radius - note this also applies to the rob channel, accepted)
- `RobCd, Add(Total Time Elapsed(), 10)` -> `RobCd, Add(Total Time Elapsed(), 15)` (cnt=2, failed-attempt cooldown, shared with rob, accepted)

# Deliverables
patch118_freja.py (script alone suffices if execution is blocked). Verification counts for the caller: `Hero(Freja)` = 3, `rule("[코어 20] 프레야 스킬 봉인 (조준 허용)")` = 1, `rule("[코어 21] 현상금 사냥꾼은 프레야")` = 1, `rule("[코어 22] 배지를 반납하면")` = 1, `석궁의 프레야` = 1, `Add(22, Multiply(10, Event Player.Roll))` = 1, `Idx), Roll) <= 2);` = 1, `Elapsed(), 40)` = 1, `? 3 : 5);` = 1, `), 5.5);` = 1, `Target)) > 10` = 2, `Elapsed(), 15)` = 2. Touch nothing else.
