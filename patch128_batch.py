# -*- coding: utf-8 -*-
"""루트 66 라이프 영문 원본에 128차 밸런스·기능 묶음을 적용한다."""

from pathlib import Path
from textwrap import dedent


PATH = Path("ROUTE66_LIFE_EN.ow")
text = PATH.read_text(encoding="utf-8")


def sub(old: str, new: str, cnt: int = 1) -> None:
    """기대 횟수를 확인한 뒤 문자열을 치환한다."""
    global text
    actual = text.count(old)
    assert actual == cnt, f"expected {cnt} occurrence(s), found {actual}: {old[:80]!r}"
    text = text.replace(old, new)


def block(source: str) -> str:
    """워크샵 규칙 블록의 들여쓰기와 끝 개행을 정규화한다."""
    return dedent(source).strip("\n") + "\n\n"


# A. 소몰이 밀기 속도 2배
sub(
    "Add(2.2, Multiply(0.9, Value In Array(Event Player.Adv, 6)))",
    "Add(4.4, Multiply(1.8, Value In Array(Event Player.Adv, 6)))",
)

# B. 사냥 수확량 보정
sub(
    "Modify Player Variable(Attacker, Yield, Add, Add(1, Value In Array(Player Variable(Attacker, Adv), 2)));",
    "Modify Player Variable(Attacker, Yield, Add, Value In Array(Player Variable(Attacker, Adv), 2));",
)

# C. 채광 QTE 보상 +3
sub(
    "Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 2));",
    "Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), 3));",
)
sub("정타! 원석 +2 (보유 {0})", "정타! 원석 +3 (보유 {0})")

# D. 일일 계약 HUD
guidance_lines = [line for line in text.splitlines() if "열차가 섰다! 금고 3칸" in line]
assert len(guidance_lines) == 1, f"expected 1 guidance line, found {len(guidance_lines)}"
guidance_line = guidance_lines[0]
contract_hud = '\t\tCreate HUD Text(Local Player.TutOn == 0 ? Local Player : False, Null, Global Variable(ContractKind) >= 1 ? Custom String("계약   {0}   {1}", Value In Array(Array(Custom String("채굴 8회"), Custom String("야수 4마리"), Custom String("배달 3건"), Custom String("소몰이 2회")), Subtract(Global Variable(ContractKind), 1)), Modulo(Local Player.Giant, 10) >= Value In Array(Array(8, 4, 3, 2), Subtract(Global Variable(ContractKind), 1)) ? Custom String("완료") : Custom String("{0} / {1}", Modulo(Local Player.Giant, 10), Value In Array(Array(8, 4, 3, 2), Subtract(Global Variable(ContractKind), 1)))) : Custom String(""), Null, Left, 4, Color(White), Color(Aqua), Color(White), Visible To Sort Order String and Color, Default Visibility);'
sub(guidance_line, guidance_line + "\n" + contract_hud)

# E. 이웃 목장 돌보기
neighbor_rule = block(
    r'''
    rule("[목장 03] 이웃의 손길")
    {
        event
        {
            Ongoing - Each Player;
            All;
            All;
        }

        conditions
        {
            Is Dummy Bot(Event Player) == False;
            Event Player.Init == 1;
            Event Player.TutOn == 0;
            Event Player.Busy == 0;
            Event Player.Zone == 12;
            Is Alive(Event Player) == True;
            Is Button Held(Event Player, Button(Crouch)) == True;
            Is Button Held(Event Player, Button(Interact)) == True;
        }

        actions
        {
            Set Player Variable(Event Player, Target, First Of(Filtered Array(All Players(All Teams), And(Current Array Element != Event Player, And(Player Variable(Current Array Element, RanchEnd) > Total Time Elapsed(), Player Variable(Current Array Element, RanchCare) == 0)))));
            If(Entity Exists(Event Player.Target));
                Set Player Variable(Event Player.Target, RanchCare, 1);
                Modify Player Variable(Event Player, Money, Add, 10);
                Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 1)));
                Small Message(Event Player, Custom String("{0}의 소에게 물을 줬다 — 품삯 $10 · 명성 +1", Event Player.Target));
                Small Message(Event Player.Target, Custom String("{0}이(가) 내 목장의 소를 돌봐줬다", Event Player));
                Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);
            Else;
                Small Message(Event Player, Custom String("돌봐줄 이웃의 소가 없다"));
            End;
            Wait(1, Ignore Condition);
        }
    }
    '''
)
sub('rule("[감옥 01] 만기 출소")', neighbor_rule + 'rule("[감옥 01] 만기 출소")')

# F. 큰길 위키 표지판: TrainPos의 첫 설정 바로 뒤
train_prefix = "\tSet Global Variable(TrainPos,"
assert text.count(train_prefix) == 2, f"expected 2 TrainPos setters, found {text.count(train_prefix)}"
build_anchor = 'rule("[코어 02] BuildWorld")'
assert text.count(build_anchor) == 1, f"expected 1 BuildWorld rule, found {text.count(build_anchor)}"
build_start = text.find(build_anchor)
build_end = text.find('\nrule("', build_start + len(build_anchor))
assert build_end >= 0, "end of BuildWorld rule not found"
train_start = text.find(train_prefix, build_start, build_end)
train_end = text.find("\n", train_start)
assert train_start >= 0 and train_end >= 0, "BuildWorld TrainPos setter line not found"
train_line = text[train_start:train_end]
wiki_sign = '\tCreate In-World Text(All Players(All Teams), Custom String("길잡이 — 궁금한 것은 공식 위키로: route66-life-wiki.ray-on.chatgpt.site"), Add(Nearest Walkable Position(Multiply(Add(Value In Array(Global Variable(LocPos), 0), Value In Array(Global Variable(LocPos), 11)), 0.5)), Vector(0, 1.8, 0)), 1.1, Do Not Clip, Visible To and Position, Color(Aqua), Default Visibility);'
sub(train_line, train_line + "\n" + wiki_sign)

# 결과 검증 후 단 한 번 기록
checks = {
    "Add(4.4, Multiply(1.8,": 1,
    "Yield, Add, Value In Array(Player Variable(Attacker, Adv), 2));": 1,
    "정타! 원석 +3": 1,
    "계약   {0}   {1}": 1,
    'rule("[목장 03] 이웃의 손길")': 1,
    "소에게 물을 줬다": 1,
    "route66-life-wiki.ray-on.chatgpt.site": 1,
    "Array(8, 4, 3, 2)": 2,
}
for needle, expected in checks.items():
    actual = text.count(needle)
    assert actual == expected, f"expected {expected} occurrence(s), found {actual}: {needle!r}"

PATH.write_text(text, encoding="utf-8")
print("patch128_batch.py: OK")
