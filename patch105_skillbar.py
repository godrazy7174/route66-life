# -*- coding: utf-8 -*-
"""세 가지 반응형 QTE를 공용 왕복 스킬바 판정으로 교체한다."""

from pathlib import Path


TARGET = Path("ROUTE66_LIFE_EN.ow")


def sub(text, old, new, cnt=1, label="replacement"):
    """정확한 출현 횟수를 확인한 뒤 문자열을 교체한다."""
    actual = text.count(old)
    assert actual == cnt, f"{label}: expected {cnt}, found {actual}"
    return text.replace(old, new)


def block(*lines):
    """워크샵 코드 블록을 한 번에 조립한다."""
    return "\n".join(lines) + "\n"


def rule_span(text, title):
    """규칙의 구조용 중괄호만 세어 [시작, 끝) 범위를 돌려준다."""
    header = f'rule("{title}")'
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == header]
    assert len(hits) == 1, f"rule {title}: expected 1, found {len(hits)}"

    start_line = hits[0]
    open_line = None
    for i in range(start_line + 1, len(lines)):
        if lines[i].strip() == "{":
            open_line = i
            break
    assert open_line is not None, f"rule {title}: opening brace not found"

    depth = 0
    close_line = None
    for i in range(open_line, len(lines)):
        token = lines[i].strip()
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1
            if depth == 0:
                close_line = i
                break
    assert close_line is not None, f"rule {title}: closing brace not found"

    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets[start_line], offsets[close_line + 1]


def replace_rule(text, title, transform):
    """지정 규칙 안에서만 변환한 뒤 규칙 전체를 정확히 한 번 교체한다."""
    start, end = rule_span(text, title)
    old = text[start:end]
    new = transform(old)
    assert new != old, f"rule {title}: transform made no change"
    return sub(text, old, new, 1, f"rule {title}")


def replace_actions(rule_text, new_body, label):
    """규칙의 actions 본문만 구조적으로 찾아 교체한다."""
    lines = rule_text.splitlines(keepends=True)
    action_lines = [i for i, line in enumerate(lines) if line.strip() == "actions"]
    assert len(action_lines) == 1, (
        f"{label} actions: expected 1, found {len(action_lines)}"
    )
    action_line = action_lines[0]
    open_line = action_line + 1
    assert open_line < len(lines) and lines[open_line].strip() == "{", (
        f"{label} actions: opening brace not found"
    )

    depth = 0
    close_line = None
    for i in range(open_line, len(lines)):
        token = lines[i].strip()
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1
            if depth == 0:
                close_line = i
                break
    assert close_line is not None, f"{label} actions: closing brace not found"

    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    body_start = offsets[open_line + 1]
    body_end = offsets[close_line]
    return rule_text[:body_start] + new_body + rule_text[body_end:]


def make_bar_frames():
    """0..16 커서 위치에 대응하는 17개 고정 문자열을 만든다."""
    frames = []
    for cursor in range(17):
        cells = []
        for index in range(17):
            if index == cursor:
                cells.append("◆")
            elif 6 <= index <= 10:
                cells.append("■")
            else:
                cells.append("□")
        frames.append("".join(cells))
    assert len(frames) == 17
    assert frames[0] == "◆□□□□□■■■■■□□□□□□"
    assert frames[8] == "□□□□□□■■◆■■□□□□□□"
    return frames


def half_sweep(destination):
    """한 번의 반주기 추적 및 입력 판정을 조립한다."""
    return [
        "\t\tIf(Event Player.Roll == -1);",
        (
            "\t\t\tChase Player Variable Over Time(Event Player, WorkProg, "
            f"{destination}, 0.9, Destination and Duration);"
        ),
        "\t\t\tWait Until(Is Button Held(Event Player, Button(Reload)), 0.9);",
        "\t\t\tIf(Is Button Held(Event Player, Button(Reload)));",
        "\t\t\t\tStop Chasing Player Variable(Event Player, WorkProg);",
        "\t\t\t\tSet Player Variable(Event Player, Roll, 0);",
        (
            "\t\t\t\tIf(And(Round To Integer(Event Player.WorkProg, To Nearest) >= 6, "
            "Round To Integer(Event Player.WorkProg, To Nearest) <= 10));"
        ),
        "\t\t\t\t\tSet Player Variable(Event Player, Roll, 1);",
        "\t\t\t\tEnd;",
        "\t\t\tEnd;",
        "\t\tEnd;",
    ]


def make_skill_rule():
    frames = make_bar_frames()
    frame_array = ", ".join(f'Custom String("{frame}")' for frame in frames)
    hud = (
        "\t\tCreate HUD Text(Event Player, Null, Value In Array(Array("
        + frame_array
        + "), Min(16, Max(0, Round To Integer(Event Player.WorkProg, To Nearest)))), "
        + 'Custom String("◆가 ■ 구간에 올 때 [{0}]", Input Binding String(Button(Reload))), '
        + "Top, 1, Color(White), Color(Orange), Color(Gray), "
        + "Visible To Sort Order String and Color, Default Visibility);"
    )

    actions = [
        "\t\tSet Player Variable(Event Player, Roll, -1);",
        "\t\tSet Player Variable(Event Player, WorkProg, 0);",
        "\t\tDestroy HUD Text(Event Player.KeyHud);",
        hud,
        "\t\tSet Player Variable(Event Player, KeyHud, Last Text ID());",
    ]
    for destination in (16, 0, 16, 0):
        actions.extend(half_sweep(destination))
    actions.extend(
        [
            "\t\tStop Chasing Player Variable(Event Player, WorkProg);",
            "\t\tDestroy HUD Text(Event Player.KeyHud);",
            "\t\tSet Player Variable(Event Player, WorkProg, 0);",
            "\t\tIf(Event Player.Roll == -1);",
            "\t\t\tSet Player Variable(Event Player, Roll, 0);",
            "\t\tEnd;",
        ]
    )

    return block(
        'rule("[스킬바 01] DoSkillBar")',
        "{",
        "\tevent",
        "\t{",
        "\t\tSubroutine;",
        "\t\tDoSkillBar;",
        "\t}",
        "",
        "\tactions",
        "\t{",
        *actions,
        "\t}",
        "}",
    ).rstrip("\n")


def rewire_mining(rule_text):
    start_marker = "\t\tWait(Random Real(0.3, 0.8), Ignore Condition);\n"
    stop_marker = "\t\tIf(Modulo(Event Player.MineCount, 10) == 0);"
    assert rule_text.count(start_marker) == 1, "mining QTE start: expected 1"
    assert rule_text.count(stop_marker) == 1, "mining QTE stop: expected 1"
    start = rule_text.index(start_marker)
    stop = rule_text.index(stop_marker, start)
    assert start < stop, "mining QTE: invalid scoped span"
    old_span = rule_text[start:stop]
    assert "광맥이 울렸다" in old_span, "mining QTE: flavor marker missing"
    assert "If(Random Integer(1, 100) > 30);" in old_span, (
        "mining QTE: old chance marker missing"
    )

    new_span = block(
        "\t\tIf(Random Integer(1, 100) <= 30);",
        '\t\t\tSmall Message(Event Player, Custom String("광맥이 울렸다 — 결을 노려라!"));',
        "\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Orange), Position Of(Event Player), 45);",
        "\t\t\tCall Subroutine(DoSkillBar);",
        "\t\t\tIf(Event Player.Roll == 1);",
        "\t\t\t\tSet Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 2));",
        '\t\t\t\tSmall Message(Event Player, Custom String("정타! 원석 +2 (보유 {0})", Value In Array(Event Player.Inv, 2)));',
        "\t\t\t\tPlay Effect(Event Player, Ring Explosion, Color(Orange), Position Of(Event Player), 1.2);",
        "\t\t\tElse;",
        '\t\t\t\tSmall Message(Event Player, Custom String("빗나갔다 — 곡괭이가 헛돌았다"));',
        "\t\t\tEnd;",
        "\t\tEnd;",
    )
    return rule_text[:start] + new_span + rule_text[stop:]


def rewire_job_event(rule_text, label, wait_range, active_var, prompt, success,
                     miss, effect_color):
    init_line = "\t\tEvent Player.Init == 1;\n"
    rule_text = sub(
        rule_text,
        init_line,
        init_line + "\t\tEvent Player.Busy == 0;\n",
        1,
        f"{label} Init condition",
    )
    new_actions = block(
        f"\t\tWait(Random Real({wait_range}), Ignore Condition);",
        (
            f"\t\tIf(And(And(Event Player.{active_var} == 1, "
            "Event Player.Busy == 0), Is Alive(Event Player)));"
        ),
        "\t\t\tSet Player Variable(Event Player, Busy, 1);",
        f'\t\t\tSmall Message(Event Player, Custom String("{prompt}"));',
        (
            "\t\t\tPlay Effect(Event Player, Buff Impact Sound, "
            f"Color({effect_color}), Position Of(Event Player), 45);"
        ),
        "\t\t\tCall Subroutine(DoSkillBar);",
        "\t\t\tIf(Event Player.Roll == 1);",
        "\t\t\t\tModify Player Variable(Event Player, Money, Add, 12);",
        "\t\t\t\tModify Player Variable(Event Player, Earned, Add, 12);",
        f'\t\t\t\tSmall Message(Event Player, Custom String("{success}"));',
        (
            "\t\t\t\tPlay Effect(Event Player, Ring Explosion, "
            f"Color({effect_color}), Position Of(Event Player), 1);"
        ),
        "\t\t\tElse;",
        f'\t\t\t\tSmall Message(Event Player, Custom String("{miss}"));',
        "\t\t\tEnd;",
        "\t\t\tSet Player Variable(Event Player, Busy, 0);",
        "\t\tEnd;",
        "\t\tWait(2, Ignore Condition);",
        f"\t\tLoop If(Event Player.{active_var} == 1);",
    )
    return replace_actions(rule_text, new_actions, label)


def verify(text):
    checks = {
        "subroutine declaration": ("\t2: DoSkillBar", 1),
        "skillbar rule": ('rule("[스킬바 01] DoSkillBar")', 1),
        "skillbar calls": ("Call Subroutine(DoSkillBar);", 3),
        "skillbar prompt": ("◆가 ■ 구간에 올 때", 1),
        "miss messages": ("빗나갔다", 3),
        "new mining chance": ("If(Random Integer(1, 100) <= 30);", 1),
        "old mining chance": ("If(Random Integer(1, 100) > 30);", 0),
        "old early message": ("손이 앞섰다", 0),
        "forward half-sweeps": (
            "Chase Player Variable Over Time(Event Player, WorkProg, 16, 0.9",
            2,
        ),
    }
    for label, (needle, expected) in checks.items():
        actual = text.count(needle)
        assert actual == expected, f"verify {label}: expected {expected}, found {actual}"


def main():
    raw = TARGET.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8")
    if newline == "\r\n":
        text = text.replace("\r\n", "\n")

    text = sub(
        text,
        "\t1: SetupPlayer",
        "\t1: SetupPlayer\n\t2: DoSkillBar",
        1,
        "subroutine declaration",
    )

    prison_anchor = 'rule("[감옥 01] 만기 출소")'
    text = sub(
        text,
        prison_anchor,
        make_skill_rule() + "\n\n" + prison_anchor,
        1,
        "prison anchor",
    )

    text = replace_rule(text, "[직업 01] DoMine", rewire_mining)
    text = replace_rule(
        text,
        "[파발 02] 흔들리는 화물",
        lambda rule_text: rewire_job_event(
            rule_text,
            "delivery event",
            "7, 14",
            "HasParcel",
            "화물 끈이 풀린다 — 잡아라!",
            "끈을 다시 묶었다 +$12",
            "빗나갔다 — 끈이 덜렁거린다",
            "Yellow",
        ),
    )
    text = replace_rule(
        text,
        "[목동 02] 날뛰는 소",
        lambda rule_text: rewire_job_event(
            rule_text,
            "cattle event",
            "6, 12",
            "CowOn",
            "소가 날뛴다 — 고삐를 잡아라!",
            "고삐를 잡아챘다 +$12",
            "빗나갔다 — 소가 콧김을 뿜는다",
            "White",
        ),
    )

    verify(text)
    output = text if newline == "\n" else text.replace("\n", "\r\n")
    TARGET.write_bytes(output.encode("utf-8"))
    print("OK: patch105_skillbar applied")


if __name__ == "__main__":
    main()
