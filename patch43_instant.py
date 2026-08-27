# -*- coding: utf-8 -*-
"""[1] 처음부터 바로 플레이 가능하게

    지금 순서:
        게임 시작 대기 -> 스폰 대기 -> 2초 -> 팀 이동 -> 2초
        -> BuildWorld(봇 0.75초) -> Ready = 1
    Ready 가 1이 되어야 SetupPlayer 도 HUD 도 돈다. 5초 넘게 아무것도 없다.

    바꾼 순서:
        데이터 전부 세팅 -> Ready = 1 (즉시)
        -> 게임 시작·스폰 대기 -> BuildWorld(표지판·봇)
    좌표·반경까지 Ready 이전에 확정하므로 구역 감지도 첫 프레임부터 정상이다.
    시작 시 팀 이동과 2초 대기 두 개는 [코어 13]이 상시로 하는 일이라 지운다.

[2] 카메라

    시선 20m + 블렌드 100 은 회전 지연이 0.28초쯤 된다 — 이게 버벅임이다.
    시선을 6m 로 당겨 같은 회전에 필요한 이동 거리를 8.5m 로 줄이고
    블렌드를 70 으로 낮춰 위치 흔들림을 다시 다듬는다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── [1-a] 좌표·반경을 Ready 이전으로 ───────────────────────────────
KEY = 'Set Global Variable(LocPos, Array(Vector(44.29'
i = s.index(KEY)
j = s.index(chr(10), i) + 1
EARLY = ('\t\tModify Global Variable(LocPos, Append To Array, Add(Value In Array(Global Variable(LocPos), 0), Vector(0, 0, -4)));\n'
         '\t\tModify Global Variable(LocPos, Append To Array, Add(Value In Array(Global Variable(LocPos), 4), Vector(6, 0, 0)));\n'
         '\t\tSet Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6));\n'
         '\t\tSet Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));\n'
         '\t\tSet Global Variable(BotHome, Value In Array(Global Variable(LocPos), 8));\n')
s = s[:j] + EARLY + s[j:]

# ── [1-b] 시작 순서 재배치 ─────────────────────────────────────────
OLD = '''		Wait Until(Is Game In Progress(), 30);
		Wait Until(Has Spawned(Host Player()), 30);
		Wait(2, Ignore Condition);
		Move Player to Team(All Players(Team 2), Team 1, -1);
		Wait(2, Ignore Condition);
		Call Subroutine(BuildWorld);
		Set Global Variable(Ready, 1);
'''
NEW = '''		Set Global Variable(Ready, 1);
		Wait Until(Is Game In Progress(), 30);
		Wait Until(Has Spawned(Host Player()), 30);
		Call Subroutine(BuildWorld);
'''
assert s.count(OLD) == 1
s = s.replace(OLD, NEW, 1)

# ── [1-c] BuildWorld 에서는 좌표를 '보정'만 ────────────────────────
L = s.split(chr(10))
out, dropped = [], 0
for ln in L:
    t = ln.strip()
    if t.startswith('Modify Global Variable(LocPos, Append To Array, Nearest Walkable'):
        idx = 9 if 'Global Variable(LocPos), 0)' in t else 10
        inner = t[t.index('Nearest Walkable'):-2]
        out.append('\t\tSet Global Variable At Index(LocPos, %d, %s);' % (idx, inner))
        continue
    if t in ('Set Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));',
             'Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6));') and dropped < 2:
        dropped += 1
        continue
    out.append(ln)
assert dropped == 2, dropped
s = chr(10).join(out)

# ── [2] 카메라 ─────────────────────────────────────────────────────
n = s.count('Multiply(Facing Direction Of(Event Player), 20)), 100);')
assert n == 2, n
s = s.replace('Multiply(Facing Direction Of(Event Player), 20)), 100);',
              'Multiply(Facing Direction Of(Event Player), 6)), 70);')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  시작       : Ready 를 데이터 세팅 직후로 -> 첫 프레임부터 HUD·수치·조작 정상')
print('  제거       : 시작 시 팀 이동 + 2초 대기 x2 (코어 13이 상시 처리)')
print('  카메라     : 시선 20m -> 6m, 블렌드 100 -> 70')
