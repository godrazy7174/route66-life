"""실기 3차 피드백 반영.

1. 설계자 모드로 장소를 지정하면 표지판에 옛 이름("시청 · 직업소개소")이 뜬다.
   -> patch4가 설계자 03의 표지판 이름 배열만 놓쳤다. 9개 신규 이름으로 교체.

2. 시작 지점이 수비팀 스폰이다.
   -> Start Forcing Spawn Room(Team 1, 0)으로 공격 스폰 강제.
   덤으로 호스트가 스폰한 뒤에 링을 깔도록 해서(Has Spawned 대기)
   기본 배치가 맵 원점(0,0,0)이 아니라 공격 스폰 주변에 생기게 한다.

3. 무법자가 아무나 쏜다.
   -> 현상금 사냥꾼이 1명 이상일 때만 출현하고, 없으면 즉시 소멸.
      공격 대상도 현상금 사냥꾼으로 한정.

4. 설계자 헤더가 좌표를 x100 정수로 중복 표시한다(좌표 패널과 겹침).
   -> 헤더에서 좌표를 빼고 조작 안내만 남긴다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

NAMES = ['파노라마 다이너', '협곡 광산', '주유소 잡화점', '모텔', '정비소 고물상',
         '살룬', '협곡 개활지', '보안관 초소', '데드락 은신처']
NAMEARR = 'Array(' + ', '.join('Custom String("%s")' % n for n in NAMES) + ')'

# ── 1) 설계자가 다시 만드는 표지판의 옛 이름 배열 교체 ──────────────
a = s.index('Value In Array(Array(Custom String("시청 · 직업소개소")')
b = s.index(', Global Variable(ArchIdx))', a)
s = s[:a] + 'Value In Array(' + NAMEARR + s[b:]
assert '시청 · 직업소개소' not in s, '옛 이름이 남아 있음'

# ── 2) 공격 스폰 강제 + 호스트 스폰 후 링 배치 ──────────────────────
s = s.replace("""		Wait Until(Is Game In Progress(), 30);
		Wait(2, Ignore Condition);
		Call Subroutine(BuildWorld);""",
"""		Wait Until(Is Game In Progress(), 30);
		Start Forcing Spawn Room(Team 1, 0);
		Wait Until(Has Spawned(Host Player()), 30);
		Wait(2, Ignore Condition);
		Call Subroutine(BuildWorld);""")

# ── 3) 무법자: 현상금 사냥꾼이 있을 때만 존재 ───────────────────────
old_spawn = """	actions
	{
		For Global Variable(Idx, 0, 3, 1);
			If(And(Value In Array(Global Variable(OutHP), Global Variable(Idx)) <= 0, Total Time Elapsed() >= Value In Array(Global Variable(OutResp), Global Variable(Idx))));"""
new_spawn = """	actions
	{
		If(Count Of(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Job) == 3)) <= 0);
			For Global Variable(Idx, 0, 3, 1);
				If(Value In Array(Global Variable(OutHP), Global Variable(Idx)) > 0);
					Destroy Effect(Value In Array(Global Variable(OutFx), Global Variable(Idx)));
					Destroy Icon(Value In Array(Global Variable(OutIco), Global Variable(Idx)));
					Set Global Variable At Index(OutHP, Global Variable(Idx), 0);
					Set Global Variable At Index(OutResp, Global Variable(Idx), 0);
				End;
			End;
			Wait(3, Ignore Condition);
			Loop();
		End;
		For Global Variable(Idx, 0, 3, 1);
			If(And(Value In Array(Global Variable(OutHP), Global Variable(Idx)) <= 0, Total Time Elapsed() >= Value In Array(Global Variable(OutResp), Global Variable(Idx))));"""
assert s.count(old_spawn) == 1, '무법자 스폰 관리 구간을 찾지 못함'
s = s.replace(old_spawn, new_spawn)

# 공격 대상을 현상금 사냥꾼으로 한정
s = s.replace(
    'And(Is Alive(Current Array Element), And(Player Variable(Current Array Element, Init) == 1, '
    'Or(Player Variable(Current Array Element, Zone) == -1, Player Variable(Current Array Element, Zone) == 8)))',
    'And(Is Alive(Current Array Element), And(Player Variable(Current Array Element, Job) == 3, '
    'Or(Player Variable(Current Array Element, Zone) == -1, Player Variable(Current Array Element, Zone) == 8)))')

# ── 4) 설계자 헤더 간소화 ───────────────────────────────────────────
a = s.index('Create HUD Text(Host Player(), Custom String("설계자 모드')
b = s.index(', Top, 5, Color(Rose)', a)
s = s[:a] + ('Create HUD Text(Host Player(), Custom String("설계자 모드"), '
             'Value In Array(' + NAMEARR + ', Global Variable(ArchIdx)), '
             'Custom String("[{0}] 이 자리로 지정 → 자동으로 다음    [{1}] 건너뛰기    부하 {2}", '
             'Input Binding String(Button(Interact)), Input Binding String(Button(Reload)), '
             'Round To Integer(Server Load(), To Nearest))') + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  옛 표지판 이름 잔존 : %d' % s.count('시청 · 직업소개소'))
print('  공격 스폰 강제      : %d' % s.count('Start Forcing Spawn Room(Team 1, 0)'))
print('  무법자 직업 게이트  : %d' % s.count('Player Variable(Current Array Element, Job) == 3'))
print('  파노라마 다이너 참조: %d' % s.count('파노라마 다이너'))
