# -*- coding: utf-8 -*-
"""밤 연출 재작업.

기존: 플레이어 눈앞에 검은 Cloud 이펙트 -> 밤이 아니라 화면 얼룩으로 보인다.
      워크샵에는 조명/후처리 제어가 없어 '어둡게 만들기'는 애초에 불가능하다.

방향 전환: 어둡게 하는 대신 '밤이 되었다는 신호'를 여러 채널로 준다.
  1) 마을 전체에 등불이 켜진다 (장소 광기둥이 주황으로 커짐)
  2) 각자 등불을 들고 다닌다 (플레이어를 따라다니는 주황 발광체)
  3) HUD 날짜/시각 색이 파랗게 바뀐다
  4) 밤에만 길 위의 발견 확률이 오른다 (밤에 돌아다닐 이유)
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 검은 구름 -> 등불 ───────────────────────────────────────────
a = s.index('rule("[월드 08] 밤 연출")')
b = s.index('\nrule(', a + 5)
NEW = '''rule("[월드 08] 밤 — 등불")
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
		Create Effect(All Players(All Teams), Orb, Color(Orange), Event Player, 0.35, Visible To Position and Radius);
		Set Player Variable(Event Player, Tmp, Last Created Entity());
		Create Effect(All Players(All Teams), Good Aura, Color(Orange), Event Player, 1.4, Visible To Position and Radius);
		Set Player Variable(Event Player, Amt, Last Created Entity());
		Wait Until(Or(Global Variable(IsNight) == 0, Not(Is Alive(Event Player))), 99999);
		Destroy Effect(Event Player.Tmp);
		Destroy Effect(Event Player.Amt);
	}
}
'''
s = s[:a] + NEW + s[b + 1:]

# ── 2) 장소 광기둥: 밤에는 주황 등불로 커진다 ──────────────────────
s = re.sub(r'Global Variable\(IsNight\) == 1 \? Color\(Sky Blue\) : Color\(Yellow\)(, Value In Array\(Global Variable\(LocPos\), \d+\), )1\.2(, Visible To Position Radius and Color\))',
           r'Global Variable(IsNight) == 1 ? Color(Orange) : Color(Yellow)\1Global Variable(IsNight) == 1 ? 2.2 : 1.2\2', s)

# ── 3) HUD 날짜/시각 색을 밤에 파랗게 ──────────────────────────────
s = s.replace('Global Variable(IsNight)), Custom String("소지금   $ {0}", Local Player.Money)',
              'Global Variable(IsNight)), Custom String("소지금   $ {0}", Local Player.Money)')
s = s.replace(', Left, 1, Color(Yellow), Color(Lime Green), Color(White), Visible To Sort Order String and Color',
              ', Left, 1, Global Variable(IsNight) == 1 ? Color(Sky Blue) : Color(Yellow), Color(Lime Green), Color(White), Visible To Sort Order String and Color')

# ── 4) 밤 진입/해제 연출 강화 ──────────────────────────────────────
s = s.replace('''			Set Global Variable(IsNight, 1);
			Big Message(All Players(All Teams), Custom String("밤이 내려앉았다 — 무법자들이 움직인다"));''',
'''			Set Global Variable(IsNight, 1);
			Big Message(All Players(All Teams), Custom String("밤이 내려앉았다 — 마을에 등불이 켜진다"));
			Small Message(All Players(All Teams), Custom String("현상금 2배. 길 위에서 뭔가 주울 확률도 오른다"));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Value In Array(Global Variable(LocPos), 0), 6);''')
s = s.replace('''		Else If(And(Global Variable(IsNight) == 1, And(Global Variable(Clock) >= 360, Global Variable(Clock) < 1200)));
			Set Global Variable(IsNight, 0);
		End;''',
'''		Else If(And(Global Variable(IsNight) == 1, And(Global Variable(Clock) >= 360, Global Variable(Clock) < 1200)));
			Set Global Variable(IsNight, 0);
			Big Message(All Players(All Teams), Custom String("동이 텄다"));
		End;''')

# ── 5) 밤에는 길 위의 발견 확률 상승 ───────────────────────────────
s = s.replace('		Wait(18, Ignore Condition);\n\t\tIf(Random Integer(1, 100) <= 12);',
              '		Wait(18, Ignore Condition);\n\t\tIf(Random Integer(1, 100) <= Add(12, Multiply(Global Variable(IsNight), 10)));')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  검은 구름 제거     : %s' % ('OK' if 'Cloud, Color(Black)' not in s else '실패'))
print('  플레이어 등불      : %d' % s.count('Orb, Color(Orange), Event Player'))
print('  광기둥 밤 주황     : %d곳' % s.count('IsNight) == 1 ? Color(Orange)'))
print('  HUD 밤 색상        : %d' % s.count('IsNight) == 1 ? Color(Sky Blue) : Color(Yellow), Color(Lime Green)'))
print('  밤 발견 확률 상승  : %d' % s.count('Add(12, Multiply(Global Variable(IsNight), 10))'))
