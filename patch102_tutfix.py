# -*- coding: utf-8 -*-
"""튜토리얼 본문을 안전하게 분할하고 야수 가죽 기본 드롭을 소폭 높인다."""

import re
from pathlib import Path


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")
SELECTOR = "Min(17, Event Player.TutStep)"
VALUE_ARRAY_PREFIX = "Value In Array(Array("
SIMPLE_CUSTOM_STRING = re.compile(
    r'Custom String\("((?:\\.|[^"\\])*)"\)'
)
ANY_CUSTOM_STRING_LITERAL = re.compile(
    r'Custom String\("((?:\\.|[^"\\])*)"'
)

with SOURCE.open("r", encoding="utf-8", newline="") as source_file:
    text = source_file.read()


def matching_paren(source, open_at):
    """문자열 리터럴을 건너뛰며 짝이 맞는 닫는 괄호 위치를 찾는다."""
    assert source[open_at] == "(", f"expected '(' at offset {open_at}"
    depth = 0
    in_string = False
    escaped = False
    for at in range(open_at, len(source)):
        char = source[at]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            assert depth >= 0, f"unbalanced ')' at offset {at}"
            if depth == 0:
                return at
    raise AssertionError(f"no matching ')' for offset {open_at}")


def top_level_items(source, start, end):
    """괄호 내부의 최상위 쉼표 기준 항목과 원래 위치를 반환한다."""
    assert 0 <= start <= end <= len(source), "invalid array bounds"
    spans = []
    item_start = start
    depth = 0
    in_string = False
    escaped = False
    for at in range(start, end):
        char = source[at]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            assert depth >= 0, f"unbalanced item ')' at offset {at}"
        elif char == "," and depth == 0:
            left = item_start
            right = at
            while left < right and source[left].isspace():
                left += 1
            while right > left and source[right - 1].isspace():
                right -= 1
            spans.append((left, right))
            item_start = at + 1
    assert not in_string, "unterminated string in array"
    assert depth == 0, f"unbalanced item parentheses: depth {depth}"
    left = item_start
    right = end
    while left < right and source[left].isspace():
        left += 1
    while right > left and source[right - 1].isspace():
        right -= 1
    spans.append((left, right))
    assert all(left < right for left, right in spans), "empty array item"
    return spans


def tutorial_body_bounds(source):
    """유일한 튜토리얼 줄에서 두 번째 배열 본문의 경계를 찾는다."""
    lines = source.splitlines(keepends=True)
    matching_lines = [index for index, line in enumerate(lines) if SELECTOR in line]
    assert len(matching_lines) == 1, (
        f"tutorial lines: expected 1, found {len(matching_lines)}"
    )
    line_index = matching_lines[0]
    line = lines[line_index]
    assert line.count(SELECTOR) == 2, (
        f"tutorial selector count on line: expected 2, found {line.count(SELECTOR)}"
    )
    starts = []
    search_at = 0
    while True:
        found = line.find(VALUE_ARRAY_PREFIX, search_at)
        if found < 0:
            break
        starts.append(found)
        search_at = found + len(VALUE_ARRAY_PREFIX)
    assert len(starts) == 2, (
        f"tutorial Value In Array expressions: expected 2, found {len(starts)}"
    )
    body_expression_start = starts[1]
    outer_open = body_expression_start + len("Value In Array")
    outer_close = matching_paren(line, outer_open)
    expression = line[body_expression_start:outer_close + 1]
    assert expression.endswith(f", {SELECTOR})"), "unexpected body selector shape"
    array_start = body_expression_start + len("Value In Array(")
    assert line.startswith("Array(", array_start), "body does not start with Array("
    array_open = array_start + len("Array")
    array_close = matching_paren(line, array_open)
    assert array_close < outer_close, "body array must be inside Value In Array"
    absolute_line_start = sum(len(part) for part in lines[:line_index])
    return (
        absolute_line_start + array_open + 1,
        absolute_line_start + array_close,
    )


def rendered_length(content):
    """\\r\\n 한 쌍을 게임 비용 2자로 계산한 소스 길이를 구한다."""
    return len(content) - 2 * content.count(r"\r\n")


def nearest_boundary(content, delimiter):
    """유효 길이의 중앙에 가장 가까운 구분자 뒤 위치를 고른다."""
    candidates = []
    search_at = 0
    while True:
        found = content.find(delimiter, search_at)
        if found < 0:
            break
        boundary = found + len(delimiter)
        candidates.append(boundary)
        search_at = found + len(delimiter)
    assert candidates, f"no split delimiter {delimiter!r}"
    middle = rendered_length(content) / 2
    return min(
        candidates,
        key=lambda boundary: (
            abs(rendered_length(content[:boundary]) - middle),
            boundary,
        ),
    )


def split_body(content):
    """줄바꿈을 우선하고 필요하면 공백에서 본문을 둘로 나눈다."""
    if r"\r\n" in content:
        boundary = nearest_boundary(content, r"\r\n")
        first = content[:boundary]
        second = content[boundary:]
        if rendered_length(first) <= 120 and rendered_length(second) <= 120:
            return first, second
    assert " " in content, "overlong tutorial body has no usable split point"
    boundary = nearest_boundary(content, " ")
    first = content[:boundary]
    second = content[boundary:]
    assert rendered_length(first) <= 120, (
        f"first split part too long: {rendered_length(first)}"
    )
    assert rendered_length(second) <= 120, (
        f"second split part too long: {rendered_length(second)}"
    )
    return first, second


body_start, body_end = tutorial_body_bounds(text)
body_items = top_level_items(text, body_start, body_end)
assert len(body_items) == 18, f"tutorial bodies: expected 18, found {len(body_items)}"

replacements = []
split_report = []
for index, (start, end) in enumerate(body_items):
    item = text[start:end]
    match = SIMPLE_CUSTOM_STRING.fullmatch(item)
    assert match is not None, f"tutorial body {index}: unexpected initial shape"
    content = match.group(1)
    before_length = rendered_length(content)
    if before_length <= 120:
        continue
    first, second = split_body(content)
    assert first + second == content, f"tutorial body {index}: visible text changed"
    assert rendered_length(first) <= 120, f"tutorial body {index}: PART1 too long"
    assert rendered_length(second) <= 120, f"tutorial body {index}: PART2 too long"
    replacement = (
        'Custom String("{0}{1}", Custom String("'
        + first
        + '"), Custom String("'
        + second
        + '"))'
    )
    replacements.append((start, end, replacement))
    split_report.append((index, before_length))

assert replacements, "expected at least one overlong tutorial body"
for start, end, replacement in reversed(replacements):
    text = text[:start] + replacement + text[end:]

old_pelt = "Set Player Variable(Attacker, Yield, Random Integer(1, 2));"
new_pelt = "Set Player Variable(Attacker, Yield, Random Integer(1, 3));"
old_pelt_count = text.count(old_pelt)
new_pelt_count = text.count(new_pelt)
assert old_pelt_count == 1, f"old pelt roll: expected 1, found {old_pelt_count}"
assert new_pelt_count == 0, f"new pelt roll before patch: expected 0, found {new_pelt_count}"
text = text.replace(old_pelt, new_pelt, 1)

# Reparse the final text and validate the exact tutorial and pelt invariants.
final_body_start, final_body_end = tutorial_body_bounds(text)
final_items = top_level_items(text, final_body_start, final_body_end)
assert len(final_items) == 18, (
    f"final tutorial bodies: expected 18, found {len(final_items)}"
)
for literal_match in ANY_CUSTOM_STRING_LITERAL.finditer(
    text[final_body_start:final_body_end]
):
    length = rendered_length(literal_match.group(1))
    assert length <= 120, f"final tutorial literal too long: {length}"
assert text.count(old_pelt) == 0, "old pelt roll remains after patch"
assert text.count(new_pelt) == 1, "new pelt roll count is not 1"

with SOURCE.open("w", encoding="utf-8", newline="") as source_file:
    source_file.write(text)


def safe_print(message):
    """호출자의 cp949 콘솔을 위해 보고 문구를 ASCII로 제한한다."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "backslashreplace").decode("ascii"))


safe_print("patch102_tutfix.py applied successfully")
safe_print(
    "tutorial splits: "
    + ", ".join(f"index={index} before={length}" for index, length in split_report)
)
safe_print("pelt roll: Random Integer(1, 2) -> Random Integer(1, 3)")
