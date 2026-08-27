# -*- coding: utf-8 -*-
"""예금을 재산세에 포함하고 튜토리얼 중 이벤트 악용을 차단한다.

기존 플레이어·전역 변수만 사용한다. 모든 수정은 고유 앵커의 개수를 검증한 뒤
한 번에 적용하며, 결과 파일은 UTF-8과 LF 줄바꿈으로 한 번만 기록한다.
"""

import io


T = chr(9)
N = chr(10)
P = "ROUTE66_LIFE_EN.ow"

with io.open(P, "r", encoding="utf-8") as source_file:
    s = source_file.read()


def sub(old, new, cnt=1, label="replacement"):
    """Assert an exact source count, then replace only that many matches."""
    global s
    found = s.count(old)
    assert found == cnt, "%s: expected %d, found %d" % (label, cnt, found)
    s = s.replace(old, new, cnt)


def line(depth, text):
    """Assemble one Workshop line with tabs and LF."""
    return T * depth + text + N


# 1a. Count cash plus deposits when deciding whether payment is exempt.
sub(
    line(4, "Else If(Event Player.Money < 100);")
    + line(5, "Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));"),
    line(4, "Else If(Add(Event Player.Money, Event Player.Deposit) < 100);")
    + line(5, "Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));"),
    1,
    "payment exemption",
)


# 1b. Calculate property tax from cash plus deposits.
sub(
    "Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, Event Player.Fame >= 70 ? 0.025 : 0.05), Down));",
    "Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Add(Event Player.Money, Event Player.Deposit), Event Player.Fame >= 70 ? 0.025 : 0.05), Down));",
    1,
    "property tax base",
)


# 1c. Deduct cash first, then take any remainder from the deposit.
sub(
    line(5, "Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);")
    + line(5, "Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));"),
    line(5, "If(Event Player.Money >= Event Player.Amt);")
    + line(6, "Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);")
    + line(5, "Else;")
    + line(6, "Modify Player Variable(Event Player, Deposit, Subtract, Subtract(Event Player.Amt, Event Player.Money));")
    + line(6, "Set Player Variable(Event Player, Money, 0);")
    + line(5, "End;")
    + line(5, "Set Player Variable(Event Player, TaxPaidRound, Global Variable(TaxRound));"),
    1,
    "split tax deduction",
)


# 1d. Count deposits in the overdue exemption as well.
sub(
    line(2, "If(Event Player.Money < 100);")
    + line(3, 'Small Message(Event Player, Custom String("털어봤자 먼지뿐 — 징수원이 포기하고 지나갔다"));'),
    line(2, "If(Add(Event Player.Money, Event Player.Deposit) < 100);")
    + line(3, 'Small Message(Event Player, Custom String("털어봤자 먼지뿐 — 징수원이 포기하고 지나갔다"));'),
    1,
    "overdue exemption",
)


# 1e. Calculate the overdue fine from cash plus deposits.
sub(
    "Set Player Variable(Event Player, Fine, Max(50, Round To Integer(Multiply(Event Player.Money, 0.1), Down)));",
    "Set Player Variable(Event Player, Fine, Max(50, Round To Integer(Multiply(Add(Event Player.Money, Event Player.Deposit), 0.1), Down)));",
    1,
    "overdue fine base",
)


# 2. Exclude tutorial players from the false-accusation target pool.
sub(
    "Random Value In Array(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Init) == 1))",
    "Random Value In Array(Filtered Array(All Players(All Teams), And(Player Variable(Current Array Element, Init) == 1, Player Variable(Current Array Element, TutOn) == 0)))",
    1,
    "false accusation tutorial exclusion",
)


# 3. Exclude tutorial players from treasure claims.
sub(
    line(2, "Event Player.Init == 1;")
    + line(2, "Global Variable(TreasureOn) == 1;"),
    line(2, "Event Player.Init == 1;")
    + line(2, "Event Player.TutOn == 0;")
    + line(2, "Global Variable(TreasureOn) == 1;"),
    1,
    "treasure tutorial exclusion",
)


# 4. State explicitly that deposits are taxable property.
sub(
    "재산의 5% (명성 70+는 절반). 떼먹으면 재산의 10%가 현상금으로 붙는다",
    "재산의 5% — 예금도 재산이다 (명성 70+는 절반). 떼먹으면 10%가 현상금으로 붙는다",
    1,
    "tax arrival small print",
)


# Final invariants requested by the caller.
expected_counts = {
    "Add(Event Player.Money, Event Player.Deposit) < 100": 2,
    "Multiply(Add(Event Player.Money, Event Player.Deposit), Event Player.Fame >= 70": 1,
    "Multiply(Add(Event Player.Money, Event Player.Deposit), 0.1)": 1,
    "Modify Player Variable(Event Player, Deposit, Subtract, Subtract(Event Player.Amt, Event Player.Money));": 1,
    "Player Variable(Current Array Element, TutOn) == 0)))": 1,
    "예금도 재산이다": 1,
}
for needle, expected in expected_counts.items():
    actual = s.count(needle)
    assert actual == expected, "final count: expected %d, found %d" % (expected, actual)

treasure_start = s.index('rule("[도파민 03] 보물 획득")')
treasure_end = s.index(N + 'rule("', treasure_start + 1)
treasure_rule = s[treasure_start:treasure_end]
treasure_tuton_ok = line(2, "Event Player.TutOn == 0;") in treasure_rule
assert treasure_tuton_ok, "treasure tutorial condition: false"

with io.open(P, "w", encoding="utf-8", newline="\n") as source_file:
    source_file.write(s)


def safe_print(message):
    """Keep all status output safe for a cp949 console."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "backslashreplace").decode("ascii"))


safe_print("patch112_taxfix.py applied successfully")
for needle, expected in expected_counts.items():
    escaped = needle.encode("unicode_escape").decode("ascii")
    safe_print("verify[%s]=%d" % (escaped, expected))
safe_print("verify[treasure_tuton_condition]=%s" % treasure_tuton_ok)
