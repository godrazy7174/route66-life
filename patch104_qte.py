# -*- coding: utf-8 -*-
"""채굴 정타 빈도를 조정하고 배달·소몰이 반응 이벤트를 한 번 적용한다.

플레이어 변수는 추가하지 않는다. 새 이벤트는 Wait와 반복 상태만 사용하며,
Reload 선입력을 실패로 처리해 연타 성공을 막는다.
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


# A. Make the mining timing event occur on 30 percent of digs.
MINE_OLD = block(
    2,
    "Wait(Random Real(0.3, 0.8), Ignore Condition);",
    "If(Is Button Held(Event Player, Button(Jump)));",
)
MINE_NEW = block(
    2,
    "Wait(Random Real(0.3, 0.8), Ignore Condition);",
    "If(Random Integer(1, 100) > 30);",
    "Else If(Is Button Held(Event Player, Button(Jump)));",
)
sub(MINE_OLD, MINE_NEW, 1, "mining timing probability")


# B. Reward a deliberate Reload response while carrying a parcel.
PARCEL_ACTIONS = (
    block(
        2,
        "Wait(Random Real(7, 14), Ignore Condition);",
        "If(And(Event Player.HasParcel == 1, Is Alive(Event Player)));",
    )
    + block(3, "If(Is Button Held(Event Player, Button(Reload)));")
    + block(4, 'Small Message(Event Player, Custom String("손이 앞섰다 — 끈을 놓쳤다"));')
    + block(3, "Else;")
    + block(
        4,
        'Small Message(Event Player, Custom String("화물 끈이 풀린다 — 지금! [{0}]", Input Binding String(Button(Reload))));',
        "Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 45);",
        "Wait Until(Is Button Held(Event Player, Button(Reload)), 0.7);",
        "If(Is Button Held(Event Player, Button(Reload)));",
    )
    + block(
        5,
        "Modify Player Variable(Event Player, Money, Add, 12);",
        "Modify Player Variable(Event Player, Earned, Add, 12);",
        'Small Message(Event Player, Custom String("끈을 다시 묶었다 +$12"));',
        "Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1);",
    )
    + block(4, "End;")
    + block(3, "End;")
    + block(2, "End;", "Wait(2, Ignore Condition);", "Loop If(Event Player.HasParcel == 1);")
)

PARCEL_RULE = mkrule(
    "[파발 02] 흔들리는 화물",
    [
        "Is Dummy Bot(Event Player) == False;",
        "Event Player.Init == 1;",
        "Event Player.HasParcel == 1;",
        "Is Alive(Event Player) == True;",
    ],
    PARCEL_ACTIONS,
)


# C. Reward the same deliberate Reload response while driving cattle.
CATTLE_ACTIONS = (
    block(
        2,
        "Wait(Random Real(6, 12), Ignore Condition);",
        "If(And(Event Player.CowOn == 1, Is Alive(Event Player)));",
    )
    + block(3, "If(Is Button Held(Event Player, Button(Reload)));")
    + block(4, 'Small Message(Event Player, Custom String("손이 앞섰다 — 고삐를 놓쳤다"));')
    + block(3, "Else;")
    + block(
        4,
        'Small Message(Event Player, Custom String("소가 날뛴다 — 지금! [{0}]", Input Binding String(Button(Reload))));',
        "Play Effect(Event Player, Buff Impact Sound, Color(White), Position Of(Event Player), 45);",
        "Wait Until(Is Button Held(Event Player, Button(Reload)), 0.7);",
        "If(Is Button Held(Event Player, Button(Reload)));",
    )
    + block(
        5,
        "Modify Player Variable(Event Player, Money, Add, 12);",
        "Modify Player Variable(Event Player, Earned, Add, 12);",
        'Small Message(Event Player, Custom String("고삐를 잡아챘다 +$12"));',
        "Play Effect(Event Player, Ring Explosion, Color(White), Position Of(Event Player), 1);",
    )
    + block(4, "End;")
    + block(3, "End;")
    + block(2, "End;", "Wait(2, Ignore Condition);", "Loop If(Event Player.CowOn == 1);")
)

CATTLE_RULE = mkrule(
    "[목동 02] 날뛰는 소",
    [
        "Is Dummy Bot(Event Player) == False;",
        "Event Player.Init == 1;",
        "Event Player.CowOn == 1;",
        "Is Alive(Event Player) == True;",
    ],
    CATTLE_ACTIONS,
)

JAIL_RULE = 'rule("[감옥 01] 만기 출소")'
sub(JAIL_RULE, PARCEL_RULE + CATTLE_RULE + JAIL_RULE, 1, "QTE rule insertion")


# Final invariants requested by the caller.
expected_counts = {
    "If(Random Integer(1, 100) > 30);": 1,
    'rule("[파발 02] 흔들리는 화물")': 1,
    'rule("[목동 02] 날뛰는 소")': 1,
    "화물 끈이 풀린다": 1,
    "소가 날뛴다": 1,
    "끈을 다시 묶었다": 1,
    "고삐를 잡아챘다": 1,
    "손이 앞섰다": 2,
}
for needle, expected in expected_counts.items():
    actual = s.count(needle)
    assert actual == expected, "final count: expected %d, found %d" % (expected, actual)

parcel_start = s.index('rule("[파발 02] 흔들리는 화물")')
cattle_start = s.index('rule("[목동 02] 날뛰는 소")')
jail_start = s.index(JAIL_RULE)
rule_order_ok = parcel_start < cattle_start < jail_start
assert rule_order_ok, "QTE rule ordering: false"

with io.open(P, "w", encoding="utf-8", newline="\n") as source_file:
    source_file.write(s)


def safe_print(message):
    """Keep success output safe for a cp949 console."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "backslashreplace").decode("ascii"))


safe_print("patch104_qte.py applied successfully")
for needle, expected in expected_counts.items():
    escaped = needle.encode("unicode_escape").decode("ascii")
    safe_print("verify[%s]=%d" % (escaped, expected))
safe_print("verify[rule_order_ok]=%s" % rule_order_ok)
