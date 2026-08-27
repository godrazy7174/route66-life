# -*- coding: utf-8 -*-
"""혼자서 다인 기능을 검증하기 위한 테스트 전용 빌드를 만든다.

    python make_test_build.py

배포용 ROUTE66_LIFE_EN.ow / ROUTE66_LIFE.ow 는 절대 건드리지 않는다.
산출물은 ROUTE66_LIFE_TEST.ow 하나뿐이며, 이 파일은 .gitignore 로 제외된다.

원래 사람이 둘 이상 있어야 확인할 수 있던 것들:
  편지 이벤트 · 강탈/체포/살해 · 임대 수입 · 이웃의 손길 ·
  총격이 무적 상태를 뚫는지 · 쥐떼 3인 게이트 · 동시 경합 · 이탈 정리

테스트 빌드는 1팀에 더미 봇 3기를 넣고 이들을 '사람'으로 취급하게 만들어
위 항목을 혼자 확인할 수 있게 한다. 봇은 텔레포트와 버튼 입력으로 조종된다.

주의: 이 빌드는 절대 공개 방에 올리지 마라. 치트 키가 살아 있다.
"""
import io
import re
import subprocess
import sys

SRC = 'ROUTE66_LIFE_EN.ow'
TMP = '_test_en.ow'
OUT = 'ROUTE66_LIFE_TEST.ow'

src = io.open(SRC, encoding='utf-8').read()
applied = []


def sub(old, new, tag, count=1):
    global src
    n = src.count(old)
    assert n == count, '%s: %d건 (%d건이어야 함)' % (tag, n, count)
    src = src.replace(old, new)
    applied.append(tag)


# ── 1) 1팀 더미 봇도 SetupPlayer 를 받게 한다 ────────────────────
# 2팀 야수는 그대로 제외해야 한다 (SetupPlayer 가 1팀으로 옮겨버리므로).
sub('\t\tIs Dummy Bot(Event Player) == False;\n\t\tEvent Player.Init != 1;',
    '\t\tOr(Is Dummy Bot(Event Player) == False, Team Of(Event Player) == Team 1) == True;\n'
    '\t\tEvent Player.Init != 1;',
    '1팀 봇에게 SetupPlayer 허용')

# ── 2) 편지 대상 필터에서 봇 제외를 푼다 ─────────────────────────
sub('And(Current Array Element != Event Player, Is Dummy Bot(Current Array Element) == False)',
    'Current Array Element != Event Player',
    '편지 대상에 봇 허용')

# ── 3) 쥐떼 게이트를 1인으로 낮춘다 ──────────────────────────────
sub('Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18',
    'Count Of(Global Variable(RatHitters)) >= 1 ? 70 : 18',
    '쥐떼 게이트 3인 -> 1인')

# ── 4) 치트 + 봇 조종 룰 ─────────────────────────────────────────
CHEATS = '''rule("[테스트 00] 봇 3기 투입")
{
\tevent
\t{
\t\tOngoing - Global;
\t}

\tconditions
\t{
\t\tGlobal Variable(Ready) == 1;
\t}

\tactions
\t{
\t\tWait(3, Ignore Condition);
\t\tIf(Not(Entity Exists(Players In Slot(5, Team 1))));
\t\t\tCreate Dummy Bot(Hero(Cassidy), Team 1, 5, Value In Array(Global Variable(LocPos), 0), Vector(1, 0, 0));
\t\tEnd;
\t\tIf(Not(Entity Exists(Players In Slot(6, Team 1))));
\t\t\tCreate Dummy Bot(Hero(Cassidy), Team 1, 6, Value In Array(Global Variable(LocPos), 0), Vector(1, 0, 0));
\t\tEnd;
\t\tIf(Not(Entity Exists(Players In Slot(7, Team 1))));
\t\t\tCreate Dummy Bot(Hero(Cassidy), Team 1, 7, Value In Array(Global Variable(LocPos), 0), Vector(1, 0, 0));
\t\tEnd;
\t\tWait(10, Ignore Condition);
\t\tLoop();
\t}
}

rule("[테스트 01] 치트 — 점프+웅크리기: 다음 날 아침")
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
\t\tEvent Player.TutOn == 0;
\t\tIs Button Held(Event Player, Button(Jump)) == True;
\t\tIs Button Held(Event Player, Button(Crouch)) == True;
\t}

\tactions
\t{
\t\tModify Global Variable(Day, Add, 1);
\t\tSet Global Variable(Clock, 400);
\t\tSet Global Variable(IsNight, 0);
\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] {0}일차 아침", Global Variable(Day)));
\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 2.5));
\t\tWait Until(Not(Is Button Held(Event Player, Button(Jump))), 5);
\t}
}

rule("[테스트 02] 치트 — 점프+근접: 밤으로")
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
\t\tEvent Player.TutOn == 0;
\t\tIs Button Held(Event Player, Button(Jump)) == True;
\t\tIs Button Held(Event Player, Button(Melee)) == True;
\t}

\tactions
\t{
\t\tSet Global Variable(Clock, 1260);
\t\tSet Global Variable(IsNight, 1);
\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] 밤으로"));
\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 2.5));
\t\tWait Until(Not(Is Button Held(Event Player, Button(Jump))), 5);
\t}
}

rule("[테스트 03] 치트 — 점프+재장전: 돈과 보급")
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
\t\tEvent Player.TutOn == 0;
\t\tIs Button Held(Event Player, Button(Jump)) == True;
\t\tIs Button Held(Event Player, Button(Reload)) == True;
\t}

\tactions
\t{
\t\tModify Player Variable(Event Player, Money, Add, 20000);
\t\tSet Player Variable(Event Player, Inv, Array(9, 9, 9, 9));
\t\tSet Player Variable(Event Player, Hunger, 100);
\t\tSet Player Variable(Event Player, Thirst, 100);
\t\tSet Player Variable(Event Player, Energy, 100);
\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] +$20,000 · 보급 가득"));
\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 2.5));
\t\tWait Until(Not(Is Button Held(Event Player, Button(Jump))), 5);
\t}
}

rule("[테스트 04] 치트 — 점프+육포: 봇 3기를 내 앞으로")
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
\t\tEvent Player.TutOn == 0;
\t\tIs Button Held(Event Player, Button(Jump)) == True;
\t\tIs Button Held(Event Player, Button(Ability 2)) == True;
\t}

\tactions
\t{
\t\tSet Global Variable(Idx, 5);
\t\tWhile(Global Variable(Idx) <= 7);
\t\t\tIf(Entity Exists(Players In Slot(Global Variable(Idx), Team 1)));
\t\t\t\tTeleport(Players In Slot(Global Variable(Idx), Team 1), Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Facing Direction Of(Event Player), 4))));
\t\t\tEnd;
\t\t\tModify Global Variable(Idx, Add, 1);
\t\tEnd;
\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] 봇을 앞으로 불렀다"));
\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 2.5));
\t\tWait Until(Not(Is Button Held(Event Player, Button(Jump))), 5);
\t}
}

rule("[테스트 05] 치트 — 점프+보조사격: 봇 2기를 표적에 겹쳐 경합 재현")
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
\t\tEvent Player.TutOn == 0;
\t\tIs Button Held(Event Player, Button(Jump)) == True;
\t\tIs Button Held(Event Player, Button(Secondary Fire)) == True;
\t}

\tactions
\t{
\t\tIf(Global Variable(TreasureOn) == 1);
\t\t\tTeleport(Players In Slot(5, Team 1), Global Variable(TreasurePos));
\t\t\tTeleport(Players In Slot(6, Team 1), Global Variable(TreasurePos));
\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] 봇 2기를 보물에 겹쳤다 — 지급이 한 번만 나야 정상"));
\t\tElse If(Global Variable(HuntPhase) >= 1);
\t\t\tTeleport(Players In Slot(5, Team 1), Global Variable(HuntTrackPos));
\t\t\tTeleport(Players In Slot(6, Team 1), Global Variable(HuntTrackPos));
\t\t\tWait(0.5, Ignore Condition);
\t\t\tPress Button(Players In Slot(5, Team 1), Button(Interact));
\t\t\tPress Button(Players In Slot(6, Team 1), Button(Interact));
\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] 봇 2기가 같은 흔적을 동시 조사 — 단계가 한 번만 올라야 정상"));
\t\tElse;
\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] 보물이나 대사냥 흔적이 떠 있을 때 쓸 것"));
\t\tEnd;
\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 4));
\t\tWait Until(Not(Is Button Held(Event Player, Button(Jump))), 5);
\t}
}

rule("[테스트 06] 치트 — 점프+실행: 봇 1기 퇴장 (이탈 정리 확인)")
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
\t\tEvent Player.TutOn == 0;
\t\tIs Button Held(Event Player, Button(Jump)) == True;
\t\tIs Button Held(Event Player, Button(Interact)) == True;
\t}

\tactions
\t{
\t\tDestroy Dummy Bot(Team 1, 7);
\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[치트] 7번 봇 퇴장 — 그 봇의 표식이 사라져야 정상"));
\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 4));
\t\tWait Until(Not(Is Button Held(Event Player, Button(Jump))), 5);
\t}
}

'''

anchor = 'rule("[코어 01] 월드 초기화")'
assert src.count(anchor) == 1
src = src.replace(anchor, CHEATS + anchor)
applied.append('치트·봇 조종 룰 7개')

io.open(TMP, 'w', encoding='utf-8', newline='\n').write(src)

for tag in applied:
    print('  + %s' % tag)

print()
for chk in ['lint.py', 'blockcheck.py', 'enumcheck.py', 'labelcheck.py']:
    r = subprocess.run([sys.executable, chk, TMP], capture_output=True, text=True, encoding='utf-8')
    bad = [l for l in (r.stdout or '').split('\n') if l.startswith('!!') or '불균형' in l or '!!' in l]
    print('  %-14s %s' % (chk, '경고 %d건' % len(bad) if bad else 'OK'))
    for l in bad[:4]:
        print('      %s' % l.strip()[:110])

subprocess.run([sys.executable, 'to_korean.py', TMP, OUT], capture_output=True, text=True, encoding='utf-8')
io.open(TMP, 'w', encoding='utf-8').close()
import os
os.remove(TMP)
print('\n생성: %s' % OUT)
print('배포용 %s / ROUTE66_LIFE.ow 는 건드리지 않았다.' % SRC)
