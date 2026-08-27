"""1. R로 행동을 바꿀 수 있다는 걸 HUD에서 직관적으로 보이게
   - 현재 행동에 ▶ 표시 + (2/4) 처럼 몇 개 중 몇 번째인지
   - 그 아래 "[R] 다음 → <다음 행동 이름>" 으로 다음 것을 미리 보여준다
   - 조작 안내는 별도 줄로 분리
2. 주유소 잡화점 패널에서 육포/물 섭취 안내 제거 (전역 안내와 중복)
3. 경제 재조정
   실측: 채굴 1회 기대수익 $94, 하루 생존비 $90 -> 한 번 캐면 하루 해결.
         도박 기대값 +$14 (플레이어 유리).
         숙박 횟수 제한이 없어 피로가 사실상 제약이 아니었다.
   목표: 하루(12분) 순이익 $250 안팎. 큰 지출은 며칠 모아야 하는 구조.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
COUNTS = [1, 4, 2, 3, 1, 3, 3, 1, 2, 3, 1]

# ── 1) 행동 목록 HUD ───────────────────────────────────────────────
a = s.index('Value In Array(Array(Custom String("행동 없음')
b = s.index(', Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx))', a)
FLAT = s[a + len('Value In Array('):b]

cnt = 'Value In Array(Array(%s), Add(Local Player.Zone, 1))' % ', '.join(str(c) for c in COUNTS)
cur = 'Value In Array(%s, Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx))' % FLAT
nxt = 'Value In Array(%s, Add(Multiply(Add(Local Player.Zone, 1), 4), Modulo(Add(Local Player.MenuIdx, 1), %s)))' % (FLAT, cnt)

sub = 'Custom String("▶  {0}      ({1}/{2})", %s, Add(Local Player.MenuIdx, 1), %s)' % (cur, cnt)
txt = ('Value In Array(Array(Custom String("[{0}] 실행", Input Binding String(Button(Interact))), '
       'Custom String("[{0}] 실행      [{1}] 다음 → {2}", Input Binding String(Button(Interact)), '
       'Input Binding String(Button(Reload)), %s)), %s > 1 ? 1 : 0)' % (nxt, cnt))

# 기존 subheader(행동 라벨) + text(조작 안내) 교체
old_sub_start = s.index('Value In Array(Array(Custom String("행동 없음')
old_sub_end = s.index('))', s.index(', Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx))', old_sub_start)) + 2
old_txt_start = s.index('Custom String("{0}   {1}   {2}", Custom String("[{0}] 행동', old_sub_end)
old_txt_end = s.index(', Right, 1,', old_txt_start)
s = s[:old_sub_start] + sub + ', ' + txt + s[old_txt_end:]

# 조작 안내를 별도 HUD 로
KEYS = ('\t\tCreate HUD Text(Local Player.TutOn == 0 ? Local Player : False, Null, Null, '
        'Custom String("{0}   {1}   {2}", Custom String("[{0}] 육포  [{1}] 물", Input Binding String(Button(Ability 2)), '
        'Input Binding String(Button(Ultimate))), Custom String("[{0}] 달리기", Input Binding String(Button(Ability 1))), '
        'Custom String("황야에서 [{0}] 강도/체포", Input Binding String(Button(Interact)))), '
        'Right, 2, Color(White), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);\n')
i = s.index('rule("[코어 08] 공용 HUD 생성")')
j = s.index('\t}\n}', i)
s = s[:j] + KEYS + s[j:]

# ── 2) 주유소 패널에서 섭취 안내 제거 ──────────────────────────────
s = s.replace('Custom String("육포 $15   물통 $10   육포 5개 $65\\r\\n[{0}] 육포 먹기   [{1}] 물 마시기", Input Binding String(Button(Ability 2)), Input Binding String(Button(Ultimate)))',
              'Custom String("육포 $15      물통 $10      육포 5개 묶음 $65")')

# ── 3) 경제 재조정 ─────────────────────────────────────────────────
ECON = [
    # 시세
    ('Set Global Variable(OrePrice, 12);', 'Set Global Variable(OrePrice, 3);'),
    ('Set Global Variable(HidePrice, 18);', 'Set Global Variable(HidePrice, 6);'),
    ('Set Global Variable(OrePrice, Random Integer(8, 22));', 'Set Global Variable(OrePrice, Random Integer(2, 5));'),
    ('Set Global Variable(HidePrice, Random Integer(12, 34));', 'Set Global Variable(HidePrice, Random Integer(4, 9));'),
    # 채굴
    ('Chase Player Variable Over Time(Event Player, WorkProg, 100, 2.6, Destination and Duration);',
     'Chase Player Variable Over Time(Event Player, WorkProg, 100, 3.5, Destination and Duration);'),
    ('Wait(2.6, Ignore Condition);', 'Wait(3.5, Ignore Condition);'),
    ('If(Event Player.Roll <= 5);\n\t\t\tSet Player Variable(Event Player, Roll, Random Integer(250, 700));',
     'If(Event Player.Roll <= 3);\n\t\t\tSet Player Variable(Event Player, Roll, Random Integer(60, 140));'),
    ('Set Player Variable(Event Player, Roll, Random Integer(1, 3));',
     'Set Player Variable(Event Player, Roll, Random Integer(1, 2));'),
    ('Modify Player Variable(Event Player, Money, Add, 150);\n\t\t\tBig Message(Event Player, Custom String("채굴 {0}회 달성 — 보너스 $150", Event Player.MineCount));',
     'Modify Player Variable(Event Player, Money, Add, 30);\n\t\t\tBig Message(Event Player, Custom String("채굴 {0}회 달성 — 보너스 $30", Event Player.MineCount));'),
    ('Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 3)));\n\t\tSet Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.5)));\n\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2)));',
     'Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 5)));\n\t\tSet Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 2)));\n\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2.5)));'),
    # 사냥
    ('Modify Player Variable(Event Player, Money, Add, 180);', 'Modify Player Variable(Event Player, Money, Add, 70);'),
    ('Big Message(All Players(All Teams), Custom String("{0} — 대형 사냥감 포획! $180", Event Player));',
     'Big Message(All Players(All Teams), Custom String("{0} — 대형 사냥감 포획! $70", Event Player));'),
    # 무법자 현상금
    ('Set Global Variable(BotBounty, 60);', 'Set Global Variable(BotBounty, 25);'),
    ('Set Global Variable(BotBounty, 180);', 'Set Global Variable(BotBounty, 80);'),
    ('Add(Total Time Elapsed(), 14)', 'Add(Total Time Elapsed(), 25)'),
    # 습격 계획
    ('Set Player Variable(Event Player, Roll, Random Integer(400, 900));',
     'Set Player Variable(Event Player, Roll, Random Integer(150, 300));'),
    ('Set Player Variable(Event Player, Roll, Random Integer(30, 60));',
     'Set Player Variable(Event Player, Roll, Random Integer(10, 20));'),
    ('Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 4)));\n\t\tSet Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.5)));',
     'Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 8)));\n\t\tSet Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 3)));\n\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 3)));'),
    # 도박
    ('If(Event Player.Roll <= 8);\n\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 400);',
     'If(Event Player.Roll <= 5);\n\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 300);'),
    ('Custom String("{0} — 술집에서 잭팟! $400", Event Player)', 'Custom String("{0} — 술집에서 잭팟! $300", Event Player)'),
    ('Else If(Event Player.Roll <= 35);\n\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 120);',
     'Else If(Event Player.Roll <= 30);\n\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 90);'),
    ('Custom String("이겼다 — $120 획득")', 'Custom String("이겼다 — $90 획득")'),
    # 패시브 욕구
    ('Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1)));\n\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 1.2)));\n\t\tSet Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 0.6)));',
     'Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.2)));\n\t\tSet Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 1.5)));\n\t\tSet Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 0.5)));'),
    # 숙박 / 위스키 / 시작 자금
    ('If(Event Player.Money < 40);', 'If(Event Player.Money < 60);'),
    ('Custom String("숙박비가 부족합니다 ($40 필요)")', 'Custom String("숙박비가 부족합니다 ($60 필요)")'),
    ('Modify Player Variable(Event Player, Money, Subtract, 40);', 'Modify Player Variable(Event Player, Money, Subtract, 60);'),
    ('Custom String("숙박 $40 — 피로 완전 회복")', 'Custom String("숙박 $60 — 하루 한 번")'),
    ('Custom String("숙박 $40\\r\\n피로가 완전히 회복된다")', 'Custom String("숙박 $60 — 하루 한 번\\r\\n피로가 완전히 회복된다")'),
    ('Custom String("$40에 하룻밤. 피로가 완전히 회복된다.")', 'Custom String("$60에 하룻밤. 피로가 완전히 회복된다. 하루 한 번뿐이다.")'),
    ('If(Event Player.Money >= 20);\n\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 20);',
     'If(Event Player.Money >= 25);\n\t\t\t\t\tModify Player Variable(Event Player, Money, Subtract, 25);'),
    ('Custom String("돈이 부족합니다 ($20 필요)")', 'Custom String("돈이 부족합니다 ($25 필요)")'),
    ('Custom String("위스키 $20 — 피로 회복")', 'Custom String("위스키 $25 — 피로 회복")'),
    ('Custom String("위스키 $20 — 피로 회복\\r\\n카드 도박 $50\\r\\n소문 듣기")', 'Custom String("위스키 $25 — 피로 회복\\r\\n카드 도박 $50\\r\\n소문 듣기")'),
    ('Set Player Variable(Event Player, Money, 120);', 'Set Player Variable(Event Player, Money, 60);'),
    ('Modify Player Variable(Event Player, Money, Add, 50);\n\t\t\tBig Message(Event Player, Custom String("안내를 마쳤다 — 육포 3, 물통 3, $50"));',
     'Modify Player Variable(Event Player, Money, Add, 30);\n\t\t\tBig Message(Event Player, Custom String("안내를 마쳤다 — 육포 3, 물통 3, $30"));'),
    ('Custom String("완주 보상  육포 3 · 물통 3 · $50\\r\\n[{0}] 실행"', 'Custom String("완주 보상  육포 3 · 물통 3 · $30\\r\\n[{0}] 실행"'),
    ('Custom String("가진 건 $120과 육포 둘, 물 둘. 어디서 무엇으로 살아갈지는 네가 정한다.")',
     'Custom String("가진 건 $60과 육포 둘, 물 둘. 어디서 무엇으로 살아갈지는 네가 정한다.")'),
]
missing = []
for old, new in ECON:
    if old not in s:
        missing.append(old.split('\n')[0][:70])
    else:
        s = s.replace(old, new, 1)

# 사냥 추적에도 소모 추가
s = s.replace('''		Big Message(Event Player, Value In Array(Array(Custom String("사냥감 발견 — 좌클릭으로 사격"), Custom String("대형 사냥감! 세 발이 필요하다")), Event Player.HuntKind));''',
'''		Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, 4)));
		Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, 1.5)));
		Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 2)));
		Big Message(Event Player, Value In Array(Array(Custom String("사냥감 발견 — 좌클릭으로 사격"), Custom String("대형 사냥감! 세 발이 필요하다")), Event Player.HuntKind));''')

# 숙박 하루 1회
s = s.replace("\t\t36: TutDone\n", "\t\t36: TutDone\n\t\t37: SleepDay\n")
s = s.replace("\t\tSet Player Variable(Event Player, MineCount, 0);",
              "\t\tSet Player Variable(Event Player, MineCount, 0);\n\t\tSet Player Variable(Event Player, SleepDay, -1);")
s = s.replace('''		If(Event Player.Money < 60);
			Small Message(Event Player, Custom String("숙박비가 부족합니다 ($60 필요)"));
			Abort;
		End;''',
'''		If(Event Player.SleepDay == Global Variable(Day));
			Small Message(Event Player, Custom String("오늘은 이미 잤다 — 내일 아침에 다시"));
			Abort;
		End;
		If(Event Player.Money < 60);
			Small Message(Event Player, Custom String("숙박비가 부족합니다 ($60 필요)"));
			Abort;
		End;
		Set Player Variable(Event Player, SleepDay, Global Variable(Day));''')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
if missing:
    print('!! 못 찾은 교체 %d건:' % len(missing))
    for m in missing:
        print('   ', m)
else:
    print('  경제 항목 %d건 전부 교체됨' % len(ECON))
print('  숙박 하루 1회 : %d' % s.count('SleepDay == Global Variable(Day)'))
print('  행동 목록 HUD : %d' % s.count('▶  {0}'))
