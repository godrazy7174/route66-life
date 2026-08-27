"""튜토리얼 개편.

1. 스페이스 = 전체 건너뛰기 -> 다음 장면으로 넘기기
   (첫 세 장면이 모두 식당이라 18초간 화면이 안 바뀌어 멈춘 것처럼 보였다.
    장면마다 신호를 초기화하고, 한 번 누르면 한 장면만 넘어간다.)

2. 접속 즉시 자동 재생 -> 식당 옆 '안내소'(10번째 장소)에서 상호작용으로 시작.
   완주 보상은 최초 1회만 지급(반복 수령 방지).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

NAMES = ['식당', '협곡 광산', '주유소 잡화점', '모텔', '정비소 고물상',
         '술집', '협곡 개활지', '보안관 초소', '무법자 은신처', '안내소']

# ── 변수 ────────────────────────────────────────────────────────────
s = s.replace("\t\t35: TutHud\n", "\t\t35: TutHud\n\t\t36: TutDone\n")

# ── 2) 안내소를 10번째 장소로 추가 ─────────────────────────────────
s = s.replace("\t\tSet Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));",
              "\t\tModify Global Variable(LocPos, Append To Array, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 0), Vector(0, 0, -8))));\n"
              "\t\tSet Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));")
s = s.replace("Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8));",
              "Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5));")

# 표지판 + 상세 패널 + 광기둥
pos9 = 'Value In Array(Global Variable(LocPos), 9)'
sign9 = (
    '\t\tCreate In-World Text(All Players(All Teams), Custom String("안내소"), Add(%s, Vector(0, 2.6, 0)), 1.7, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);\n'
    '\t\tCreate In-World Text(Distance Between(Local Player, %s) < 22 ? Local Player : False, Custom String("튜토리얼 — 처음이라면 여기서\\r\\n완주 보상  육포 3 · 물통 3 · $50\\r\\n[{0}] 실행", Input Binding String(Button(Interact))), Add(%s, Vector(0, 1.5, 0)), 0.95, Do Not Clip, Visible To Position and String, Color(White), Default Visibility);\n'
    '\t\tCreate Effect(All Players(All Teams), Light Shaft, Color(Aqua), %s, 1.2, Visible To Position and Radius);\n' % (pos9, pos9, pos9, pos9))
_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + sign9 + s[b:]

# 구역 감지 0..10
s = s.replace('For Player Variable(Event Player, Idx, 0, 9, 1);', 'For Player Variable(Event Player, Idx, 0, 10, 1);')

# 액션 수 / 라벨 / 구역 이름
s = s.replace('Array(1, 4, 2, 3, 1, 3, 3, 1, 2, 3), Add(Event Player.Zone, 1))',
              'Array(1, 4, 2, 3, 1, 3, 3, 1, 2, 3, 1), Add(Event Player.Zone, 1))')
s = s.replace('Custom String("무법자 합류 — 데드락 갱단")', 'Custom String("무법자 합류")')
s = s.replace('Custom String("습격 계획 (무법자 전용)"), Custom String("-"))',
              'Custom String("습격 계획 (무법자 전용)"), Custom String("-"), Custom String("튜토리얼 보기"), Custom String("-"), Custom String("-"), Custom String("-"))')
s = s.replace('Custom String("보안관 초소"), Custom String("무법자 은신처"))',
              'Custom String("보안관 초소"), Custom String("무법자 은신처"), Custom String("안내소"))')

# 디스패처에 9번 분기
s = s.replace('''				Else;
					Call Subroutine(DoPlan);
				End;
			End;
		End;''',
'''				Else;
					Call Subroutine(DoPlan);
				End;
			End;
		Else If(Event Player.Zone == 9);
			Call Subroutine(DoTutorial);
		End;''')

# ── 자동 재생 제거 / 식당 점프 다시보기 규칙 제거 ──────────────────
s = s.replace("\t\tCall Subroutine(DoTutorial);\n\t}\n}", "\t}\n}")
a = s.index('rule("[튜토리얼 03] 다시 보기 (식당에서 점프 2초)")')
b = s.index('\nrule(', a + 5)
s = s[:a] + s[b + 1:]

# ── 1) 스페이스 = 다음 장면 ────────────────────────────────────────
import re
s = re.sub(r'\t\tIf\(Event Player\.TutSkip == 0\);\n(\t\t\tSet Player Variable\(Event Player, TutStep, \d+\);\n)(\t\t\tStart Camera\([^\n]+\n)\t\t\tWait Until\(Event Player\.TutSkip == 1, 5\.5\);\n\t\tEnd;',
           lambda m: ('\t\tSet Player Variable(Event Player, TutSkip, 0);\n' + m.group(1) + m.group(2)
                      + '\t\tWait Until(Event Player.TutSkip == 1, 7);'), s)
s = s.replace('Custom String("[{0}] 건너뛰기", Input Binding String(Button(Jump)))',
              'Custom String("[{0}] 다음", Input Binding String(Button(Jump)))')
s = s.replace('Small Message(Event Player, Custom String("[{0}] 를 누르면 건너뜁니다", Input Binding String(Button(Jump))));\n\t\t', '')

# ── 보상 1회 제한 ──────────────────────────────────────────────────
s = s.replace('''		Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 3));
		Set Player Variable At Index(Event Player, Inv, 1, Add(Value In Array(Event Player.Inv, 1), 3));
		Modify Player Variable(Event Player, Money, Add, 50);
		Big Message(Event Player, Custom String("떠돌이의 첫날이 시작된다"));
		Play Effect(Event Player, Good Explosion, Color(Lime Green), Position Of(Event Player), 2);''',
'''		If(Event Player.TutDone == 0);
			Set Player Variable(Event Player, TutDone, 1);
			Set Player Variable At Index(Event Player, Inv, 0, Add(Value In Array(Event Player.Inv, 0), 3));
			Set Player Variable At Index(Event Player, Inv, 1, Add(Value In Array(Event Player.Inv, 1), 3));
			Modify Player Variable(Event Player, Money, Add, 50);
			Big Message(Event Player, Custom String("안내를 마쳤다 — 육포 3, 물통 3, $50"));
			Play Effect(Event Player, Good Explosion, Color(Lime Green), Position Of(Event Player), 2);
		Else;
			Small Message(Event Player, Custom String("보상은 최초 1회만 지급됩니다"));
		End;''')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  안내소 참조     : %d' % s.count('안내소'))
print('  장면당 신호 초기화: %d' % s.count('Set Player Variable(Event Player, TutSkip, 0);'))
print('  자동 재생 잔존  : %d' % s.count('Teleport(Event Player, Value In Array(Global Variable(LocPos), 0));\n\t\tCall Subroutine(DoTutorial);'))
print('  보상 1회 제한   : %d' % s.count('TutDone == 0'))
