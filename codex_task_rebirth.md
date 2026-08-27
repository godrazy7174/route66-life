Implement the 환생 (rebirth) system in this Overwatch 2 Workshop project by writing ONE Python patch script, patch100_rebirth.py. Work non-interactively: never ask questions, decide within this spec, print a final summary report.

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~4,815 lines). Do NOT edit ROUTE66_LIFE.ow.
- STUDY patch99_rebuildperks.py / patch95_ranch.py for helpers and conventions. `# -*- coding: utf-8 -*-` + Korean docstring, sub() assert-counted, one write.
- Player variables are FULL: declare NO new variable. `Rebirth` (92) already exists and is already saved/restored by the save-code rules - do not touch those. The double-press confirm timer reuses `EntryCur` (83, only otherwise used during save-code entry).
- Sandbox may block Python - if so, hand-apply exactly and say validation must be re-run.
- Validation: python patch100_rebirth.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS and no bare grouping parens; whole-function-argument ternary fine (nest via Custom String for chained title logic exactly as specified below). Custom String max 3 args. Message values must be display-stable. Korean as-is in Custom String.

# Design
A player who finished the rebuild ladder (Rebuild == 5) can board the dawn train at the stagecoach station and be reborn: full reset of wealth and progress, keeping job XP/advancements, Fame/Noto, and gaining a permanent morning income bonus (+10% of yesterday's earnings per rebirth, max 5) plus a priority title.

## Edit 1 - station menu 4 -> 5
`Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 4, 4, 1, 1)` occurs EXACTLY 3 times; replace all 3 (cnt=3) with `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 5, 4, 1, 1)` (index 12, zone 11 정거장, 4 -> 5).

## Edit 2 - label (cnt=1)
Replace `Custom String("가축 출하 — 마리당 $60"), Custom String("-")` with `Custom String("가축 출하 — 마리당 $60"), Custom String("새 출발의 기차 — 환생")`.

## Edit 3 - zone-11 chain: add the rebirth branch
3a. Replace anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Event Player.RanchReady <= 0);` with (3 tabs)`Else If(Event Player.MenuIdx == 3);`(newline)(4 tabs)`If(Event Player.RanchReady <= 0);` (cnt=1).
3b. The zone-11 chain closes with (4 tabs)`End;`(newline)(3 tabs)`End;`(newline)(2 tabs)`Else If(Event Player.Zone == 12);` (cnt=1). Insert between the first End; and the second a new depth-3 `Else;` branch (the rebirth logic, depth 4 unless nested):
- If(Event Player.Rebuild < 5);
  - Small Message(Event Player, Custom String("기차역을 재건한 자만 이 기차에 오른다 (재건 {0}/5)", Event Player.Rebuild)); plus Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
- Else If(Event Player.Rebirth >= 5);
  - Small Message(Event Player, Custom String("이미 전설이다 — 다섯 번의 새벽을 지났다")); plus the red debuff sound;
- Else If(Event Player.EntryCur >= Total Time Elapsed());
  (the confirmed second press - execute the rebirth:)
  - Set Player Variable(Event Player, EntryCur, 0);
  - Modify Player Variable(Event Player, Rebirth, Add, 1);
  - For Player Variable(Event Player, Idx, 0, 11, 1);
    - If(Value In Array(Global Variable(BldOwner), Event Player.Idx) == Event Player);
      - Set Global Variable At Index(BldOwner, Event Player.Idx, 0);
    - End;
  - End;
  - Set Player Variable(Event Player, Money, 60);
  - Set Player Variable(Event Player, Deposit, 0);
  - Set Player Variable(Event Player, Inv, Array(2, 2, 0, 0));
  - Set Player Variable(Event Player, Pick, 0);
  - Set Player Variable(Event Player, HasBag, 0);
  - Set Player Variable(Event Player, HasHorse, 0);
  - Set Player Variable(Event Player, HasHome, 0);
  - Set Player Variable(Event Player, Whisky, 0);
  - Set Player Variable(Event Player, Rebuild, 0);
  - Set Player Variable(Event Player, Tier, 0);
  - Set Player Variable(Event Player, Bounty, 0);
  - Set Player Variable(Event Player, Sack, 0);
  - Set Player Variable(Event Player, HasPowder, 0);
  - Set Player Variable(Event Player, BrewVats, 0); Set Player Variable(Event Player, BrewEnd, 0); Set Player Variable(Event Player, BrewReady, 0);
  - Set Player Variable(Event Player, RanchPens, 0); Set Player Variable(Event Player, RanchEnd, 0); Set Player Variable(Event Player, RanchReady, 0); Set Player Variable(Event Player, RanchCare, 0);
  - If(Event Player.Contraband == 1); Set Player Variable(Event Player, Contraband, 0); Destroy Icon(Event Player.SmuggleIco); End;
  - If(Event Player.Escort == 1); Set Player Variable(Event Player, Escort, 0); Destroy Icon(Event Player.EscortIco); Destroy Effect(Event Player.EscortFx); End;
  - If(Event Player.HasParcel == 1); Set Player Variable(Event Player, HasParcel, 0); Destroy Icon(Event Player.DelIcon); End;
  - If(Event Player.CowOn == 1); Set Player Variable(Event Player, CowOn, 0); Destroy Effect(Event Player.CowFx); Destroy Icon(Event Player.CowIco); End;
  - Set Player Variable(Event Player, Earned, 0);
  - Set Player Variable(Event Player, DayStart, 0);
  - Set Player Variable(Event Player, GoalDone, 0);
  - Stop Forcing Player To Be Hero(Event Player);
  - Teleport(Event Player, Value In Array(Global Variable(LocPos), 0));
  - Big Message(All Players(All Teams), Custom String("{0} — 새벽 기차를 타고 다시 태어났다!! (환생 {1}회)", Event Player, Event Player.Rebirth));
  - Small Message(Event Player, Custom String("명성·악명·직업 경험은 남는다 — 아침마다 어제 수입의 {0}%가 얹힌다", Multiply(10, Event Player.Rebirth)));
  - Play Effect(All Players(All Teams), Ring Explosion, Color(White), Position Of(Event Player), 8);
  - Play Effect(All Players(All Teams), Buff Explosion Sound, Color(White), Position Of(Event Player), 250);
- Else;
  - Set Player Variable(Event Player, EntryCur, Add(Total Time Elapsed(), 10));
  - Big Message(Event Player, Custom String("정말 떠나는가 — 10초 안에 다시 실행하면 환생한다"));
  - Small Message(Event Player, Custom String("전 재산·장비·부동산·사업·재건이 사라진다. 남는 것: 직업 경험 · 명성/악명 · 환생의 가호"));
- End;

## Edit 4 - morning rebirth bonus
In rule "[월드 05] 아침 정산", insert immediately BEFORE the line `		If(Event Player.Deposit >= 100);` (the interest block added by patch99, cnt=1):
- If(And(Event Player.Rebirth >= 1, Event Player.Earned > Event Player.DayStart));
  - Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Subtract(Event Player.Earned, Event Player.DayStart), Multiply(0.1, Event Player.Rebirth)), Down));
  - If(Event Player.Amt >= 1);
    - Modify Player Variable(Event Player, Money, Add, Event Player.Amt);
    - Small Message(Event Player, Custom String("환생의 가호 — 어제 수입의 {0}%, +$ {1}", Multiply(10, Event Player.Rebirth), Event Player.Amt));
  - End;
- End;

## Edit 5 - priority title over the head (cnt=2, the fragment appears in exactly two identical name-tag lines)
Replace this exact fragment:
`Event Player.Rebuild >= 5 ? Custom String("66번 국도의 재건자") : Value In Array(Array(Custom String("떠돌이"), Custom String("일꾼"), Custom String("정착민"), Custom String("유지"), Custom String("거상"), Custom String("66번 국도의 주인")), Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), Event Player.Money >= 2500), Event Player.Money >= 6000), Event Player.Money >= 15000))`
with:
`Event Player.Rebirth >= 1 ? Value In Array(Array(Custom String("환생자"), Custom String("환생자"), Custom String("불사조"), Custom String("불사조"), Custom String("66번 국도의 전설")), Subtract(Min(5, Event Player.Rebirth), 1)) : Custom String("{0}", ` + THE ORIGINAL FRAGMENT + `)`
(i.e. the old expression survives verbatim, wrapped in Custom String("{0}", ...) as the ternary's else-arm. Wanted status stays the outermost priority because it wraps this whole expression already.)

## Edit 6 - station signboard (cnt=1)
After the line `가축 출하 — 목장에서 기른 소, 마리당 $60` and its literal backslash-r backslash-n sequence (chr(92)+'r'+chr(92)+'n'), append `새 출발의 기차 — 재건을 마친 자는 전 재산을 두고 다시 태어난다` plus the same newline sequence.

# Deliverables
patch100_rebirth.py, applied. Verify and print counts: `새 출발의 기차 — 환생` = 1, `새벽 기차를 타고 다시 태어났다` = 1, `환생의 가호` = 2 (menu warning small-message uses the phrase once and the morning bonus once), `정말 떠나는가` = 1, `Custom String("환생자")` = 2, `66번 국도의 전설` = 2, `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 5, 4, 1, 1)` = 3, `Stop Forcing Player To Be Hero(Event Player);` = 1, `재건을 마친 자는 전 재산을 두고` = 1. Report what changed, whether validation ran, and the counts. Touch nothing else - especially not the save-code rules.
