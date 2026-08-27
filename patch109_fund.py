# -*- coding: utf-8 -*-
"""서버 공동 국도 부흥 기금을 ROUTE66_LIFE_EN.ow에 한 번만 적용한다."""

from pathlib import Path


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")


def block(newline, *lines):
    """현재 소스의 줄바꿈 형식으로 여러 줄 문자열을 만든다."""
    return newline.join(lines)


def sub(text, old, new, count, label):
    """치환 전 앵커 수를 검증한 뒤 정확히 지정된 횟수만 치환한다."""
    actual = text.count(old)
    if actual != count:
        raise AssertionError(
            f"{label}: expected {count} occurrences, found {actual}"
        )
    return text.replace(old, new)


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


def insert_into_rule(text, title, anchor, insertion, label):
    """고유한 규칙 안의 한 앵커에만 새 동작을 삽입한다."""
    start, end = rule_span(text, title, label)
    rule_text = text[start:end]
    actual = rule_text.count(anchor)
    if actual != 1:
        raise AssertionError(
            f"{label}: expected one scoped anchor, found {actual}"
        )
    rule_text = rule_text.replace(anchor, insertion + anchor)
    return text[:start] + rule_text + text[end:]


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

    patched = sub(
        patched,
        "\t\t57: ContractKind",
        block(
            newline,
            "\t\t57: ContractKind",
            "\t\t58: Fund",
            "\t\t59: FundTier",
        ),
        1,
        "global fund variables",
    )

    old_station_menu = (
        "Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 5, 4, 1, 1)"
    )
    new_station_menu = (
        "Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 6, 4, 1, 1)"
    )
    patched = sub(
        patched,
        old_station_menu,
        new_station_menu,
        3,
        "station menu count",
    )

    patched = sub(
        patched,
        'Custom String("새 출발의 기차 — 환생"), Custom String("-")',
        'Custom String("새 출발의 기차 — 환생"), Custom String("부흥 기금 기부 $1,000")',
        1,
        "fund menu label",
    )

    patched = sub(
        patched,
        block(
            newline,
            "\t\t\tElse;",
            "\t\t\t\tIf(Event Player.Rebuild < 5);",
        ),
        block(
            newline,
            "\t\t\tElse If(Event Player.MenuIdx == 4);",
            "\t\t\t\tIf(Event Player.Rebuild < 5);",
        ),
        1,
        "rebirth branch index",
    )

    zone_11_close = block(
        newline,
        "\t\t\t\tEnd;",
        "\t\t\tEnd;",
        "\t\tElse If(Event Player.Zone == 12);",
    )
    donation_branch = block(
        newline,
        "\t\t\t\tEnd;",
        "\t\t\tElse;",
        "\t\t\t\tIf(Event Player.Money < 1000);",
        ' \t\t\t\t\tSmall Message(Event Player, Custom String("돈이 부족합니다 ($1000 필요)"));'.lstrip(" "),
        "\t\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
        "\t\t\t\tElse;",
        "\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 1000);",
        "\t\t\t\t\tModify Global Variable(Fund, Add, 1000);",
        "\t\t\t\t\tSet Player Variable(Event Player, Amt, Global Variable(Fund));",
        "\t\t\t\t\tSet Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));",
        ' \t\t\t\t\tBig Message(All Players(All Teams), Custom String("{0} — 부흥 기금에 $1,000 (기금 $ {1})", Event Player, Event Player.Amt));'.lstrip(" "),
        "\t\t\t\t\tPlay Effect(All Players(All Teams), Buff Impact Sound, Color(Yellow), Position Of(Event Player), 90);",
        "\t\t\t\tEnd;",
        "\t\t\tEnd;",
        "\t\tElse If(Event Player.Zone == 12);",
    )
    patched = sub(
        patched,
        zone_11_close,
        donation_branch,
        1,
        "station donation branch",
    )

    rest_position = (
        "Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 0), "
        "Value In Array(Global Variable(LocPos), 11)), 0.5))"
    )
    fund_rules = block(
        newline,
        'rule("[기금 01] 부흥의 불")',
        "{",
        "\tevent",
        "\t{",
        "\t\tOngoing - Global;",
        "\t}",
        "",
        "\tconditions",
        "\t{",
        "\t\tGlobal Variable(Ready) == 1;",
        "\t\tGlobal Variable(FundTier) <= 2;",
        "\t\tGlobal Variable(Fund) >= Value In Array(Array(60000, 180000, 400000), Global Variable(FundTier));",
        "\t}",
        "",
        "\tactions",
        "\t{",
        "\t\tModify Global Variable(FundTier, Add, 1);",
        "\t\tIf(Global Variable(FundTier) == 1);",
        f"\t\t\tCreate Effect(All Players(All Teams), Sphere, Color(Orange), Add({rest_position}, Vector(0, 0.5, 0)), 0.8, None);",
        f"\t\t\tCreate Effect(All Players(All Teams), Light Shaft, Color(Orange), {rest_position}, 1.4, None);",
        f'\t\t\tCreate In-World Text(All Players(All Teams), Custom String("길손의 쉼터"), Add({rest_position}, Vector(0, 2.4, 0)), 1.3, Do Not Clip, Visible To and Position, Color(Orange), Default Visibility);',
        ' \t\t\tBig Message(All Players(All Teams), Custom String("부흥 기금 1단계!! 길손의 쉼터가 세워졌다 — 길목의 모닥불에서 몸을 데워라"));'.lstrip(" "),
        "\t\tElse If(Global Variable(FundTier) == 2);",
        ' \t\t\tBig Message(All Players(All Teams), Custom String("부흥 기금 2단계!! 역마차 급행로 개통 — 배달·금괴 호송 보수 +15%"));'.lstrip(" "),
        "\t\tElse;",
        ' \t\t\tBig Message(All Players(All Teams), Custom String("부흥 기금 3단계!! 국도 대축제 — 오늘의 직업 1.75배 · 밤마다 불꽃놀이 · 아침마다 명성 +1"));'.lstrip(" "),
        "\t\tEnd;",
        f"\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Orange), {rest_position}, 8);",
        f"\t\tPlay Effect(All Players(All Teams), Buff Explosion Sound, Color(Orange), {rest_position}, 250);",
        "\t\tWait(0.5, Ignore Condition);",
        "\t}",
        "}",
        "",
        'rule("[기금 02] 모닥불 곁")',
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
        "\t\tGlobal Variable(FundTier) >= 1;",
        "\t\tIs Alive(Event Player) == True;",
        f"\t\tDistance Between(Position Of(Event Player), {rest_position}) < 8;",
        "\t}",
        "",
        "\tactions",
        "\t{",
        "\t\tWait(10, Ignore Condition);",
        f"\t\tIf(And(Distance Between(Position Of(Event Player), {rest_position}) < 8, Is Alive(Event Player)));",
        "\t\t\tSet Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 1)));",
        "\t\t\tSet Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 1.5)));",
        "\t\t\tPlay Effect(Event Player, Good Pickup Effect, Color(Orange), Position Of(Event Player), 1);",
        "\t\tEnd;",
        f"\t\tLoop If(Distance Between(Position Of(Event Player), {rest_position}) < 8);",
        "\t}",
        "}",
        "",
        'rule("[기금 03] 축제의 밤")',
        "{",
        "\tevent",
        "\t{",
        "\t\tOngoing - Global;",
        "\t}",
        "",
        "\tconditions",
        "\t{",
        "\t\tGlobal Variable(FundTier) >= 3;",
        "\t\tGlobal Variable(IsNight) == 1;",
        "\t}",
        "",
        "\tactions",
        "\t{",
        "\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 0), Vector(Random Real(-10, 10), 14, Random Real(-10, 10))), 7);",
        "\t\tPlay Effect(All Players(All Teams), Explosion Sound, Color(Yellow), Value In Array(Global Variable(LocPos), 0), 200);",
        "\t\tWait(1.2, Ignore Condition);",
        "\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 0), Vector(Random Real(-10, 10), 14, Random Real(-10, 10))), 7);",
        "\t\tPlay Effect(All Players(All Teams), Explosion Sound, Color(Yellow), Value In Array(Global Variable(LocPos), 0), 200);",
        "\t\tWait(1.2, Ignore Condition);",
        "\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 0), Vector(Random Real(-10, 10), 14, Random Real(-10, 10))), 7);",
        "\t\tPlay Effect(All Players(All Teams), Explosion Sound, Color(Yellow), Value In Array(Global Variable(LocPos), 0), 200);",
        "\t\tWait(1.2, Ignore Condition);",
        ' \t\tBig Message(All Players(All Teams), Custom String("국도 대축제의 밤 — 불꽃이 66번 국도를 밝힌다"));'.lstrip(" "),
        "\t\tWait Until(Global Variable(IsNight) == 0, 99999);",
        "\t}",
        "}",
    )
    prison_anchor = 'rule("[감옥 01] 만기 출소")'
    patched = sub(
        patched,
        prison_anchor,
        fund_rules + newline + newline + prison_anchor,
        1,
        "fund rules insertion",
    )

    delivery_anchor = (
        "\t\tModify Player Variable(Event Player, Money, Add, "
        "Event Player.RunPay);"
    )
    delivery_boost = block(
        newline,
        "\t\tIf(Global Variable(FundTier) >= 2);",
        "\t\t\tSet Player Variable(Event Player, RunPay, Round To Integer(Multiply(Event Player.RunPay, 1.15), To Nearest));",
        "\t\tEnd;",
    ) + newline
    patched = insert_into_rule(
        patched,
        "[파발 01] 배달 도착 — 자동 정산",
        delivery_anchor,
        delivery_boost,
        "delivery fund boost",
    )

    escort_anchor = (
        "\t\t\t\t\tSet Player Variable(Event Player, EscortPay, Round To Integer("
        "Add(40, Multiply(Distance Between(Value In Array(Global Variable(LocPos), "
        "11), Event Player.EscortPos), 2.5)), To Nearest));"
    )
    escort_boost = block(
        newline,
        escort_anchor,
        "\t\t\t\t\tIf(Global Variable(FundTier) >= 2);",
        "\t\t\t\t\t\tSet Player Variable(Event Player, EscortPay, Round To Integer(Multiply(Event Player.EscortPay, 1.15), To Nearest));",
        "\t\t\t\t\tEnd;",
    )
    patched = sub(
        patched,
        escort_anchor,
        escort_boost,
        1,
        "escort fund boost",
    )

    today_job_lines = (
        (
            "Set Player Variable(Event Player, MineGain, Round To Integer(Multiply("
            "Player Variable(Event Player, MineGain), 1.5), To Nearest));",
            "Set Player Variable(Event Player, MineGain, Round To Integer(Multiply("
            "Player Variable(Event Player, MineGain), Global Variable(FundTier) >= 3 "
            "? 1.75 : 1.5), To Nearest));",
            2,
            "miner today-job bonus",
        ),
        (
            "Set Player Variable(Attacker, Yield, Round To Integer(Multiply("
            "Player Variable(Attacker, Yield), 1.5), To Nearest));",
            "Set Player Variable(Attacker, Yield, Round To Integer(Multiply("
            "Player Variable(Attacker, Yield), Global Variable(FundTier) >= 3 "
            "? 1.75 : 1.5), To Nearest));",
            1,
            "hunter today-job bonus",
        ),
        (
            "Set Player Variable(Event Player, PlanPay, Round To Integer(Multiply("
            "Player Variable(Event Player, PlanPay), 1.5), To Nearest));",
            "Set Player Variable(Event Player, PlanPay, Round To Integer(Multiply("
            "Player Variable(Event Player, PlanPay), Global Variable(FundTier) >= 3 "
            "? 1.75 : 1.5), To Nearest));",
            2,
            "outlaw today-job bonus",
        ),
        (
            "Set Player Variable(Event Player, RunPay, Round To Integer(Multiply("
            "Player Variable(Event Player, RunPay), 1.5), To Nearest));",
            "Set Player Variable(Event Player, RunPay, Round To Integer(Multiply("
            "Player Variable(Event Player, RunPay), Global Variable(FundTier) >= 3 "
            "? 1.75 : 1.5), To Nearest));",
            2,
            "courier today-job bonus",
        ),
    )
    for old, new, count, label in today_job_lines:
        patched = sub(patched, old, new, count, label)

    morning_anchor = (
        "\t\tIf(And(Event Player.Rebirth >= 1, "
        "Event Player.Earned > Event Player.DayStart));"
    )
    morning_fame = block(
        newline,
        "\t\tIf(Global Variable(FundTier) >= 3);",
        "\t\t\tSet Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 1)));",
        "\t\tEnd;",
    ) + newline
    patched = sub(
        patched,
        morning_anchor,
        morning_fame + morning_anchor,
        1,
        "festival morning fame",
    )

    old_hud = (
        'Custom String("소지금   $ {0}   예금 $ {1}", Local Player.Money, '
        "Local Player.Deposit), Null,"
    )
    new_hud = (
        'Custom String("소지금   $ {0}   예금 $ {1}", Local Player.Money, '
        'Local Player.Deposit), Custom String("부흥 기금 $ {0}   ({1}/3)", '
        "Global Variable(Fund), Global Variable(FundTier)),"
    )
    patched = sub(patched, old_hud, new_hud, 1, "fund HUD line")

    sign_line = (
        "새 출발의 기차 — 재건을 마친 자는 전 재산을 두고 다시 태어난다"
        "\\r\\n"
    )
    patched = sub(
        patched,
        sign_line,
        sign_line + "부흥 기금 — $1000씩 모아 쉼터·급행로·대축제를 연다\\r\\n",
        1,
        "station fund sign",
    )

    checks = (
        ("\t\t58: Fund", 1, "Fund global"),
        ("\t\t59: FundTier", 1, "FundTier global"),
        ("부흥 기금 기부 $1,000", 1, "fund menu label"),
        ("부흥 기금에 $1,000", 1, "donation callout"),
        ('rule("[기금 01] 부흥의 불")', 1, "fund tier rule"),
        ('rule("[기금 02] 모닥불 곁")', 1, "rest stop rule"),
        ('rule("[기금 03] 축제의 밤")', 1, "festival rule"),
        ("길손의 쉼터", 2, "rest stop text"),
        ("? 1.75 : 1.5), To Nearest));", 7, "festival job bonus"),
        ("Multiply(Event Player.RunPay, 1.15)", 2, "delivery boost"),  # cow adv 1.15 pre-exists
        ("Multiply(Event Player.EscortPay, 1.15)", 1, "escort boost"),
        ("부흥 기금 $ {0}", 1, "fund HUD"),
        (new_station_menu, 3, "six-item station menu"),
        (old_station_menu, 0, "old station menu"),
    )
    for needle, expected, label in checks:
        expect_count(patched, needle, expected, label)

    if patched == source:
        raise AssertionError("patch produced no changes")
    with SOURCE.open("w", encoding="utf-8", newline="") as source_file:
        source_file.write(patched)

    print("OK: patch109_fund.py applied")
    print("OK: required counts verified")
    print("OK: save rules unchanged")


if __name__ == "__main__":
    main()
