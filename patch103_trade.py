# -*- coding: utf-8 -*-
"""플레이어 간 $100 송금과 채굴 정타 타이밍 보너스를 한 번 적용한다.

플레이어 변수는 추가하지 않는다. 송금 대상은 기존 Target을 재사용하며,
송금액은 Earned에 더하지 않아 일일 수입 목표에 영향을 주지 않는다.
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


def insert_into(rule_header, section, insertion):
    """Insert before a unique anchor inside one section of one unique rule.

    ``insertion`` is ``(anchor, payload)``. The section and rule boundaries are
    validated before the scoped replacement is made.
    """
    global s
    assert s.count(rule_header) == 1, "rule header: expected 1"
    section_name, label = section
    anchor, payload = insertion

    rule_start = s.index(rule_header)
    next_rule = s.find(N + 'rule("', rule_start + len(rule_header))
    rule_end = len(s) if next_rule < 0 else next_rule + len(N)
    rule_text = s[rule_start:rule_end]

    section_open = T + section_name + N + T + "{" + N
    assert rule_text.count(section_open) == 1, "%s section: expected 1" % label
    section_start = rule_text.index(section_open) + len(section_open)
    section_end = rule_text.find(N + T + "}", section_start)
    assert section_end >= 0, "%s section: closing brace not found" % label
    section_text = rule_text[section_start:section_end]
    found = section_text.count(anchor)
    assert found == 1, "%s anchor: expected 1, found %d" % (label, found)

    section_text = section_text.replace(anchor, payload + anchor, 1)
    rule_text = rule_text[:section_start] + section_text + rule_text[section_end:]
    s = s[:rule_start] + rule_text + s[rule_end:]


def mkrule(name, conditions, actions):
    """Build one Ongoing - Each Player rule in project formatting."""
    return (
        'rule("%s")' % name
        + N
        + "{"
        + N
        + T
        + "event"
        + N
        + T
        + "{"
        + N
        + block(2, "Ongoing - Each Player;", "All;", "All;")
        + T
        + "}"
        + N
        + N
        + T
        + "conditions"
        + N
        + T
        + "{"
        + N
        + "".join(T * 2 + condition + N for condition in conditions)
        + T
        + "}"
        + N
        + N
        + T
        + "actions"
        + N
        + T
        + "{"
        + N
        + actions
        + T
        + "}"
        + N
        + "}"
        + N
        + N
    )


# A1. Keep ordinary melee robbery/arrest separate from crouch + melee transfer.
MELEE_CONDITION = T * 2 + "Is Button Held(Event Player, Button(Melee)) == True;"
insert_into(
    'rule("[범죄 01] 황야에서 강도 / 체포 (F)")',
    ("conditions", "crime crouch separation"),
    (MELEE_CONDITION, block(2, "Is Button Held(Event Player, Button(Crouch)) == False;")),
)


# A2. Transfer exactly $100 to the aimed living player without modifying Earned.
TARGET_EXPR = "Set Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(Players Within Radius(Eye Position(Event Player), 9, All Teams, Surfaces), And(Current Array Element != Event Player, And(Is Dummy Bot(Current Array Element) == False, And(Player Variable(Current Array Element, TutOn) == 0, And(Has Status(Current Array Element, Asleep) == False, And(Is Alive(Current Array Element), Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Eye Position(Current Array Element))) >= 0.93)))))), Distance Between(Eye Position(Event Player), Eye Position(Current Array Element)))));"

TRADE_ACTIONS = (
    block(2, TARGET_EXPR, "If(Not(Entity Exists(Event Player.Target)));")
    + block(
        3,
        'Small Message(Event Player, Custom String("건넬 상대가 없다 — 9m 안의 상대를 조준하고 웅크린 채 [{0}]", Input Binding String(Button(Melee))));',
        "Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
    )
    + block(2, "Else If(Event Player.Money < 100);")
    + block(
        3,
        'Small Message(Event Player, Custom String("건넬 돈이 부족하다 — $100씩 건넨다"));',
        "Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
    )
    + block(2, "Else;")
    + block(
        3,
        "Modify Player Variable(Event Player, Money, Subtract, 100);",
        "Modify Player Variable(Event Player.Target, Money, Add, 100);",
        'Small Message(Event Player, Custom String("{0}에게 $100을 건넸다", Event Player.Target));',
        'Small Message(Event Player.Target, Custom String("{0}이(가) $100을 건넸다", Event Player));',
        "Play Effect(Event Player.Target, Buff Impact Sound, Color(Lime Green), Position Of(Event Player.Target), 60);",
    )
    + block(2, "End;", "Wait(0.6, Ignore Condition);")
)

TRADE_RULE = mkrule(
    "[거래 01] 돈 건네기 (웅크리기+V)",
    [
        "Is Dummy Bot(Event Player) == False;",
        "Event Player.Init == 1;",
        "Event Player.Busy == 0;",
        "Global Variable(ArchOn) == 0;",
        "Is Alive(Event Player) == True;",
        "Is Button Held(Event Player, Button(Crouch)) == True;",
        "Is Button Held(Event Player, Button(Melee)) == True;",
    ],
    TRADE_ACTIONS,
)

sub(
    'rule("[감옥 01] 만기 출소")',
    TRADE_RULE + 'rule("[감옥 01] 만기 출소")',
    1,
    "trade rule insertion",
)


# A3. Advertise both meanings of the melee key in the existing HUD hint.
sub(
    'Custom String("[{0}] 강도/체포", Input Binding String(Button(Melee)))',
    'Custom String("[{0}] 강도/체포 · 앉아서 [{0}] 송금", Input Binding String(Button(Melee)))',
    1,
    "trade HUD hint",
)


# B. Add a random tell and a 0.5 second jump reaction window after each dig.
MINE_MILESTONE = T * 2 + "If(Modulo(Event Player.MineCount, 10) == 0);"
MINE_TIMING = (
    block(
        2,
        "Wait(Random Real(0.3, 0.8), Ignore Condition);",
        "If(Is Button Held(Event Player, Button(Jump)));",
    )
    + block(3, 'Small Message(Event Player, Custom String("성급한 곡괭이질 — 정타를 놓쳤다"));')
    + block(2, "Else;")
    + block(
        3,
        'Small Message(Event Player, Custom String("광맥이 울렸다 — 지금! [{0}]", Input Binding String(Button(Jump))));',
        "Play Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 45);",
        "Wait Until(Is Button Held(Event Player, Button(Jump)), 0.5);",
        "If(Is Button Held(Event Player, Button(Jump)));",
    )
    + block(
        4,
        "Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 2));",
        'Small Message(Event Player, Custom String("정타! 원석 +2 (보유 {0})", Value In Array(Event Player.Inv, 2)));',
        "Play Effect(Event Player, Ring Explosion, Color(Orange), Position Of(Event Player), 1.2);",
    )
    + block(3, "End;")
    + block(2, "End;")
)

insert_into(
    'rule("[직업 01] DoMine")',
    ("actions", "mining timing"),
    (MINE_MILESTONE, MINE_TIMING),
)


# Final invariants, including the scoped ordering requested by the caller.
expected_counts = {
    'rule("[거래 01] 돈 건네기 (웅크리기+V)")': 1,
    "$100을 건넸다": 2,
    "정타! 원석 +2": 1,
    "광맥이 울렸다": 1,
    "성급한 곡괭이질": 1,
    "앉아서 [{0}] 송금": 1,
}
for needle, expected in expected_counts.items():
    actual = s.count(needle)
    assert actual == expected, "final count: expected %d, found %d" % (expected, actual)

crime_header = 'rule("[범죄 01] 황야에서 강도 / 체포 (F)")'
crime_start = s.index(crime_header)
crime_end = s.find(N + 'rule("', crime_start + len(crime_header))
crime_rule = s[crime_start:] if crime_end < 0 else s[crime_start:crime_end]
crime_pair = block(
    2,
    "Is Button Held(Event Player, Button(Crouch)) == False;",
    "Is Button Held(Event Player, Button(Melee)) == True;",
).rstrip(N)
crime_crouch_before_melee = crime_rule.count(crime_pair) == 1
assert crime_crouch_before_melee, "crime crouch ordering: false"

with io.open(P, "w", encoding="utf-8", newline="\n") as source_file:
    source_file.write(s)


def safe_print(message):
    """Keep success output safe for a cp949 console."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "backslashreplace").decode("ascii"))


safe_print("patch103_trade.py applied successfully")
for needle, expected in expected_counts.items():
    escaped = needle.encode("unicode_escape").decode("ascii")
    safe_print("verify[%s]=%d" % (escaped, expected))
safe_print("verify[crime_crouch_before_melee]=%s" % crime_crouch_before_melee)
