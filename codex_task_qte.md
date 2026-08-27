Tune the mining timing event's frequency and add matching micro-events to the delivery and cattle-drive jobs in this Overwatch 2 Workshop project, via ONE Python patch script patch104_qte.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,028 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch103_trade.py: sub() assert-counted, block() assembly, one write, UTF-8 header, Korean docstring. Player variables are FULL: NO new variables (the two new rules below need none - they use Wait/loop state only).
- Validation (run if possible): python patch104_qte.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens. Custom String max 3 args. Korean as-is. An `If` branch with an empty body followed by `Else If` is valid - we use that to add a probability gate without re-indenting.

# Edit 1 - mining 정타 becomes a 30% chance per dig
In rule "[직업 01] DoMine", the timing block added by patch103 starts with these two lines (cnt=1 for the pair):
(2 tabs)`Wait(Random Real(0.3, 0.8), Ignore Condition);`(newline)(2 tabs)`If(Is Button Held(Event Player, Button(Jump)));`
Replace with:
(2 tabs)`Wait(Random Real(0.3, 0.8), Ignore Condition);`(newline)(2 tabs)`If(Random Integer(1, 100) > 30);`(newline)(2 tabs)`Else If(Is Button Held(Event Player, Button(Jump)));`
(The empty If branch swallows 70% of digs; the rest of the chain - 성급/프롬프트/End - is untouched and keeps its indentation.)

# Edit 2 - new rule "[파발 02] 흔들리는 화물"
Insert directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor), FIRST of the two new rules:
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.HasParcel == 1; Is Alive(Event Player) == True.
Actions:
- Wait(Random Real(7, 14), Ignore Condition);
- If(And(Event Player.HasParcel == 1, Is Alive(Event Player)));
  - If(Is Button Held(Event Player, Button(Reload)));
    - Small Message(Event Player, Custom String("손이 앞섰다 — 끈을 놓쳤다"));
  - Else;
    - Small Message(Event Player, Custom String("화물 끈이 풀린다 — 지금! [{0}]", Input Binding String(Button(Reload))));
    - Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 45);
    - Wait Until(Is Button Held(Event Player, Button(Reload)), 0.7);
    - If(Is Button Held(Event Player, Button(Reload)));
      - Modify Player Variable(Event Player, Money, Add, 12);
      - Modify Player Variable(Event Player, Earned, Add, 12);
      - Small Message(Event Player, Custom String("끈을 다시 묶었다 +$12"));
      - Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1);
    - End;
  - End;
- End;
- Wait(2, Ignore Condition);
- Loop If(Event Player.HasParcel == 1);

# Edit 3 - new rule "[목동 02] 날뛰는 소"
Insert directly after the [파발 02] rule (i.e. also before rule("[감옥 01] 만기 출소")):
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.CowOn == 1; Is Alive(Event Player) == True.
Actions:
- Wait(Random Real(6, 12), Ignore Condition);
- If(And(Event Player.CowOn == 1, Is Alive(Event Player)));
  - If(Is Button Held(Event Player, Button(Reload)));
    - Small Message(Event Player, Custom String("손이 앞섰다 — 고삐를 놓쳤다"));
  - Else;
    - Small Message(Event Player, Custom String("소가 날뛴다 — 지금! [{0}]", Input Binding String(Button(Reload))));
    - Play Effect(Event Player, Buff Impact Sound, Color(White), Position Of(Event Player), 45);
    - Wait Until(Is Button Held(Event Player, Button(Reload)), 0.7);
    - If(Is Button Held(Event Player, Button(Reload)));
      - Modify Player Variable(Event Player, Money, Add, 12);
      - Modify Player Variable(Event Player, Earned, Add, 12);
      - Small Message(Event Player, Custom String("고삐를 잡아챘다 +$12"));
      - Play Effect(Event Player, Ring Explosion, Color(White), Position Of(Event Player), 1);
    - End;
  - End;
- End;
- Wait(2, Ignore Condition);
- Loop If(Event Player.CowOn == 1);

(Both new rules use the Reload key, NOT Jump - runners jump constantly while traversing, so a jump-based prompt would auto-succeed; Reload is a deliberate press. Holding Reload in advance fails the prompt, same anti-mash rule as mining. One-ish prompt every 6-14s while carrying/driving = a few per run.)

# Deliverables
patch104_qte.py (script alone suffices if execution is blocked). Verification counts for the caller: `If(Random Integer(1, 100) > 30);` = 1, `rule("[파발 02] 흔들리는 화물")` = 1, `rule("[목동 02] 날뛰는 소")` = 1, `화물 끈이 풀린다` = 1, `소가 날뛴다` = 1, `끈을 다시 묶었다` = 1, `고삐를 잡아챘다` = 1, `손이 앞섰다` = 2. Touch nothing else.
