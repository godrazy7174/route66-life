"""튜토리얼 추가 (레퍼런스 '헬조선' 방식 차용).

레퍼런스 구조: Rooted+Phased Out+Invisible로 플레이어를 고정하고
Start Camera로 시점을 옮겨가며 Small Message로 설명, 마지막에 완주 보상.

우리 쪽 개선점:
 - 카메라 위치를 별도 좌표로 찍지 않고 9곳 실측 좌표에서 자동 계산한다
   (해당 장소 상공 9m, 뒤 13m에서 그 장소를 내려다봄).
 - 최초 접속 시 자동 1회 실행. 점프로 언제든 건너뛰기.
 - 식당에서 제자리에 서서 점프 2초로 다시 볼 수 있다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 변수/서브루틴 ───────────────────────────────────────────────────
s = s.replace("\t\t31: Sprinting\n", "\t\t31: Sprinting\n\t\t32: TutOn\n\t\t33: TutSkip\n")
s = s.replace("\t7: DoPlan\n", "\t7: DoPlan\n\t8: DoTutorial\n")

# 최초 접속 시 자동 실행
s = s.replace("""		Big Message(Event Player, Custom String("당신은 66번 국도의 떠돌이입니다"));""",
              """		Call Subroutine(DoTutorial);""")
s = s.replace("""		Small Message(Event Player, Custom String("시청에서 직업을 고르세요.  [{0}] 선택  [{1}] 실행", Input Binding String(Button(Reload)), Input Binding String(Button(Interact))));\n""", "")

# ── 튜토리얼 대본 (장소 인덱스, 제목, 설명, 초) ────────────────────
BEATS = [
    (0, "66번 국도", "여기서 살아남아라. 굶지 않고, 목마르지 않고, 지치지 않는 것이 시작이다.", 4.5),
    (0, "허기 · 갈증 · 피로", "셋 다 시간이 지나면 줄어든다. 허기나 갈증이 0이 되면 피를 흘리기 시작한다.", 4.5),
    (0, "식당", "직업을 고르고 밥을 먹는 곳. 죽으면 여기로 돌아온다.", 4),
    (1, "협곡 광산", "광부의 일터. 캘 때마다 원석이 나오고, 가끔 금맥이 터진다.", 4),
    (6, "협곡 개활지", "사냥꾼의 일터. 흔적을 쫓으면 사냥감이 나타난다. 좌클릭으로 직접 쏴라.", 4.5),
    (8, "무법자 은신처", "무법자가 되는 곳. 강탈과 습격으로 크게 벌지만, 목에 값이 붙는다.", 4.5),
    (7, "보안관 초소", "현상금 사냥꾼이 상금을 확인하고, 수배자가 벌금을 내는 곳.", 4),
    (2, "주유소 잡화점", "육포와 물통을 산다. [E]로 먹고 [Q]로 마신다.", 4),
    (4, "정비소 고물상", "원석과 가죽을 판다. 시세는 매일 아침 바뀌니 값을 보고 팔아라.", 4),
    (5, "술집", "위스키로 피로를 풀고, 카드로 돈을 잃는다.", 3.5),
    (3, "모텔", "$40에 하룻밤. 피로가 완전히 회복된다.", 3.5),
    (0, "조작", "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기", 5),
    (0, "밤을 조심해라", "밤이 되면 현상금이 두 배가 된다. 황야에서 [F]는 강도이자 체포다.", 4.5),
]

beats = []
for i, (loc, title, body, t) in enumerate(BEATS):
    beats.append('\t\tIf(Event Player.TutSkip == 0);')
    beats.append('\t\t\tStart Camera(Event Player, Add(Value In Array(Global Variable(LocPos), %d), Vector(0, 9, 13)), Value In Array(Global Variable(LocPos), %d), 0);' % (loc, loc))
    beats.append('\t\t\tBig Message(Event Player, Custom String("%s"));' % title)
    beats.append('\t\t\tSmall Message(Event Player, Custom String("%s"));' % body)
    beats.append('\t\t\tWait Until(Event Player.TutSkip == 1, %s);' % t)
    beats.append('\t\tEnd;')

TUTORIAL = '''
rule("[튜토리얼 01] DoTutorial")
{
	event
	{
		Subroutine;
		DoTutorial;
	}

	actions
	{
		Set Player Variable(Event Player, TutOn, 1);
		Set Player Variable(Event Player, TutSkip, 0);
		Set Player Variable(Event Player, Busy, 1);
		Set Status(Event Player, Null, Rooted, 9999);
		Set Status(Event Player, Null, Phased Out, 9999);
		Set Invisible(Event Player, All);
		Small Message(Event Player, Custom String("[{0}] 를 누르면 건너뜁니다", Input Binding String(Button(Jump))));
		Wait(2, Ignore Condition);
''' + '\n'.join(beats) + '''
		Stop Camera(Event Player);
		Set Invisible(Event Player, None);
		Clear Status(Event Player, Phased Out);
		Clear Status(Event Player, Rooted);
		Teleport(Event Player, Value In Array(Global Variable(LocPos), 0));
		Set Player Variable(Event Player, TutOn, 0);
		Set Player Variable(Event Player, Busy, 0);
		Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 3));
		Set Player Variable At Index(Event Player, Inv, 1, Add(Value In Array(Event Player.Inv, 1), 3));
		Modify Player Variable(Event Player, Money, Add, 50);
		Big Message(Event Player, Custom String("떠돌이의 첫날이 시작된다"));
		Small Message(Event Player, Custom String("보급품 육포 3, 물통 3, 그리고 $50을 받았다"));
		Play Effect(Event Player, Good Explosion, Color(Lime Green), Position Of(Event Player), 2);
	}
}

rule("[튜토리얼 02] 건너뛰기 (점프)")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Event Player.TutOn == 1;
		Is Button Held(Event Player, Button(Jump)) == True;
	}

	actions
	{
		Set Player Variable(Event Player, TutSkip, 1);
	}
}

rule("[튜토리얼 03] 다시 보기 (식당에서 점프 2초)")
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
		Event Player.TutOn == 0;
		Event Player.Busy == 0;
		Event Player.Zone == 0;
		Is Moving(Event Player) == False;
		Is Button Held(Event Player, Button(Jump)) == True;
	}

	actions
	{
		Wait(2, Abort When False);
		Call Subroutine(DoTutorial);
	}
}
'''
s = s.replace('\nrule("[코어 05] 캐서디 스킬 봉인")', TUTORIAL + '\nrule("[코어 05] 캐서디 스킬 봉인")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('튜토리얼 추가 완료')
print('  장면 수      : %d' % len(BEATS))
print('  DoTutorial   : %d회 참조' % s.count('DoTutorial'))
print('  건너뛰기/다시보기: %d / %d' % (s.count('[튜토리얼 02]'), s.count('[튜토리얼 03]')))
