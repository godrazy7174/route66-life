Implement player-to-player money handover (송금) and a mining timing minigame (채굴 정타) in this Overwatch 2 Workshop project by writing ONE Python patch script, patch103_trade.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949 console).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~4,974 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch101_mastery.py / patch89_bankheist.py: sub() assert-counted, block() tab/newline assembly with chr(9)/chr(10), insert_into(rule_header, section, insertion) for rule-scoped edits, one write, `# -*- coding: utf-8 -*-`, Korean docstring.
- Player variables are FULL: declare NO new variable (this patch needs none - reuse Target/Idx/Tmp-free flow exactly as specified).
- Validation (run if possible): python patch103_trade.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens. Custom String max 3 args. Message values display-stable. Korean as-is.

# Part A - 송금 (crouch + V hands $100 to the aimed player)
A1. Key separation: rule "[범죄 01] 황야에서 강도 / 체포 (F)" currently triggers on Melee held with no crouch check. Using insert_into scoped to that rule's conditions block, insert a new condition line immediately BEFORE its line `		Is Button Held(Event Player, Button(Melee)) == True;` (that exact line text appears 3 times in the file - you MUST scope by the rule header, which is unique):
`		Is Button Held(Event Player, Button(Crouch)) == False;`

A2. New rule inserted directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor):
rule("[거래 01] 돈 건네기 (웅크리기+V)")
event Ongoing - Each Player / All / All.
Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.Busy == 0; Global Variable(ArchOn) == 0; Is Alive(Event Player) == True; Is Button Held(Event Player, Button(Crouch)) == True; Is Button Held(Event Player, Button(Melee)) == True.
Actions:
- Set Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(Players Within Radius(Eye Position(Event Player), 9, All Teams, Surfaces), And(Current Array Element != Event Player, And(Is Dummy Bot(Current Array Element) == False, And(Player Variable(Current Array Element, TutOn) == 0, And(Has Status(Current Array Element, Asleep) == False, And(Is Alive(Current Array Element), Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Eye Position(Current Array Element))) >= 0.93)))))), Distance Between(Eye Position(Event Player), Eye Position(Current Array Element)))));
- If(Not(Entity Exists(Event Player.Target)));
  - Small Message(Event Player, Custom String("건넬 상대가 없다 — 9m 안의 상대를 조준하고 웅크린 채 [{0}]", Input Binding String(Button(Melee))));
  - Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- Else If(Event Player.Money < 100);
  - Small Message(Event Player, Custom String("건넬 돈이 부족하다 — $100씩 건넨다"));
  - Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- Else;
  - Modify Player Variable(Event Player, Money, Subtract, 100);
  - Modify Player Variable(Event Player.Target, Money, Add, 100);
  - Small Message(Event Player, Custom String("{0}에게 $100을 건넸다", Event Player.Target));
  - Small Message(Event Player.Target, Custom String("{0}이(가) $100을 건넸다", Event Player));
  - Play Effect(Event Player.Target, Buff Impact Sound, Color(Lime Green), Position Of(Event Player.Target), 60);
- End;
- Wait(0.6, Ignore Condition);
(Received money must NOT touch Earned - a transfer is not income and must not feed the daily goal.)

A3. HUD hint (cnt=1): replace `Custom String("[{0}] 강도/체포", Input Binding String(Button(Melee)))` with `Custom String("[{0}] 강도/체포 · 앉아서 [{0}] 송금", Input Binding String(Button(Melee)))`.

# Part B - 채굴 정타 (timing bonus after each dig)
In rule "[직업 01] DoMine", insert immediately BEFORE the line (cnt=1) `		If(Modulo(Event Player.MineCount, 10) == 0);` this block (depth 2 base):
- Wait(Random Real(0.3, 0.8), Ignore Condition);
- If(Is Button Held(Event Player, Button(Jump)));
  - Small Message(Event Player, Custom String("성급한 곡괭이질 — 정타를 놓쳤다"));
- Else;
  - Small Message(Event Player, Custom String("광맥이 울렸다 — 지금! [{0}]", Input Binding String(Button(Jump))));
  - Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 45);
  - Wait Until(Is Button Held(Event Player, Button(Jump)), 0.5);
  - If(Is Button Held(Event Player, Button(Jump)));
    - Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 2));
    - Small Message(Event Player, Custom String("정타! 원석 +2 (보유 {0})", Value In Array(Event Player.Inv, 2)));
    - Play Effect(Event Player, Ring Explosion, Color(Orange), Position Of(Event Player), 1.2);
  - End;
- End;
(The random pre-delay punishes holding jump in advance; the 0.5s reaction window rewards attention. Busy is already 1 for the whole DoMine flow, so no state flag is needed.)

# Deliverables
patch103_trade.py (script alone suffices if execution is blocked). Verification counts for the caller: `rule("[거래 01] 돈 건네기 (웅크리기+V)")` = 1, `$100을 건넸다` = 2, `정타! 원석 +2` = 1, `광맥이 울렸다` = 1, `성급한 곡괭이질` = 1, `앉아서 [{0}] 송금` = 1, and inside rule "[범죄 01]" a crouch-False condition now precedes the Melee condition (verify by scoped search and report true/false). Touch nothing else.
