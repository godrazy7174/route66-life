# -*- coding: utf-8 -*-
"""야수: 리퍼 -> 제트팩 캣, 그리고 배회.

기존: 드러난 뒤에도 Move Speed 0 이라 그 자리에 서 있기만 했다.
수정: 드러나 있는 동안 1~2.5초마다 방향을 새로 잡아 돌아다닌다.
      숨을 때 throttle을 끊어 제자리로 되돌린다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 영웅 교체 ───────────────────────────────────────────────────
assert s.count('Create Dummy Bot(Hero(Reaper)') == 1
s = s.replace('Create Dummy Bot(Hero(Reaper)', 'Create Dummy Bot(Hero(Jetpack Cat)', 1)

# ── 2) 숨을 때 이동 입력 해제 ──────────────────────────────────────
OLD = '\t\tSet Move Speed(Event Player, 0);\n\t\tSet Invisible(Event Player, All);'
assert s.count(OLD) == 1
s = s.replace(OLD, '\t\tStop Throttle In Direction(Event Player);\n' + OLD, 1)

# ── 3) 배회 룰 ─────────────────────────────────────────────────────
WANDER = '''rule("[직업 03-3] 야수 배회")
{
	event
	{
		Ongoing - Each Player;
		Team 2;
		All;
	}

	conditions
	{
		Is Dummy Bot(Event Player) == True;
		Global Variable(Ready) == 1;
		Is Alive(Event Player) == True;
		Value In Array(Global Variable(BeastTimer), Slot Of(Event Player)) > Total Time Elapsed();
	}

	actions
	{
		Set Move Speed(Event Player, 75);
		Start Throttle In Direction(Event Player, Vector(Random Real(-1, 1), 0, Random Real(-1, 1)), 1, To World, Replace existing throttle, Direction and Magnitude);
		Wait(Random Real(1, 2.5), Ignore Condition);
		Loop If(Value In Array(Global Variable(BeastTimer), Slot Of(Event Player)) > Total Time Elapsed());
		Stop Throttle In Direction(Event Player);
	}
}

'''
anchor = 'rule("[직업 03-2] 야수 처치")'
assert anchor in s
s = s.replace(anchor, WANDER + anchor, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# ── 4) 한글 변환기에 영웅 이름 추가 ────────────────────────────────
t = io.open('to_korean.py', encoding='utf-8').read()
OLDH = "    ('Hero(Reaper)', 'Hero(리퍼)'),"
assert OLDH in t
t = t.replace(OLDH, OLDH + "\n    ('Hero(Jetpack Cat)', 'Hero(제트팩 캣)'),", 1)
io.open('to_korean.py', 'w', encoding='utf-8', newline='\n').write(t)

print('패치 완료')
print('  야수 영웅 : 리퍼 -> 제트팩 캣')
print('  배회      : 1~2.5초마다 무작위 방향, 속도 75%')
print('  은신 시   : throttle 해제')
