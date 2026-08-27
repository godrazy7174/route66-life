# -*- coding: utf-8 -*-
"""프레야 현상금 사냥꾼, 야수 난이도, 체포 난이도를 한 번에 반영한다."""

from pathlib import Path


PATH = Path("ROUTE66_LIFE_EN.ow")


with PATH.open("r", encoding="utf-8", newline="") as f:
    text = f.read()

eol = "\r\n" if "\r\n" in text else "\n"


def sub(old, new, cnt=1):
    """정확한 출현 횟수를 확인한 뒤 문자열을 치환한다."""
    global text
    found = text.count(old)
    assert found == cnt, (
        "replace count mismatch: expected %d, found %d for %r"
        % (cnt, found, old)
    )
    text = text.replace(old, new)


def block(name, lines):
    """워크샵의 event/conditions/actions 블록을 만든다."""
    body = eol.join("\t\t" + line for line in lines)
    return eol.join(("\t" + name, "\t{", body, "\t}"))


def mkrule(name, event, conditions, actions):
    """워크샵 규칙 하나를 조립한다."""
    return eol.join(
        (
            'rule("' + name + '")',
            "{",
            block("event", event),
            "",
            block("conditions", conditions),
            "",
            block("actions", actions),
            "}",
        )
    )


def rule_text(name):
    """이름이 일치하는 규칙 전체를 중괄호 균형으로 찾는다."""
    anchor = 'rule("' + name + '")'
    assert text.count(anchor) == 1, "rule anchor count mismatch: " + repr(anchor)
    start = text.index(anchor)
    brace = text.index("{", start + len(anchor))
    depth = 0
    quoted = False
    escaped = False
    for pos in range(brace, len(text)):
        char = text[pos]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : pos + 1]
    raise AssertionError("unterminated rule: " + repr(name))


# A1: 애쉬 봉인 규칙의 구조와 액션을 그대로 복제한다.
core06 = rule_text("[코어 06] 애쉬 스킬 봉인 (조준경 허용)")
assert core06.count('rule("[코어 06] 애쉬 스킬 봉인 (조준경 허용)")') == 1
assert core06.count("Hero Of(Event Player) == Hero(Ashe);") == 1
core20 = core06.replace(
    'rule("[코어 06] 애쉬 스킬 봉인 (조준경 허용)")',
    'rule("[코어 20] 프레야 스킬 봉인 (조준 허용)")',
)
core20 = core20.replace(
    "Hero Of(Event Player) == Hero(Ashe);",
    "Hero Of(Event Player) == Hero(Freja);",
)
sub(core06, core06 + eol + eol + core20)


# A2-A3: 프레야 강제 선택과 배지 반납 시 복구.
core21 = mkrule(
    "[코어 21] 현상금 사냥꾼은 프레야",
    ("Ongoing - Each Player;", "All;", "All;"),
    (
        "Is Dummy Bot(Event Player) == False;",
        "Event Player.Init == 1;",
        "Event Player.Job == 3;",
    ),
    ("Start Forcing Player To Be Hero(Event Player, Hero(Freja));",),
)
core22 = mkrule(
    "[코어 22] 배지를 반납하면",
    ("Ongoing - Each Player;", "All;", "All;"),
    (
        "Is Dummy Bot(Event Player) == False;",
        "Event Player.Init == 1;",
        "Event Player.Job != 3;",
        "Hero Of(Event Player) == Hero(Freja);",
    ),
    (
        "If(Event Player.HasHorse == 1);",
        "Start Forcing Player To Be Hero(Event Player, Hero(Shion));",
        "Else If(Event Player.HasBag == 1);",
        "Start Forcing Player To Be Hero(Event Player, Hero(Tracer));",
        "Else;",
        "Stop Forcing Player To Be Hero(Event Player);",
        "End;",
    ),
)
core07 = 'rule("[코어 07] 궁극기 게이지 상시 제거")'
sub(core07, core21 + eol + eol + core22 + eol + eol + core07)

sub(
    "배지를 받았다 — 현상금 사냥꾼. 전단이 붙은 자($300+)를 산 채로 잡아라",
    "배지를 받았다 — 석궁의 프레야가 된다. 전단이 붙은 자($300+)를 산 채로 잡아라",
)


# B: 변종 확률, 공개 시간, 3단계 배회 난이도.
sub(
    "Add(11, Multiply(5, Event Player.Roll))",
    "Add(22, Multiply(10, Event Player.Roll))",
)
sub("Idx), Roll) <= 1);", "Idx), Roll) <= 2);")
sub(
    "RevealEnd, Add(Total Time Elapsed(), 30)",
    "RevealEnd, Add(Total Time Elapsed(), 40)",
)
sub("Random Integer(1, 100) <= 35);", "Random Integer(1, 100) <= 25);")
sub("Random Integer(1, 100) <= 5);", "Random Integer(1, 100) <= 3);")
sub(
    "Else If(Random Integer(1, 100) <= 18);",
    "Else If(Random Integer(1, 100) <= 12);",
)
sub("Random Integer(230, 270)", "Random Integer(210, 250)", cnt=2)
sub("Random Integer(150, 220)", "Random Integer(140, 200)")


# C: 체포 채널, 이탈 반경, 실패 후 재시도 대기.
sub("? 2.5 : 4);", "? 3 : 5);")
sub("), 4.5);", "), 5.5);")
sub("Position Of(Event Player.Target)) > 12", "Position Of(Event Player.Target)) > 10", cnt=2)
sub(
    "RobCd, Add(Total Time Elapsed(), 10)",
    "RobCd, Add(Total Time Elapsed(), 15)",
    cnt=2,
)


# 호출자가 확인할 최종 불변식.
checks = (
    ("Hero(Freja)", 3),
    ('rule("[코어 20] 프레야 스킬 봉인 (조준 허용)")', 1),
    ('rule("[코어 21] 현상금 사냥꾼은 프레야")', 1),
    ('rule("[코어 22] 배지를 반납하면")', 1),
    ("석궁의 프레야", 1),
    ("Add(22, Multiply(10, Event Player.Roll))", 1),
    ("Idx), Roll) <= 2);", 1),
    ("Elapsed(), 40)", 1),
    ("? 3 : 5);", 1),
    ("), 5.5);", 3),
    ("Target)) > 10", 2),
    ("Elapsed(), 15)", 2),
)
for needle, expected in checks:
    found = text.count(needle)
    assert found == expected, (
        "final count mismatch: expected %d, found %d for %r"
        % (expected, found, needle)
    )

with PATH.open("w", encoding="utf-8", newline="") as f:
    f.write(text)

print("patch118_freja.py: OK")
