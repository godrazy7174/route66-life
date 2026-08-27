"""1. 구역 진입 효과음 제거
2. 3인칭 카메라 끊김
   blendSpeed를 0(매 프레임 스냅)으로 둬서 레이캐스트가 흔들릴 때마다
   카메라가 튀었다. 레퍼런스가 쓰는 60으로 바꿔 보간을 준다.
3. 기본 UI 제거 + 3인칭 고정
   Disable Hero HUD로 체력·궁극기·스킬·탄약 UI를 전부 끈다.
   대신 체력을 우리 HUD에 직접 표시(안 보이면 곤란하니까).
   V 토글을 없애고 항상 3인칭. 사망/부활·튜토리얼 종료 후에도 자동 재적용.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 구역 진입 효과음 제거 ───────────────────────────────────────
old_snd = """			If(Event Player.Zone != -1);
				Play Effect(Event Player, Buff Impact Sound, Color(White), Position Of(Event Player), 100);
			End;
"""
assert s.count(old_snd) == 1, '구역 진입 효과음을 찾지 못함'
s = s.replace(old_snd, "")

# ── 2) 카메라 보간 ─────────────────────────────────────────────────
CAM = ('Start Camera(Event Player, Ray Cast Hit Position(Position Of(Event Player), '
       'Add(Add(Position Of(Event Player), Vector(0, 1.8, 0)), Multiply(Facing Direction Of(Event Player), -2.8)), '
       'Empty Array, All Players(All Teams), False), '
       'Add(Eye Position(Event Player), Multiply(Facing Direction Of(Event Player), 1000)), 60);')

# ── 3) V 토글 제거 -> 상시 3인칭 ───────────────────────────────────
a = s.index('rule("[조작 05] 시점 전환 (V)")')
b = s.index('\nrule("[조작 03] 행동 실행 (F)")')
s = s[:a] + s[b + 1:]

FIX3RD = '''
rule("[코어 12] 3인칭 시점 고정")
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
		Is Alive(Event Player) == True;
	}

	actions
	{
		Wait(0.3, Ignore Condition);
		''' + CAM + '''
	}
}
'''
s = s.replace('\nrule("[조작 03] 행동 실행 (F)")', FIX3RD + '\nrule("[조작 03] 행동 실행 (F)")')

# 튜토리얼 종료 시 무조건 3인칭 복귀
import re
s = re.sub(r'\t\tIf\(Event Player\.ThirdPerson == 1\);\n\t\t\tStart Camera\(Event Player, Ray Cast Hit Position\(Add\(Position Of[^\n]+\n\t\tEnd;',
           '\t\t' + CAM, s)

# ── 3) 기본 영웅 UI 제거 ───────────────────────────────────────────
s = s.replace("\t\tDisable Game Mode In-World UI(Event Player);",
              "\t\tDisable Game Mode In-World UI(Event Player);\n\t\tDisable Hero HUD(Event Player);")

# 체력을 우리 HUD에 표시
s = s.replace('Custom String("허기 {0}   갈증 {1}   피로 {2}", Round To Integer(Local Player.Hunger, Down), Round To Integer(Local Player.Thirst, Down), Round To Integer(Local Player.Energy, Down))',
              'Custom String("{0}      {1}", Custom String("체력 {0}", Round To Integer(Health(Local Player), Down)), Custom String("허기 {0}  갈증 {1}  피로 {2}", Round To Integer(Local Player.Hunger, Down), Round To Integer(Local Player.Thirst, Down), Round To Integer(Local Player.Energy, Down)))')

# 조작 안내에서 시점 전환 제거
s = s.replace('Custom String("[{0}] 달리기  [{1}] 시점", Input Binding String(Button(Ability 1)), Input Binding String(Button(Melee)))',
              'Custom String("[{0}] 달리기", Input Binding String(Button(Ability 1)))')
s = s.replace('[Shift] 달리기 · [V] 시점 전환 · 황야에서 [F]는 강도', '[Shift] 달리기 · 황야에서 [F]는 강도이자 체포')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  구역 진입 효과음 : %d개 남음' % s.count('Buff Impact Sound, Color(White), Position Of(Event Player), 100'))
print('  카메라 보간 60   : %d곳' % s.count(', 60);'))
print('  Hero HUD 제거    : %d' % s.count('Disable Hero HUD'))
print('  V 토글 잔존      : %d' % s.count('시점 전환 (V)'))
print('  체력 표시        : %d' % s.count('Custom String("체력 {0}"'))
