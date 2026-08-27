#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""야수 배회 4단계와 체포 전 제압 조건을 적용한다."""

from pathlib import Path
import re


PATH = Path("ROUTE66_LIFE_EN.ow")
text = PATH.read_text(encoding="utf-8")


def sub(old, new, cnt=1):
    """예상 횟수를 확인한 뒤 문자열을 치환한다."""
    global text
    found = text.count(old)
    assert found == cnt, f"expected {cnt} occurrence(s), found {found}: {old!r}"
    text = text.replace(old, new)


def workshop_length(value):
    """워크샵의 CR/LF 이스케이프를 두 글자로 세어 리터럴 길이를 구한다."""
    return len(value.replace(r"\r\n", "XX"))


def literal_tokens(value):
    """보호 문구와 이스케이프를 자르지 않는 토큰으로 나눈다."""
    protected = "쏴서 제압한 뒤 수갑을 채운다"
    tokens = []
    index = 0
    while index < len(value):
        if value.startswith(protected, index):
            tokens.append(protected)
            index += len(protected)
        elif value.startswith(r"\r\n", index):
            tokens.append(r"\r\n")
            index += 4
        elif value[index] == "\\" and index + 1 < len(value):
            tokens.append(value[index:index + 2])
            index += 2
        else:
            tokens.append(value[index])
            index += 1
    return tokens


def split_literal(value, limit=120):
    """리터럴을 워크샵 제한 이내의 조각으로 나눈다."""
    parts = []
    current = []
    current_length = 0
    for token in literal_tokens(value):
        token_length = workshop_length(token)
        assert token_length <= limit, f"unsplittable literal token: {token!r}"
        if current and current_length + token_length > limit:
            parts.append("".join(current))
            current = []
            current_length = 0
        current.append(token)
        current_length += token_length
    if current:
        parts.append("".join(current))
    return parts


def balanced_concat(parts):
    """리터럴 조각을 균형 잡힌 두 갈래 Custom String으로 묶는다."""
    if len(parts) == 1:
        return f'Custom String("{parts[0]}")'
    middle = len(parts) // 2
    left = balanced_concat(parts[:middle])
    right = balanced_concat(parts[middle:])
    return f'Custom String("{{0}}{{1}}", {left}, {right})'


def guard_tutorial_literals(source):
    """120자를 넘는 잎 Custom String을 나누고 중첩 쌍을 재균형화한다."""
    leaf = re.compile(r'Custom String\("((?:\\.|[^"\\])*)"\)')

    def replace(match):
        value = match.group(1)
        if workshop_length(value) <= 120:
            return match.group(0)
        return balanced_concat(split_literal(value))

    guarded = leaf.sub(replace, source)
    literals = re.findall(r'"((?:\\.|[^"\\])*)"', guarded)
    too_long = [value for value in literals if workshop_length(value) > 120]
    assert not too_long, f"Custom String literal(s) still exceed 120: {too_long[:3]!r}"
    return guarded


sub("Random Integer(1, 100) <= 25);", "Random Integer(1, 100) <= 15);")
sub("Random Integer(1, 100) <= 3);", "Random Integer(1, 100) <= 0);")
sub("Else If(Random Integer(1, 100) <= 12);", "Else If(Random Integer(1, 100) <= 8);")
sub("Random Integer(210, 250)", "Random Integer(190, 230)", cnt=2)
sub("Random Integer(140, 200)", "Random Integer(130, 180)")

non_hunter_gate = (
    "\t\t\tIf(Event Player.Job != 3);\n"
    "\t\t\t\tSet Player Variable(Event Player, Busy, 0);\n"
    "\t\t\t\tSmall Message(Event Player, Custom String(\"체포는 현상금 사냥꾼의 일이다 — 보안관 초소에서 전직할 수 있다\"));\n"
    "\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);\n"
    "\t\t\t\tAbort;\n"
    "\t\t\tEnd;\n"
)
subdue_gate = (
    "\t\t\tIf(Health(Event Player.Target) >= Multiply(Max Health(Event Player.Target), 0.5));\n"
    "\t\t\t\tSet Player Variable(Event Player, Busy, 0);\n"
    "\t\t\t\tSmall Message(Event Player, Custom String(\"아직 팔팔하다 — 쏴서 제압해라 (체력 절반 미만이어야 수갑을 채운다)\"));\n"
    "\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);\n"
    "\t\t\t\tAbort;\n"
    "\t\t\tEnd;\n"
)
sub(non_hunter_gate, non_hunter_gate + subdue_gate)

sub(
    "전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 전직은 보안관 초소에서.",
    "전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 쏴서 제압한 뒤 수갑을 채운다.",
)
sub(
    "배지 — 체포는 현상금 사냥꾼의 일, 전직은 여기서",
    "배지 — 체포는 현상금 사냥꾼의 일, 제압(체력 절반)이 먼저다",
)

text = guard_tutorial_literals(text)

expected_counts = {
    "Random Integer(1, 100) <= 15);": 1,
    "Random Integer(1, 100) <= 0);": 1,
    "Else If(Random Integer(1, 100) <= 8);": 1,
    "Random Integer(190, 230)": 2,
    "Random Integer(130, 180)": 1,
    "아직 팔팔하다": 1,
    "Multiply(Max Health(Event Player.Target), 0.5)": 1,
    "쏴서 제압한 뒤 수갑을 채운다": 1,
    "제압(체력 절반)이 먼저다": 1,
}
for needle, expected in expected_counts.items():
    found = text.count(needle)
    assert found == expected, f"postcondition expected {expected}, found {found}: {needle!r}"

PATH.write_text(text, encoding="utf-8")
print("patch119_subdue: OK")
