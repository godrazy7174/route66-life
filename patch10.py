"""실기 7차 피드백.

1. 튜토리얼 카메라가 지형을 관통
   -> 고정 오프셋 대신 Ray Cast Hit Position으로 장소에서 카메라 자리까지
      광선을 쏴, 벽에 막히면 그 지점에 카메라를 둔다(레퍼런스와 같은 기법).

2. 자막이 Big Message(흰색 대형) + Small Message(빨간 박스)로 이원화
   -> 둘 다 버리고 HUD 텍스트 하나로 통일. 흰색, 지속시간 4초 -> 5.5초.
      장면 번호(TutStep)로 내용을 바꾸므로 텍스트 요소는 1개만 쓴다.

3. 장소에 이름만 있고 상세 정보가 없음 (레퍼런스는 가격/재고/키를 표시)
   -> 장소마다 상세 패널을 추가. 22m 안에서만 보이고, 시세처럼 변하는 값은
      실시간 반영. 이름표는 멀리서도 보이게 그대로 둔다.
      루프 대신 인덱스를 상수로 펼쳐서(재평가 버그 회피) 위치 재평가를 켰다.
      덕분에 설계자 모드로 장소를 옮기면 표지판이 자동으로 따라간다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

NAMES = ['식당', '협곡 광산', '주유소 잡화점', '모텔', '정비소 고물상',
         '술집', '협곡 개활지', '보안관 초소', '무법자 은신처']

KEY_R = 'Input Binding String(Button(Reload))'
KEY_F = 'Input Binding String(Button(Interact))'
KEY_E = 'Input Binding String(Button(Ability 2))'
KEY_Q = 'Input Binding String(Button(Ultimate))'

DETAIL = [
    'Custom String("전직  광부 · 사냥꾼 · 현상금 사냥꾼\\r\\n식사 $12\\r\\n[{0}] 행동 선택   [{1}] 실행", %s, %s)' % (KEY_R, KEY_F),
    'Custom String("채굴 — 원석 획득\\r\\n정밀 탐사 $30\\r\\n오늘 원석 시세  $ {0}", Global Variable(OrePrice))',
    'Custom String("육포 $15   물통 $10   육포 5개 $65\\r\\n[{0}] 육포 먹기   [{1}] 물 마시기", %s, %s)' % (KEY_E, KEY_Q),
    'Custom String("숙박 $40\\r\\n피로가 완전히 회복된다")',
    'Custom String("원석  $ {0}       가죽  $ {1}\\r\\n시세는 매일 아침 바뀐다", Global Variable(OrePrice), Global Variable(HidePrice))',
    'Custom String("위스키 $20 — 피로 회복\\r\\n카드 도박 $50\\r\\n소문 듣기")',
    'Custom String("흔적 추적 → 사냥감 출현\\r\\n좌클릭으로 직접 쏴서 잡는다")',
    'Custom String("벌금 $100 — 수배 말소\\r\\n현상금 게시판\\r\\n무법자 1명당  $ {0}", Global Variable(BotBounty))',
    'Custom String("무법자 합류\\r\\n장물 거래 — 무법자 165% / 일반 130%\\r\\n습격 계획 (무법자 전용)")',
]

# ── 3) BuildWorld: 이름표 + 상세 패널을 상수 인덱스로 펼침 ──────────
lines = []
for i, n in enumerate(NAMES):
    pos = 'Value In Array(Global Variable(LocPos), %d)' % i
    lines.append('\t\tCreate In-World Text(All Players(All Teams), Custom String("%s"), Add(%s, Vector(0, 2.6, 0)), 1.7, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);' % (n, pos))
    lines.append('\t\tCreate In-World Text(Distance Between(Local Player, %s) < 22 ? Local Player : False, %s, Add(%s, Vector(0, 1.5, 0)), 0.95, Do Not Clip, Visible To Position and String, Color(White), Default Visibility);' % (pos, DETAIL[i], pos))
    lines.append('\t\tCreate Effect(All Players(All Teams), Light Shaft, Color(Yellow), %s, 1.2, Visible To and Position);' % pos)

_bw = s.index('rule("[코어 02] BuildWorld")')
a = s.index('\t\tSet Global Variable(SignIds, Empty Array);', _bw)
b = s.index('\t}\n}', a)
s = s[:a] + '\n'.join(lines) + '\n' + s[b:]

# 설계자 모드의 표지판 파괴/재생성은 이제 불필요 (위치가 자동 추종)
a = s.index('\t\tDestroy In-World Text(Value In Array(Global Variable(SignIds), Global Variable(ArchIdx)));')
b = s.index('\t\tPlay Effect(Host Player(), Good Explosion', a)
s = s[:a] + s[b:]

# ── 1) + 2) 튜토리얼 재작성 ────────────────────────────────────────
s = s.replace("\t\t33: TutSkip\n", "\t\t33: TutSkip\n\t\t34: TutStep\n\t\t35: TutHud\n")

BEATS = [
    (0, "66번 국도", "여기서 살아남아라. 굶지 않고, 목마르지 않고, 지치지 않는 것이 시작이다."),
    (0, "허기 · 갈증 · 피로", "셋 다 시간이 지나면 줄어든다. 허기나 갈증이 0이 되면 피를 흘리기 시작한다."),
    (0, "식당", "직업을 고르고 밥을 먹는 곳. 죽으면 여기로 돌아온다."),
    (1, "협곡 광산", "광부의 일터. 캘 때마다 원석이 나오고, 가끔 금맥이 터진다."),
    (6, "협곡 개활지", "사냥꾼의 일터. 흔적을 쫓으면 사냥감이 나타난다. 좌클릭으로 직접 쏴라."),
    (8, "무법자 은신처", "무법자가 되는 곳. 강탈과 습격으로 크게 벌지만, 목에 값이 붙는다."),
    (7, "보안관 초소", "현상금 사냥꾼이 상금을 확인하고, 수배자가 벌금을 내는 곳."),
    (2, "주유소 잡화점", "육포와 물통을 산다. E로 먹고 Q로 마신다."),
    (4, "정비소 고물상", "원석과 가죽을 판다. 시세는 매일 아침 바뀌니 값을 보고 팔아라."),
    (5, "술집", "위스키로 피로를 풀고, 카드로 돈을 잃는다."),
    (3, "모텔", "$40에 하룻밤. 피로가 완전히 회복된다."),
    (0, "조작", "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기"),
    (0, "밤을 조심해라", "밤이 되면 현상금이 두 배가 된다. 황야에서 [F]는 강도이자 체포다."),
]
TITLES = 'Array(' + ', '.join('Custom String("%s")' % b[1] for b in BEATS) + ')'
BODIES = 'Array(' + ', '.join('Custom String("%s")' % b[2] for b in BEATS) + ')'

beats = []
for i, (loc, _, _) in enumerate(BEATS):
    p = 'Value In Array(Global Variable(LocPos), %d)' % loc
    cam = ('Ray Cast Hit Position(Add(%s, Vector(0, 2, 0)), Add(%s, Vector(0, 6, 9)), Empty Array, All Players(All Teams), False)' % (p, p))
    beats.append('\t\tIf(Event Player.TutSkip == 0);')
    beats.append('\t\t\tSet Player Variable(Event Player, TutStep, %d);' % i)
    beats.append('\t\t\tStart Camera(Event Player, %s, %s, 0);' % (cam, p))
    beats.append('\t\t\tWait Until(Event Player.TutSkip == 1, 5.5);')
    beats.append('\t\tEnd;')

a = s.index('rule("[튜토리얼 01] DoTutorial")')
b = s.index('\nrule("[튜토리얼 02]')
NEW_TUT = '''rule("[튜토리얼 01] DoTutorial")
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
		Set Player Variable(Event Player, TutStep, 0);
		Set Player Variable(Event Player, Busy, 1);
		Set Status(Event Player, Null, Rooted, 9999);
		Set Status(Event Player, Null, Phased Out, 9999);
		Set Invisible(Event Player, All);
		Create HUD Text(Event Player, Value In Array(''' + TITLES + ''', Event Player.TutStep), Value In Array(''' + BODIES + ''', Event Player.TutStep), Custom String("[{0}] 건너뛰기", Input Binding String(Button(Jump))), Top, 20, Color(White), Color(White), Color(White), Visible To Sort Order String and Color, Default Visibility);
		Set Player Variable(Event Player, TutHud, Last Text ID());
		Wait(1.5, Ignore Condition);
''' + '\n'.join(beats) + '''
		Destroy HUD Text(Event Player.TutHud);
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
		Play Effect(Event Player, Good Explosion, Color(Lime Green), Position Of(Event Player), 2);
	}
}
'''
s = s[:a] + NEW_TUT + s[b + 1:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  상세 패널      : %d개' % s.count('Visible To Position and String, Color(White)'))
print('  이름표         : %d개' % s.count('Visible To and Position, Color(Yellow)'))
print('  카메라 레이캐스트: %d개' % s.count('Ray Cast Hit Position(Add(Value In Array(Global Variable(LocPos)'))
print('  Big/Small 자막 잔존: %d' % (s.count('Big Message(Event Player, Custom String("66번 국도")')))
