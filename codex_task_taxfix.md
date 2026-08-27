Fix four audited bugs in this Overwatch 2 Workshop project via ONE Python patch script patch112_taxfix.py. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,318 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch104_qte.py: sub() assert-counted with the counts stated below, chr(9)/chr(10) assembly, one write, UTF-8 header, Korean docstring. NO new variables.
- Validation (run if possible): python patch112_taxfix.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow && python labelcheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens; whole-function-argument ternary fine. Korean as-is.

# Fix 1 - property tax must count bank deposits (closes the deposit tax-evasion exploit)
1a. Payment exemption (the two-line anchor is unique, cnt=1): replace
(4 tabs)`Else If(Event Player.Money < 100);`(newline)(5 tabs)`Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));`
with the same two lines but the first becomes
(4 tabs)`Else If(Add(Event Player.Money, Event Player.Deposit) < 100);`
1b. Tax base (cnt=1): replace
`Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, Event Player.Fame >= 70 ? 0.025 : 0.05), Down));`
with
`Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Add(Event Player.Money, Event Player.Deposit), Event Player.Fame >= 70 ? 0.025 : 0.05), Down));`
1c. Split deduction (cnt=1): replace the line
(5 tabs)`Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);`
that appears in the SAME Else-branch (it is the only occurrence of that exact line at 5-tab depth immediately followed by (5 tabs)`Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));` - anchor on the two-line pair, cnt=1) with:
(5 tabs)`If(Event Player.Money >= Event Player.Amt);`
(6 tabs)`Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);`
(5 tabs)`Else;`
(6 tabs)`Modify Player Variable(Event Player, Deposit, Subtract, Subtract(Event Player.Amt, Event Player.Money));`
(6 tabs)`Set Player Variable(Event Player, Money, 0);`
(5 tabs)`End;`
followed by the unchanged TaxPaidRound line.
1d. Overdue exemption in rule "[세금 03] 체납 처벌" (two-line anchor, cnt=1): replace
(2 tabs)`If(Event Player.Money < 100);`(newline)(3 tabs)`Small Message(Event Player, Custom String("털어봤자 먼지뿐 — 징수원이 포기하고 지나갔다"));`
with the same but the first line becomes (2 tabs)`If(Add(Event Player.Money, Event Player.Deposit) < 100);`
1e. Overdue fine base (cnt=1): replace
`Set Player Variable(Event Player, Fine, Max(50, Round To Integer(Multiply(Event Player.Money, 0.1), Down)));`
with
`Set Player Variable(Event Player, Fine, Max(50, Round To Integer(Multiply(Add(Event Player.Money, Event Player.Deposit), 0.1), Down)));`

# Fix 2 - the 누명 random event must not target players still in the tutorial (cnt=1)
Replace
`Random Value In Array(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Init) == 1))`
with
`Random Value In Array(Filtered Array(All Players(All Teams), And(Player Variable(Current Array Element, Init) == 1, Player Variable(Current Array Element, TutOn) == 0)))`

# Fix 3 - treasure chests must not be claimable by tutorial players
In rule "[도파민 03] 보물 획득", insert after the condition line (2 tabs)`Event Player.Init == 1;` and before (2 tabs)`Global Variable(TreasureOn) == 1;` (anchor on the two-line pair, cnt=1) a new condition line:
(2 tabs)`Event Player.TutOn == 0;`

# Fix 4 - tax arrival small-print mentions deposits
Replace (cnt=1) `재산의 5% (명성 70+는 절반). 떼먹으면 재산의 10%가 현상금으로 붙는다` with `재산의 5% — 예금도 재산이다 (명성 70+는 절반). 떼먹으면 10%가 현상금으로 붙는다`

# Deliverables
patch112_taxfix.py (script alone suffices if execution is blocked). Verification counts for the caller: `Add(Event Player.Money, Event Player.Deposit) < 100` = 2, `Multiply(Add(Event Player.Money, Event Player.Deposit), Event Player.Fame >= 70` = 1, `Multiply(Add(Event Player.Money, Event Player.Deposit), 0.1)` = 1, `Modify Player Variable(Event Player, Deposit, Subtract, Subtract(Event Player.Amt, Event Player.Money));` = 1, `Player Variable(Current Array Element, TutOn) == 0)))` = 1, `예금도 재산이다` = 1, and in [도파민 03] the TutOn condition exists = report true/false. Touch nothing else.
