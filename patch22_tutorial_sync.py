# -*- coding: utf-8 -*-
"""튜토리얼 자막 <-> 카메라 장소 불일치 수정.

어긋나 있던 것
  "평판"          -> 정비소를 비춤 (평판은 장물/은신처 이야기)
  "하루는 12분"    -> 모텔을 비춤 (시세 이야기인데)
  "사건은 터진다"   -> 술집을 비춤 (월드 이벤트는 특정 장소가 없음)
그리고 나중에 추가된 대장간·안내소는 튜토리얼에 아예 안 나왔다.

-> 장면마다 '그 장소에서 실제로 하는 일'을 말하도록 대본을 다시 짠다.
   11곳 중 9곳이 자기 차례에 등장한다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

BEATS = [
    (0, "66번 국도", "이기는 게임이 아니다. 서부에서 하루하루를 버티고, 자기 삶을 쌓아 올리는 게임이다."),
    (2, "굶주림과 목마름", "허기와 갈증은 쉬지 않고 줄어든다. 여기서 육포와 물통을 사서\\r\\n[E]로 먹고 [Q]로 마신다. 0이 되면 피를 흘린다."),
    (3, "피로", "피로가 바닥나면 아무 일도 할 수 없다.\\r\\n하룻밤 $60, 하루 한 번뿐이다. 잘 곳을 마련하는 게 첫 목표다."),
    (0, "직업", "광부 · 사냥꾼 · 현상금 사냥꾼 · 무법자, 그리고 아무것도 아닌 떠돌이.\\r\\n여기 구인 게시판에서 언제든 바꿀 수 있다."),
    (1, "광부", "캘 때마다 원석이 나오고 가끔 금맥이 터진다.\\r\\n쉬지 않고 이어 캐면 연속 보너스가 붙는다."),
    (6, "사냥꾼", "야수는 숨어 있어 흔적을 쫓아야 모습을 드러낸다.\\r\\n드러난 30초 안에 좌클릭으로 직접 맞혀야 한다."),
    (8, "무법자", "강탈과 습격으로 크게 번다. 대신 그만큼 목에 값이 붙는다.\\r\\n훔친 물건은 여기서 제값보다 비싸게 넘길 수 있다."),
    (7, "현상금 사냥꾼", "현상금이 붙은 자는 누구든 잡을 수 있다.\\r\\n쫓기는 쪽이라면 여기서 벌금을 내고 수배를 지운다."),
    (4, "돈으로 바꾸기", "캔 원석과 잡은 가죽은 여기서 현금이 된다.\\r\\n시세는 매일 아침 바뀌니 값을 보고 팔아라."),
    (10, "장비", "곡괭이를 벼리면 캘 때마다 더 나오고, 말을 사면 더 빨리 움직인다.\\r\\n번 돈은 결국 여기로 돌아온다."),
    (0, "하루와 밤", "12분이 하루다. 아침마다 시세가 바뀌고, 밤이 되면 현상금이 두 배가 된다.\\r\\n하루 목표를 채우면 보너스가 붙는다."),
    (5, "사건", "몇 분에 한 번씩 세상에 일이 생긴다. 금맥 소동, 모래폭풍, 역마차 도착, 누명.\\r\\n보물 상자가 떨어지면 먼저 닿는 사람이 임자다. 소문은 여기서 듣는다."),
    (9, "시작", "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기\\r\\n가진 건 $60과 육포 둘, 물 둘. 어디서 무엇으로 살아갈지는 네가 정한다."),
]

TITLES = 'Array(' + ', '.join('Custom String("%s")' % b[1] for b in BEATS) + ')'
BODIES = 'Array(' + ', '.join('Custom String("%s")' % b[2] for b in BEATS) + ')'

# ── 제목/본문 배열 교체 ────────────────────────────────────────────
a = s.index('Create HUD Text(Event Player, Value In Array(Array(Custom String("66번 국도")')
b = s.index(', Custom String("[{0}] 다음"', a)
s = s[:a] + ('Create HUD Text(Event Player, Value In Array(%s, Event Player.TutStep), Value In Array(%s, Event Player.TutStep)'
             % (TITLES, BODIES)) + s[b:]

# ── 장면별 카메라 장소 교체 ────────────────────────────────────────
beats = []
for i, (loc, _, _) in enumerate(BEATS):
    p = 'Value In Array(Global Variable(LocPos), %d)' % loc
    cam = ('Ray Cast Hit Position(Add(%s, Vector(0, 2, 0)), Add(%s, Vector(0, 6, 9)), Empty Array, All Players(All Teams), False)' % (p, p))
    beats.append('\t\tSet Player Variable(Event Player, TutSkip, 0);')
    beats.append('\t\tSet Player Variable(Event Player, TutStep, %d);' % i)
    beats.append('\t\tStart Camera(Event Player, %s, %s, 0);' % (cam, p))
    beats.append('\t\tWait Until(Event Player.TutSkip == 1, 7);')

a = s.index('\t\tSet Player Variable(Event Player, TutSkip, 0);\n\t\tSet Player Variable(Event Player, TutStep, 0);')
b = s.index('\t\tDestroy HUD Text(Event Player.TutHud);')
s = s[:a] + '\n'.join(beats) + '\n' + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

NAMES = ['식당', '협곡 광산', '주유소 잡화점', '모텔', '정비소 고물상',
         '술집', '협곡 개활지', '보안관 초소', '무법자 은신처', '안내소', '대장간']
print('패치 완료 — 장면 %d개' % len(BEATS))
print()
print('  %-3s %-14s %s' % ('#', '제목', '비추는 장소'))
print('  ' + '-' * 44)
for i, (loc, title, _) in enumerate(BEATS):
    print('  %-3d %-14s %s' % (i + 1, title, NAMES[loc]))
