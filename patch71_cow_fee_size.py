# -*- coding: utf-8 -*-
"""[1] 소몰이 편의: 소가 목장 뒷방·기둥 뒤에 숨는 문제
    - 소환을 목장 -> 역마차 정거장 방향 축(7~11m, 좌우 ±4m)으로 한정.
      두 장소가 같은 홀에 있으므로 뒷방으로는 못 들어간다.
    - 야수 눈 표식처럼 소에도 흰 표식(벽 너머 표시)을 붙인다.

[2] 배달 수주 메시지의 보수가 항상 기본값으로 나오는 문제
    메시지 안에 거리 계산식이 통째로 들어가 재평가 때 무너졌다.
    수주 순간 RunPay 에 확정하고 그 값을 표시한다.

[3] '설정 크기가 너무 큽니다' — 용량 절감 (기능 무손실)
    - R 메뉴 '다음 -> 이름' 미리보기 폐지: 84칸 라벨 배열 통째 사본이었다.
      이제 '[F] 실행  [R] 다음' 만 표시 (본 메뉴 이름은 어차피 크게 떠 있음).
    - 설계자 좌표 목록 15줄 -> 현재 선택 1줄 (이름은 상단에 이미 표시됨).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)
L11 = 'Value In Array(Global Variable(LocPos), 11)'
L12 = 'Value In Array(Global Variable(LocPos), 12)'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ [1] 소 소환 축 한정 + 표식 ════════════════════════════════════
assert 'CowIco' not in s
sub('\t\t77: WallHP\n', '\t\t77: WallHP\n\t\t78: CowIco\n')

sub('Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(%s, Vector(Multiply(Random Real(7, 12), Random Integer(0, 1) == 1 ? 1 : -1), 0, Multiply(Random Real(7, 12), Random Integer(0, 1) == 1 ? 1 : -1)))));' % L12,
    'Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Add(%s, Multiply(Direction Towards(%s, %s), Random Real(7, 11))), Vector(Random Real(-4, 4), 0, Random Real(-4, 4)))));' % (L12, L12, L11))

ICO_MAKE = (T*5 + 'Destroy Icon(Event Player.CowIco);' + NLC
          + T*5 + 'Create Icon(All Players(All Teams), Add(Event Player.CowPos, Vector(0, 1.6, 0)), Circle, Visible To and Position, Color(White), True);' + NLC
          + T*5 + 'Set Player Variable(Event Player, CowIco, Last Created Entity());' + NLC)
sub('''					Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, None);
					Set Player Variable(Event Player, CowFx, Last Created Entity());
					Big Message(Event Player, Custom String("소가 벌판에 있다 — 몸으로 밀어 우리로!"));''',
'''					Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, None);
					Set Player Variable(Event Player, CowFx, Last Created Entity());
''' + ICO_MAKE
+ '''					Big Message(Event Player, Custom String("소가 벌판에 있다 — 몸으로 밀어 우리로!"));''')

ICO_MOVE = (T*3 + 'Destroy Icon(Event Player.CowIco);' + NLC
          + T*3 + 'Create Icon(All Players(All Teams), Add(Event Player.CowPos, Vector(0, 1.6, 0)), Circle, Visible To and Position, Color(White), True);' + NLC
          + T*3 + 'Set Player Variable(Event Player, CowIco, Last Created Entity());' + NLC)
sub('''			Destroy Effect(Event Player.CowFx);
			Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, None);
			Set Player Variable(Event Player, CowFx, Last Created Entity());
		End;''',
'''			Destroy Effect(Event Player.CowFx);
			Create Effect(All Players(All Teams), Sphere, Color(White), Event Player.CowPos, 0.7, None);
			Set Player Variable(Event Player, CowFx, Last Created Entity());
''' + ICO_MOVE + '''		End;''')

sub('''			Set Player Variable(Event Player, CowOn, 0);
			Destroy Effect(Event Player.CowFx);
			Small Message(Event Player, Custom String("소를 잃어버렸다..."));''',
'''			Set Player Variable(Event Player, CowOn, 0);
			Destroy Effect(Event Player.CowFx);
			Destroy Icon(Event Player.CowIco);
			Small Message(Event Player, Custom String("소를 잃어버렸다..."));''')
sub('''			Set Player Variable(Event Player, CowOn, 0);
			Destroy Effect(Event Player.CowFx);
			Set Player Variable(Event Player, RunPay,''',
'''			Set Player Variable(Event Player, CowOn, 0);
			Destroy Effect(Event Player.CowFx);
			Destroy Icon(Event Player.CowIco);
			Set Player Variable(Event Player, RunPay,''')
sub('''		If(Event Player.CowOn == 1);
			Set Player Variable(Event Player, CowOn, 0);
			Destroy Effect(Event Player.CowFx);
		End;''',
'''		If(Event Player.CowOn == 1);
			Set Player Variable(Event Player, CowOn, 0);
			Destroy Effect(Event Player.CowFx);
			Destroy Icon(Event Player.CowIco);
		End;''')

# ══ [2] 수주 보수 확정 표시 ═══════════════════════════════════════
NAMES11 = ('Array(Custom String("식당"), Custom String("협곡 광산"), Custom String("주유소 잡화점"), Custom String("모텔"), '
           'Custom String("정비소 고물상"), Custom String("술집"), Custom String("협곡 개활지"), Custom String("보안관 초소"), '
           'Custom String("무법자 은신처"), Custom String("안내소"), Custom String("대장간"))')
FEE = 'Round To Integer(Add(15, Multiply(Distance Between(%s, Value In Array(Global Variable(LocPos), Event Player.DelDest)), 2)), To Nearest)' % L11
sub('\t\t\t\t\tBig Message(Event Player, Custom String("화물 접수 — {0}까지! 기본 보수 $ {1}", Value In Array(%s, Event Player.DelDest), %s));' % (NAMES11, FEE),
    '\t\t\t\t\tSet Player Variable(Event Player, RunPay, %s);\n' % FEE
  + '\t\t\t\t\tBig Message(Event Player, Custom String("화물 접수 — {0}까지! 기본 보수 $ {1}", Value In Array(%s, Event Player.DelDest), Event Player.RunPay));' % NAMES11)

# ══ [3a] R 메뉴 미리보기 사본 제거 ════════════════════════════════
CNT = 'Array(1, 1, 4, 4, 2, 3, 4, 3, 5, 4, 1, 4, 3, 3, 1, 1)'
START = ', Value In Array(Array(Custom String("[{0}] 실행", Input Binding String(Button(Interact))), Custom String("[{0}] 실행      [{1}] 다음 → {2}"'
i = s.index(START)
j = s.index(', Right, 1, Color(Aqua)', i)
NEWSUB = (', Value In Array(Array(Custom String("[{0}] 실행", Input Binding String(Button(Interact))), '
          'Custom String("[{0}] 실행      [{1}] 다음", Input Binding String(Button(Interact)), Input Binding String(Button(Reload)))), '
          'Value In Array(%s, Add(Local Player.Zone, 1)) > 1 ? 1 : 0)' % CNT)
s = s[:i] + NEWSUB + s[j:]

# ══ [3b] 설계자 좌표 15줄 -> 1줄 ══════════════════════════════════
a = s.index('Create HUD Text(Host Player(), Null, Custom String("{0}   {1}", Custom String("0 식당")')
a = s.rindex(NLC, 0, a) + 1
last = s.index('Custom String("14 식당 3호점")')
b = s.index('Modify Global Variable(ArchHud, Append To Array, Last Text ID());', last)
b = s.index(NLC, b) + 1
ONE = (T*3 + 'Create HUD Text(Host Player(), Null, Custom String("X {0}   Y {1}   Z {2}", X Component Of(Value In Array(Global Variable(LocPos), Global Variable(ArchIdx))), Y Component Of(Value In Array(Global Variable(LocPos), Global Variable(ArchIdx))), Z Component Of(Value In Array(Global Variable(LocPos), Global Variable(ArchIdx)))), Null, Left, 10, Color(White), Color(Aqua), Color(White), Visible To Sort Order String and Color, Default Visibility);' + NLC
     + T*3 + 'Modify Global Variable(ArchHud, Append To Array, Last Text ID());' + NLC)
s = s[:a] + ONE + s[b:]
sub('Custom String("설계자 모드 ON — 15곳 좌표가 왼쪽에 표시됩니다")',
    'Custom String("설계자 모드 ON — 선택한 곳의 좌표가 왼쪽에 표시됩니다")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('완료 — 소 표식·축 소환 / 보수 확정 표시 / 용량 절감 2건')
