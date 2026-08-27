"""돈을 버는 이유를 만든다.

현재 문제: 수입은 전부 의식주로 되돌아가고, 남은 돈이 갈 곳이 없다.
           목표도 없고 진행도가 눈에 보이지도 않는다.

세 층으로 답한다.
  1층 장비(대장간, 11번째 장소) — 즉각 체감되고 반복 구매되는 목표
       곡괭이 4단계 / 가죽 배낭 / 말
  2층 내 방(모텔)   — 큰 한 방 목표. 숙박 무료 + 하루 1회 제한 해제
  3층 칭호          — 순자산에 따라 머리 위 호칭이 바뀐다(레퍼런스의 『 』 표기 차용).
                      혼자 해도 보이고, 여럿이면 서열이 보인다.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

NAMES = ['식당', '협곡 광산', '주유소 잡화점', '모텔', '정비소 고물상',
         '술집', '협곡 개활지', '보안관 초소', '무법자 은신처', '안내소', '대장간']
COUNTS = [1, 4, 2, 3, 2, 3, 3, 1, 2, 3, 1, 3]
ACTIONS = [
    ['행동 없음 — 마을로 이동하세요', '-', '-', '-'],
    ['전직: 광부', '전직: 사냥꾼', '전직: 현상금 사냥꾼', '식사 $12 — 허기 회복'],
    ['채굴하기', '정밀 탐사 $30', '-', '-'],
    ['육포 구매 $15', '물통 구매 $10', '육포 5개 묶음 $65', '-'],
    ['숙박 $60 — 하루 한 번', '내 방 마련 $3500', '-', '-'],
    ['원석 전량 판매', '가죽 전량 판매', '오늘의 시세', '-'],
    ['위스키 $25 — 피로 회복', '카드 도박 $50', '소문 듣기', '-'],
    ['흔적 추적 — 사냥감 출현', '-', '-', '-'],
    ['벌금 납부 $100 — 현상금 말소', '현상금 게시판', '-', '-'],
    ['무법자 합류', '장물 거래', '습격 계획 (무법자 전용)', '-'],
    ['튜토리얼 보기', '-', '-', '-'],
    ['곡괭이 강화', '가죽 배낭 $800', '말 $2000', '-'],
]


def arr(items):
    return 'Array(' + ', '.join('Custom String("%s")' % x for x in items) + ')'


FLAT = arr([a for g in ACTIONS for a in g])
ZONEARR = arr(['황야'] + NAMES)

# ── 변수 ────────────────────────────────────────────────────────────
s = s.replace("\t\t38: Amt\n", "\t\t38: Amt\n\t\t39: Pick\n\t\t40: HasBag\n\t\t41: HasHorse\n\t\t42: HasHome\n")
s = s.replace("\t\tSet Player Variable(Event Player, SleepDay, -1);",
              "\t\tSet Player Variable(Event Player, SleepDay, -1);\n"
              "\t\tSet Player Variable(Event Player, Pick, 0);\n"
              "\t\tSet Player Variable(Event Player, HasBag, 0);\n"
              "\t\tSet Player Variable(Event Player, HasHorse, 0);\n"
              "\t\tSet Player Variable(Event Player, HasHome, 0);")

# ── 대장간을 11번째 장소로 ─────────────────────────────────────────
s = s.replace("\t\tSet Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));",
              "\t\tModify Global Variable(LocPos, Append To Array, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 4), Vector(6, 0, 0))));\n"
              "\t\tSet Global Variable(Anchor, Value In Array(Global Variable(LocPos), 0));")
s = s.replace("Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5));",
              "Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8, 5, 6));")
s = s.replace('For Player Variable(Event Player, Idx, 0, 10, 1);', 'For Player Variable(Event Player, Idx, 0, 11, 1);')

pos10 = 'Value In Array(Global Variable(LocPos), 10)'
smith = (
    '\t\tCreate In-World Text(All Players(All Teams), Custom String("대장간"), Add(%s, Vector(0, 2.6, 0)), 1.7, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);\n'
    '\t\tCreate In-World Text(And(Distance Between(Local Player, %s) < 22, Local Player.TutOn == 0) ? Local Player : False, Custom String("{0}{1}", Custom String("곡괭이 Lv.{0}  —  채굴 수확 +{1}\\r\\n가죽 배낭 $800  ·  말 $2000\\r\\n", Local Player.Pick, Local Player.Pick), Custom String("[{0}] 행동 선택      [{1}] 실행", Input Binding String(Button(Reload)), Input Binding String(Button(Interact)))), Add(%s, Vector(0, 1.5, 0)), 0.95, Do Not Clip, Visible To Position and String, Color(White), Default Visibility);\n'
    '\t\tCreate Effect(All Players(All Teams), Light Shaft, Color(Orange), %s, 1.2, Visible To Position and Radius);\n' % (pos10, pos10, pos10, pos10))
_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + smith + s[b:]

# ── 배열 교체 (행동 라벨 / 구역 이름 / 개수) ───────────────────────
a = s.index('Value In Array(Array(Custom String("행동 없음')
b = s.index(', Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx))', a)
old_flat = s[a + len('Value In Array('):b]
s = s.replace(old_flat, FLAT)
a = s.index('Value In Array(Array(Custom String("황야")')
b = s.index(', Add(Local Player.Zone, 1))', a)
s = s.replace(s[a + len('Value In Array('):b], ZONEARR)
s = re.sub(r'Array\(1, 4, 2, 3, 1, 3, 3, 1, 2, 3, 1\)', 'Array(%s)' % ', '.join(str(c) for c in COUNTS), s)

# 모텔 패널 문구 갱신
s = s.replace('Custom String("숙박 $60 — 하루 한 번\\r\\n피로가 완전히 회복된다\\r\\n")',
              'Custom String("숙박 $60 — 하루 한 번\\r\\n내 방 마련 $3500 — 이후 숙박 무료, 횟수 제한 없음\\r\\n")')
s = s.replace('Custom String("숙박 $60 — 하루 한 번\\r\\n피로가 완전히 회복된다"), Custom String("[{0}] 실행"',
              'Custom String("숙박 $60 — 하루 한 번\\r\\n내 방 마련 $3500\\r\\n"), Custom String("[{0}] 행동 선택      [{1}] 실행"')

# ── 디스패처: 모텔 2행동 + 대장간 ──────────────────────────────────
s = s.replace('''		Else If(Event Player.Zone == 3);
			Call Subroutine(DoSleep);''',
'''		Else If(Event Player.Zone == 3);
			If(Event Player.MenuIdx == 0);
				Call Subroutine(DoSleep);
			Else;
				If(Event Player.HasHome == 1);
					Small Message(Event Player, Custom String("이미 내 방이 있다"));
				Else If(Event Player.Money >= 3500);
					Modify Player Variable(Event Player, Money, Subtract, 3500);
					Set Player Variable(Event Player, HasHome, 1);
					Big Message(All Players(All Teams), Custom String("{0} — 모텔에 자기 방을 마련했다", Event Player));
					Small Message(Event Player, Custom String("이제 숙박이 무료이고 하루 횟수 제한도 없다"));
					Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 3);
				Else;
					Small Message(Event Player, Custom String("돈이 부족합니다 ($3500 필요)"));
				End;
			End;''')

s = s.replace('''		Else If(Event Player.Zone == 9);
			Call Subroutine(DoTutorial);
		End;''',
'''		Else If(Event Player.Zone == 9);
			Call Subroutine(DoTutorial);
		Else If(Event Player.Zone == 10);
			If(Event Player.MenuIdx == 0);
				If(Event Player.Pick >= 4);
					Small Message(Event Player, Custom String("곡괭이가 이미 최고 등급이다"));
				Else;
					Set Player Variable(Event Player, Amt, Value In Array(Array(250, 600, 1400, 3000), Event Player.Pick));
					If(Event Player.Money >= Event Player.Amt);
						Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);
						Modify Player Variable(Event Player, Pick, Add, 1);
						Big Message(Event Player, Custom String("곡괭이 Lv.{0} — 채굴 수확 +{1}", Event Player.Pick, Event Player.Pick));
						Play Effect(Event Player, Buff Explosion Sound, Color(Orange), Position Of(Event Player), 100);
					Else;
						Small Message(Event Player, Custom String("돈이 부족합니다 ($ {0} 필요)", Event Player.Amt));
					End;
				End;
			Else If(Event Player.MenuIdx == 1);
				If(Event Player.HasBag == 1);
					Small Message(Event Player, Custom String("이미 가죽 배낭이 있다"));
				Else If(Event Player.Money >= 800);
					Modify Player Variable(Event Player, Money, Subtract, 800);
					Set Player Variable(Event Player, HasBag, 1);
					Big Message(Event Player, Custom String("가죽 배낭 — 달리기 피로 소모 절반"));
					Play Effect(Event Player, Buff Explosion Sound, Color(Orange), Position Of(Event Player), 100);
				Else;
					Small Message(Event Player, Custom String("돈이 부족합니다 ($800 필요)"));
				End;
			Else;
				If(Event Player.HasHorse == 1);
					Small Message(Event Player, Custom String("이미 말이 있다"));
				Else If(Event Player.Money >= 2000);
					Modify Player Variable(Event Player, Money, Subtract, 2000);
					Set Player Variable(Event Player, HasHorse, 1);
					Big Message(All Players(All Teams), Custom String("{0} — 말을 샀다", Event Player));
					Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 3);
				Else;
					Small Message(Event Player, Custom String("돈이 부족합니다 ($2000 필요)"));
				End;
			End;
		End;''')

# ── 장비 효과 ──────────────────────────────────────────────────────
# 곡괭이: 채굴 수확 +Pick
s = s.replace('''			If(Event Player.Job == 1);
				Modify Player Variable(Event Player, Roll, Add, 1);
				Set Player Variable At Index(Event Player, JobXP, 1, Add(Value In Array(Event Player.JobXP, 1), 12));
			End;''',
'''			If(Event Player.Job == 1);
				Modify Player Variable(Event Player, Roll, Add, 1);
				Set Player Variable At Index(Event Player, JobXP, 1, Add(Value In Array(Event Player.JobXP, 1), 12));
			End;
			Modify Player Variable(Event Player, Roll, Add, Event Player.Pick);''')

# 배낭: 달리기 피로 소모 절반 (3초 -> 6초)
s = s.replace('''		Set Move Speed(Event Player, 165);
		Wait(3, Ignore Condition);''',
'''		Set Move Speed(Event Player, Add(165, Multiply(Event Player.HasHorse, 25)));
		Wait(Add(3, Multiply(Event Player.HasBag, 3)), Ignore Condition);''')

# 말: 평소 이동속도 +25
s = s.replace('''			If(Event Player.Sprinting == 0);
				Set Move Speed(Event Player, 100);
			End;
			Set Aim Speed(Event Player, 100);''',
'''			If(Event Player.Sprinting == 0);
				Set Move Speed(Event Player, Add(100, Multiply(Event Player.HasHorse, 25)));
			End;
			Set Aim Speed(Event Player, 100);''')
s = s.replace('''		Else;
			Set Move Speed(Event Player, 100);
		End;
	}
}''',
'''		Else;
			Set Move Speed(Event Player, Add(100, Multiply(Event Player.HasHorse, 25)));
		End;
	}
}''')

# 내 방: 숙박 무료 + 하루 제한 해제
s = s.replace('''		If(Event Player.SleepDay == Global Variable(Day));
			Small Message(Event Player, Custom String("오늘은 이미 잤다 — 내일 아침에 다시"));
			Abort;
		End;
		If(Event Player.Money < 60);
			Small Message(Event Player, Custom String("숙박비가 부족합니다 ($60 필요)"));
			Abort;
		End;
		Set Player Variable(Event Player, SleepDay, Global Variable(Day));
		Modify Player Variable(Event Player, Money, Subtract, 60);''',
'''		If(And(Event Player.HasHome == 0, Event Player.SleepDay == Global Variable(Day)));
			Small Message(Event Player, Custom String("오늘은 이미 잤다 — 내일 아침에 다시"));
			Abort;
		End;
		If(And(Event Player.HasHome == 0, Event Player.Money < 60));
			Small Message(Event Player, Custom String("숙박비가 부족합니다 ($60 필요)"));
			Abort;
		End;
		Set Player Variable(Event Player, SleepDay, Global Variable(Day));
		If(Event Player.HasHome == 0);
			Modify Player Variable(Event Player, Money, Subtract, 60);
		End;''')

# ── 칭호 (머리 위 표시) ────────────────────────────────────────────
TIER = ('Value In Array(Array(Custom String("떠돌이"), Custom String("일꾼"), Custom String("정착민"), '
        'Custom String("유지"), Custom String("거상"), Custom String("66번 국도의 주인")), '
        'Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), Event Player.Money >= 2500), '
        'Event Player.Money >= 6000), Event Player.Money >= 15000))')
TITLE = ('\t\tCreate In-World Text(All Players(All Teams), Custom String("『 {0} 』 {1}", '
         'Event Player.Bounty > 0 ? Custom String("수배 중") : %s, Event Player), '
         'Event Player, 1.1, Clip Against Surfaces, Visible To Position String and Color, '
         'Event Player.Bounty > 0 ? Color(Red) : Color(White), Default Visibility);\n' % TIER)
s = s.replace("\t\tWait Until(Has Spawned(Event Player), 30);", TITLE + "\t\tWait Until(Has Spawned(Event Player), 30);")

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  대장간 장소     : %d' % s.count('Custom String("대장간")'))
print('  장비 변수       : Pick/HasBag/HasHorse/HasHome %d' % s.count('Set Player Variable(Event Player, HasHome, 0)'))
print('  칭호 표시       : %d' % s.count('『 {0} 』 {1}'))
print('  행동 라벨 배열  : %d칸' % (FLAT.count('Custom String(')))
