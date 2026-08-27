# -*- coding: utf-8 -*-
"""Apply mastery milestones and the server-wide daily contract once.

Player variables are full, so this patch deliberately reuses Giant for real
players. Team 2 beast dummies keep using Giant as their size tier; real players
pack it as ``MasteryPaid * 10 + ContractProg``. MasteryPaid is the number of
milestones already rewarded, while ContractProg is 0..8 and 9 is the completed
sentinel. The daily reset clears only ContractProg.
"""

from pathlib import Path


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")

with SOURCE.open("r", encoding="utf-8", newline="") as source_file:
    text = source_file.read()

newline = "\r\n" if "\r\n" in text else "\n"


def block(*lines):
    """Join source lines using the file's existing newline convention."""
    return newline.join(lines)


def sub(old, new, cnt, label):
    """Validate an anchor count, then replace exactly that many occurrences."""
    global text
    found = text.count(old)
    assert found == cnt, f"{label}: expected {cnt}, found {found}"
    text = text.replace(old, new, cnt)


def insert_into(rule_header, anchor, insertion, label):
    """Insert after a unique anchor within one uniquely named rule."""
    global text
    header_count = text.count(rule_header)
    assert header_count == 1, f"{label} header: expected 1, found {header_count}"
    rule_start = text.index(rule_header)
    next_rule = text.find(newline + 'rule("', rule_start + len(rule_header))
    rule_end = len(text) if next_rule < 0 else next_rule + len(newline)
    rule_text = text[rule_start:rule_end]
    anchor_count = rule_text.count(anchor)
    assert anchor_count == 1, f"{label} anchor: expected 1, found {anchor_count}"
    anchor_end = rule_text.index(anchor) + len(anchor)
    rule_text = rule_text[:anchor_end] + newline + insertion + rule_text[anchor_end:]
    text = text[:rule_start] + rule_text + text[rule_end:]


def insert_after_line(line_text, new_line_text, label):
    """Insert a same-indentation line after a unique full-line payload."""
    global text
    found = text.count(line_text)
    assert found == 1, f"{label}: expected 1, found {found}"
    at = text.index(line_text)
    line_start = text.rfind(newline, 0, at) + len(newline)
    indent = text[line_start:at]
    assert not indent.strip(), f"{label}: anchor is not a standalone line"
    text = text[:at + len(line_text)] + newline + indent + new_line_text + text[at + len(line_text):]


def contract_progress(depth, subject, kind, target):
    """Build one daily-contract progress hook at the requested action depth."""
    t = "\t"
    return block(
        t * depth + f"If(And(Global Variable(ContractKind) == {kind}, Modulo(Player Variable({subject}, Giant), 10) < {target}));",
        t * (depth + 1) + f"Modify Player Variable({subject}, Giant, Add, 1);",
        t * (depth + 1) + f"If(Modulo(Player Variable({subject}, Giant), 10) == {target});",
        t * (depth + 2) + f"Modify Player Variable({subject}, Giant, Add, Subtract(9, {target}));",
        t * (depth + 2) + f"Modify Player Variable({subject}, Money, Add, 150);",
        t * (depth + 2) + f"Modify Player Variable({subject}, Earned, Add, 150);",
        t * (depth + 2) + f"Set Player Variable({subject}, Fame, Min(100, Add(Player Variable({subject}, Fame), 3)));",
        t * (depth + 2) + f'Big Message({subject}, Custom String("오늘의 계약 달성! +$150 · 명성 +3"));',
        t * (depth + 2) + f"Play Effect({subject}, Buff Explosion Sound, Color(Yellow), Position Of({subject}), 120);",
        t * (depth + 1) + "Else;",
        t * (depth + 2) + f'Small Message({subject}, Custom String("오늘의 계약 — 진행 {{0}} / {{1}}", Modulo(Player Variable({subject}, Giant), 10), {target}));',
        t * (depth + 1) + "End;",
        t * depth + "End;",
    )


# One new global variable.
sub(
    "\t\t56: HuntIdx",
    block("\t\t56: HuntIdx", "\t\t57: ContractKind"),
    1,
    "global ContractKind",
)

# Draw the server-wide contract at sunrise.
sunrise_anchor = '\t\t\tBig Message(All Players(All Teams), Custom String("새 아침 — 오늘은 {0}의 날! 해당 직업 보수 1.5배", Value In Array(Array(Custom String("뜨내기"), Custom String("광부"), Custom String("사냥꾼"), Custom String("현상금 사냥꾼"), Custom String("무법자"), Custom String("파발꾼"), Custom String("목동")), Global Variable(TodayJob))));'
sub(
    sunrise_anchor,
    block(
        sunrise_anchor,
        "\t\t\tSet Global Variable(ContractKind, Random Integer(1, 4));",
        '\t\t\tBig Message(All Players(All Teams), Custom String("오늘의 계약 — {0} (달성 시 $150 · 명성 +3)", Value In Array(Array(Custom String("채굴 8회"), Custom String("야수 4마리"), Custom String("배달 3건"), Custom String("소몰이 2회")), Subtract(Global Variable(ContractKind), 1))));',
    ),
    1,
    "sunrise contract draw",
)

# Clear only the daily progress digit during morning settlement.
morning_anchor = "\t\tIf(And(Event Player.Rebirth >= 1, Event Player.Earned > Event Player.DayStart));"
sub(
    morning_anchor,
    block(
        "\t\tSet Player Variable(Event Player, Giant, Multiply(Round To Integer(Divide(Event Player.Giant, 10), Down), 10));",
        morning_anchor,
    ),
    1,
    "daily progress reset",
)

# Mining progress.
mine_anchor = "\t\tSet Player Variable(Event Player, LastMine, Total Time Elapsed());"
sub(
    mine_anchor,
    block(mine_anchor, contract_progress(2, "Event Player", 1, 8)),
    1,
    "mining contract hook",
)

# Beast-kill progress is awarded to the attacker, not the Team 2 dummy.
beast_anchor = "\t\tSet Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 1)));"
sub(
    beast_anchor,
    block(beast_anchor, contract_progress(2, "Attacker", 2, 4)),
    1,
    "beast contract hook",
)

# Delivery has a duplicate Earned/RunPay line elsewhere, so scope it to this rule.
insert_into(
    'rule("[파발 01] 배달 도착 — 자동 정산")',
    "\t\tModify Player Variable(Event Player, Earned, Add, Event Player.RunPay);",
    contract_progress(2, "Event Player", 3, 3),
    "delivery contract hook",
)

# Cattle-drive progress.
ranch_anchor = '\t\t\tBig Message(Event Player, Custom String("우리에 몰아넣었다!   +$ {0}   (잡화점 육포 재고 +6)", Event Player.RunPay));'
sub(
    ranch_anchor,
    block(ranch_anchor, contract_progress(3, "Event Player", 4, 2)),
    1,
    "ranch contract hook",
)

# Mastery pays one outstanding milestone per rule pass until the counter catches up.
milestone_total = "Add(Add(Add(Add(Add(Add(Add(Add(Value In Array(Event Player.JobXP, 1) >= 2500, Value In Array(Event Player.JobXP, 1) >= 5000), Add(Value In Array(Event Player.JobXP, 1) >= 10000, Value In Array(Event Player.JobXP, 2) >= 2500)), Add(Value In Array(Event Player.JobXP, 2) >= 5000, Value In Array(Event Player.JobXP, 2) >= 10000)), Add(Value In Array(Event Player.JobXP, 3) >= 2500, Value In Array(Event Player.JobXP, 3) >= 5000)), Add(Value In Array(Event Player.JobXP, 3) >= 10000, Value In Array(Event Player.JobXP, 4) >= 2500)), Add(Value In Array(Event Player.JobXP, 4) >= 5000, Value In Array(Event Player.JobXP, 4) >= 10000)), Add(Add(Value In Array(Event Player.JobXP, 5) >= 2500, Value In Array(Event Player.JobXP, 5) >= 5000), Add(Value In Array(Event Player.JobXP, 5) >= 10000, Value In Array(Event Player.JobXP, 6) >= 2500))), Add(Value In Array(Event Player.JobXP, 6) >= 5000, Value In Array(Event Player.JobXP, 6) >= 10000))"
mastery_rule = block(
    'rule("[마스터리 01] 한 길의 장인")',
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
    "\t\t" + milestone_total + " > Round To Integer(Divide(Event Player.Giant, 10), Down);",
    "\t}",
    "",
    "\tactions",
    "\t{",
    "\t\tModify Player Variable(Event Player, Giant, Add, 10);",
    "\t\tModify Player Variable(Event Player, Money, Add, 1000);",
    "\t\tModify Player Variable(Event Player, Earned, Add, 1000);",
    '\t\tBig Message(All Players(All Teams), Custom String("{0} — 한 길의 장인이 되었다! (마스터리 {1}) +$1,000", Event Player, Round To Integer(Divide(Event Player.Giant, 10), Down)));',
    "\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 4);",
    "\t\tPlay Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 200);",
    "\t\tWait(1, Ignore Condition);",
    "\t}",
    "}",
    "",
)
prison_anchor = 'rule("[감옥 01] 만기 출소")'
sub(
    prison_anchor,
    mastery_rule + newline + prison_anchor,
    1,
    "mastery rule insertion",
)

# Display the paid mastery count in both head-tag variants.
old_head_tag = 'Custom String("명성 {0} · 악명 {1}", Event Player.Fame, Event Player.Noto)'
new_head_tag = 'Custom String("명성 {0} · 악명 {1}{2}", Event Player.Fame, Event Player.Noto, Event Player.Giant >= 10 ? Custom String(" · ★{0}", Round To Integer(Divide(Event Player.Giant, 10), Down)) : Custom String(""))'
sub(old_head_tag, new_head_tag, 2, "mastery head-tag stars")

# Store at most one decimal digit of the mastery-paid counter in SaveC.
old_save_c = "Set Player Variable(Event Player, SaveC, Add(Multiply(Event Player.Rebuild, 100000), Multiply(Event Player.Rebirth, 10000)));"
new_save_c = "Set Player Variable(Event Player, SaveC, Add(Add(Multiply(Event Player.Rebuild, 100000), Multiply(Event Player.Rebirth, 10000)), Multiply(Min(9, Round To Integer(Divide(Event Player.Giant, 10), Down)), 1000)));"
sub(old_save_c, new_save_c, 1, "mastery save digit")

# Restore the mastery-paid digit; contract progress intentionally starts at zero.
insert_after_line(
    "Set Player Variable(Event Player, Rebirth, Modulo(Round To Integer(Divide(Event Player.EnterC, 10000), Down), 10));",
    "Set Player Variable(Event Player, Giant, Multiply(Modulo(Round To Integer(Divide(Event Player.EnterC, 1000), Down), 10), 10));",
    "mastery restore digit",
)


expected_counts = {
    "57: ContractKind": 1,
    "오늘의 계약 — {0}": 1,
    "오늘의 계약 달성!": 4,
    "오늘의 계약 — 진행": 4,
    'rule("[마스터리 01] 한 길의 장인")': 1,
    "한 길의 장인이 되었다": 1,
    " · ★{0}": 2,
    "Multiply(Min(9, Round To Integer(Divide(Event Player.Giant, 10), Down)), 1000)": 1,
    "Divide(Event Player.EnterC, 1000), Down), 10), 10)": 1,
}
for needle, expected in expected_counts.items():
    actual = text.count(needle)
    assert actual == expected, f"final count {needle!r}: expected {expected}, found {actual}"

with SOURCE.open("w", encoding="utf-8", newline="") as source_file:
    source_file.write(text)


def safe_print(message):
    """Keep the caller's cp949 console safe; all report text is ASCII."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "backslashreplace").decode("ascii"))


safe_print("patch101_mastery.py applied successfully")
safe_print("summary: 1 global, 1 daily draw, 1 reset, 4 progress hooks, 1 mastery rule")
safe_print("summary: 2 head tags, 1 save digit, 1 restore digit")
for needle, expected in expected_counts.items():
    safe_print(f"verify[{needle.encode('unicode_escape').decode('ascii')}]={expected}")
