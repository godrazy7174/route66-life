Implement two things in this Overwatch 2 Workshop script project by writing ONE Python patch script: (A) tutorial expansion 16 -> 18 pages plus one line added to an existing page, (B) infinite ammo for all player heroes. Work non-interactively: never ask questions, decide within this spec, and print a final summary report at the end.

# Project context
- ROUTE66_LIFE_EN.ow is the English source of truth (~4,724 lines). ROUTE66_LIFE.ow is the Korean build generated from it.
- All changes are made via atomic Python patch scripts. STUDY patch95_ranch.py / patch93_escort.py for the sub()/block() helpers, chr(9)/chr(10) assembly, and assert-counted substitutions. Write patch97_tutorial.py with `# -*- coding: utf-8 -*-` header and a Korean docstring.
- IMPORTANT: player variables are FULL (128/128). Do NOT declare any new variable, player or global. This patch needs none.
- Your sandbox may block running Python (`CreateProcessAsUserW failed: 5`). If Python runs, run the validation pipeline below. If it does not, apply the patch to ROUTE66_LIFE_EN.ow by hand-editing it to EXACTLY what the patch script would produce, verify by careful re-reading, and say clearly in your report that validation must be re-run by the caller. Do NOT edit ROUTE66_LIFE.ow.
- Validation pipeline: python patch97_tutorial.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow
  A pre-existing "possibly undeclared player vars" warning listing bare numbers is noise. If lint/enumcheck flags the element names `Ammo`, `Max Ammo`, or `Set Ammo` as unknown, that is EXPECTED (they are new to this file): report it and do NOT edit lint.py or any validator - the caller handles the dictionaries.

# Doctrine
1. No ternary inside a comparison RHS, no bare grouping parens; whole-function-argument ternary is fine.
2. Korean text goes inside Custom String("...") as-is (UTF-8). Inside tutorial body strings, newlines are the literal two-character sequences backslash-r and backslash-n - build them in Python as chr(92)+'r'+chr(92)+'n' (call it RN). The tutorial page bodies live inside ONE giant Create HUD Text line; all substitutions below are plain string replacements inside it.

# Part A - tutorial expansion (16 -> 18 pages)
The tutorial is one Create HUD Text call containing a title array (16 Custom Strings), a body array (16 Custom Strings), a page counter "({1}/16)", two `Min(15, Event Player.TutStep)` index clamps, plus a For loop and a camera-position array in the same rule. Two new pages are inserted between page 13 (사건) and page 14 (긴 여정): new page 14 「사흘의 리듬」 and new page 15 「두 갈래 큰 길」; 긴 여정 and 시작 shift to 16 and 17.

A1. Title array (cnt=1): replace
`Custom String("사건"), Custom String("긴 여정")`
with
`Custom String("사건"), Custom String("사흘의 리듬"), Custom String("두 갈래 큰 길"), Custom String("긴 여정")`

A2. Body array (cnt=1): replace
`소문은 여기서 듣는다."), Custom String("돈이 쌓이면`
with
`소문은 여기서 듣는다."), Custom String("` + BODY14 + `"), Custom String("` + BODY15 + `"), Custom String("돈이 쌓이면`
where (RN = the literal backslash-r backslash-n sequence):
BODY14 = `밤마다 금고 마차가 어둠 속 어딘가에 멈춘다 — 먼저 터는 자가 임자, 대신 악명이 붙는다.` RN `사흘에 한 번 저녁이면 열차가 선다 — 대장간의 화약 $200이 금고를 연다.` RN `그다음 날 아침엔 대야수의 흔적이 나타난다 — 함께 쫓고, 기여한 만큼 나눈다.`
BODY15 = `명성 30이면 목장에서 소를 치고, 악명 30이면 뒷골목에서 밀주를 담근다.` RN `은신처의 밀수, 정거장의 금괴 호송 — 나르는 동안 질주할 수 없고, 죽거나 털리면 끝이다.` RN `마을이 되살아나면(재건 3단계) 밤의 은행이 간 큰 자를 기다린다.`

A3. Outlaw page (page 6) extra line (cnt=1): replace
`목값 $300이면 전단이 돌고, $800이면 마을이 문을 걸어 잠근다.")`
with
`목값 $300이면 전단이 돌고, $800이면 마을이 문을 걸어 잠근다.` RN `습격의 장물은 자루에 담긴다 — 은신처에서 정산하고, 진 채로 죽으면 흘린다.")`

A4. Index clamps (cnt=2): replace `Min(15, Event Player.TutStep)` with `Min(17, Event Player.TutStep)` (both occurrences).

A5. Page counter (cnt=1): replace `({1}/16)` with `({1}/18)`.

A6. Step loop (cnt=1): replace `For Player Variable(Event Player, TutStep, 0, 16, 1);` with `For Player Variable(Event Player, TutStep, 0, 18, 1);`

A7. Camera-position array (cnt=2, it appears twice inside the Start Camera line): replace
`Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 9, 9)`
with
`Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 11, 12, 9, 9)`
(new page 14 looks at location 11 역마차 정거장, new page 15 at location 12 목장; the final two 9s for 긴 여정/시작 stay.)

Do NOT touch the completion-reward block or anything else in the tutorial rules.

# Part B - infinite ammo
Insert ONE new rule directly before rule("[코어 07] 궁극기 게이지 상시 제거") (cnt=1 anchor):

rule("[코어 18] 무한 탄창")
event Ongoing - Each Player / All / All.
Conditions:
- Is Dummy Bot(Event Player) == False;
- Event Player.Init == 1;
- Is Alive(Event Player) == True;
- Ammo(Event Player, 0) < Max Ammo(Event Player, 0);
Actions:
- Set Ammo(Event Player, 0, Max Ammo(Event Player, 0));
- Wait(0.25, Ignore Condition);
- Loop If(Ammo(Event Player, 0) < Max Ammo(Event Player, 0));

(Clip index 0 covers Cassidy, Ashe, Tracer, and Shion. Beast dummies never fire, and the Is Dummy Bot condition excludes them anyway.)

# Deliverables
- patch97_tutorial.py in the project dir, every sub() assert-counted with the counts stated above.
- Apply it (via Python if the sandbox allows, otherwise exact hand-application to ROUTE66_LIFE_EN.ow only).
- Verify in ROUTE66_LIFE_EN.ow (count occurrences) and print in your final report: "사흘의 리듬" = 1, "두 갈래 큰 길" = 1, "기여한 만큼 나눈다" = 1, "간 큰 자를 기다린다" = 2 (one pre-existing on the hideout signboard + the new tutorial body), "진 채로 죽으면 흘린다" = 1, "({1}/18)" = 1, "Min(17, Event Player.TutStep)" = 2, "TutStep, 0, 18, 1" = 1, `Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 11, 12, 9, 9)` = 2, rule("[코어 18] 무한 탄창") = 1, "Set Ammo(Event Player, 0, Max Ammo(Event Player, 0));" = 1.
- Final report: what you changed, whether validation actually ran, and the occurrence counts. Do not modify anything outside this feature. Do not reformat existing code. Do not edit ROUTE66_LIFE.ow.
