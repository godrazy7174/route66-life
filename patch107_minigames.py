# -*- coding: utf-8 -*-
"""직업별 미니게임을 분리하고 광부 스킬바 난이도를 조정한다."""

from pathlib import Path
import re


SOURCE = Path("ROUTE66_LIFE_EN.ow")


def sub(text, old, new, count, label):
    """정확한 출현 횟수를 확인한 뒤 문자열을 치환한다."""
    actual = text.count(old)
    if actual != count:
        raise AssertionError(
            f"{label}: expected {count} occurrences, found {actual}"
        )
    return text.replace(old, new)


def block(*lines):
    """워크샵 액션 블록을 한 번에 조립한다."""
    return "\n".join(lines)


def closing_brace(text, opening, label):
    """문자열 리터럴을 건너뛰며 여는 중괄호와 짝인 위치를 찾는다."""
    if opening < 0 or text[opening] != "{":
        raise AssertionError(f"{label}: opening brace not found")

    depth = 0
    quoted = False
    escaped = False
    for index in range(opening, len(text)):
        char = text[index]
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
                return index

    raise AssertionError(f"{label}: closing brace not found")


def rule_span(text, title, label):
    """고유한 규칙 헤더부터 그 규칙의 닫는 중괄호까지 범위를 구한다."""
    header = f'rule("{title}")'
    actual = text.count(header)
    if actual != 1:
        raise AssertionError(
            f"{label}: expected one rule header, found {actual}"
        )
    start = text.index(header)
    opening = text.find("{", start + len(header))
    end = closing_brace(text, opening, label)
    return start, end + 1


def replace_actions(text, title, actions, label, newline):
    """이벤트와 조건은 유지하고 고유 규칙의 actions 본문만 교체한다."""
    rule_start, rule_end = rule_span(text, title, label)
    rule_text = text[rule_start:rule_end]
    matches = list(re.finditer(r"(?m)^[ \t]*actions[ \t]*\r?$", rule_text))
    if len(matches) != 1:
        raise AssertionError(
            f"{label}: expected one actions block, found {len(matches)}"
        )

    actions_line = rule_start + matches[0].start()
    opening = text.find("{", actions_line, rule_end)
    closing = closing_brace(text, opening, label + " actions")
    if closing >= rule_end:
        raise AssertionError(f"{label}: actions block escaped rule")

    closing_line = text.rfind("\n", opening, closing) + 1
    closing_indent = text[closing_line:closing]
    if closing_indent.strip():
        raise AssertionError(f"{label}: malformed actions closing indent")

    rendered = actions.replace("\n", newline)
    replacement = newline + rendered + newline + closing_indent
    return text[: opening + 1] + replacement + text[closing:]


def expect_count(text, needle, expected, label):
    """완성된 소스의 검증용 문자열 출현 횟수를 확인한다."""
    actual = text.count(needle)
    if actual != expected:
        raise AssertionError(
            f"{label}: expected {expected} occurrences, found {actual}"
        )


def main():
    with SOURCE.open("r", encoding="utf-8", newline="") as source_file:
        source = source_file.read()
    newline = "\r\n" if "\r\n" in source else "\n"
    patched = source

    miner_title = "[스킬바 01] DoSkillBar"
    miner_start, miner_end = rule_span(patched, miner_title, "miner")
    miner_rule = patched[miner_start:miner_end]
    miner_rule = sub(miner_rule, "0.9", "0.72", 8, "miner sweep")
    patched = patched[:miner_start] + miner_rule + patched[miner_end:]

    courier_actions = block(
        "\t\tWait(Random Real(7, 14), Ignore Condition);",
        "\t\tIf(And(And(Event Player.HasParcel == 1, Event Player.Busy == 0), Is Alive(Event Player)));",
        "\t\t\tSet Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Direction From Angles(Random Real(0, 360), 0), 17))));",
        "\t\t\tCreate Effect(All Players(All Teams), Light Shaft, Color(Yellow), Event Player.DialTgt, 1.2, None);",
        "\t\t\tSet Player Variable(Event Player, DialPin, Last Created Entity());",
        "\t\t\tCreate Icon(Event Player, Add(Event Player.DialTgt, Vector(0, 2.5, 0)), Circle, Visible To and Position, Color(Yellow), True);",
        "\t\t\tSet Player Variable(Event Player, DialCur, Last Created Entity());",
        "\t\t\tBig Message(Event Player, Custom String(\"샛길이 보인다 — 7초 안에 빛기둥을 밟아라!\"));",
        "\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 45);",
        "\t\t\tWait Until(Or(Or(Distance Between(Position Of(Event Player), Event Player.DialTgt) < 3, Event Player.Busy == 1), Or(Event Player.HasParcel != 1, Not(Is Alive(Event Player)))), 7);",
        "\t\t\tDestroy Effect(Event Player.DialPin);",
        "\t\t\tDestroy Icon(Event Player.DialCur);",
        "\t\t\tIf(And(And(Distance Between(Position Of(Event Player), Event Player.DialTgt) < 3, Event Player.HasParcel == 1), Is Alive(Event Player)));",
        "\t\t\t\tModify Player Variable(Event Player, Money, Add, 15);",
        "\t\t\t\tModify Player Variable(Event Player, Earned, Add, 15);",
        "\t\t\t\tSmall Message(Event Player, Custom String(\"샛길로 질렀다 +$15\"));",
        "\t\t\t\tPlay Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1.2);",
        "\t\t\tElse;",
        "\t\t\t\tSmall Message(Event Player, Custom String(\"샛길이 흙먼지에 묻혔다\"));",
        "\t\t\tEnd;",
        "\t\tEnd;",
        "\t\tWait(2, Ignore Condition);",
        "\t\tLoop If(Event Player.HasParcel == 1);",
    )
    patched = replace_actions(
        patched,
        "[파발 02] 흔들리는 화물",
        courier_actions,
        "courier",
        newline,
    )

    sample = block(
        "\t\t\tIf(And(Is Moving(Event Player) == False, Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Event Player.CowPos)) >= 0.85));",
        "\t\t\t\tModify Player Variable(Event Player, WorkProg, Add, 1);",
        "\t\t\tEnd;",
        "\t\t\tWait(0.5, Ignore Condition);",
    )
    cowherd_actions = block(
        "\t\tWait(Random Real(6, 12), Ignore Condition);",
        "\t\tIf(And(And(Event Player.CowOn == 1, Event Player.Busy == 0), Is Alive(Event Player)));",
        "\t\t\tSet Player Variable(Event Player, WorkProg, 0);",
        "\t\t\tBig Message(Event Player, Custom String(\"소가 겁먹었다 — 2초간 멈춰 서서 소를 바라봐라!\"));",
        "\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(White), Position Of(Event Player), 45);",
        "\t\t\tWait(0.5, Ignore Condition);",
        sample,
        sample,
        sample,
        sample,
        "\t\t\tIf(And(Event Player.WorkProg >= 4, Event Player.CowOn == 1));",
        "\t\t\t\tModify Player Variable(Event Player, Money, Add, 12);",
        "\t\t\t\tModify Player Variable(Event Player, Earned, Add, 12);",
        "\t\t\t\tSmall Message(Event Player, Custom String(\"소가 진정했다 +$12\"));",
        "\t\t\t\tPlay Effect(Event Player, Ring Explosion, Color(White), Position Of(Event Player), 1);",
        "\t\t\tElse;",
        "\t\t\t\tSmall Message(Event Player, Custom String(\"소가 콧대를 세운다 — 눈을 피했다\"));",
        "\t\t\tEnd;",
        "\t\t\tSet Player Variable(Event Player, WorkProg, 0);",
        "\t\tEnd;",
        "\t\tWait(2, Ignore Condition);",
        "\t\tLoop If(Event Player.CowOn == 1);",
    )
    patched = replace_actions(
        patched,
        "[목동 02] 날뛰는 소",
        cowherd_actions,
        "cowherd",
        newline,
    )

    checks = (
        ("0.72", 8, "miner duration"),
        ("샛길이 보인다", 1, "courier prompt"),
        ("샛길로 질렀다", 1, "courier success"),
        ("샛길이 흙먼지에 묻혔다", 1, "courier failure"),
        ("소가 겁먹었다", 1, "cowherd prompt"),
        ("소가 진정했다", 1, "cowherd success"),
        ("소가 콧대를 세운다", 1, "cowherd failure"),
        ("화물 끈이 풀린다", 0, "old courier game"),
        ("소가 날뛴다", 0, "old cowherd game"),
        ("Call Subroutine(DoSkillBar);", 1, "skillbar callers"),
    )
    for needle, expected, label in checks:
        expect_count(patched, needle, expected, label)

    if patched == source:
        raise AssertionError("patch produced no changes")
    with SOURCE.open("w", encoding="utf-8", newline="") as source_file:
        source_file.write(patched)
    print("OK: patch107_minigames.py applied")


if __name__ == "__main__":
    main()
