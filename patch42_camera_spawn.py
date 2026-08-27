# -*- coding: utf-8 -*-
"""[1] 화면이 안 돌아가는 문제

    Start Camera(플레이어, 위치, 시선지점, 블렌드속도)
    블렌드 속도는 '거리'를 따라가는 속도다. 그런데 시선 지점을
        Eye Position + 바라보는 방향 * 1000
    으로 잡아놨다. 90도만 돌려도 시선 지점이 1400m를 이동하므로
    블렌드 60으로는 따라잡는 데 20초가 넘게 걸린다. 사실상 안 돌아간다.
    -> 시선 지점을 20m 앞으로. 같은 각도가 28m 이동이라 즉시 따라온다.

    광선 시작점도 고친다. Position Of() 는 발밑이라 광선이 바닥에
    바로 부딪혀 카메라가 발치에 박힐 수 있었다. -> Eye Position 에서 쏜다.

    블렌드는 60 -> 100. 위치 추적이 빨라져 걸리는 느낌이 줄어든다.

[2] 스폰 방에서 잠깐 머물다 식당으로 순간이동하는 문제

    LocPos 가 BuildWorld 안에서 만들어지는데, BuildWorld 는 코어 01이
    4초 넘게 기다린 뒤에야 호출된다. 그전까지는 식당 좌표를 모르니
    보낼 수가 없었다.
    -> 좌표 배열을 코어 01 맨 앞으로 옮기고, 스폰 즉시 보내는 룰을 둔다.
       기본 HUD 도 그 자리에서 바로 끈다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
L = io.open(P, encoding='utf-8').read().split(chr(10))

# ── [1] 카메라 ─────────────────────────────────────────────────────
OLDCAM = ('Start Camera(Event Player, Ray Cast Hit Position(Position Of(Event Player), '
          'Add(Add(Position Of(Event Player), Vector(0, 1.8, 0)), Multiply(Facing Direction Of(Event Player), -2.8)), '
          'Empty Array, All Players(All Teams), False), '
          'Add(Eye Position(Event Player), Multiply(Facing Direction Of(Event Player), 1000)), 60);')
NEWCAM = ('Start Camera(Event Player, Ray Cast Hit Position(Eye Position(Event Player), '
          'Add(Eye Position(Event Player), Multiply(Facing Direction Of(Event Player), -3.2)), '
          'Empty Array, All Players(All Teams), False), '
          'Add(Eye Position(Event Player), Multiply(Facing Direction Of(Event Player), 20)), 100);')
n = 0
for i, ln in enumerate(L):
    if OLDCAM in ln:
        L[i] = ln.replace(OLDCAM, NEWCAM)
        n += 1
assert n == 2, n

# ── [2] 좌표를 코어 01 맨 앞으로 ───────────────────────────────────
src = next(i for i, x in enumerate(L) if 'Set Global Variable(LocPos, Array(Vector(44.29' in x)
coord = L.pop(src).strip()
dst = next(i for i, x in enumerate(L) if 'Set Global Variable(Ready, 0);' in x)
L.insert(dst + 1, '\t\t' + coord)

# ── 스폰 즉시 식당으로 ─────────────────────────────────────────────
RULE = '''rule("[코어 14] 스폰 즉시 식당으로")
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
		Event Player.Init != 1;
		Count Of(Global Variable(LocPos)) > 0;
		Has Spawned(Event Player) == True;
		Is Alive(Event Player) == True;
	}

	actions
	{
		Disable Game Mode HUD(Event Player);
		Disable Game Mode In-World UI(Event Player);
		Disable Hero HUD(Event Player);
		Teleport(Event Player, Value In Array(Global Variable(LocPos), 0));
	}
}

'''
s = chr(10).join(L)

# SetupPlayer 끝의 중복 순간이동 제거 (이제 위 룰이 먼저 처리한다)
OLDT = ('\t\tWait Until(Has Spawned(Event Player), 30);\n'
        '\t\tWait(0.2, Ignore Condition);\n'
        '\t\tTeleport(Event Player, Value In Array(Global Variable(LocPos), 0));\n')
assert s.count(OLDT) == 1
s = s.replace(OLDT, '', 1)

s = s.replace('rule("[튜토리얼 01] DoTutorial")', RULE + 'rule("[튜토리얼 01] DoTutorial")', 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  카메라 시선  : 1000m -> 20m  (회전이 안 되던 직접 원인)')
print('  카메라 광선  : 발밑 -> 눈높이에서 발사')
print('  블렌드 속도  : 60 -> 100')
print('  스폰         : 좌표를 코어 01 맨 앞으로 옮기고 스폰 즉시 식당으로 + 기본 HUD 즉시 해제')
