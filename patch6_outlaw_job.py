"""무법자를 플레이어 직업(Job 4)으로 추가.

설계:
 - 전직 장소는 다이너 구인 게시판이 아니라 데드락 은신처.
   갱단에 들어가는 걸 시청 게시판에서 신청할 수는 없으니까.
 - 은신처 행동 3개: 무법자 합류 / 장물 거래 / 습격 계획
 - 무법자 혜택: 강도 강탈률 25% -> 40%, 장물 130% -> 165%
 - 무법자 노가다: 습격 계획 3.5초. 3회 모으면 역마차 습격이 터져
   $400~900 + 전체 공지, 대신 현상금 +200.
 - NPC 무법자는 그대로 현상금 사냥꾼 전용 PvE로 남는다(서로 안 쏨).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 변수/서브루틴 ───────────────────────────────────────────────────
s = s.replace("\t\t29: ShotTgt\n", "\t\t29: ShotTgt\n\t\t30: Plan\n")
s = s.replace("\t6: RollEvent\n", "\t6: RollEvent\n\t7: DoPlan\n")
s = s.replace("Set Player Variable(Event Player, JobXP, Array(0, 0, 0, 0));",
              "Set Player Variable(Event Player, JobXP, Array(0, 0, 0, 0, 0));\n\t\tSet Player Variable(Event Player, Plan, 0);")

# ── 직업 이름 배열 (HUD) ────────────────────────────────────────────
s = s.replace('Array(Custom String("떠돌이"), Custom String("광부"), Custom String("사냥꾼"), Custom String("현상금 사냥꾼"))',
              'Array(Custom String("떠돌이"), Custom String("광부"), Custom String("사냥꾼"), Custom String("현상금 사냥꾼"), Custom String("무법자"))')

# ── 은신처 액션 수 1 -> 3 ───────────────────────────────────────────
s = s.replace('Array(1, 4, 2, 3, 1, 3, 3, 1, 2, 1), Add(Event Player.Zone, 1))',
              'Array(1, 4, 2, 3, 1, 3, 3, 1, 2, 3), Add(Event Player.Zone, 1))')

# ── 은신처 라벨 3개 ─────────────────────────────────────────────────
s = s.replace('Custom String("장물 거래 — 시세 130%, 평판 -5"), Custom String("-"), Custom String("-"), Custom String("-"))',
              'Custom String("무법자 합류 — 데드락 갱단"), Custom String("장물 거래"), Custom String("습격 계획 (무법자 전용)"), Custom String("-"))')

# ── 은신처 분기 전면 교체 ───────────────────────────────────────────
a = s.index('\t\tElse If(Event Player.Zone == 8);')
b = s.index('\n\t\tEnd;\n\t}\n}', a)
new8 = '''		Else If(Event Player.Zone == 8);
			If(Event Player.MenuIdx == 0);
				If(Event Player.Job == 4);
					Small Message(Event Player, Custom String("이미 데드락 소속이다"));
				Else;
					Set Player Variable(Event Player, Job, 4);
					Set Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 5)));
					Big Message(Event Player, Custom String("데드락 갱단에 합류했다 — 무법자"));
					Small Message(Event Player, Custom String("강탈 40%, 장물 165%. 습격 계획 3회면 역마차를 턴다"));
					Play Effect(Event Player, Ring Explosion, Color(Purple), Position Of(Event Player), 2);
				End;
			Else If(Event Player.MenuIdx == 1);
				Set Player Variable(Event Player, Roll, Add(Multiply(Value In Array(Event Player.Inv, 2), Global Variable(OrePrice)), Multiply(Value In Array(Event Player.Inv, 3), Global Variable(HidePrice))));
				If(Event Player.Job == 4);
					Set Player Variable(Event Player, Roll, Round To Integer(Multiply(Event Player.Roll, 1.65), Down));
				Else;
					Set Player Variable(Event Player, Roll, Round To Integer(Multiply(Event Player.Roll, 1.3), Down));
				End;
				If(Event Player.Roll > 0);
					Modify Player Variable(Event Player, Money, Add, Event Player.Roll);
					Modify Player Variable(Event Player, Earned, Add, Event Player.Roll);
					Set Player Variable At Index(Event Player, Inv, 2, 0);
					Set Player Variable At Index(Event Player, Inv, 3, 0);
					Set Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 5)));
					Small Message(Event Player, Custom String("장물을 넘겼다 — $ {0}   (평판 -5)", Event Player.Roll));
					Play Effect(Event Player, Buff Explosion Sound, Color(Purple), Position Of(Event Player), 100);
				Else;
					Small Message(Event Player, Custom String("넘길 원석이나 가죽이 없습니다"));
				End;
			Else;
				If(Event Player.Job != 4);
					Small Message(Event Player, Custom String("무법자만 할 수 있다 — 먼저 합류해라"));
				Else;
					Call Subroutine(DoPlan);
				End;
			End;'''
s = s[:a] + new8 + s[b:]

# ── 강도: 무법자는 40% ──────────────────────────────────────────────
old_rob = '\t\t\tSet Player Variable(Event Player, Roll, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.25), Down));'
new_rob = ('\t\t\tSet Player Variable(Event Player, Roll, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.25), Down));\n'
           '\t\t\tIf(Event Player.Job == 4);\n'
           '\t\t\t\tSet Player Variable(Event Player, Roll, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.4), Down));\n'
           '\t\t\tEnd;')
assert s.count(old_rob) == 1, '강도 계산 구간을 찾지 못함'
s = s.replace(old_rob, new_rob)

# ── DoPlan 서브루틴 ────────────────────────────────────────────────
DOPLAN = '''
rule("[직업 04] DoPlan")
{
	event
	{
		Subroutine;
		DoPlan;
	}

	actions
	{
		Set Player Variable(Event Player, Busy, 1);
		Set Player Variable(Event Player, WorkProg, 0);
		Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("습격 계획 중..."), Top, 0, Color(Purple), Color(White), Visible To Values and Color, Default Visibility);
		Set Player Variable(Event Player, WorkBar, Last Text ID());
		Chase Player Variable Over Time(Event Player, WorkProg, 100, 3.5, Destination and Duration);
		Wait(3.5, Ignore Condition);
		Stop Chasing Player Variable(Event Player, WorkProg);
		Destroy HUD Text(Event Player.WorkBar);
		Modify Player Variable(Event Player, Plan, Add, 1);
		Set Player Variable At Index(Event Player, JobXP, 4, Add(Value In Array(Event Player.JobXP, 4), 15));
		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 4)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.5)));
		If(Event Player.Plan >= 3);
			Set Player Variable(Event Player, Plan, 0);
			Set Player Variable(Event Player, Roll, Random Integer(400, 900));
			Modify Player Variable(Event Player, Money, Add, Event Player.Roll);
			Modify Player Variable(Event Player, Earned, Add, Event Player.Roll);
			Modify Player Variable(Event Player, Bounty, Add, 200);
			Set Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 15)));
			Big Message(All Players(All Teams), Custom String("{0} — 역마차 습격 성공! $ {1}", Event Player, Event Player.Roll));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Purple), Position Of(Event Player), 4);
			Wait(2, Ignore Condition);
			Small Message(Event Player, Custom String("현상금 $ {0} — 이제 쫓기는 몸이다", Event Player.Bounty));
		Else;
			Set Player Variable(Event Player, Roll, Random Integer(30, 60));
			Modify Player Variable(Event Player, Money, Add, Event Player.Roll);
			Small Message(Event Player, Custom String("계획 {0}/3 — 정찰비 $ {1}", Event Player.Plan, Event Player.Roll));
		End;
		Set Player Variable(Event Player, Busy, 0);
	}
}
'''
s = s.replace('\nrule("[생활 01] DoSleep")', DOPLAN + '\nrule("[생활 01] DoSleep")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('무법자 직업 추가 완료')
for probe in ('무법자 합류', 'DoPlan', 'Plan, Add, 1', '0.4), Down'):
    print('  %-16s %d회' % (probe, s.count(probe)))
