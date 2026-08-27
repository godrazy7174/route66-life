# -*- coding: utf-8 -*-
"""낡은 장화 보행 보너스를 추가하고 직업 미니게임 튜토리얼을 보강한다."""

import re
from pathlib import Path


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")
SELECTOR = "Min(17, Event Player.TutStep)"
VALUE_ARRAY_PREFIX = "Value In Array(Array("
RN = chr(92) + "r" + chr(92) + "n"
SIMPLE_CUSTOM_STRING = re.compile(
    r'Custom String\("((?:\\.|[^"\\])*)"\)'
)
JOINED_CUSTOM_STRING = re.compile(
    r'Custom String\("\{0\}\{1\}", Custom String\("((?:\\.|[^"\\])*)"\), '
    r'Custom String\("((?:\\.|[^"\\])*)"\)\)'
)
ANY_CUSTOM_STRING_LITERAL = re.compile(
    r'Custom String\("((?:\\.|[^"\\])*)"'
)
PAGE_NAMES = (
    "route66",
    "hunger_thirst",
    "fatigue",
    "jobs",
    "miner",
    "hunter",
    "outlaw",
    "bounty_hunter",
    "courier",
    "cowherd",
    "selling",
    "gear",
    "day_night",
    "events",
    "three_day_cycle",
    "two_paths",
    "long_journey",
    "start",
)
APPENDS = (
    (
        4,
        "쉬지 않고 이어 캐면 연속 보너스가 붙는다.",
        "가끔 광맥이 울린다 — ◆가 ■ 구간에 올 때 [R]이 정타다.",
    ),
    (
        8,
        "대신 화물을 든 채 털리면 빼앗긴다.",
        "달리다 샛길 빛기둥이 보이면 7초 안에 밟아라 — 웃돈이 붙는다.",
    ),
    (
        9,
        "접근 각도가 실력이다.",
        "소가 겁먹으면 멈춰 서서 바라봐라 — 진정하면 웃돈이 붙는다.",
    ),
)


def sub(text, old, new, count, label):
    """정확한 출현 횟수를 확인한 뒤 문자열을 치환한다."""
    actual = text.count(old)
    if actual != count:
        raise AssertionError(
            f"{label}: expected {count} occurrences, found {actual}"
        )
    return text.replace(old, new)


def expect_count(text, needle, expected, label):
    """완성된 소스의 검증용 문자열 출현 횟수를 확인한다."""
    actual = text.count(needle)
    if actual != expected:
        raise AssertionError(
            f"{label}: expected {expected} occurrences, found {actual}"
        )


def matching_paren(source, open_at):
    """문자열 리터럴을 건너뛰며 짝이 맞는 닫는 괄호 위치를 찾는다."""
    if open_at < 0 or source[open_at] != "(":
        raise AssertionError(f"expected '(' at offset {open_at}")
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
            if depth < 0:
                raise AssertionError(f"unbalanced ')' at offset {at}")
            if depth == 0:
                return at
    raise AssertionError(f"no matching ')' for offset {open_at}")


def top_level_items(source, start, end):
    """괄호 내부의 최상위 쉼표 기준 항목과 위치를 반환한다."""
    if not 0 <= start <= end <= len(source):
        raise AssertionError("invalid array bounds")
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
            if depth < 0:
                raise AssertionError(f"unbalanced item ')' at offset {at}")
        elif char == "," and depth == 0:
            left = item_start
            right = at
            while left < right and source[left].isspace():
                left += 1
            while right > left and source[right - 1].isspace():
                right -= 1
            spans.append((left, right))
            item_start = at + 1
    if in_string:
        raise AssertionError("unterminated string in array")
    if depth != 0:
        raise AssertionError(f"unbalanced item parentheses: depth {depth}")
    left = item_start
    right = end
    while left < right and source[left].isspace():
        left += 1
    while right > left and source[right - 1].isspace():
        right -= 1
    spans.append((left, right))
    if not all(left < right for left, right in spans):
        raise AssertionError("empty array item")
    return spans


def tutorial_body_bounds(source):
    """유일한 튜토리얼 줄에서 두 번째 배열 본문의 경계를 찾는다."""
    lines = source.splitlines(keepends=True)
    matching_lines = [index for index, line in enumerate(lines) if SELECTOR in line]
    if len(matching_lines) != 1:
        raise AssertionError(
            f"tutorial lines: expected 1, found {len(matching_lines)}"
        )
    line_index = matching_lines[0]
    line = lines[line_index]
    if line.count(SELECTOR) != 2:
        raise AssertionError(
            "tutorial selector count on line: "
            f"expected 2, found {line.count(SELECTOR)}"
        )
    starts = []
    search_at = 0
    while True:
        found = line.find(VALUE_ARRAY_PREFIX, search_at)
        if found < 0:
            break
        starts.append(found)
        search_at = found + len(VALUE_ARRAY_PREFIX)
    if len(starts) != 2:
        raise AssertionError(
            "tutorial Value In Array expressions: "
            f"expected 2, found {len(starts)}"
        )
    body_expression_start = starts[1]
    outer_open = body_expression_start + len("Value In Array")
    outer_close = matching_paren(line, outer_open)
    expression = line[body_expression_start : outer_close + 1]
    if not expression.endswith(f", {SELECTOR})"):
        raise AssertionError("unexpected body selector shape")
    array_start = body_expression_start + len("Value In Array(")
    if not line.startswith("Array(", array_start):
        raise AssertionError("body does not start with Array(")
    array_open = array_start + len("Array")
    array_close = matching_paren(line, array_open)
    if array_close >= outer_close:
        raise AssertionError("body array must be inside Value In Array")
    absolute_line_start = sum(len(part) for part in lines[:line_index])
    return absolute_line_start + array_open + 1, absolute_line_start + array_close


def rendered_length(content):
    """\\r\\n 한 쌍을 게임 비용 2자로 계산한 소스 길이를 구한다."""
    return len(content) - 2 * content.count(RN)


def nearest_rn_boundary(content):
    """유효 길이의 중앙에 가장 가까운 줄바꿈 뒤 위치를 고른다."""
    candidates = []
    search_at = 0
    while True:
        found = content.find(RN, search_at)
        if found < 0:
            break
        candidates.append(found + len(RN))
        search_at = found + len(RN)
    if not candidates:
        raise AssertionError("overlong tutorial body has no RN split boundary")
    middle = rendered_length(content) / 2
    return min(
        candidates,
        key=lambda boundary: (
            abs(rendered_length(content[:boundary]) - middle),
            boundary,
        ),
    )


def split_body(content, page_index):
    """중앙에 가까운 줄바꿈에서 본문을 두 리터럴로 나눈다."""
    boundary = nearest_rn_boundary(content)
    first = content[:boundary]
    second = content[boundary:]
    first_length = rendered_length(first)
    second_length = rendered_length(second)
    if first_length > 120 or second_length > 120:
        raise AssertionError(
            f"tutorial body {page_index}: split lengths "
            f"{first_length}, {second_length} exceed 120"
        )
    return first, second


def parse_body(item, page_index):
    """단일 본문 또는 두 부분 연결 본문을 분해한다."""
    simple_match = SIMPLE_CUSTOM_STRING.fullmatch(item)
    if simple_match is not None:
        return "simple", (simple_match.group(1),)
    joined_match = JOINED_CUSTOM_STRING.fullmatch(item)
    if joined_match is not None:
        return "joined", (joined_match.group(1), joined_match.group(2))
    raise AssertionError(f"tutorial body {page_index}: unexpected shape")


def joined_body(first, second):
    """두 본문 리터럴을 {0}{1} 표현식으로 연결한다."""
    return (
        'Custom String("{0}{1}", Custom String("'
        + first
        + '"), Custom String("'
        + second
        + '"))'
    )


def safe_print(message):
    """호출자의 cp949 콘솔을 위해 ASCII 보고만 출력한다."""
    print(message.encode("ascii", "backslashreplace").decode("ascii"))


def main():
    with SOURCE.open("r", encoding="utf-8", newline="") as source_file:
        source = source_file.read()

    old_speed = "Set Move Speed(Event Player, 100);"
    new_speed = (
        "Set Move Speed(Event Player, And(Event Player.HasBag == 0, "
        "Event Player.HasHorse == 0) ? 110 : 100);"
    )
    expect_count(source, new_speed, 0, "new boot speed before patch")
    patched = sub(source, old_speed, new_speed, 2, "walk speed restores")

    for page_index, anchor, addition in APPENDS:
        expect_count(patched, addition, 0, f"page {page_index} addition before patch")

    body_start, body_end = tutorial_body_bounds(patched)
    body_spans = top_level_items(patched, body_start, body_end)
    if len(body_spans) != 18:
        raise AssertionError(
            f"tutorial bodies: expected 18, found {len(body_spans)}"
        )

    replacements = []
    split_report = []
    append_by_page = {
        page_index: (anchor, addition)
        for page_index, anchor, addition in APPENDS
    }
    for page_index, (start, end) in enumerate(body_spans):
        item = patched[start:end]
        if page_index in append_by_page:
            anchor, addition = append_by_page[page_index]
            item = sub(
                item,
                anchor,
                anchor + RN + addition,
                1,
                f"page {page_index} tutorial append anchor",
            )

        shape, parts = parse_body(item, page_index)
        if shape == "simple" and rendered_length(parts[0]) > 120:
            first, second = split_body(parts[0], page_index)
            item = joined_body(first, second)
            split_report.append(
                (
                    page_index,
                    "split",
                    rendered_length(parts[0]),
                    rendered_length(first),
                    rendered_length(second),
                )
            )
        elif shape == "joined" and any(
            rendered_length(part) > 120 for part in parts
        ):
            content = parts[0] + parts[1]
            first, second = split_body(content, page_index)
            item = joined_body(first, second)
            split_report.append(
                (
                    page_index,
                    "rebalanced",
                    rendered_length(content),
                    rendered_length(first),
                    rendered_length(second),
                )
            )
        replacements.append((start - body_start, end - body_start, item))

    old_body = patched[body_start:body_end]
    new_body = old_body
    for start, end, item in reversed(replacements):
        new_body = new_body[:start] + item + new_body[end:]
    patched = sub(patched, old_body, new_body, 1, "tutorial body array")

    final_body_start, final_body_end = tutorial_body_bounds(patched)
    final_spans = top_level_items(patched, final_body_start, final_body_end)
    if len(final_spans) != 18:
        raise AssertionError(
            f"final tutorial bodies: expected 18, found {len(final_spans)}"
        )
    for page_index, (start, end) in enumerate(final_spans):
        shape, parts = parse_body(patched[start:end], page_index)
        for part in parts:
            length = rendered_length(part)
            if length > 120:
                raise AssertionError(
                    f"final tutorial body {page_index} literal too long: {length}"
                )
    for literal_match in ANY_CUSTOM_STRING_LITERAL.finditer(
        patched[final_body_start:final_body_end]
    ):
        length = rendered_length(literal_match.group(1))
        if length > 120:
            raise AssertionError(f"final tutorial literal too long: {length}")

    expect_count(patched, old_speed, 0, "old walk speed restores")
    expect_count(patched, "? 110 : 100);", 2, "new boot speed suffix")
    expect_count(patched, "[R]이 정타다", 1, "miner tutorial line")
    expect_count(patched, "샛길 빛기둥이 보이면", 1, "courier tutorial line")
    expect_count(patched, "소가 겁먹으면 멈춰 서서", 1, "cowherd tutorial line")
    if patched == source:
        raise AssertionError("patch produced no changes")

    with SOURCE.open("w", encoding="utf-8", newline="") as source_file:
        source_file.write(patched)

    safe_print("OK: patch108_boots.py applied")
    safe_print("walk speed: boosted restores=2 old restores=0")
    if split_report:
        for page_index, action, total, first, second in split_report:
            safe_print(
                "tutorial guard: "
                f"page={page_index} name={PAGE_NAMES[page_index]} "
                f"action={action} total={total} parts={first},{second}"
            )
    else:
        safe_print("tutorial guard: no pages split or rebalanced")
    safe_print("tutorial literals: all <= 120")


if __name__ == "__main__":
    main()
