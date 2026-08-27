# -*- coding: utf-8 -*-
"""시뮬레이션 결과 반영 + 동기부여 + 낮 고정.

시뮬로 드러난 것
 - 하루 순이익이 $1,127 (설계 목표 $300의 4배)
 - 원인 1: 어떤 작업도 피로를 '요구'하지 않아 피로 0으로도 무한 채굴
 - 원인 2: 위스키가 $25에 채굴 8회분($138)을 사주는 무한 루프
 - 원인 3: 내 방이 숙박 횟수 제한을 아예 없애 피로가 무의미
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 변수 ────────────────────────────────────────────────────────────
s = s.replace("\t\t42: HasHome\n",
              "\t\t42: HasHome\n\t\t43: Whisky\n\t\t44: SleepCount\n\t\t45: GoalDone\n\t\t46: DayStart\n\t\t47: LastDay\n")
s = s.replace("\t\t17: Tmp\n", "\t\t17: Tmp\n\t\t18: RankArr\n\t\t19: DailyGoal\n")
s = s.replace("\t\tSet Player Variable(Event Player, Pick, 0);",
              "\t\tSet Player Variable(Event Player, Pick, 0);\n\t\tSet Player Variable(Event Player, LastDay, -1);")
s = s.replace("\t\tSet Global Variable(BotBounty, 60);", "\t\tSet Global Variable(BotBounty, 12);\n\t\tSet Global Variable(DailyGoal, 400);\n\t\tSet Global Variable(RankArr, Empty Array);")

# ── 1) 피로 하드 게이트 ────────────────────────────────────────────
GATE = ('\t\tIf(Event Player.Energy < %d);\n'
        '\t\t\tSmall Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));\n'
        '\t\t\tAbort;\n'
        '\t\tEnd;\n')
for sub, need in (('DoMine', 5), ('DoHunt', 4), ('DoPlan', 6)):
    a = s.index('\t\t%s;\n\t}\n\n\tactions\n\t{\n' % sub) + len('\t\t%s;\n\t}\n\n\tactions\n\t{\n' % sub)
    s = s[:a] + (GATE % need) + s[a:]

# ── 2) 경제 수치 ───────────────────────────────────────────────────
ECON = [
    ('Chase Player Variable Over Time(Event Player, WorkProg, 100, 3.5, Destination and Duration);\n\t\tPlay Effect(All Players(All Teams), Bad Explosion, Color(Gray)',
     'Chase Player Variable Over Time(Event Player, WorkProg, 100, 4.5, Destination and Duration);\n\t\tPlay Effect(All Players(All Teams), Bad Explosion, Color(Gray)'),
    ('Set Global Variable(OrePrice, Random Integer(2, 5));', 'Set Global Variable(OrePrice, Random Integer(3, 6));'),
    ('Set Global Variable(HidePrice, Random Integer(4, 9));', 'Set Global Variable(HidePrice, Random Integer(6, 12));'),
    ('Set Player Variable(Event Player, Roll, Random Integer(60, 140));', 'Set Player Variable(Event Player, Roll, Random Integer(50, 130));'),
    ('Modify Player Variable(Event Player, Money, Add, 30);\n\t\t\tBig Message(Event Player, Custom String("채굴 {0}회 달성 — 보너스 $30"',
     'Modify Player Variable(Event Player, Money, Add, 25);\n\t\t\tBig Message(Event Player, Custom String("채굴 {0}회 달성 — 보너스 $25"'),
    ('Set Global Variable(BotBounty, 25);', 'Set Global Variable(BotBounty, 12);'),
    ('Set Global Variable(BotBounty, 80);', 'Set Global Variable(BotBounty, 40);'),
    ('Add(Total Time Elapsed(), 25)', 'Add(Total Time Elapsed(), 35)'),
    ('Add(Event Player.Hunger, 45)', 'Add(Event Player.Hunger, 55)'),
    ('Add(Event Player.Thirst, 45)', 'Add(Event Player.Thirst, 55)'),
    ('Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 40)));',
     'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 30)));'),
    # 장비 가격
    ('Array(250, 600, 1400, 3000)', 'Array(500, 1200, 2500, 5000)'),
    ('Event Player.Money >= 800', 'Event Player.Money >= 1800'),
    ('Modify Player Variable(Event Player, Money, Subtract, 800);', 'Modify Player Variable(Event Player, Money, Subtract, 1800);'),
    ('Custom String("돈이 부족합니다 ($800 필요)")', 'Custom String("돈이 부족합니다 ($1800 필요)")'),
    ('Event Player.Money >= 2000', 'Event Player.Money >= 3500'),
    ('Modify Player Variable(Event Player, Money, Subtract, 2000);', 'Modify Player Variable(Event Player, Money, Subtract, 3500);'),
    ('Custom String("돈이 부족합니다 ($2000 필요)")', 'Custom String("돈이 부족합니다 ($3500 필요)")'),
    ('Event Player.Money >= 3500);\n\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 3500);\n\t\t\t\t\tSet Player Variable(Event Player, HasHome, 1);',
     'Event Player.Money >= 7000);\n\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 7000);\n\t\t\t\t\tSet Player Variable(Event Player, HasHome, 1);'),
    ('Custom String("돈이 부족합니다 ($3500 필요)"));\n\t\t\t\tEnd;\n\t\t\tEnd;', 'Custom String("돈이 부족합니다 ($7000 필요)"));\n\t\t\t\tEnd;\n\t\t\tEnd;'),
    ('내 방 마련 $3500', '내 방 마련 $7000'),
    ('가죽 배낭 $800  ·  말 $2000', '가죽 배낭 $1800  ·  말 $3500'),
    ('가죽 배낭 $800', '가죽 배낭 $1800'),
    ('말 $2000', '말 $3500'),
]
missing = [o for o, _ in ECON if o not in s]
for o, n in ECON:
    s = s.replace(o, n, 1)

# 위스키 하루 2잔
s = s.replace('''				If(Event Player.Money >= 25);
					Modify Player Variable(Event Player, Money, Subtract, 25);''',
'''				If(Event Player.Whisky >= 2);
					Small Message(Event Player, Custom String("오늘은 그만 마셔라 — 하루 두 잔까지"));
				Else If(Event Player.Money >= 25);
					Modify Player Variable(Event Player, Money, Subtract, 25);
					Modify Player Variable(Event Player, Whisky, Add, 1);''')

# 숙박 횟수: 기본 1회, 내 방이면 2회
s = s.replace('''		If(And(Event Player.HasHome == 0, Event Player.SleepDay == Global Variable(Day)));
			Small Message(Event Player, Custom String("오늘은 이미 잤다 — 내일 아침에 다시"));
			Abort;
		End;''',
'''		If(Event Player.SleepCount >= Add(1, Event Player.HasHome));
			Small Message(Event Player, Custom String("오늘은 더 잘 수 없다 — 내일 아침에 다시"));
			Abort;
		End;''')
s = s.replace('\t\tSet Player Variable(Event Player, SleepDay, Global Variable(Day));',
              '\t\tModify Player Variable(Event Player, SleepCount, Add, 1);')

# ── 3) 직업 레벨 보상: 금맥 확률 +1%p/Lv (상한 12) ─────────────────
s = s.replace('''		If(Event Player.Job == 1);
			Modify Player Variable(Event Player, Roll, Subtract, 3);
		End;''',
'''		If(Event Player.Job == 1);
			Modify Player Variable(Event Player, Roll, Subtract, 2);
			Modify Player Variable(Event Player, Roll, Subtract, Min(12, Round To Integer(Divide(Value In Array(Event Player.JobXP, 1), 250), Down)));
		End;''')
s = s.replace('Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 100), Down))',
              'Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 250), Down))')

# ── 4) 아침 정산 + 일일 목표 + 재산 순위 ───────────────────────────
NEW_RULES = '''
rule("[월드 05] 아침 정산")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Event Player.Init == 1;
		Event Player.LastDay != Global Variable(Day);
	}

	actions
	{
		Set Player Variable(Event Player, LastDay, Global Variable(Day));
		Set Player Variable(Event Player, Whisky, 0);
		Set Player Variable(Event Player, SleepCount, 0);
		Set Player Variable(Event Player, GoalDone, 0);
		Set Player Variable(Event Player, DayStart, Event Player.Earned);
	}
}

rule("[월드 06] 일일 목표 달성")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Event Player.Init == 1;
		Event Player.GoalDone == 0;
		Subtract(Event Player.Earned, Event Player.DayStart) >= Global Variable(DailyGoal);
	}

	actions
	{
		Set Player Variable(Event Player, GoalDone, 1);
		Modify Player Variable(Event Player, Money, Add, 200);
		Set Player Variable(Event Player, Rep, Min(100, Add(Event Player.Rep, 3)));
		Big Message(Event Player, Custom String("오늘의 목표 달성 — 보너스 $200"));
		Play Effect(Event Player, Good Explosion, Color(Lime Green), Position Of(Event Player), 2);
	}
}

rule("[월드 07] 재산 순위 갱신")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Global Variable(Ready) == 1;
	}

	actions
	{
		Set Global Variable(RankArr, Sorted Array(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Init) == 1), Subtract(0, Player Variable(Current Array Element, Money))));
		Wait(3, Ignore Condition);
		Loop();
	}
}
'''
s = s.replace('\nrule("[조작 01] 행동 커서 이동 (R)")', NEW_RULES + '\nrule("[조작 01] 행동 커서 이동 (R)")')

# 아침에 목표액 갱신
s = s.replace("\t\t\tSet Global Variable(HidePrice, Random Integer(6, 12));",
              "\t\t\tSet Global Variable(HidePrice, Random Integer(6, 12));\n\t\t\tSet Global Variable(DailyGoal, Add(400, Multiply(Global Variable(Day), 80)));")

# HUD: 일일 목표 + 재산 순위
EXTRA = ('\t\tCreate HUD Text(Local Player.TutOn == 0 ? Local Player : False, Null, '
         'Custom String("오늘 목표   $ {0} / {1}", Max(0, Round To Integer(Subtract(Local Player.Earned, Local Player.DayStart), Down)), Global Variable(DailyGoal)), '
         'Custom String("{0}{1}", Custom String("1위  {0}   $ {1}\\r\\n", Value In Array(Global Variable(RankArr), 0), Player Variable(Value In Array(Global Variable(RankArr), 0), Money)), '
         'Count Of(Global Variable(RankArr)) > 1 ? Custom String("2위  {0}   $ {1}", Value In Array(Global Variable(RankArr), 1), Player Variable(Value In Array(Global Variable(RankArr), 1), Money)) : Custom String("")), '
         'Left, 3, Color(White), Color(Yellow), Color(Aqua), Visible To Sort Order String and Color, Default Visibility);\n')
i = s.index('rule("[코어 08] 공용 HUD 생성")')
j = s.index('\t}\n}', i)
s = s[:j] + EXTRA + s[j:]

# ── 5) 곡괭이 비용을 라벨과 패널에 표시 ────────────────────────────
PICKCOST = ('Local Player.Pick >= 4 ? Custom String("곡괭이 — 최고 등급") : '
            'Custom String("곡괭이 강화 $ {0}", Value In Array(Array(500, 1200, 2500, 5000), Local Player.Pick))')
s = s.replace('Custom String("곡괭이 강화")', PICKCOST)
s = s.replace('Custom String("곡괭이 Lv.{0}  —  채굴 수확 +{1}\\r\\n가죽 배낭 $1800  ·  말 $3500\\r\\n", Local Player.Pick, Local Player.Pick)',
              'Custom String("{0}{1}", Custom String("곡괭이 Lv.{0} — 수확 +{1}      다음 {2}\\r\\n", Local Player.Pick, Local Player.Pick, Local Player.Pick >= 4 ? Custom String("최고 등급") : Custom String("$ {0}", Value In Array(Array(500, 1200, 2500, 5000), Local Player.Pick))), Custom String("가죽 배낭 $1800  ·  말 $3500\\r\\n"))')

# ── 6) 낮 고정 + 밤 이펙트 ─────────────────────────────────────────
s = re.sub(r'(Create Effect\(All Players\(All Teams\), Light Shaft, )Color\((?:Yellow|Orange)\)(, Value In Array\(Global Variable\(LocPos\), \d+\), 1\.2, )Visible To Position and Radius\);',
           r'\1Global Variable(IsNight) == 1 ? Color(Sky Blue) : Color(Yellow)\2Visible To Position Radius and Color);', s)

NIGHT = '''
rule("[월드 08] 밤 연출")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Event Player.Init == 1;
		Global Variable(IsNight) == 1;
		Is Alive(Event Player) == True;
	}

	actions
	{
		Create Effect(Event Player, Cloud, Color(Black), Eye Position(Event Player), 5, Visible To Position and Radius);
		Set Player Variable(Event Player, Tmp, Last Created Entity());
		Wait Until(Or(Global Variable(IsNight) == 0, Not(Is Alive(Event Player))), 99999);
		Destroy Effect(Event Player.Tmp);
	}
}
'''
s = s.replace('\nrule("[월드 05] 아침 정산")', NIGHT + '\nrule("[월드 05] 아침 정산")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
if missing:
    print('!! 못 찾은 교체:', len(missing))
    for m in missing:
        print('   ', m[:70])
print('  피로 게이트    : %d곳' % s.count('너무 지쳤다'))
print('  위스키 제한    : %d' % s.count('하루 두 잔까지'))
print('  일일 목표/순위 : %d / %d' % (s.count('오늘의 목표 달성'), s.count('RankArr, Sorted Array')))
print('  밤 광기둥      : %d곳' % s.count('IsNight) == 1 ? Color(Sky Blue)'))
