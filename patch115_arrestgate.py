# -*- coding: utf-8 -*-
"""체포 권한을 현상금 사냥꾼에게 제한하고 보안관 초소 전직 메뉴를 추가한다."""

from pathlib import Path


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")


def block(*lines):
    return "\n".join(lines) + "\n"


def matching_paren(text, open_pos):
    depth = 0
    quoted = False
    escaped = False
    for pos in range(open_pos, len(text)):
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
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return pos
    raise AssertionError("unclosed parenthesis in tutorial body")


def split_args(body):
    args = []
    start = 0
    depth = 0
    quoted = False
    escaped = False
    for pos, char in enumerate(body):
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
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == "," and depth == 0:
            args.append(body[start:pos].strip())
            start = pos + 1
    args.append(body[start:].strip())
    return args


def custom_args(expression):
    expression = expression.strip()
    prefix = "Custom String("
    if not expression.startswith(prefix):
        return None
    open_pos = len("Custom String")
    close_pos = matching_paren(expression, open_pos)
    if close_pos != len(expression) - 1:
        return None
    return split_args(expression[open_pos + 1:close_pos])


def quoted_content(argument):
    argument = argument.strip()
    if len(argument) >= 2 and argument[0] == '"' and argument[-1] == '"':
        return argument[1:-1]
    return None


def custom_units(content):
    return len(content.replace("\\r\\n", "xx"))


def split_custom_content(content, limit=120):
    tokens = []
    pos = 0
    while pos < len(content):
        if content.startswith("\\r\\n", pos):
            tokens.append(("\\r\\n", 2))
            pos += 4
        else:
            tokens.append((content[pos], 1))
            pos += 1

    chunks = []
    while tokens:
        width = 0
        take = 0
        while take < len(tokens) and width + tokens[take][1] <= limit:
            width += tokens[take][1]
            take += 1
        if take == len(tokens):
            chunks.append("".join(token for token, _ in tokens))
            break
        assert take > 0, "tutorial split made no progress"
        preferred = 0
        preferred_width = 0
        running_width = 0
        for idx in range(take):
            running_width += tokens[idx][1]
            if tokens[idx][0].isspace() or tokens[idx][0] == "\\r\\n":
                preferred = idx + 1
                preferred_width = running_width
        if preferred and preferred_width >= limit // 2:
            take = preferred
        chunks.append("".join(token for token, _ in tokens[:take]))
        tokens = tokens[take:]
    return chunks


def flatten_concat(expression):
    args = custom_args(expression)
    if args and len(args) == 3 and quoted_content(args[0]) == "{0}{1}":
        return flatten_concat(args[1]) + flatten_concat(args[2])
    return [expression.strip()]


def balanced_concat(expressions):
    assert expressions, "empty tutorial concatenation"
    if len(expressions) == 1:
        return expressions[0]
    middle = (len(expressions) + 1) // 2
    left = balanced_concat(expressions[:middle])
    right = balanced_concat(expressions[middle:])
    return 'Custom String("{0}{1}", ' + left + ", " + right + ")"


def tutorial_length_guard(text, marker):
    prefix = "Custom String("
    calls = []
    search_pos = 0
    while True:
        start = text.find(prefix, search_pos)
        if start < 0:
            break
        open_pos = start + len("Custom String")
        end = matching_paren(text, open_pos)
        calls.append((start, end + 1))
        search_pos = start + 1

    direct = []
    for start, end in calls:
        args = custom_args(text[start:end])
        first = quoted_content(args[0]) if args else None
        if first is not None and marker in first:
            direct.append((start, end))
    assert len(direct) == 1, (
        "tutorial marker call count mismatch: expected 1, got " + str(len(direct))
    )

    root_start, root_end = direct[0]
    while True:
        parents = []
        for start, end in calls:
            if start < root_start and root_end < end:
                args = custom_args(text[start:end])
                if args and len(args) == 3 and quoted_content(args[0]) == "{0}{1}":
                    parents.append((end - start, start, end))
        if not parents:
            break
        _, root_start, root_end = min(parents)

    atoms = flatten_concat(text[root_start:root_end])
    guarded = []
    for atom in atoms:
        args = custom_args(atom)
        content = quoted_content(args[0]) if args and len(args) == 1 else None
        if content is not None and custom_units(content) > 120:
            guarded.extend(
                'Custom String("' + chunk + '")'
                for chunk in split_custom_content(content)
            )
        else:
            guarded.append(atom)

    replacement = balanced_concat(guarded)
    verify_pos = 0
    while True:
        start = replacement.find(prefix, verify_pos)
        if start < 0:
            break
        end = matching_paren(replacement, start + len("Custom String")) + 1
        args = custom_args(replacement[start:end])
        first = quoted_content(args[0]) if args else None
        if first is not None:
            assert custom_units(first) <= 120, "tutorial literal exceeds 120 chars"
        verify_pos = start + 1
    return text[:root_start] + replacement + text[root_end:]


data = SOURCE.read_text(encoding="utf-8")


def sub(old, new, count=1, label="substitution"):
    global data
    actual = data.count(old)
    assert actual == count, (
        label + " count mismatch: expected " + str(count) + ", got " + str(actual)
    )
    data = data.replace(old, new)


sub(
    block(
        "\t\tIf(Player Variable(Event Player.Target, Bounty) > 0);",
        "\t\t\tSet Player Variable(Event Player, JobArg, 3);",
        "\t\t\tCall Subroutine(BecomeJob);",
    ),
    block(
        "\t\tIf(Player Variable(Event Player.Target, Bounty) >= 300);",
        "\t\t\tIf(Event Player.Job != 3);",
        "\t\t\t\tSet Player Variable(Event Player, Busy, 0);",
        "\t\t\t\tSmall Message(Event Player, Custom String(\"체포는 현상금 사냥꾼의 일이다 — 보안관 초소에서 전직할 수 있다\"));",
        "\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
        "\t\t\t\tAbort;",
        "\t\t\tEnd;",
    ),
    label="arrest setup gate",
)

sub(
    block(
        "\t\tChase Player Variable Over Time(Event Player, WorkProg, 100, And(And(Event Player.Job == 3, Value In Array(Event Player.Adv, Event Player.Job) == 1), Player Variable(Event Player.Target, Bounty) > 0) ? 2 : 3, Destination and Duration);",
    ),
    block(
        "\t\tSet Player Variable(Event Player, Amt, 3);",
        "\t\tIf(Player Variable(Event Player.Target, Bounty) >= 300);",
        "\t\t\tSet Player Variable(Event Player, Amt, Value In Array(Event Player.Adv, 3) == 1 ? 2.5 : 4);",
        "\t\tEnd;",
        "\t\tChase Player Variable Over Time(Event Player, WorkProg, 100, Event Player.Amt, Destination and Duration);",
    ),
    label="arrest channel duration",
)

sub(
    block(
        "\t\tWait Until(Or(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 3.5);",
    ),
    block(
        "\t\tWait Until(Or(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12, Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))), Event Player.WorkProg >= 99), 4.5);",
    ),
    label="arrest wait timeout",
)

sub(
    "Else If(Player Variable(Event Player.Target, Bounty) > 0);",
    "Else If(Player Variable(Event Player.Target, Bounty) >= 300);",
    label="arrest result threshold",
)

sub(
    "Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 6, 4, 1, 1)",
    "Array(1, 1, 3, 4, 2, 3, 5, 2, 5, 6, 6, 5, 6, 4, 1, 1)",
    count=3,
    label="sheriff menu counts",
)

sub(
    'Custom String("재산세 납부 — 징수 기간만"), Custom String("-")',
    'Custom String("재산세 납부 — 징수 기간만"), Custom String("전직: 현상금 사냥꾼")',
    label="sheriff menu label",
)

sub(
    block(
        "\t\t\tElse;",
        "\t\t\t\tIf(Global Variable(TaxOn) == 0);",
    ),
    block(
        "\t\t\tElse If(Event Player.MenuIdx == 3);",
        "\t\t\t\tIf(Global Variable(TaxOn) == 0);",
    ),
    label="sheriff menu tax branch",
)

sub(
    block(
        "\t\t\t\tEnd;",
        "\t\t\tEnd;",
        "\t\tElse If(Event Player.Zone == 8);",
    ),
    block(
        "\t\t\t\tEnd;",
        "\t\t\tElse;",
        "\t\t\t\tIf(Event Player.Job == 3);",
        "\t\t\t\t\tSmall Message(Event Player, Custom String(\"이미 현상금 사냥꾼이다\"));",
        "\t\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
        "\t\t\t\tElse;",
        "\t\t\t\t\tSet Player Variable(Event Player, JobArg, 3);",
        "\t\t\t\t\tCall Subroutine(BecomeJob);",
        "\t\t\t\t\tBig Message(Event Player, Custom String(\"배지를 받았다 — 현상금 사냥꾼. 전단이 붙은 자($300+)를 산 채로 잡아라\"));",
        "\t\t\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 80);",
        "\t\t\t\tEnd;",
        "\t\t\tEnd;",
        "\t\tElse If(Event Player.Zone == 8);",
    ),
    label="sheriff bounty hunter branch",
)

sign_head = "체포 시도 — 허기"
assert data.count(sign_head) == 1, "sheriff sign head count mismatch"
sign_start = data.index(sign_head)
sign_end = data.find("\\r\\n", sign_start)
assert sign_end >= 0, "sheriff sign line terminator missing"
sign_anchor = data[sign_start:sign_end + 4]
sub(
    sign_anchor,
    sign_anchor + "배지 — 체포는 현상금 사냥꾼의 일, 전직은 여기서\\r\\n",
    label="sheriff signboard",
)

sub(
    "현상금이 붙은 자는 누구든 잡을 수 있다.",
    "전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 전직은 보안관 초소에서.",
    label="bounty hunter tutorial",
)

data = tutorial_length_guard(
    data,
    "전단이 붙은 자($300+)는 현상금 사냥꾼만 잡는다 — 전직은 보안관 초소에서.",
)


def expect(needle, count, label):
    actual = data.count(needle)
    assert actual == count, (
        label + " verification mismatch: expected " + str(count) + ", got " + str(actual)
    )


expect("Bounty) >= 300", 3, "bounty threshold")
expect("체포는 현상금 사냥꾼의 일이다", 1, "hunter-only message")
expect("전직: 현상금 사냥꾼", 1, "hunter menu label")
expect("배지를 받았다", 1, "badge message")
expect("? 2.5 : 4);", 1, "hunter duration")
expect("? 2 : 3, Destination and Duration", 0, "old duration")
expect("Set Player Variable(Event Player, JobArg, 3);", 1, "job conversion")
expect("전단이 붙은 자($300+)", 2, "wanted poster copy")
expect(
    "Array(1, 1, 3, 4, 2, 3, 5, 2, 5, 6, 6, 5, 6, 4, 1, 1)",
    3,
    "sheriff menu counts",
)
expect("배지 — 체포는", 1, "sheriff badge sign")

SOURCE.write_text(data, encoding="utf-8")
print("patch115_arrestgate.py: OK")
