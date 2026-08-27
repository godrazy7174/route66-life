Implement a new game feature in this Overwatch 2 Workshop script project by writing ONE Python patch script: "내 목장 경영" (player-owned ranch business), the lawful mirror of the moonshine brewery. Work non-interactively: never ask questions, decide within this spec, and print a final summary report at the end.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,625 lines). ROUTE66_LIFE.ow is the Korean build generated from it.
- All changes are made via atomic Python patch scripts. STUDY patch91_moonshine.py first - this feature deliberately mirrors its structure (build -> feed -> mature -> sell, multiplexed into one menu slot plus one expansion slot). Also see patch93_escort.py for the station menu-chain edit pattern. Reuse their sub()/block() helpers, chr(9)/chr(10) assembly, and RN = chr(92)+'r'+chr(92)+'n' for signboard newlines.
- Your sandbox may block running Python (`CreateProcessAsUserW failed: 5`). If Python runs, run the validation pipeline below. If it does not, apply the patch to ROUTE66_LIFE_EN.ow by hand-editing it to EXACTLY what the patch script would produce, verify by careful re-reading, and say clearly in your report that validation must be re-run by the caller. Do NOT edit ROUTE66_LIFE.ow.
- Validation pipeline: python patch95_ranch.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow
  (a pre-existing "possibly undeclared player vars" warning listing bare numbers is noise; any NEW warning is a failure.)

# Workshop doctrine (MUST follow)
1. No ternary inside a comparison right-hand side, no bare grouping parens; a ternary as a WHOLE function argument is fine.
2. Custom String max 3 format args; nest for more.
3. Messages re-evaluate while displayed: shown values must be stable (SellQty/SellSum snapshot pattern from patch91).
4. Korean text goes inside Custom String("...") literals as-is (UTF-8).
5. patch95_ranch.py with `# -*- coding: utf-8 -*-` header and Korean docstring, every sub() assert-counted with the counts given below.

# Existing facts (trust these; do not re-derive)
- Zone 12 = 목장 (ranch), zone 11 = 역마차 정거장 (station). Inventory: Inv index 0 = 육포 (jerky), Inv index 1 = 물통 (water). Game day = 720 seconds. Fame/Noto capped at 100. Lawful income adds to both Money and Earned. SellQty (37) and SellSum (44) are reusable snapshot vars for sale messages.
- The red failure sound line used everywhere: Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);

# Feature spec
Build a ranch ($2,000, requires Fame >= 30 - the lawful mirror of the brewery's Noto 30). Feed it 물통 2 + 육포 1 -> one game day (720s) of rearing -> cattle ready (3 per pen). During rearing the owner must visit the ranch menu ONCE to tend the cattle (물 주기); if they never do, the batch matures thin (1 per pen instead of 3). Sell ready cattle at the STATION for $60/head ($70 if the player has the 목장주 advancement, Value In Array(Event Player.Adv, 6) == 1). Expansion: second pen $5,000 -> 6 per batch. Round-lifetime asset like the brewery - never saved to the save code (nothing to do for this; just don't touch save rules).

New player variables (append right after the line `		123: HuntDmg`, same 2-tab indent):
124 Ranch, 125 RanchPens, 126 RanchEnd, 127 RanchReady, 128 RanchCare

## Edit 1 - menu slot counts
`Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 3, 2, 1, 1)` occurs EXACTLY 3 times. Replace all 3 (cnt=3) with `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 4, 4, 1, 1)` (station index 12: 3 -> 4; ranch index 13: 2 -> 4).

## Edit 2 - menu labels (each cnt=1, in the single flat label array)
- `Custom String("배달 수주"), Custom String("승급: 역마차장 — Lv.4"), Custom String("금괴 호송 계약"), Custom String("-")` -> same but the trailing `Custom String("-")` becomes `Custom String("가축 출하 — 마리당 $60")`
- `Custom String("소 몰기 시작"), Custom String("승급: 목장주 — Lv.4"), Custom String("-"), Custom String("-")` -> same but the two trailing `Custom String("-")` become `Custom String("내 목장"), Custom String("우리 증설 $5000")`

## Edit 3 - station zone-11 chain: add MenuIdx 3 (cattle shipping)
3a. Replace anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Event Player.Escort == 1);` with (3 tabs)`Else If(Event Player.MenuIdx == 2);`(newline)(4 tabs)`If(Event Player.Escort == 1);` (cnt=1).
3b. The zone-11 chain closes with the exact sequence (4 tabs)`End;`(newline)(3 tabs)`End;`(newline)(2 tabs)`Else If(Event Player.Zone == 12);` (cnt=1). Insert between the first `End;` and the second a new depth-3 `Else;` branch:
- If(Event Player.RanchReady <= 0);
  - Small Message(Event Player, Custom String("넘길 소가 없다 — 목장에서 길러 와라")); plus the red debuff sound;
- Else;
  - Set Player Variable(Event Player, SellQty, Event Player.RanchReady);
  - Set Player Variable(Event Player, Amt, Value In Array(Event Player.Adv, 6) == 1 ? 70 : 60);
  - Set Player Variable(Event Player, SellSum, Multiply(Event Player.SellQty, Event Player.Amt));
  - Set Player Variable(Event Player, RanchReady, 0);
  - Modify Player Variable(Event Player, Money, Add, Event Player.SellSum);
  - Modify Player Variable(Event Player, Earned, Add, Event Player.SellSum);
  - Small Message(Event Player, Custom String("소 {0}마리를 넘겼다 — +$ {1}", Event Player.SellQty, Event Player.SellSum));
  - Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 120);
- End;

## Edit 4 - ranch zone-12 chain: add MenuIdx 2 (my ranch) and MenuIdx 3 (expansion)
4a. Replace anchor (3 tabs)`Else;`(newline)(4 tabs)`If(Event Player.Job != 6);` with (3 tabs)`Else If(Event Player.MenuIdx == 1);`(newline)(4 tabs)`If(Event Player.Job != 6);` (cnt=1).
4b. Anchor on the promotion tail (cnt=1): (5 tabs)`Small Message(Event Player, Custom String("몰이 보수 +15% · 소가 더 성큼 밀린다"));`(newline)(5 tabs)`Play Effect(All Players(All Teams), Ring Explosion, Color(Lime Green), Position Of(Event Player), 4);`(newline)(5 tabs)`Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 200);`(newline)(4 tabs)`End;`(newline) - append immediately AFTER this whole sequence the two new depth-3 branches:

`Else If(Event Player.MenuIdx == 2);` (내 목장 - multiplexed like the brewery's menu):
- If(Event Player.Ranch == 0);
  - If(Event Player.Fame < 30);
    - Small Message(Event Player, Custom String("목장은 신용이 필요하다 — 명성 30을 쌓아 와라 (현재 {0})", Event Player.Fame)); plus red debuff sound;
  - Else If(Event Player.Money >= 2000);
    - Modify Player Variable(Event Player, Money, Subtract, 2000);
    - Set Player Variable(Event Player, Ranch, 1);
    - Set Player Variable(Event Player, RanchPens, 1);
    - Big Message(Event Player, Custom String("내 목장을 차렸다 — 물통 2개와 육포 1개면 소를 들인다"));
    - Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 140);
  - Else;
    - Small Message(Event Player, Custom String("돈이 부족합니다 ($2000 필요)")); plus red debuff sound;
  - End;
- Else If(Event Player.RanchReady > 0);
  - Small Message(Event Player, Custom String("출하 준비 {0}마리 — 역마차 정거장에서 넘겨라", Event Player.RanchReady));
- Else If(Event Player.RanchEnd > Total Time Elapsed());
  - If(Event Player.RanchCare == 0);
    - Set Player Variable(Event Player, RanchCare, 1);
    - Small Message(Event Player, Custom String("물과 여물을 챙겨줬다 — 소가 살이 오른다"));
    - Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);
  - Else;
    - Small Message(Event Player, Custom String("소는 잘 크고 있다 — {0}초 뒤 출하", Round To Integer(Subtract(Event Player.RanchEnd, Total Time Elapsed()), Up)));
  - End;
- Else If(And(Value In Array(Event Player.Inv, 1) >= 2, Value In Array(Event Player.Inv, 0) >= 1));
  - Set Player Variable At Index(Event Player, Inv, 1, Subtract(Value In Array(Event Player.Inv, 1), 2));
  - Set Player Variable At Index(Event Player, Inv, 0, Subtract(Value In Array(Event Player.Inv, 0), 1));
  - Set Player Variable(Event Player, RanchEnd, Add(Total Time Elapsed(), 720));
  - Set Player Variable(Event Player, RanchCare, 0);
  - Big Message(Event Player, Custom String("소를 들였다 — 하루 뒤 출하. 크는 동안 한 번은 들러서 돌봐라"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);
- Else;
  - Small Message(Event Player, Custom String("물통 2개와 육포 1개가 필요하다 (물 {0} · 육포 {1})", Value In Array(Event Player.Inv, 1), Value In Array(Event Player.Inv, 0))); plus red debuff sound;
- End;

`Else If(Event Player.MenuIdx == 3);` (expansion):
- If(Event Player.Ranch == 0);
  - Small Message(Event Player, Custom String("목장부터 차려라")); plus red debuff sound;
- Else If(Event Player.RanchPens >= 2);
  - Small Message(Event Player, Custom String("이미 최대 규모다 — 한 번에 6마리")); plus red debuff sound;
- Else If(Event Player.Money >= 5000);
  - Modify Player Variable(Event Player, Money, Subtract, 5000);
  - Set Player Variable(Event Player, RanchPens, 2);
  - Big Message(Event Player, Custom String("우리를 늘렸다 — 이제 한 번에 6마리"));
  - Play Effect(Event Player, Buff Explosion Sound, Color(Lime Green), Position Of(Event Player), 140);
- Else;
  - Small Message(Event Player, Custom String("돈이 부족합니다 ($5000 필요)")); plus red debuff sound;
- End;

## Edit 5 - new rule "[목장 02] 소가 다 컸다" (maturity, mirror of "[양조 01] 밀주 숙성 완료")
Insert directly before rule("[감옥 01] 만기 출소"). event Ongoing - Each Player / All / All. Conditions: Event Player.Ranch == 1; Event Player.RanchEnd > 0; Total Time Elapsed() >= Event Player.RanchEnd.
Actions:
- Set Player Variable(Event Player, RanchEnd, 0);
- Set Player Variable(Event Player, RanchReady, Multiply(Event Player.RanchCare == 1 ? 3 : 1, Event Player.RanchPens));
- If(Event Player.RanchCare == 1);
  - Big Message(Event Player, Custom String("소가 통통하게 컸다 — {0}마리 출하 준비 완료", Event Player.RanchReady));
  - Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 80);
- Else;
  - Big Message(Event Player, Custom String("돌보지 않은 우리 — 야윈 소 {0}마리뿐이다", Event Player.RanchReady));
  - Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 80);
- End;

## Edit 6 - signboards (each cnt=1; RN = the literal backslash-r backslash-n sequence)
- Ranch signboard: after the line `몰이 성공 — 허기 3 · 갈증 2.5 · 피로 5` and its RN, append `내 목장 $2000 (명성 30) — 물통 2·육포 1이 하루 만에 소가 된다` plus RN.
- Station signboard: after the line `금괴 호송 — 수배 없는 자만 · 질주 불가 · 악명 높은 자들이 노린다` and its RN, append `가축 출하 — 목장에서 기른 소, 마리당 $60` plus RN.

# Deliverables
- patch95_ranch.py in the project dir, every sub() assert-counted.
- Apply it (via Python if the sandbox allows, otherwise exact hand-application to ROUTE66_LIFE_EN.ow only).
- Verify in ROUTE66_LIFE_EN.ow (count occurrences) and print in your final report: "내 목장을 차렸다" = 1, "소를 들였다" = 1, "물과 여물을 챙겨줬다" = 1, "소가 통통하게 컸다" = 1, "야윈 소" = 1, "소 {0}마리를 넘겼다" = 1, "우리를 늘렸다" = 1, rule("[목장 02] = 1, `128: RanchCare` = 1, `Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 4, 5, 4, 4, 1, 1)` = 3, both signboard lines = 1 each.
- Final report: what you changed, whether validation actually ran, and the occurrence counts. Do not modify anything outside this feature. Do not reformat existing code. Do not edit ROUTE66_LIFE.ow.
