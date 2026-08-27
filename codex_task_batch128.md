Apply a balance-and-features batch to this Overwatch 2 Workshop project via ONE Python patch script patch128_batch.py: cow-push speed x2, hunter yield trim, mining-QTE reward +3, a daily-contract HUD line, neighbor ranch-tending (light employment), and an in-world wiki signpost. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949). IMPORTANT: write all Korean text as literal UTF-8 characters in the script, never as \\u escapes.

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,348 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted (occurrence counts via str.count), block() assembly, one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch128_batch.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens; a ternary as a WHOLE function argument is fine (used in Edit D exactly as written). Custom String literals <= 120 chars. Korean as-is.

# Edit A - cow push step x2 (cnt=1)
`Add(2.2, Multiply(0.9, Value In Array(Event Player.Adv, 6)))` -> `Add(4.4, Multiply(1.8, Value In Array(Event Player.Adv, 6)))`

# Edit B - hunter yield trim (cnt=1)
`Modify Player Variable(Attacker, Yield, Add, Add(1, Value In Array(Player Variable(Attacker, Adv), 2)));` -> `Modify Player Variable(Attacker, Yield, Add, Value In Array(Player Variable(Attacker, Adv), 2));`

# Edit C - mining QTE reward +2 -> +3 (each cnt=1)
- `Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 2));` -> `..., 3));` (this exact line is the QTE success line - the trailing `, 2));` becomes `, 3));`)
- `정타! 원석 +2 (보유 {0})` -> `정타! 원석 +3 (보유 {0})`

# Edit D - daily-contract HUD line
Locate the single line containing `열차가 섰다! 금고 3칸` (the event-guidance Create HUD Text inserted recently, cnt=1). Insert immediately AFTER that whole line (same 2-tab indent) a new line:
`		Create HUD Text(Local Player.TutOn == 0 ? Local Player : False, Null, Global Variable(ContractKind) >= 1 ? Custom String("계약   {0}   {1}", Value In Array(Array(Custom String("채굴 8회"), Custom String("야수 4마리"), Custom String("배달 3건"), Custom String("소몰이 2회")), Subtract(Global Variable(ContractKind), 1)), Modulo(Local Player.Giant, 10) >= Value In Array(Array(8, 4, 3, 2), Subtract(Global Variable(ContractKind), 1)) ? Custom String("완료") : Custom String("{0} / {1}", Modulo(Local Player.Giant, 10), Value In Array(Array(8, 4, 3, 2), Subtract(Global Variable(ContractKind), 1)))) : Custom String(""), Null, Left, 4, Color(White), Color(Aqua), Color(White), Visible To Sort Order String and Color, Default Visibility);`

# Edit E - neighbor tending (light employment): new rule inserted directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor)
rule("[목장 03] 이웃의 손길")
event Ongoing - Each Player / All / All.
Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.TutOn == 0; Event Player.Busy == 0; Event Player.Zone == 12; Is Alive(Event Player) == True; Is Button Held(Event Player, Button(Crouch)) == True; Is Button Held(Event Player, Button(Interact)) == True.
Actions:
- Set Player Variable(Event Player, Target, First Of(Filtered Array(All Players(All Teams), And(Current Array Element != Event Player, And(Player Variable(Current Array Element, RanchEnd) > Total Time Elapsed(), Player Variable(Current Array Element, RanchCare) == 0)))));
- If(Entity Exists(Event Player.Target));
  - Set Player Variable(Event Player.Target, RanchCare, 1);
  - Modify Player Variable(Event Player, Money, Add, 10);
  - Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 1)));
  - Small Message(Event Player, Custom String("{0}의 소에게 물을 줬다 — 품삯 $10 · 명성 +1", Event Player.Target));
  - Small Message(Event Player.Target, Custom String("{0}이(가) 내 목장의 소를 돌봐줬다", Event Player));
  - Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);
- Else;
  - Small Message(Event Player, Custom String("돌봐줄 이웃의 소가 없다"));
- End;
- Wait(1, Ignore Condition);
(Note: crouch+F at the ranch does not collide with property purchase - the ranch is not a purchasable building.)

# Edit F - in-world wiki signpost on the main road
In rule "[코어 02] BuildWorld", insert immediately AFTER the line starting `	Set Global Variable(TrainPos,` (locate it inside BuildWorld - the fragment `Set Global Variable(TrainPos` occurs 2 times in the file; the BuildWorld one is the FIRST occurrence; scope by taking the first) a new line (1-tab indent):
`	Create In-World Text(All Players(All Teams), Custom String("길잡이 — 궁금한 것은 공식 위키로: route66-life-wiki.ray-on.chatgpt.site"), Add(Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 0), Value In Array(Global Variable(LocPos), 11)), 0.5)), Vector(0, 1.8, 0)), 1.1, Do Not Clip, Visible To and Position, Color(Aqua), Default Visibility);`

# Deliverables
patch128_batch.py (script alone suffices if execution is blocked). Verification counts for the caller: `Add(4.4, Multiply(1.8,` = 1, `Yield, Add, Value In Array(Player Variable(Attacker, Adv), 2));` = 1, `정타! 원석 +3` = 1, `계약   {0}   {1}` = 1, `rule("[목장 03] 이웃의 손길")` = 1, `소에게 물을 줬다` = 1, `route66-life-wiki.ray-on.chatgpt.site` = 1, `Array(8, 4, 3, 2)` = 2. Touch nothing else.
