Add a free fatigue-recovery fallback ("쪼그려 쉬기" - crouch resting) to this Overwatch 2 Workshop project via ONE Python patch script patch113_rest.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,324 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted, block() assembly, one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch113_rest.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Design
A penniless player has no way to recover Energy (모텔 $90, 위스키 $38, gated perks only) and soft-locks at 0. Fix: crouching while standing still slowly restores Energy - +1 per 5 seconds, anywhere, free. Slow enough that paid recovery stays dominant. Hunger/thirst keep decaying naturally, which self-limits camping.

## Edit 1 - new rule, inserted directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor)
rule("[생활 03] 쪼그려 쉬기")
event Ongoing - Each Player / All / All.
Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.TutOn == 0; Event Player.Busy == 0; Is Alive(Event Player) == True; Is Crouching(Event Player) == True; Is Moving(Event Player) == False; Event Player.Energy < 100.
Actions:
- Small Message(Event Player, Custom String("바닥에 쪼그려 앉아 숨을 고른다 — 느리게 피로가 돌아온다"));
- Wait(5, Ignore Condition);
- If(And(And(Is Crouching(Event Player) == True, Is Moving(Event Player) == False), And(Is Alive(Event Player), Event Player.Busy == 0)));
  - Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 1)));
  - Play Effect(Event Player, Good Pickup Effect, Color(Gray), Position Of(Event Player), 0.8);
- End;
- Loop If(And(And(Is Crouching(Event Player) == True, Is Moving(Event Player) == False), And(Is Alive(Event Player), Event Player.Energy < 100)));

## Edit 2 - tutorial hint
In the single tutorial Create HUD Text line (the one containing `Min(17, Event Player.TutStep)`), the 피로 page body contains the text `하룻밤 $90에 피로를 40 되찾는다. 내 방을 마련하면 80으로 늘어난다.` (cnt=1). Append after it: the literal backslash-r backslash-n escape (chr(92)+'r'+chr(92)+'n') plus `빈털터리라면 쪼그려 앉아 숨을 골라라 — 느리지만 공짜다.`
Then verify that page's quoted literal length (each RN escape counted as 2) is <= 120; if it exceeds, split it into nested Custom String("{0}{1}", ...) at the RN boundary nearest the middle (patch102 pattern).

# Deliverables
patch113_rest.py (script alone suffices if execution is blocked). Verification counts for the caller: `rule("[생활 03] 쪼그려 쉬기")` = 1, `쪼그려 앉아 숨을 고른다` = 1, `느리지만 공짜다` = 1, `Is Crouching(Event Player) == True` >= 3. Touch nothing else.
