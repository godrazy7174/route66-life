Implement two things in this Overwatch 2 Workshop script project by writing ONE Python patch script: (A) a health-fill bugfix for giant/legendary beasts, (B) a new server event "전설의 야수 대사냥" (the Great Hunt). Work non-interactively: never ask questions, decide within this spec, and print a final summary report at the end.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,430 lines, a western life-sim Workshop gamemode). ROUTE66_LIFE.ow is the Korean build generated from it.
- All changes are made via atomic Python patch scripts (patchNN_name.py) that read ROUTE66_LIFE_EN.ow, perform exact-string substitutions with assert-counted occurrences, and write the file ONCE at the end. STUDY patch93_escort.py and patch91_moonshine.py first - they are the style references: their sub() helper, block()-style chr(9)/chr(10) tab/newline assembly (never raw backslash escapes in generated content), and their rule-insertion pattern are all patterns you must reuse.
- Your sandbox may block running Python (`CreateProcessAsUserW failed: 5`). If Python runs, run the validation pipeline below. If it does not, apply the patch to ROUTE66_LIFE_EN.ow by hand-editing it to EXACTLY what the patch script would produce, verify by careful re-reading, and say clearly in your report that validation must be re-run by the caller. Do NOT edit ROUTE66_LIFE.ow (the Korean build) - the caller regenerates it.
- Validation pipeline (all must pass, run from the project dir):
  python patch94_hunt.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow
  lint prints Korean check names; a pre-existing "possibly undeclared player vars" warning listing bare numbers is noise - ignore it. Any NEW warning or error is a failure you must fix before finishing.

# Workshop scripting rules you MUST follow (hard-won project doctrine)
1. Never place a ternary inside a comparison right-hand side and never use bare grouping parentheses like `X <= (a ? b : c)` - precompute into a variable first. A ternary as a whole function argument is fine.
2. Custom String takes max 3 format args; nest Custom Strings for more.
3. Messages re-evaluate while displayed: values shown in messages must be stable during display. Prefer constant strings; where a variable appears, it must not change during the ~2s display window.
4. Icons/effects are created and destroyed on state transitions - never rely on conditional visible-to with global state.
5. Korean text goes inside Custom String("...") literals as-is (files are UTF-8).
6. Write the patch file as patch94_hunt.py in UTF-8 with a `# -*- coding: utf-8 -*-` header and a Korean docstring, matching patch91's format. Every sub() assert-counted.

# Relevant existing machinery (do not re-derive; trust this)
- Time: Global Variable(Day) (starts 1, increments daily), Global Variable(Clock) (0..1440, 420=7am start, day rolls at 1440), Global Variable(IsNight) (0 day / 1 night; night is Clock >= 1200 or < 360). Train day is Modulo(Day, 3) == 0 - the hunt uses Modulo(Day, 3) == 1 so they never collide.
- Beasts: 3 Team 2 dummy bots kept alive by rule "[직업 03-5] 야수 정원 감시 — 항상 3마리". Rule "[직업 03] 야수 은신" fully resets and re-hides any beast once Total Time Elapsed() >= its RevealEnd (resets Max Health 40, removes pools, stops scaling, Giant=0, phases out). Rule "[직업 03-3] 야수 배회" makes revealed beasts run/jump and LEASHES them within 11m of LocPos index 6 (협곡 개활지) - so the Great Hunt battle happens at the 개활지 by design. Rule "[직업 03-4] 야수 위치 표시" already creates a tracking icon over any revealed beast. Rule "[직업 03-2] 야수 처치" (event Player Died / Team 2) pays normal hunt loot on any beast death - it will ALSO fire when the Great Hunt beast dies; that is intentional and harmless (last-hitter gets a few normal pelts), do NOT edit it.
- Pelts inventory slot: Modify Player Variable At Index(player, Inv, 3, Add, N). Fame cap: Set Player Variable(p, Fame, Min(100, Add(..., N))). Lawful money also adds to Earned.
- Effects/icons/reevaluation tokens already used in this file (safe to use): Sphere, Light Shaft, Ring Explosion, Explosion Sound, Buff Impact Sound, Buff Explosion Sound, Circle, Diamond, "Visible To and Position", "Visible To Position Radius and Color". Events already used: Ongoing - Global, Ongoing - Each Player, Player Died. You will additionally use the standard event "Player Dealt Damage" (with Victim and Event Damage) - write it exactly like the engine spells it.

# Part A - health-fill fix (처방)
In rule "[직업 02] DoHunt", the reveal loop raises max health but never fills it. Two insertions, each cnt=1:
- After the line `Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 50, False);` insert (same indent, depth 4): `Heal(Value In Array(Event Player.Target, Event Player.Idx), Null, 9999);`
- After the line `Start Scaling Player(Value In Array(Event Player.Target, Event Player.Idx), 2.4, False);` insert (same indent, depth 4): `Heal(Value In Array(Event Player.Target, Event Player.Idx), Null, 9999);`

# Part B - 전설의 야수 대사냥 (Great Hunt)
A 3-day-cycle server event: at morning of every hunt day, a track appears somewhere on the map; players investigate tracks with [F] three times; the third investigation awakens the Great Beast at the 개활지; everyone damages it; on death, rewards are split by damage contribution. At nightfall the whole event retreats if unfinished.

New global variables (append right after the line `		48: TrainIco`, same 2-tab indent):
49 HuntPhase, 50 HuntBeast, 51 HuntTrackPos, 52 HuntTrackIco, 53 HuntTrackFx, 54 HuntDay, 55 HuntArr, 56 HuntIdx
New player variable (append right after the line `		122: EscortFx`): 123 HuntDmg

## Edit B1 - exclude the hunt beast from normal tracking
The line `Set Player Variable(Event Player, Target, Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))));` occurs once. Replace its filter with:
`Set Player Variable(Event Player, Target, Filtered Array(All Players(Team 2), And(And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element)), Current Array Element != Global Variable(HuntBeast))));`
(cnt=1; run this sub BEFORE inserting the new rules so the count stays unambiguous.)

## Edit B2 - five new rules, inserted directly before rule("[감옥 01] 만기 출소") in this order

### rule("[대사냥 01] 대야수의 흔적")
event Ongoing - Global. Conditions: Global Variable(Ready) == 1; Modulo(Global Variable(Day), 3) == 1; Global Variable(Day) >= 4; Global Variable(Day) > Global Variable(HuntDay); Global Variable(IsNight) == 0.
Actions:
- Set Global Variable(HuntDay, Global Variable(Day));
- Set Global Variable(HuntPhase, 1);
- Set Global Variable(HuntTrackPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-18, 18), 0, Random Real(-18, 18)))));
- Destroy Icon(Global Variable(HuntTrackIco)); Destroy Effect(Global Variable(HuntTrackFx));
- Create Effect(All Players(All Teams), Light Shaft, Color(Orange), Global Variable(HuntTrackPos), 1.5, Visible To Position Radius and Color); Set Global Variable(HuntTrackFx, Last Created Entity());
- Create Icon(All Players(All Teams), Add(Global Variable(HuntTrackPos), Vector(0, 3, 0)), Circle, Visible To and Position, Color(Orange), True); Set Global Variable(HuntTrackIco, Last Created Entity());
- Big Message(All Players(All Teams), Custom String("대사냥의 날 — 대야수의 흔적이 나타났다! 주황 표식을 조사하라"));
- Play Effect(All Players(All Teams), Buff Impact Sound, Color(Orange), Global Variable(HuntTrackPos), 200);

### rule("[대사냥 02] 흔적 조사 (F)")
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Event Player.Busy == 0; Global Variable(ArchOn) == 0; Global Variable(HuntPhase) >= 1; Global Variable(HuntPhase) <= 3; Is Alive(Event Player) == True; Distance Between(Position Of(Event Player), Global Variable(HuntTrackPos)) < 5; Is Button Held(Event Player, Button(Crouch)) == False; Is Button Held(Event Player, Button(Interact)) == True.
Actions:
- Destroy Icon(Global Variable(HuntTrackIco)); Destroy Effect(Global Variable(HuntTrackFx));
- If(Global Variable(HuntPhase) <= 2);
  - Modify Global Variable(HuntPhase, Add, 1);
  - Set Global Variable(HuntTrackPos, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), Random Integer(0, 12)), Vector(Random Real(-18, 18), 0, Random Real(-18, 18)))));
  - Create Effect(All Players(All Teams), Light Shaft, Color(Orange), Global Variable(HuntTrackPos), 1.5, Visible To Position Radius and Color); Set Global Variable(HuntTrackFx, Last Created Entity());
  - Create Icon(All Players(All Teams), Add(Global Variable(HuntTrackPos), Vector(0, 3, 0)), Circle, Visible To and Position, Color(Orange), True); Set Global Variable(HuntTrackIco, Last Created Entity());
  - Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));
  - Big Message(All Players(All Teams), Custom String("흔적을 찾았다 — 냄새가 짙어진다. 다음 표식으로"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 60);
- Else;
  - Set Global Variable(HuntPhase, 4);
  - Set Global Variable(HuntBeast, First Of(Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element)))));
  - Set Player Variable(Global Variable(HuntBeast), RevealEnd, Add(Total Time Elapsed(), 9999));
  - Set Player Variable(Global Variable(HuntBeast), Giant, 0);
  - Set Max Health(Global Variable(HuntBeast), 1000);
  - Remove All Health Pools From Player(Global Variable(HuntBeast));
  - Add Health Pool To Player(Global Variable(HuntBeast), Health, 8000, True, True);
  - Heal(Global Variable(HuntBeast), Null, 9999);
  - Start Scaling Player(Global Variable(HuntBeast), 30, False);
  - Clear Status(Global Variable(HuntBeast), Phased Out);
  - Set Invisible(Global Variable(HuntBeast), None);
  - Teleport(Global Variable(HuntBeast), Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-5, 5), 0, Random Real(-5, 5)))));
  - Set Player Variable(All Players(All Teams), HuntDmg, 0);
  - Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));
  - Big Message(All Players(All Teams), Custom String("대야수가 깨어났다!! 협곡 개활지다 — 쓰러뜨린 몫은 기여만큼 나눈다"));
  - Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Global Variable(HuntBeast)), 20);
  - Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(Global Variable(HuntBeast)), 300);
- End;
- Wait(0.3, Ignore Condition);

### rule("[대사냥 03] 기여 기록")
event Player Dealt Damage / All / All. Conditions: Global Variable(HuntPhase) == 4; Victim == Global Variable(HuntBeast); Is Dummy Bot(Event Player) == False.
Actions: Modify Player Variable(Event Player, HuntDmg, Add, Event Damage);

### rule("[대사냥 04] 대야수 토벌")
event Player Died / Team 2 / All. Conditions: Is Dummy Bot(Victim) == True; Global Variable(HuntPhase) == 4; Victim == Global Variable(HuntBeast).
Actions:
- Set Global Variable(HuntPhase, 0);
- Set Global Variable(HuntArr, Sorted Array(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, HuntDmg) >= 1), Subtract(0, Player Variable(Current Array Element, HuntDmg))));
- For Global Variable(HuntIdx, 0, Count Of(Global Variable(HuntArr)), 1);
  - Modify Player Variable At Index(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Inv, 3, Add, 15);
  - Set Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Fame, Min(100, Add(Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Fame), 10)));
  - Modify Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Money, Add, 200);
  - Modify Player Variable(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Earned, Add, 200);
  - Small Message(Value In Array(Global Variable(HuntArr), Global Variable(HuntIdx)), Custom String("대사냥 보상 — 가죽 15장 · $200 · 명성 +10"));
- End;
- If(Count Of(Global Variable(HuntArr)) >= 1);
  - Modify Player Variable At Index(First Of(Global Variable(HuntArr)), Inv, 3, Add, 35);
  - Modify Player Variable(First Of(Global Variable(HuntArr)), Money, Add, 300);
  - Modify Player Variable(First Of(Global Variable(HuntArr)), Earned, Add, 300);
  - Big Message(All Players(All Teams), Custom String("{0} — 대야수 토벌의 일등 공신! (가죽 +35 · +$300)", First Of(Global Variable(HuntArr))));
- End;
- Big Message(All Players(All Teams), Custom String("대야수가 쓰러졌다!! 참가자 모두에게 몫이 돌아간다"));
- Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Victim), 20);
- Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Red), Position Of(Victim), 300);
- Set Player Variable(Victim, RevealEnd, 0);
- Set Player Variable(All Players(All Teams), HuntDmg, 0);
- Set Global Variable(HuntBeast, Null);
(The generic beast-death rule and the re-hide rule handle the dummy's own stat cleanup; do not duplicate it beyond RevealEnd=0.)

### rule("[대사냥 05] 밤이 오면 물러난다")
event Ongoing - Global. Conditions: Global Variable(HuntPhase) >= 1; Global Variable(IsNight) == 1.
Actions:
- If(Global Variable(HuntPhase) == 4);
  - Set Player Variable(Global Variable(HuntBeast), RevealEnd, 0);
- Else;
  - Destroy Icon(Global Variable(HuntTrackIco)); Destroy Effect(Global Variable(HuntTrackFx));
- End;
- Set Global Variable(HuntPhase, 0);
- Set Global Variable(HuntBeast, Null);
- Set Player Variable(All Players(All Teams), HuntDmg, 0);
- Big Message(All Players(All Teams), Custom String("대야수의 기척이 밤 속으로 사라졌다 — 사흘 뒤를 노려라"));

# Deliverables
- patch94_hunt.py in the project dir, every sub() assert-counted.
- Apply it (via Python if the sandbox allows, otherwise by exact hand-application to ROUTE66_LIFE_EN.ow only).
- Verify in ROUTE66_LIFE_EN.ow (count occurrences) and print the counts in your final report: `Heal(Value In Array(Event Player.Target, Event Player.Idx), Null, 9999);` = 2, `rule("[대사냥 0` = 5, "대사냥의 날" = 1, "대야수가 깨어났다" = 1, "대야수가 쓰러졌다" = 1, "일등 공신" = 1, "밤 속으로 사라졌다" = 1, `!= Global Variable(HuntBeast)` = 1, `56: HuntIdx` = 1, `123: HuntDmg` = 1, `Player Dealt Damage` = 1.
- Final report: what you changed, whether validation actually ran, and the occurrence counts. Do not modify anything outside this feature. Do not reformat existing code. Do not edit ROUTE66_LIFE.ow.
