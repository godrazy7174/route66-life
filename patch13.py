"""1. 자막 겹침 (2차)
   남은 충돌은 튜토리얼 상단 자막 <-> 평소 HUD(좌측 상태창 / 우측 행동창)다.
   상단 중앙 자막이 길어지면 좌우로 퍼져 양쪽 HUD를 덮는다.
   -> 튜토리얼 중에는 평소 HUD 3개를 그 플레이어에게만 숨긴다.
      긴 본문은 두 줄로 쪼갠다.

2. 3인칭 시점
   레퍼런스의 3인칭 카메라 기법을 차용:
   플레이어 뒤쪽 지점까지 광선을 쏴 벽에 막히면 그 앞에 카메라를 둔다.
   V 키로 전환 (근접공격은 어차피 '좌클릭 외 공격 금지' 조건상 꺼야 하므로
   그 자리를 시점 전환으로 쓴다).
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 변수 ────────────────────────────────────────────────────────────
s = s.replace("\t\t36: TutDone\n", "\t\t36: TutDone\n\t\t37: ThirdPerson\n")

# ── 1) 튜토리얼 중 평소 HUD 숨김 ───────────────────────────────────
n = 0
for anchor in ('Create HUD Text(Local Player, Custom String("{0}일차',
               'Create HUD Text(Local Player, Custom String("허기 {0}',
               'Create HUD Text(Local Player, Value In Array(Array(Custom String("황야")'):
    i = s.index(anchor)
    s = s[:i] + s[i:].replace('Create HUD Text(Local Player, ',
                              'Create HUD Text(Local Player.TutOn == 0 ? Local Player : False, ', 1)
    n += 1

# 긴 본문을 두 줄로
SPLIT = [
    ("허기 · 갈증 · 피로가 쉬지 않고 줄어든다. 허기나 갈증이 0이면 피를 흘리고, 피로가 0이면 느려진다.",
     "허기 · 갈증 · 피로가 쉬지 않고 줄어든다.\\r\\n허기나 갈증이 0이면 피를 흘리고, 피로가 0이면 느려진다."),
    ("채굴은 안전하지만 느리다. 대신 스무 번에 한 번쯤 금맥이 터진다. 이 게임의 벌이는 대개 이런 식이다.",
     "채굴은 안전하지만 느리다. 대신 스무 번에 한 번쯤 금맥이 터진다.\\r\\n이 게임의 벌이는 대개 이런 식이다."),
    ("무법자는 남의 주머니에서 번다. 강탈은 빠르고 크다. 대신 그 액수만큼 네 목에 현상금이 붙는다.",
     "무법자는 남의 주머니에서 번다. 강탈은 빠르고 크다.\\r\\n대신 그 액수만큼 네 목에 현상금이 붙는다."),
    ("현상금이 붙은 자는 누구든 잡을 수 있다. 현상금 사냥꾼은 그걸로 먹고산다. 벌금을 내면 지워진다.",
     "현상금이 붙은 자는 누구든 잡을 수 있다.\\r\\n현상금 사냥꾼은 그걸로 먹고산다. 벌금을 내면 지워진다."),
    ("사냥감은 좌클릭으로 직접 맞혀야 한다. 스킬은 전부 봉인돼 있고, 총 한 자루가 전부다.",
     "사냥감은 좌클릭으로 직접 맞혀야 한다.\\r\\n스킬은 전부 봉인돼 있고, 총 한 자루가 전부다."),
    ("선택이 쌓여 평판이 된다. 장물은 제값보다 비싸게 팔리지만, 팔 때마다 평판이 깎인다.",
     "선택이 쌓여 평판이 된다.\\r\\n장물은 제값보다 비싸게 팔리지만, 팔 때마다 평판이 깎인다."),
    ("몇 분에 한 번씩 세상에 일이 생긴다. 금맥 소동, 모래폭풍, 무법자 습격. 놓치면 손해다.",
     "몇 분에 한 번씩 세상에 일이 생긴다.\\r\\n금맥 소동, 모래폭풍, 무법자 습격. 놓치면 손해다."),
    ("[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기 · 황야에서 [F]는 강도이자 체포",
     "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물\\r\\n[Shift] 달리기 · [V] 시점 전환 · 황야에서 [F]는 강도"),
    ("먹고 마시고 자는 데 전부 돈이 든다. 벌지 못하면 굶는다. 그래서 직업을 고른다.",
     "먹고 마시고 자는 데 전부 돈이 든다. 벌지 못하면 굶는다.\\r\\n그래서 직업을 고른다."),
]
for a, b in SPLIT:
    s = s.replace(a, b)

# ── HUD 조작 안내에 시점 전환 추가 ─────────────────────────────────
s = s.replace('Custom String("[{0}] 행동 선택   [{1}] 실행   {2}", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)), Custom String("[{0}] 육포  [{1}] 물  [{2}] 달리기", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate)), Input Binding String(Button(Ability 1))))',
              'Custom String("{0}   {1}   {2}", Custom String("[{0}] 행동  [{1}] 실행", Input Binding String(Button(Reload)), Input Binding String(Button(Interact))), Custom String("[{0}] 육포  [{1}] 물", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate))), Custom String("[{0}] 달리기  [{1}] 시점", Input Binding String(Button(Ability 1)), Input Binding String(Button(Melee))))')

# ── 2) 3인칭 시점 ──────────────────────────────────────────────────
CAM = ('Start Camera(Event Player, Ray Cast Hit Position(Add(Position Of(Event Player), Vector(0, 1.5, 0)), '
       'Add(Add(Position Of(Event Player), Vector(0, 1.9, 0)), Multiply(Facing Direction Of(Event Player), -3.2)), '
       'Empty Array, All Players(All Teams), False), '
       'Add(Eye Position(Event Player), Multiply(Facing Direction Of(Event Player), 1000)), 0);')

THIRD = '''
rule("[조작 05] 시점 전환 (V)")
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
		Is Button Held(Event Player, Button(Melee)) == True;
	}

	actions
	{
		If(Event Player.ThirdPerson == 0);
			Set Player Variable(Event Player, ThirdPerson, 1);
			''' + CAM + '''
			Small Message(Event Player, Custom String("3인칭 시점"));
		Else;
			Set Player Variable(Event Player, ThirdPerson, 0);
			Stop Camera(Event Player);
			Small Message(Event Player, Custom String("1인칭 시점"));
		End;
	}
}
'''
s = s.replace('\nrule("[조작 03] 행동 실행 (F)")', THIRD + '\nrule("[조작 03] 행동 실행 (F)")')

# 근접공격 봉인 (좌클릭 외 공격 금지 조건 준수 + V를 시점 전환에 사용)
s = s.replace("\t\tSet Ultimate Charge(Event Player, 0);\n\t\tDisallow Button(Event Player, Button(Ability 1));",
              "\t\tSet Ultimate Charge(Event Player, 0);\n\t\tSet Melee Enabled(Event Player, False);\n\t\tDisallow Button(Event Player, Button(Ability 1));")

# 튜토리얼 종료 시 3인칭이었다면 복구
s = s.replace('''		Destroy HUD Text(Event Player.TutHud);
		Stop Camera(Event Player);''',
'''		Destroy HUD Text(Event Player.TutHud);
		Stop Camera(Event Player);
		If(Event Player.ThirdPerson == 1);
			''' + CAM + '''
		End;''')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  튜토리얼 중 숨기는 HUD : %d개' % n)
print('  두 줄로 쪼갠 자막      : %d개' % sum(1 for a, b in SPLIT if b in s))
print('  3인칭 카메라 호출      : %d곳' % s.count('Start Camera(Event Player, Ray Cast Hit Position(Add(Position Of'))
print('  근접공격 봉인          : %d' % s.count('Set Melee Enabled(Event Player, False)'))
