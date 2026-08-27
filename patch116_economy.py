# -*- coding: utf-8 -*-
"""술집 소문과 수배 아이콘을 정리하고 노동 수입을 약 20퍼센트 낮춘다.

계약·숙련 보상과 강도·체포·송금 보상은 건드리지 않으며 새 변수는 추가하지 않는다.
모든 변경은 정확한 원문 개수를 확인한 뒤 한 번만 저장한다.
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


def block(depth, *lines):
    """Assemble Workshop lines with tabs and LF using ASCII-safe delimiters."""
    return "".join(T * depth + line + N for line in lines)


# A. Leave only the event rumor output; market prices remain at the scrapyard.
RUMOR_PRICE = block(
    4,
    'Small Message(Event Player, Custom String("소문 — 원석 $ {0}, 가죽 $ {1}", Global Variable(OrePrice), Global Variable(HidePrice)));',
    "Play Effect(Event Player, Debuff Impact Sound, Color(Sky Blue), Position Of(Event Player), 25);",
    "Wait(2, Ignore Condition);",
)
sub(RUMOR_PRICE, "", 1, "bar rumor market price")


# B. Remove the periodic wanted poster icon rule, preserving later wanted rules.
WANTED_01 = 'rule("[수배 01] 전단 노출")'
WANTED_02 = 'rule("[수배 02] 전단 경고")'
assert s.count(WANTED_01) == 1, "wanted 01 header: expected 1, found %d" % s.count(WANTED_01)
assert s.count(WANTED_02) == 1, "wanted 02 header: expected 1, found %d" % s.count(WANTED_02)
wanted_start = s.index(WANTED_01)
warning_start = s.index(WANTED_02)
assert wanted_start < warning_start, "wanted rule ordering: false"
sub(s[wanted_start:warning_start], "", 1, "wanted 01 entire rule")
assert s.count("수배 01") == 0, "wanted 01 removal: expected 0, found %d" % s.count("수배 01")
assert s.count("WantedIco") == 1, "WantedIco declaration: expected 1, found %d" % s.count("WantedIco")


# C. Scale labor income down by about 20 percent.
sub(
    "Set Global Variable(OrePrice, Random Integer(3, 6));",
    "Set Global Variable(OrePrice, Random Integer(2, 5));",
    1,
    "daily ore price",
)
sub(
    "Set Global Variable(HidePrice, Random Integer(4, 7));",
    "Set Global Variable(HidePrice, Random Integer(3, 6));",
    1,
    "daily hide price",
)
sub("Set Global Variable(OrePrice, 3);", "Set Global Variable(OrePrice, 2);", 1, "initial ore price")
sub("Set Global Variable(HidePrice, 6);", "Set Global Variable(HidePrice, 5);", 1, "initial hide price")
sub("Random Integer(50, 130)", "Random Integer(40, 105)", 1, "gold vein payout")
sub(
    "Multiply(Min(Event Player.Streak, 25), 4)",
    "Multiply(Min(Event Player.Streak, 25), 3)",
    1,
    "mining streak payout",
)
sub(
    "Modify Player Variable(Event Player, Money, Add, 25);",
    "Modify Player Variable(Event Player, Money, Add, 20);",
    1,
    "ten-mine bonus",
)

for old_amount, new_amount in ((250, 200), (50, 40), (60, 48)):
    sub(
        "Modify Player Variable(Attacker, Money, Add, %d);" % old_amount,
        "Modify Player Variable(Attacker, Money, Add, %d);" % new_amount,
        1,
        "hunting money %d" % old_amount,
    )
    sub(
        "Modify Player Variable(Attacker, Earned, Add, %d);" % old_amount,
        "Modify Player Variable(Attacker, Earned, Add, %d);" % new_amount,
        1,
        "hunting earned %d" % old_amount,
    )

sub(
    "Add(15, Multiply(Distance Between",
    "Add(12, Multiply(Distance Between",
    2,
    "delivery base payout",
)
sub(
    "Value In Array(Global Variable(LocPos), Event Player.DelDest)), 1.3)",
    "Value In Array(Global Variable(LocPos), Event Player.DelDest)), 1.05)",
    2,
    "delivery distance multiplier",
)
sub("Add(165, Multiply(3,", "Add(132, Multiply(2.4,", 1, "cattle drive payout")
sub("Random Integer(65, 125)", "Random Integer(52, 100)", 1, "raid main payout")
sub("Random Integer(8, 15)", "Random Integer(6, 12)", 1, "raid fallback payout")

sub(
    "Add(40, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2.5)),",
    "Add(32, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Event Player.EscortPos), 2)),",
    1,
    "gold escort payout",
)
sub(
    "Add(30, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 8), Event Player.SmugglePos), 2.5)),",
    "Add(24, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 8), Event Player.SmugglePos), 2)),",
    1,
    "smuggling payout",
)
sub("? 70 : 60", "? 56 : 48", 1, "ranch shipment payout")
sub(
    "Multiply(Event Player.BrewReady, 60)",
    "Multiply(Event Player.BrewReady, 48)",
    1,
    "moonshine backdoor payout",
)

sub(
    "Modify Player Variable(Event Player, Money, Add, 12);",
    "Modify Player Variable(Event Player, Money, Add, 10);",
    1,
    "minigame money 12",
)
sub(
    "Modify Player Variable(Event Player, Earned, Add, 12);",
    "Modify Player Variable(Event Player, Earned, Add, 10);",
    1,
    "minigame earned 12",
)
sub(
    "Modify Player Variable(Event Player, Money, Add, 15);",
    "Modify Player Variable(Event Player, Money, Add, 12);",
    1,
    "minigame money 15",
)
sub(
    "Modify Player Variable(Event Player, Earned, Add, 15);",
    "Modify Player Variable(Event Player, Earned, Add, 12);",
    1,
    "minigame earned 15",
)

sub("Set Global Variable(DailyGoal, 480);", "Set Global Variable(DailyGoal, 384);", 1, "initial daily goal")
sub(
    "Set Global Variable(DailyGoal, Add(400, Multiply(Global Variable(Day), 80)));",
    "Set Global Variable(DailyGoal, Add(320, Multiply(Global Variable(Day), 64)));",
    1,
    "scaled daily goal",
)
sub("가축 출하 — 마리당 $60", "가축 출하 — 마리당 $48", 1, "ranch shipment label")
sub("가축 출하 — 목장에서 기른 소, 마리당 $60", "가축 출하 — 목장에서 기른 소, 마리당 $48", 1, "ranch shipment signboard")

bottle_price_count = s.count("병당 $60")
if bottle_price_count:
    sub("병당 $60", "병당 $48", bottle_price_count, "moonshine bottle signs")


# Final invariants requested by the caller.
expected_counts = {
    "소문 — 원석": 0,
    'rule("[수배 01]': 0,
    "WantedIco": 1,
    "Random Integer(2, 5)": 1,
    "Random Integer(40, 105)": 1,
    "Add(132, Multiply(2.4,": 1,
    "? 56 : 48": 1,
    "Multiply(Event Player.BrewReady, 48)": 1,
    "DailyGoal, 384": 1,
    "Add(320, Multiply(Global Variable(Day), 64))": 1,
    "가축 출하 — 마리당 $48": 1,
}
for needle, expected in expected_counts.items():
    actual = s.count(needle)
    assert actual == expected, "final count: expected %d, found %d" % (expected, actual)

with io.open(P, "w", encoding="utf-8", newline="\n") as source_file:
    source_file.write(s)


def safe_print(message):
    """Keep success output safe for a cp949 console."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "backslashreplace").decode("ascii"))


safe_print("patch116_economy.py applied successfully")
for needle, expected in expected_counts.items():
    escaped = needle.encode("unicode_escape").decode("ascii")
    safe_print("verify[%s]=%d" % (escaped, expected))
