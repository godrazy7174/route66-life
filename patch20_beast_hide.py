# -*- coding: utf-8 -*-
"""야수가 상시 노출되어 흔적 추적이 무의미한 문제 수정.

기존: 리퍼 봇 3기가 개활지에 그냥 서 있음 -> 걸어가서 쏘면 끝
변경: 평소에는 투명 + Phased Out(총알이 통과, 무적) 상태로 숨어 있고,
      흔적 추적에 성공해야 30초간 모습을 드러낸다.
      시간이 지나면 다시 숨는다. 아이콘도 드러난 동안만 보인다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 전역 변수 ──────────────────────────────────────────────────────
s = s.replace("\t\t25: DailyGoal\n", "\t\t25: DailyGoal\n\t\t26: BeastTimer\n")
s = s.replace("\t\tSet Global Variable(RankArr, Empty Array);",
              "\t\tSet Global Variable(RankArr, Empty Array);\n\t\tSet Global Variable(BeastTimer, Array(0, 0, 0));")

# ── 야수 관리 규칙 교체: 은신 상태 유지 ────────────────────────────
a = s.index('rule("[직업 03] 야수 관리")')
b = s.index('\nrule("[직업 03-2] 야수 처치")')
NEW = '''rule("[직업 03] 야수 은신")
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
		Total Time Elapsed() >= Value In Array(Global Variable(BeastTimer), Slot Of(Event Player));
	}

	actions
	{
		Set Max Health(Event Player, 40);
		Set Ability 1 Enabled(Event Player, False);
		Set Ability 2 Enabled(Event Player, False);
		Set Ultimate Ability Enabled(Event Player, False);
		Set Primary Fire Enabled(Event Player, False);
		Set Secondary Fire Enabled(Event Player, False);
		Set Move Speed(Event Player, 0);
		Set Invisible(Event Player, All);
		Set Status(Event Player, Null, Phased Out, 9999);
		Teleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-14, 14), 0, Random Real(-14, 14)))));
	}
}
'''
s = s[:a] + NEW + s[b + 1:]

# ── 아이콘: 드러난 동안만 보이게 (인덱스를 상수로 펼침) ────────────
icons = []
for i in range(3):
    bot = 'First Of(Filtered Array(All Players(Team 2), Slot Of(Current Array Element) == %d))' % i
    vis = 'Value In Array(Global Variable(BeastTimer), %d) > Total Time Elapsed() ? All Players(All Teams) : False' % i
    icons.append('\t\tCreate Icon(%s, %s, Eye, Visible To and Position, Color(Orange), True);' % (vis, bot))
_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + '\n'.join(icons) + '\n' + s[b:]

# ── DoHunt: 숨은 야수만 대상으로, 추적하면 30초간 드러냄 ───────────
s = s.replace(
    'Set Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))), Distance Between(Position Of(Event Player), Position Of(Current Array Element)))));',
    'Set Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), And(Is Alive(Current Array Element), Value In Array(Global Variable(BeastTimer), Slot Of(Current Array Element)) <= Total Time Elapsed()))), Distance Between(Position Of(Event Player), Position Of(Current Array Element)))));')

s = s.replace('''		Teleport(Event Player.Target, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Facing Direction Of(Event Player), 16))));
		Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player.Target), 2);
		Big Message(Event Player, Custom String("야수를 몰아냈다 — 쏴라"));''',
'''		Set Global Variable At Index(BeastTimer, Slot Of(Event Player.Target), Add(Total Time Elapsed(), 30));
		Teleport(Event Player.Target, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Facing Direction Of(Event Player), 16))));
		Clear Status(Event Player.Target, Phased Out);
		Set Invisible(Event Player.Target, None);
		Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player.Target), 2);
		Big Message(Event Player, Custom String("야수를 몰아냈다 — 30초 안에 쏴라"));''')

# 처치 시 타이머 초기화 (다시 숨도록)
s = s.replace('''		Wait(25, Ignore Condition);
		Teleport(Victim, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-12, 12), 0, Random Real(-12, 12)))));''',
'''		Set Global Variable At Index(BeastTimer, Slot Of(Victim), 0);
		Wait(25, Ignore Condition);
		Teleport(Victim, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-12, 12), 0, Random Real(-12, 12)))));''')

# ── 안내 문구 ──────────────────────────────────────────────────────
s = s.replace('Custom String("흔적 추적 — 야수를 앞으로 몰아낸다\\r\\n좌클릭으로 직접 쏴서 잡는다\\r\\n")',
              'Custom String("야수는 숨어 있다 — 추적해야 모습을 드러낸다\\r\\n드러난 30초 안에 좌클릭으로 잡아라\\r\\n")')
s = s.replace('Custom String("사냥꾼의 일터. 흔적을 쫓으면 사냥감이 나타난다. 좌클릭으로 직접 쏴라.")',
              'Custom String("사냥꾼의 일터. 야수는 숨어 있어 추적해야 나타난다.\\r\\n드러난 30초 안에 좌클릭으로 잡아야 한다.")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  은신 규칙       : %d' % s.count('[직업 03] 야수 은신'))
print('  BeastTimer 사용 : %d곳' % s.count('BeastTimer'))
print('  조건부 아이콘   : %d개' % s.count('> Total Time Elapsed() ? All Players(All Teams) : False'))
