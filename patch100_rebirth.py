# -*- coding: utf-8 -*-
"""환생 시스템을 ROUTE66_LIFE_EN.ow에 한 번만 적용하는 패치."""

from pathlib import Path


SOURCE = Path(__file__).with_name("ROUTE66_LIFE_EN.ow")


with SOURCE.open("r", encoding="utf-8", newline="") as source_file:
    text = source_file.read()

newline = "\r\n" if "\r\n" in text else "\n"


def block(*lines):
    """현재 소스의 줄바꿈 형식으로 여러 줄 문자열을 만든다."""
    return newline.join(lines)


def sub(old, new, cnt, label):
    """치환 전 앵커 수를 검증한 뒤 정확히 지정된 횟수만 치환한다."""
    global text
    found = text.count(old)
    assert found == cnt, f"{label}: expected {cnt}, found {found}"
    text = text.replace(old, new)


old_station_menu = "Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 4, 4, 1, 1)"
new_station_menu = "Array(1, 1, 3, 4, 2, 3, 5, 2, 4, 6, 6, 5, 5, 4, 1, 1)"
sub(old_station_menu, new_station_menu, 3, "정거장 메뉴 수 4→5")

sub(
    'Custom String("가축 출하 — 마리당 $60"), Custom String("-")',
    'Custom String("가축 출하 — 마리당 $60"), Custom String("새 출발의 기차 — 환생")',
    1,
    "환생 메뉴 라벨",
)

sub(
    block(
        "\t\t\tElse;",
        "\t\t\t\tIf(Event Player.RanchReady <= 0);",
    ),
    block(
        "\t\t\tElse If(Event Player.MenuIdx == 3);",
        "\t\t\t\tIf(Event Player.RanchReady <= 0);",
    ),
    1,
    "정거장 목장 분기",
)

zone_11_close = block(
    "\t\t\t\tEnd;",
    "\t\t\tEnd;",
    "\t\tElse If(Event Player.Zone == 12);",
)
rebirth_branch = block(
    "\t\t\t\tEnd;",
    "\t\t\tElse;",
    "\t\t\t\tIf(Event Player.Rebuild < 5);",
    ' \t\t\t\t\tSmall Message(Event Player, Custom String("기차역을 재건한 자만 이 기차에 오른다 (재건 {0}/5)", Event Player.Rebuild));'.lstrip(" "),
    "\t\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
    "\t\t\t\tElse If(Event Player.Rebirth >= 5);",
    ' \t\t\t\t\tSmall Message(Event Player, Custom String("이미 전설이다 — 다섯 번의 새벽을 지났다"));'.lstrip(" "),
    "\t\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);",
    "\t\t\t\tElse If(Event Player.EntryCur >= Total Time Elapsed());",
    "\t\t\t\t\tSet Player Variable(Event Player, EntryCur, 0);",
    "\t\t\t\t\tModify Player Variable(Event Player, Rebirth, Add, 1);",
    "\t\t\t\t\tFor Player Variable(Event Player, Idx, 0, 11, 1);",
    "\t\t\t\t\t\tIf(Value In Array(Global Variable(BldOwner), Event Player.Idx) == Event Player);",
    "\t\t\t\t\t\t\tSet Global Variable At Index(BldOwner, Event Player.Idx, 0);",
    "\t\t\t\t\t\tEnd;",
    "\t\t\t\t\tEnd;",
    "\t\t\t\t\tSet Player Variable(Event Player, Money, 60);",
    "\t\t\t\t\tSet Player Variable(Event Player, Deposit, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, Inv, Array(2, 2, 0, 0));",
    "\t\t\t\t\tSet Player Variable(Event Player, Pick, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, HasBag, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, HasHorse, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, HasHome, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, Whisky, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, Rebuild, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, Tier, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, Bounty, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, Sack, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, HasPowder, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, BrewVats, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, BrewEnd, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, BrewReady, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, RanchPens, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, RanchEnd, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, RanchReady, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, RanchCare, 0);",
    "\t\t\t\t\tIf(Event Player.Contraband == 1);",
    "\t\t\t\t\t\tSet Player Variable(Event Player, Contraband, 0);",
    "\t\t\t\t\t\tDestroy Icon(Event Player.SmuggleIco);",
    "\t\t\t\t\tEnd;",
    "\t\t\t\t\tIf(Event Player.Escort == 1);",
    "\t\t\t\t\t\tSet Player Variable(Event Player, Escort, 0);",
    "\t\t\t\t\t\tDestroy Icon(Event Player.EscortIco);",
    "\t\t\t\t\t\tDestroy Effect(Event Player.EscortFx);",
    "\t\t\t\t\tEnd;",
    "\t\t\t\t\tIf(Event Player.HasParcel == 1);",
    "\t\t\t\t\t\tSet Player Variable(Event Player, HasParcel, 0);",
    "\t\t\t\t\t\tDestroy Icon(Event Player.DelIcon);",
    "\t\t\t\t\tEnd;",
    "\t\t\t\t\tIf(Event Player.CowOn == 1);",
    "\t\t\t\t\t\tSet Player Variable(Event Player, CowOn, 0);",
    "\t\t\t\t\t\tDestroy Effect(Event Player.CowFx);",
    "\t\t\t\t\t\tDestroy Icon(Event Player.CowIco);",
    "\t\t\t\t\tEnd;",
    "\t\t\t\t\tSet Player Variable(Event Player, Earned, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, DayStart, 0);",
    "\t\t\t\t\tSet Player Variable(Event Player, GoalDone, 0);",
    "\t\t\t\t\tStop Forcing Player To Be Hero(Event Player);",
    "\t\t\t\t\tTeleport(Event Player, Value In Array(Global Variable(LocPos), 0));",
    ' \t\t\t\t\tBig Message(All Players(All Teams), Custom String("{0} — 새벽 기차를 타고 다시 태어났다!! (환생 {1}회)", Event Player, Event Player.Rebirth));'.lstrip(" "),
    ' \t\t\t\t\tSmall Message(Event Player, Custom String("명성·악명·직업 경험은 남는다 — 아침마다 어제 수입의 {0}%가 얹힌다", Multiply(10, Event Player.Rebirth)));'.lstrip(" "),
    "\t\t\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(White), Position Of(Event Player), 8);",
    "\t\t\t\t\tPlay Effect(All Players(All Teams), Buff Explosion Sound, Color(White), Position Of(Event Player), 250);",
    "\t\t\t\tElse;",
    "\t\t\t\t\tSet Player Variable(Event Player, EntryCur, Add(Total Time Elapsed(), 10));",
    ' \t\t\t\t\tBig Message(Event Player, Custom String("정말 떠나는가 — 10초 안에 다시 실행하면 환생한다"));'.lstrip(" "),
    ' \t\t\t\t\tSmall Message(Event Player, Custom String("전 재산·장비·부동산·사업·재건이 사라진다. 남는 것: 직업 경험 · 명성/악명 · 환생의 가호"));'.lstrip(" "),
    "\t\t\t\tEnd;",
    "\t\t\tEnd;",
    "\t\tElse If(Event Player.Zone == 12);",
)
sub(zone_11_close, rebirth_branch, 1, "정거장 환생 분기")

interest_anchor = "\t\tIf(Event Player.Deposit >= 100);"
morning_bonus = block(
    "\t\tIf(And(Event Player.Rebirth >= 1, Event Player.Earned > Event Player.DayStart));",
    "\t\t\tSet Player Variable(Event Player, Amt, Round To Integer(Multiply(Subtract(Event Player.Earned, Event Player.DayStart), Multiply(0.1, Event Player.Rebirth)), Down));",
    "\t\t\tIf(Event Player.Amt >= 1);",
    "\t\t\t\tModify Player Variable(Event Player, Money, Add, Event Player.Amt);",
    ' \t\t\t\tSmall Message(Event Player, Custom String("환생의 가호 — 어제 수입의 {0}%, +$ {1}", Multiply(10, Event Player.Rebirth), Event Player.Amt));'.lstrip(" "),
    "\t\t\tEnd;",
    "\t\tEnd;",
    interest_anchor,
)
sub(interest_anchor, morning_bonus, 1, "아침 환생 보너스")

old_title = (
    'Event Player.Rebuild >= 5 ? Custom String("66번 국도의 재건자") : '
    'Value In Array(Array(Custom String("떠돌이"), Custom String("일꾼"), Custom String("정착민"), '
    'Custom String("유지"), Custom String("거상"), Custom String("66번 국도의 주인")), '
    'Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), '
    'Event Player.Money >= 2500), Event Player.Money >= 6000), Event Player.Money >= 15000))'
)
new_title = (
    'Event Player.Rebirth >= 1 ? Value In Array(Array(Custom String("환생자"), '
    'Custom String("환생자"), Custom String("불사조"), Custom String("불사조"), '
    'Custom String("66번 국도의 전설")), Subtract(Min(5, Event Player.Rebirth), 1)) : '
    'Custom String("{0}", ' + old_title + ")"
)
sub(old_title, new_title, 2, "머리 위 환생 우선 칭호")

sign_line = "가축 출하 — 목장에서 기른 소, 마리당 $60\\r\\n"
sub(
    sign_line,
    sign_line + "새 출발의 기차 — 재건을 마친 자는 전 재산을 두고 다시 태어난다\\r\\n",
    1,
    "정거장 안내판",
)

expected_counts = {
    "새 출발의 기차 — 환생": 1,
    "새벽 기차를 타고 다시 태어났다": 1,
    "환생의 가호": 2,
    "정말 떠나는가": 1,
    "66번 국도의 전설": 2,
    new_station_menu: 3,
    "Stop Forcing Player To Be Hero(Event Player);": 1,
    "재건을 마친 자는 전 재산을 두고": 1,
}
for needle, expected in expected_counts.items():
    actual = text.count(needle)
    assert actual == expected, f"최종 카운트 {needle!r}: expected {expected}, found {actual}"

# 명세의 칭호 배열은 각 이름표 줄에 "환생자"를 두 번 둔다. 따라서 줄은 2개이고
# 원문 리터럴 출현 수는 4개다. 두 값 모두 검증해 모호함 없이 보고한다.
rebirth_title_lines = sum('Custom String("환생자")' in line for line in text.splitlines())
rebirth_title_literals = text.count('Custom String("환생자")')
assert rebirth_title_lines == 2, f"환생자 칭호 줄: expected 2, found {rebirth_title_lines}"
assert rebirth_title_literals == 4, f"환생자 리터럴: expected 4, found {rebirth_title_literals}"

with SOURCE.open("w", encoding="utf-8", newline="") as source_file:
    source_file.write(text)

print("patch100_rebirth.py 적용 완료")
print("변경: 정거장 5번째 메뉴, 2단계 환생 확인/초기화, 아침 수입 보너스, 우선 칭호, 안내판")
print("저장 코드 규칙: 변경 없음")
for needle, expected in expected_counts.items():
    print(f"{needle} = {expected}")
print(f'Custom String("환생자") = {rebirth_title_lines}개 이름표 줄 ({rebirth_title_literals}개 리터럴)')
