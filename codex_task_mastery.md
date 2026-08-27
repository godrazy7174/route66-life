Implement 마스터리 마일스톤 + 오늘의 계약 in this Overwatch 2 Workshop project by writing ONE Python patch script, patch101_mastery.py. Work non-interactively: never ask questions, decide within this spec, print a final summary report. If the sandbox blocks Python, just WRITE the patch script and say so - the caller will run it (that happened last time; the script alone is a complete deliverable). NEVER print the verification counts with non-ASCII text via print() - the caller's console is cp949; guard your final prints with try/except or ASCII-only labels.

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~4,889 lines). Do NOT edit ROUTE66_LIFE.ow.
- STUDY patch100_rebirth.py / patch89_bankheist.py: reuse sub(), block(), and patch89's insert_into(rule_header, section, insertion) helper (rule-scoped insertion - you will need it for two RunPay sites that are ambiguous globally).
- Player variables are FULL. NO new player variable. This patch reuses the real-player side of `Giant` (49): beasts (Team 2 dummies) use Giant for size tier, but REAL players never touch it - so for real players we pack `Giant = MasteryPaid*10 + ContractProg` (paid ≤ ~21, prog 0..9, 9 = done sentinel). Document this in the docstring.
- One new GLOBAL is allowed: append `		57: ContractKind` right after the line `		56: HuntIdx` (cnt=1 anchor).
- Validation (run if possible): python patch101_mastery.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens; whole-argument ternary fine. Custom String max 3 args. Message values display-stable. Korean as-is.

# Part A - 오늘의 계약 (daily server-wide contract)
Kinds: 1 = 채굴 8회, 2 = 야수 4마리, 3 = 배달 3건, 4 = 소몰이 2회. Reward on completion: $150 + Earned +150 + Fame +3.

A1. Draw at sunrise - insert immediately AFTER the line (cnt=1)
`			Big Message(All Players(All Teams), Custom String("새 아침 — 오늘은 {0}의 날! 해당 직업 보수 1.5배", Value In Array(Array(Custom String("뜨내기"), Custom String("광부"), Custom String("사냥꾼"), Custom String("현상금 사냥꾼"), Custom String("무법자"), Custom String("파발꾼"), Custom String("목동")), Global Variable(TodayJob))));`
these lines (same 3-tab indent):
- Set Global Variable(ContractKind, Random Integer(1, 4));
- Big Message(All Players(All Teams), Custom String("오늘의 계약 — {0} (달성 시 $150 · 명성 +3)", Value In Array(Array(Custom String("채굴 8회"), Custom String("야수 4마리"), Custom String("배달 3건"), Custom String("소몰이 2회")), Subtract(Global Variable(ContractKind), 1))));

A2. Per-player daily progress reset - in rule "[월드 05] 아침 정산", insert immediately BEFORE the line `		If(And(Event Player.Rebirth >= 1, Event Player.Earned > Event Player.DayStart));` (cnt=1):
- Set Player Variable(Event Player, Giant, Multiply(Round To Integer(Divide(Event Player.Giant, 10), Down), 10));

A3. Four progress hooks. Each hook is this block, parameterized by SUBJECT X (Event Player or Attacker), kind K, and target T:
If(And(Global Variable(ContractKind) == K, Modulo(Player Variable(X, Giant), 10) < T));
	Modify Player Variable(X, Giant, Add, 1);
	If(Modulo(Player Variable(X, Giant), 10) == T);
		Modify Player Variable(X, Giant, Add, Subtract(9, T));
		Modify Player Variable(X, Money, Add, 150);
		Modify Player Variable(X, Earned, Add, 150);
		Set Player Variable(X, Fame, Min(100, Add(Player Variable(X, Fame), 3)));
		Big Message(X, Custom String("오늘의 계약 달성! +$150 · 명성 +3"));
		Play Effect(X, Buff Explosion Sound, Color(Yellow), Position Of(X), 120);
	Else;
		Small Message(X, Custom String("오늘의 계약 — 진행 {0} / {1}", Modulo(Player Variable(X, Giant), 10), T));
	End;
End;
Hook sites (match each site's local indent depth):
- 채굴 (K=1, T=8, X=Event Player): insert immediately after the line `		Set Player Variable(Event Player, LastMine, Total Time Elapsed());` (cnt=1, in DoMine).
- 야수 (K=2, T=4, X=Attacker): insert immediately after the line `		Set Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 1)));` (cnt=1, in the beast-kill rule).
- 배달 (K=3, T=3, X=Event Player): inside rule "[파발 01] 배달 도착 — 자동 정산", insert immediately after its line `		Modify Player Variable(Event Player, Earned, Add, Event Player.RunPay);` (use insert-like rule-scoped replacement: locate the rule header `rule("[파발 01] 배달 도착 — 자동 정산")` (unique), then the FIRST occurrence of that Earned/RunPay line after it - the same line text also exists in the 목동 rule, so global cnt is 2 and you must scope by rule).
- 소몰이 (K=4, T=2, X=Event Player): insert immediately after the line (cnt=1) `			Big Message(Event Player, Custom String("우리에 몰아넣었다!   +$ {0}   (잡화점 육포 재고 +6)", Event Player.RunPay));`

# Part B - 마스터리 마일스톤
Each job (indices 1..6) has milestones at JobXP 2,500 / 5,000 / 10,000. Reaching one pays $1,000 (+Earned) once, announced server-wide. Paid count lives in the tens+ digits of Giant.

B1. New rule inserted directly before rule("[감옥 01] 만기 출소") (cnt=1 anchor):
rule("[마스터리 01] 한 길의 장인")
event Ongoing - Each Player / All / All.
Conditions:
- Is Dummy Bot(Event Player) == False;
- Event Player.Init == 1;
- one condition line comparing the milestone total to the paid counter:
`Add(Add(Add(Add(Add(Add(Add(Add(Value In Array(Event Player.JobXP, 1) >= 2500, Value In Array(Event Player.JobXP, 1) >= 5000), Add(Value In Array(Event Player.JobXP, 1) >= 10000, Value In Array(Event Player.JobXP, 2) >= 2500)), Add(Value In Array(Event Player.JobXP, 2) >= 5000, Value In Array(Event Player.JobXP, 2) >= 10000)), Add(Value In Array(Event Player.JobXP, 3) >= 2500, Value In Array(Event Player.JobXP, 3) >= 5000)), Add(Value In Array(Event Player.JobXP, 3) >= 10000, Value In Array(Event Player.JobXP, 4) >= 2500)), Add(Value In Array(Event Player.JobXP, 4) >= 5000, Value In Array(Event Player.JobXP, 4) >= 10000)), Add(Add(Value In Array(Event Player.JobXP, 5) >= 2500, Value In Array(Event Player.JobXP, 5) >= 5000), Add(Value In Array(Event Player.JobXP, 5) >= 10000, Value In Array(Event Player.JobXP, 6) >= 2500))), Add(Value In Array(Event Player.JobXP, 6) >= 5000, Value In Array(Event Player.JobXP, 6) >= 10000)) > Round To Integer(Divide(Event Player.Giant, 10), Down);`
Actions:
- Modify Player Variable(Event Player, Giant, Add, 10);
- Modify Player Variable(Event Player, Money, Add, 1000);
- Modify Player Variable(Event Player, Earned, Add, 1000);
- Big Message(All Players(All Teams), Custom String("{0} — 한 길의 장인이 되었다! (마스터리 {1}) +$1,000", Event Player, Round To Integer(Divide(Event Player.Giant, 10), Down)));
- Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 4);
- Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 200);
- Wait(1, Ignore Condition);

B2. Head-tag star - replace (cnt=2) `Custom String("명성 {0} · 악명 {1}", Event Player.Fame, Event Player.Noto)` with `Custom String("명성 {0} · 악명 {1}{2}", Event Player.Fame, Event Player.Noto, Event Player.Giant >= 10 ? Custom String(" · ★{0}", Round To Integer(Divide(Event Player.Giant, 10), Down)) : Custom String(""))`.

B3. Save code spare digit (record only, max 9) - replace (cnt=1)
`Set Player Variable(Event Player, SaveC, Add(Multiply(Event Player.Rebuild, 100000), Multiply(Event Player.Rebirth, 10000)));`
with
`Set Player Variable(Event Player, SaveC, Add(Add(Multiply(Event Player.Rebuild, 100000), Multiply(Event Player.Rebirth, 10000)), Multiply(Min(9, Round To Integer(Divide(Event Player.Giant, 10), Down)), 1000)));`
(The existing checksum line right after already covers all leading digits - do not touch it.)

B4. Restore - insert immediately after the line (cnt=1)
`		Set Player Variable(Event Player, Rebirth, Modulo(Round To Integer(Divide(Event Player.EnterC, 10000), Down), 10));`
this line (same indent):
`		Set Player Variable(Event Player, Giant, Multiply(Modulo(Round To Integer(Divide(Event Player.EnterC, 1000), Down), 10), 10));`

# Deliverables
patch101_mastery.py (script alone suffices if the sandbox blocks execution). Verification counts for the caller to check: `57: ContractKind` = 1, `오늘의 계약 — {0}` = 1, `오늘의 계약 달성!` = 4, `오늘의 계약 — 진행` = 4, `rule("[마스터리 01] 한 길의 장인")` = 1, `한 길의 장인이 되었다` = 1, ` · ★{0}` = 2, `Multiply(Min(9, Round To Integer(Divide(Event Player.Giant, 10), Down)), 1000)` = 1, `Divide(Event Player.EnterC, 1000), Down), 10), 10)` = 1. Report what you did and whether validation ran. Touch nothing else.
