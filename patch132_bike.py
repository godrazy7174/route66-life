# -*- coding: utf-8 -*-
"""patch132: 시온 바이크 가속 — [E] 바이크 탑승 중 이동 배율 200%.

문제: 말($5500) 구매 후 시온의 [E] 바이크가 워크샵 이동 배율을 전혀 받지
못해(기본 100%), 질주(165%)와 차이가 없거나 오히려 느렸다.
해결: 바이크 사용 중(Is Using Ability 2) 이동 배율 200%를 0.25초마다
재적용하는 규칙 [조작 05]를 추가. Sprinting=1 가드로 [월드 03] 5초
루프의 속도 리셋을 차단하고, 종료 시 기존 else-체인 그대로 복원.
"""
import io, sys

PATH = "ROUTE66_LIFE_EN.ow"

with io.open(PATH, "r", encoding="utf-8") as f:
    src = f.read()

def sub(old, new, cnt):
    n = src.count(old)
    assert n == cnt, "expected %d, found %d: %r" % (cnt, n, old[:60])
    return src.replace(old, new)

ANCHOR = 'rule("[코어 12] 3인칭 시점 고정")'

NEW_RULE = '''rule("[조작 05] 바이크 질주 (시온 E)")
{
\tevent
\t{
\t\tOngoing - Each Player;
\t\tAll;
\t\tAll;
\t}

\tconditions
\t{
\t\tIs Dummy Bot(Event Player) == False;
\t\tEvent Player.Init == 1;
\t\tHero Of(Event Player) == Hero(Shion);
\t\tIs Using Ability 2(Event Player) == True;
\t\tIs Alive(Event Player) == True;
\t}

\tactions
\t{
\t\tSet Player Variable(Event Player, Sprinting, 1);
\t\tSet Move Speed(Event Player, 200);
\t\tWait(0.25, Ignore Condition);
\t\tLoop If(And(Is Using Ability 2(Event Player), Is Alive(Event Player)));
\t\tSet Player Variable(Event Player, Sprinting, 0);
\t\tIf(Or(Event Player.Hunger <= 0, Event Player.Thirst <= 0));
\t\t\tSet Move Speed(Event Player, 70);
\t\tElse If(Event Player.Energy <= 0);
\t\t\tSet Move Speed(Event Player, 80);
\t\tElse;
\t\t\tSet Move Speed(Event Player, And(Event Player.HasBag == 0, Event Player.HasHorse == 0) ? 110 : 100);
\t\tEnd;
\t}
}

'''

src = sub(ANCHOR, NEW_RULE + ANCHOR, 1)

with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(src)

print("patch132 OK: bike sprint rule inserted (200% while riding)")
