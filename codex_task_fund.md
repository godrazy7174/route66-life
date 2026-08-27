Implement the server-communal "국도 부흥 기금" (Route 66 revival fund) in this Overwatch 2 Workshop project via ONE Python patch script patch109_fund.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,200 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch100_rebirth.py / patch107_minigames.py: sub() assert-counted, block() assembly, insert_into-style rule-scoped edits where noted, one write, UTF-8 header, Korean docstring.
- Player variables are FULL: NO new player variables. TWO new globals are allowed. Room-lifetime asset: nothing is saved to the save code (do not touch save rules).
- Validation (run if possible): python patch109_fund.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens; whole-function-argument ternary fine. Custom String max 3 args, literals <= 120 chars. Big/Small Message values must be display-stable (snapshot into Amt where noted). Korean as-is.

# Design
All players donate $1,000 a press into one server fund at the stagecoach station. Cumulative milestones open shared facilities: $60,000 -> 길손의 쉼터 (a physical campfire rest stop on the road between the diner and the station: regen zone), $180,000 -> 역마차 급행로 (server-wide delivery & gold-escort pay +15%), $400,000 -> 국도 대축제 (nightly fireworks, today's-job bonus 1.5x -> 1.75x, everyone +1 Fame each morning). Donors get Fame +2 per donation and a server-wide callout. The shared rest-stop position is ALWAYS computed inline as:
`Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 0), Value In Array(Global Variable(LocPos), 11)), 0.5))`
(deterministic; no position variable needed).

## Edit 1 - globals
Append after the line `		57: ContractKind` (cnt=1): `		58: Fund` and `		59: FundTier` (same 2-tab indent, two lines).

## Edit 2 - station menu 5 -> 6
`Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 5, 4, 1, 1)` occurs EXACTLY 3 times; replace all 3 (cnt=3) with `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 6, 4, 1, 1)`.

## Edit 3 - label (cnt=1)
Replace `Custom String("새 출발의 기차 — 환생"), Custom String("-")` with `Custom String("새 출발의 기차 — 환생"), Custom String("부흥 기금 기부 $1,000")`.

## Edit 4 - station chain: donation branch
4a. Replace anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Event Player.Rebuild < 5);` with (3 tabs)`Else If(Event Player.MenuIdx == 4);`(newline)(4 tabs)`If(Event Player.Rebuild < 5);` (cnt=1).
4b. At the zone-11 chain close - the sequence (4 tabs)`End;`(newline)(3 tabs)`End;`(newline)(2 tabs)`Else If(Event Player.Zone == 12);` (cnt=1) - insert between the first End; and the second a new depth-3 `Else;` branch:
- If(Event Player.Money < 1000);
  - Small Message(Event Player, Custom String("돈이 부족합니다 ($1000 필요)")); plus Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- Else;
  - Modify Player Variable(Event Player, Money, Subtract, 1000);
  - Modify Global Variable(Fund, Add, 1000);
  - Set Player Variable(Event Player, Amt, Global Variable(Fund));
  - Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));
  - Big Message(All Players(All Teams), Custom String("{0} — 부흥 기금에 $1,000 (기금 $ {1})", Event Player, Event Player.Amt));
  - Play Effect(All Players(All Teams), Buff Impact Sound, Color(Yellow), Position Of(Event Player), 90);
- End;

## Edit 5 - three new rules, inserted directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor), in this order

### rule("[기금 01] 부흥의 불")
event Ongoing - Global. Conditions: Global Variable(Ready) == 1; Global Variable(FundTier) <= 2; Global Variable(Fund) >= Value In Array(Array(60000, 180000, 400000), Global Variable(FundTier)).
Actions:
- Modify Global Variable(FundTier, Add, 1);
- If(Global Variable(FundTier) == 1);
  - Create Effect(All Players(All Teams), Sphere, Color(Orange), Add(<the inline rest-stop position expression>, Vector(0, 0.5, 0)), 0.8, None);
  - Create Effect(All Players(All Teams), Light Shaft, Color(Orange), <the inline rest-stop position expression>, 1.4, None);
  - Create In-World Text(All Players(All Teams), Custom String("길손의 쉼터"), Add(<the inline rest-stop position expression>, Vector(0, 2.4, 0)), 1.3, Do Not Clip, Visible To and Position, Color(Orange), Default Visibility);
  - Big Message(All Players(All Teams), Custom String("부흥 기금 1단계!! 길손의 쉼터가 세워졌다 — 길목의 모닥불에서 몸을 데워라"));
- Else If(Global Variable(FundTier) == 2);
  - Big Message(All Players(All Teams), Custom String("부흥 기금 2단계!! 역마차 급행로 개통 — 배달·금괴 호송 보수 +15%"));
- Else;
  - Big Message(All Players(All Teams), Custom String("부흥 기금 3단계!! 국도 대축제 — 오늘의 직업 1.75배 · 밤마다 불꽃놀이 · 아침마다 명성 +1"));
- End;
- Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), <the inline rest-stop position expression>, 8);
- Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Orange), <the inline rest-stop position expression>, 250);
- Wait(0.5, Ignore Condition);
(Condition note: when FundTier reaches 3 the array index is out of range and Value In Array returns 0, but FundTier <= 2 already blocks the rule - safe.)

### rule("[기금 02] 모닥불 곁")
event Ongoing - Each Player / All / All. Conditions: Is Dummy Bot(Event Player) == False; Event Player.Init == 1; Global Variable(FundTier) >= 1; Is Alive(Event Player) == True; Distance Between(Position Of(Event Player), <the inline rest-stop position expression>) < 8.
Actions:
- Wait(10, Ignore Condition);
- If(And(Distance Between(Position Of(Event Player), <the inline rest-stop position expression>) < 8, Is Alive(Event Player)));
  - Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 1)));
  - Set Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 1.5)));
  - Play Effect(Event Player, Good Pickup Effect, Color(Orange), Position Of(Event Player), 1);
- End;
- Loop If(Distance Between(Position Of(Event Player), <the inline rest-stop position expression>) < 8);

### rule("[기금 03] 축제의 밤")
event Ongoing - Global. Conditions: Global Variable(FundTier) >= 3; Global Variable(IsNight) == 1.
Actions: three volleys, each volley being:
- Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 0), Vector(Random Real(-10, 10), 14, Random Real(-10, 10))), 7);
- Play Effect(All Players(All Teams), Explosion Sound, Color(Yellow), Value In Array(Global Variable(LocPos), 0), 200);
- Wait(1.2, Ignore Condition);
then:
- Big Message(All Players(All Teams), Custom String("국도 대축제의 밤 — 불꽃이 66번 국도를 밝힌다"));
- Wait Until(Global Variable(IsNight) == 0, 99999);
(Refires automatically each night while tier 3 holds.)

## Edit 6 - express-road pay boosts (+15% at tier 2)
6a. Delivery: inside rule "[파발 01] 배달 도착 — 자동 정산", insert immediately BEFORE its line `		Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);` (rule-scoped - that line also exists in the cattle rule, so locate via the [파발 01] rule header, which is unique):
- If(Global Variable(FundTier) >= 2);
  - Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, 1.15), To Nearest));
- End;
6b. Escort: insert immediately AFTER the line (cnt=1) `					Set Player Variable(Event Player, EscortPay, Round To Integer(Add(40, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2.5)), To Nearest));` (same indent):
- If(Global Variable(FundTier) >= 2);
  - Set Player Variable(Event Player, EscortPay, Round To Integer(Multiply(Event Player.EscortPay, 1.15), To Nearest));
- End;

## Edit 7 - festival today's-job multiplier (1.5 -> 1.75 at tier 3)
Replace the fragment `, 1.5), To Nearest));` with `, Global Variable(FundTier) >= 3 ? 1.75 : 1.5), To Nearest));` ONLY in these exact lines (assert-counted per pattern):
- `Set Player Variable(Event Player, MineGain, Round To Integer(Multiply(Player Variable(Event Player, MineGain), 1.5), To Nearest));` (cnt=2)
- `Set Player Variable(Attacker, Yield, Round To Integer(Multiply(Player Variable(Attacker, Yield), 1.5), To Nearest));` (cnt=1)
- `Set Player Variable(Event Player, PlanPay, Round To Integer(Multiply(Player Variable(Event Player, PlanPay), 1.5), To Nearest));` (cnt=2)
- `Set Player Variable(Event Player, RunPay, Round To Integer(Multiply(Player Variable(Event Player, RunPay), 1.5), To Nearest));` (cnt=2)

## Edit 8 - festival morning fame
In rule "[월드 05] 아침 정산", insert immediately BEFORE the line `		If(And(Event Player.Rebirth >= 1, Event Player.Earned > Event Player.DayStart));` (cnt=1):
- If(Global Variable(FundTier) >= 3);
  - Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 1)));
- End;

## Edit 9 - HUD fund line (cnt=1)
Replace `Custom String("소지금   $ {0}   예금 $ {1}", Local Player.Money, Local Player.Deposit), Null,` with `Custom String("소지금   $ {0}   예금 $ {1}", Local Player.Money, Local Player.Deposit), Custom String("부흥 기금 $ {0}   ({1}/3)", Global Variable(Fund), Global Variable(FundTier)),`.

## Edit 10 - station signboard (cnt=1)
After the line `새 출발의 기차 — 재건을 마친 자는 전 재산을 두고 다시 태어난다` and its RN escape (chr(92)+'r'+chr(92)+'n'), append `부흥 기금 — $1000씩 모아 쉼터·급행로·대축제를 연다` plus the same RN.

# Deliverables
patch109_fund.py (script alone suffices if execution is blocked). Verification counts for the caller: `58: Fund` = 1, `59: FundTier` = 1, `부흥 기금 기부 $1,000` = 1, `부흥 기금에 $1,000` = 1, `rule("[기금 01] 부흥의 불")` = 1, `rule("[기금 02] 모닥불 곁")` = 1, `rule("[기금 03] 축제의 밤")` = 1, `길손의 쉼터` = 2, `? 1.75 : 1.5), To Nearest));` = 7, `Multiply(Event Player.RunPay, 1.15)` = 1, `Multiply(Event Player.EscortPay, 1.15)` = 1, `부흥 기금 $ {0}` = 1, `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 6, 4, 1, 1)` = 3. Touch nothing else.
