# -*- coding: utf-8 -*-
"""빈털터리 플레이어를 위한 무료 피로 회복 규칙과 튜토리얼 안내를 추가한다."""

from pathlib import Path
import re


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")


def sub(text, old, new, cnt=1):
    """정확히 cnt번 존재하는 문자열만 치환한다."""
    actual = text.count(old)
    assert actual == cnt, (
        "replacement count mismatch: expected %d, found %d" % (cnt, actual)
    )
    return text.replace(old, new)


def block(*lines):
    """현재 소스의 줄바꿈으로 Workshop 블록을 조립한다."""
    return EOL.join(lines)


def literal_length(content):
    """Workshop RN escape 하나를 두 글자로 세어 문자열 길이를 구한다."""
    return len(content) - (2 * content.count("\\r\\n"))


def split_tutorial_literal(text):
    """필요한 경우 튜토리얼 본문을 가장 가까운 RN 경계에서 둘로 나눈다."""
    lines = [
        line
        for line in text.splitlines()
        if "Min(17, Event Player.TutStep)" in line
    ]
    assert len(lines) == 1, "tutorial HUD line count mismatch"
    line = lines[0]

    quoted = re.compile(r'"(?:\\.|[^"\\])*"')
    matches = [
        match
        for match in quoted.finditer(line)
        if TUTORIAL_NEW in match.group(0)
    ]
    assert len(matches) == 1, "fatigue tutorial literal count mismatch"
    match = matches[0]
    content = match.group(0)[1:-1]
    length = literal_length(content)
    if length <= 120:
        return text, (length,)

    boundaries = []
    start = 0
    while True:
        pos = content.find("\\r\\n", start)
        if pos < 0:
            break
        split_at = pos + 4
        if 0 < split_at < len(content):
            boundaries.append(split_at)
        start = pos + 4
    assert boundaries, "long tutorial literal has no RN split boundary"

    split_at = min(
        boundaries,
        key=lambda pos: abs(
            literal_length(content[:pos]) - literal_length(content[pos:])
        ),
    )
    left = content[:split_at]
    right = content[split_at:]
    lengths = (literal_length(left), literal_length(right))
    assert max(lengths) <= 120, "split tutorial literal still exceeds 120"

    before = line[: match.start()]
    call_start_match = re.search(r"Custom String\(\s*$", before)
    assert call_start_match is not None, "tutorial Custom String start not found"
    after = line[match.end() :]
    call_end_match = re.match(r"\s*\)", after)
    assert call_end_match is not None, "tutorial Custom String end not found"

    call_start = call_start_match.start()
    call_end = match.end() + call_end_match.end()
    nested = (
        'Custom String("{0}{1}", Custom String("'
        + left
        + '"), Custom String("'
        + right
        + '"))'
    )
    new_line = line[:call_start] + nested + line[call_end:]
    return sub(text, line, new_line, cnt=1), lengths


raw = SOURCE.read_bytes()
text = raw.decode("utf-8")
EOL = "\r\n" if b"\r\n" in raw else "\n"

REST_RULE = block(
    'rule("[생활 03] 쪼그려 쉬기")',
    "{",
    "\tevent",
    "\t{",
    "\t\tOngoing - Each Player;",
    "\t\tAll;",
    "\t\tAll;",
    "\t}",
    "",
    "\tconditions",
    "\t{",
    "\t\tIs Dummy Bot(Event Player) == False;",
    "\t\tEvent Player.Init == 1;",
    "\t\tEvent Player.TutOn == 0;",
    "\t\tEvent Player.Busy == 0;",
    "\t\tIs Alive(Event Player) == True;",
    "\t\tIs Crouching(Event Player) == True;",
    "\t\tIs Moving(Event Player) == False;",
    "\t\tEvent Player.Energy < 100;",
    "\t}",
    "",
    "\tactions",
    "\t{",
    "\t\tSmall Message(Event Player, Custom String(\"바닥에 쪼그려 앉아 숨을 고른다 — 느리게 피로가 돌아온다\"));",
    "\t\tWait(5, Ignore Condition);",
    "\t\tIf(And(And(Is Crouching(Event Player) == True, Is Moving(Event Player) == False), And(Is Alive(Event Player), Event Player.Busy == 0)));",
    "\t\t\tSet Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 1)));",
    "\t\t\tPlay Effect(Event Player, Good Pickup Effect, Color(Gray), Position Of(Event Player), 0.8);",
    "\t\tEnd;",
    "\t\tLoop If(And(And(Is Crouching(Event Player) == True, Is Moving(Event Player) == False), And(Is Alive(Event Player), Event Player.Energy < 100)));",
    "\t}",
    "}",
)

JAIL_ANCHOR = 'rule("[감옥 01] 만기 출소")'
text = sub(text, JAIL_ANCHOR, block(REST_RULE, "", JAIL_ANCHOR), cnt=1)

TUTORIAL_OLD = "하룻밤 $90에 피로를 40 되찾는다. 내 방을 마련하면 80으로 늘어난다."
TUTORIAL_NEW = (
    TUTORIAL_OLD
    + "\\r\\n"
    + "빈털터리라면 쪼그려 앉아 숨을 골라라 — 느리지만 공짜다."
)
text = sub(text, TUTORIAL_OLD, TUTORIAL_NEW, cnt=1)
text, tutorial_lengths = split_tutorial_literal(text)

assert text.count('rule("[생활 03] 쪼그려 쉬기")') == 1
assert text.count("쪼그려 앉아 숨을 고른다") == 1
assert text.count("느리지만 공짜다") == 1
assert text.count("Is Crouching(Event Player) == True") >= 3
assert max(tutorial_lengths) <= 120

SOURCE.write_bytes(text.encode("utf-8"))

print("patch113_rest.py: OK")
print("tutorial literal lengths: " + ",".join(map(str, tutorial_lengths)))
print("rest rule count: 1")
print("rest message count: 1")
print("tutorial hint count: 1")
print("crouch condition count: %d" % text.count("Is Crouching(Event Player) == True"))
