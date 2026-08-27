"""실기 4차 피드백.

1. 공격 스폰에서 시작하지 않음
   -> Start Forcing Spawn Room은 방 번호를 확신할 수 없어 제거.
      대신 SetupPlayer가 '스폰을 마칠 때까지 기다린 뒤' 0번 장소로 텔레포트.
      기존에는 Wait(0.5) 뒤 바로 텔레포트해서, 아직 스폰 전이면 무효였다.

2. 좌표 확정 -> 링 자동 배치를 실측 좌표 하드코딩으로 교체.

3. 서부 용어를 일반 명사로:
   파노라마 다이너->식당, 살룬->술집, 협곡 개활지->협곡 사냥터,
   데드락 은신처->무법자 은신처

4. 보급품 키가 물통을 강제 소비함
   원인: 갈증<=허기면 물부터 마시는데 갈증이 더 빨리 닳아 사실상 항상 물.
   -> 분리. Disallow Button은 입력 감지를 막지 않으므로(레퍼런스에서 확인)
      봉인된 E/Q 버튼을 입력으로 쓴다. E=육포, Q=물.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 3) 이름 변경 (다른 수정보다 먼저: 배열 매칭이 깨지지 않게) ──────
for old, new in [('파노라마 다이너', '식당'), ('살룬', '술집'),
                 ('협곡 개활지', '협곡 사냥터'), ('데드락 은신처', '무법자 은신처')]:
    s = s.replace(old, new)
s = s.replace('Custom String("데드락 갱단에 합류했다 — 무법자")', 'Custom String("무법자가 되었다")')
s = s.replace('Custom String("무법자 합류 — 데드락 갱단")', 'Custom String("무법자 합류")')
s = s.replace('Custom String("이미 데드락 소속이다")', 'Custom String("이미 무법자다")')

# ── 2) 실측 좌표 하드코딩 ───────────────────────────────────────────
COORDS = [
    (44.29, 2.39, 62.28),    # 0 식당
    (21.71, 2.07, 17.81),    # 1 협곡 광산
    (31.96, 2.14, -2.84),    # 2 주유소 잡화점
    (-11.17, 3.02, -4.93),   # 3 모텔
    (-16.24, 3.49, -46.07),  # 4 정비소 고물상
    (-34.83, 3.43, -17.51),  # 5 술집
    (-16.38, 3.31, -27.15),  # 6 협곡 사냥터
    (-75.34, 6.50, 21.36),   # 7 보안관 초소
    (7.66, 8.99, -41.28),    # 8 무법자 은신처
]
vecs = ', '.join('Vector(%s, %s, %s)' % c for c in COORDS)
a = s.index('\t\tSet Global Variable(Anchor, Nearest Walkable Position(Position Of(Host Player())));')
b = s.index('\t\tSet Global Variable(LocRad,')
s = s[:a] + ('\t\tSet Global Variable(LocPos, Array(%s));\n' % vecs) + \
    '\t\tSet Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));\n' + s[b:]

# ── 1) 스폰 완료를 기다린 뒤 텔레포트 ───────────────────────────────
s = s.replace("""		Wait(0.5, Ignore Condition);
		Teleport(Event Player, Value In Array(Global Variable(LocPos), 0));""",
"""		Wait Until(Has Spawned(Event Player), 30);
		Wait(0.5, Ignore Condition);
		Teleport(Event Player, Value In Array(Global Variable(LocPos), 0));""")
s = s.replace("\t\tStart Forcing Spawn Room(Team 1, 0);\n", "")

# ── 4) 보급품 분리: E=육포, Q=물 ───────────────────────────────────
a = s.index('rule("[조작 02] 보급품 사용 (V)")')
b = s.index('\nrule("[조작 03]')
NEW = '''rule("[조작 02] 육포 먹기 (E)")
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
		Is Button Held(Event Player, Button(Ability 2)) == True;
	}

	actions
	{
		If(Value In Array(Event Player.Inv, 0) >= 1);
			Set Player Variable At Index(Event Player, Inv, 0, Subtract(Value In Array(Event Player.Inv, 0), 1));
			Set Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 45)));
			Heal(Event Player, Null, 40);
			Small Message(Event Player, Custom String("육포를 먹었다 — 허기 {0}", Round To Integer(Event Player.Hunger, Down)));
			Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 50);
		Else;
			Small Message(Event Player, Custom String("육포가 없습니다 — 주유소 잡화점에서 구매"));
		End;
	}
}

rule("[조작 02-2] 물 마시기 (Q)")
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
		Is Button Held(Event Player, Button(Ultimate)) == True;
	}

	actions
	{
		If(Value In Array(Event Player.Inv, 1) >= 1);
			Set Player Variable At Index(Event Player, Inv, 1, Subtract(Value In Array(Event Player.Inv, 1), 1));
			Set Player Variable(Event Player, Thirst, Min(100, Add(Event Player.Thirst, 45)));
			Heal(Event Player, Null, 25);
			Small Message(Event Player, Custom String("물을 마셨다 — 갈증 {0}", Round To Integer(Event Player.Thirst, Down)));
			Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 50);
		Else;
			Small Message(Event Player, Custom String("물통이 없습니다 — 주유소 잡화점에서 구매"));
		End;
	}
}

'''
s = s[:a] + NEW + s[b + 1:]

# HUD 키 안내 갱신
s = s.replace('Custom String("[{0}] 행동 선택    [{1}] 실행    [{2}] 보급품", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)), Input Binding String(Button(Melee)))',
              'Custom String("[{0}] 행동 선택   [{1}] 실행   {2}", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)), Custom String("[{0}] 육포   [{1}] 물", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate))))')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  좌표 하드코딩   : %d개' % s.count('Vector(44.29'))
print('  옛 이름 잔존    : %d' % (s.count('파노라마') + s.count('살룬') + s.count('데드락')))
print('  스폰 대기 추가  : %d' % s.count('Wait Until(Has Spawned(Event Player), 30)'))
print('  E 육포 / Q 물   : %d / %d' % (s.count('육포 먹기 (E)'), s.count('물 마시기 (Q)')))
