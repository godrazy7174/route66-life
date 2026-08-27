# -*- coding: utf-8 -*-
"""설계자 모드를 제거하고 야수 배회 움직임을 소폭 완화한다."""

from pathlib import Path


path = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")
with path.open("r", encoding="utf-8", newline="") as f:
    text = f.read()


def sub(old, new, cnt):
    global text
    assert text.count(old) == cnt, "unexpected replacement count"
    text = text.replace(old, new)


sub(
    "Set Jump Vertical Speed(Event Player, Random Integer(120, 380));",
    "Set Jump Vertical Speed(Event Player, Random Integer(120, 320));",
    2,
)
sub(
    "If(Random Integer(1, 100) <= 60);",
    "If(Random Integer(1, 100) <= 50);",
    1,
)

blink_first = "\t\t\tIf(Random Integer(1, 100) <= 10);"
blink_second = (
    "\t\t\t\tTeleport(Event Player, Nearest Walkable Position(Add(Position Of(Event Player), "
    "Vector(Random Real(-5, 5)"
)
blink_lf = blink_first + "\n" + blink_second
blink_crlf = blink_first + "\r\n" + blink_second
assert text.count(blink_lf) + text.count(blink_crlf) == 1, "unexpected blink anchor count"
blink_old = blink_crlf if text.count(blink_crlf) == 1 else blink_lf
blink_new = blink_old.replace("<= 10", "<= 8", 1)
sub(blink_old, blink_new, 1)

architect_01 = 'rule("[설계자 01] 모드 토글 (호스트: Ctrl 2초)")'
architect_02 = 'rule("[설계자 02] 다음 장소 (R)")'
architect_03 = 'rule("[설계자 03] 이 자리로 지정 (F)")'
assert text.count(architect_01) == 1, "unexpected architect 01 count"
assert text.count(architect_02) == 1, "unexpected architect 02 count"
assert text.count(architect_03) == 1, "unexpected architect 03 count"

index_01 = text.index(architect_01)
index_02 = text.index(architect_02)
index_03 = text.index(architect_03)
rule_indexes = []
search_from = 0
while True:
    rule_index = text.find('rule("', search_from)
    if rule_index == -1:
        break
    rule_indexes.append(rule_index)
    search_from = rule_index + 1

assert index_01 < index_02 < index_03, "unexpected architect rule order"
assert all(
    rule_index < index_01
    for rule_index in rule_indexes
    if rule_index not in (index_01, index_02, index_03)
), "architect rules are not last"
assert rule_indexes[-3:] == [index_01, index_02, index_03], "unexpected trailing rules"

line_start = text.rfind("\n", 0, index_01) + 1
assert text[line_start:index_01].strip() == "", "architect 01 is not at line start"
newline = "\r\n" if "\r\n" in text else "\n"
text = text[:line_start].rstrip() + newline

assert text.endswith("}" + newline), "unexpected final rule ending"
assert not text.endswith(newline + newline), "more than one trailing newline"
assert text.count("설계자") == 0, "architect text remains"
assert text.count("ArchHud") == 1, "ArchHud refs beyond declaration"  # decl line stays by design
assert text.count("Random Integer(120, 320)") == 2, "unexpected softened hop count"
assert text.count("Random Integer(120, 380)") == 0, "old hop remains"
assert text.count("Random Integer(1, 100) <= 50);") == 1, "unexpected jump chance count"
assert text.count(blink_new) == 1, "blink chance was not updated"

with path.open("w", encoding="utf-8", newline="") as f:
    f.write(text)

print("patch114_architect.py: OK")
