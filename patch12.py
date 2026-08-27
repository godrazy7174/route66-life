"""튜토리얼 3차 개편.

1. 자막 겹침
   원인: 장소 상세 패널(인월드 텍스트)이 튜토리얼 카메라 앞에 그대로 떠서
         상단 HUD 자막과 포개졌다. 목표 설명(Set Objective Description)도
         같은 상단 영역을 쓴다.
   -> 튜토리얼 중에는 상세 패널을 숨기고, 목표 설명은 없앤다.

2. 튜토리얼이 건물 안내에 그침
   -> 게임 자체를 설명하도록 대본을 다시 씀.
      무엇을 하는 게임인지 / 무엇이 압박인지 / 돈은 왜 필요한지 /
      직업이 어떻게 갈리는지 / 평판과 현상금이 어떻게 맞물리는지 /
      하루와 사건이 어떻게 굴러가는지. 건물은 배경으로만 쓴다.

3. 안내소가 공중에 뜬 것처럼 보이고 식당에서 멀다
   -> 오프셋 8m -> 4m, 표지 높이도 낮춘다.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 튜토리얼 중 상세 패널 숨김 ──────────────────────────────────
n = len(re.findall(r'Distance Between\(Local Player, (Value In Array\(Global Variable\(LocPos\), \d+\))\) < 22 \? Local Player : False', s))
s = re.sub(r'Distance Between\(Local Player, (Value In Array\(Global Variable\(LocPos\), \d+\))\) < 22 \? Local Player : False',
           r'And(Distance Between(Local Player, \1) < 22, Local Player.TutOn == 0) ? Local Player : False', s)

# 목표 설명 제거 (상단 영역 충돌)
s = re.sub(r'\t\tSet Objective Description\([^\n]*\n', '', s)

# ── 3) 안내소를 식당 가까이, 표지 높이 낮춤 ────────────────────────
s = s.replace('Add(Value In Array(Global Variable(LocPos), 0), Vector(0, 0, -8))',
              'Add(Value In Array(Global Variable(LocPos), 0), Vector(0, 0, -4))')
s = s.replace('Custom String("안내소"), Add(Value In Array(Global Variable(LocPos), 9), Vector(0, 2.6, 0)), 1.7',
              'Custom String("안내소"), Add(Value In Array(Global Variable(LocPos), 9), Vector(0, 2.1, 0)), 1.5')

# ── 2) 대본 교체 ───────────────────────────────────────────────────
BEATS = [
    (0, "66번 국도", "이기는 게임이 아니다. 서부에서 하루하루를 버티고, 자기 삶을 쌓아 올리는 게임이다."),
    (0, "세 가지 압박", "허기 · 갈증 · 피로가 쉬지 않고 줄어든다. 허기나 갈증이 0이면 피를 흘리고, 피로가 0이면 느려진다."),
    (2, "돈이 전부다", "먹고 마시고 자는 데 전부 돈이 든다. 벌지 못하면 굶는다. 그래서 직업을 고른다."),
    (0, "직업은 다섯", "광부 · 사냥꾼 · 현상금 사냥꾼 · 무법자, 그리고 아무것도 아닌 떠돌이. 언제든 바꿀 수 있다."),
    (1, "노가다와 한탕", "채굴은 안전하지만 느리다. 대신 스무 번에 한 번쯤 금맥이 터진다. 이 게임의 벌이는 대개 이런 식이다."),
    (6, "총을 쓰는 순간", "사냥감은 좌클릭으로 직접 맞혀야 한다. 스킬은 전부 봉인돼 있고, 총 한 자루가 전부다."),
    (8, "다른 길", "무법자는 남의 주머니에서 번다. 강탈은 빠르고 크다. 대신 그 액수만큼 네 목에 현상금이 붙는다."),
    (7, "쫓고 쫓기다", "현상금이 붙은 자는 누구든 잡을 수 있다. 현상금 사냥꾼은 그걸로 먹고산다. 벌금을 내면 지워진다."),
    (4, "평판", "선택이 쌓여 평판이 된다. 장물은 제값보다 비싸게 팔리지만, 팔 때마다 평판이 깎인다."),
    (3, "하루는 12분", "아침마다 원석과 가죽 시세가 바뀐다. 밤이 되면 현상금이 두 배가 된다."),
    (5, "사건은 터진다", "몇 분에 한 번씩 세상에 일이 생긴다. 금맥 소동, 모래폭풍, 무법자 습격. 놓치면 손해다."),
    (0, "조작", "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기 · 황야에서 [F]는 강도이자 체포"),
    (0, "시작", "가진 건 $120과 육포 둘, 물 둘. 어디서 무엇으로 살아갈지는 네가 정한다."),
]
TITLES = 'Array(' + ', '.join('Custom String("%s")' % b[1] for b in BEATS) + ')'
BODIES = 'Array(' + ', '.join('Custom String("%s")' % b[2] for b in BEATS) + ')'

# 제목/본문 배열 교체
a = s.index('Create HUD Text(Event Player, Value In Array(Array(Custom String("66번 국도")')
b = s.index(', Custom String("[{0}] 다음"', a)
s = s[:a] + ('Create HUD Text(Event Player, Value In Array(%s, Event Player.TutStep), Value In Array(%s, Event Player.TutStep)' % (TITLES, BODIES)) + s[b:]

# 장면별 카메라 장소 교체
beats = []
for i, (loc, _, _) in enumerate(BEATS):
    p = 'Value In Array(Global Variable(LocPos), %d)' % loc
    cam = ('Ray Cast Hit Position(Add(%s, Vector(0, 2, 0)), Add(%s, Vector(0, 6, 9)), Empty Array, All Players(All Teams), False)' % (p, p))
    beats.append('\t\tSet Player Variable(Event Player, TutSkip, 0);')
    beats.append('\t\tSet Player Variable(Event Player, TutStep, %d);' % i)
    beats.append('\t\tStart Camera(Event Player, %s, %s, 0);' % (cam, p))
    beats.append('\t\tWait Until(Event Player.TutSkip == 1, 7);')

a = s.index('\t\tSet Player Variable(Event Player, TutSkip, 0);\n\t\t\tSet Player Variable(Event Player, TutStep, 0);')
b = s.index('\t\tDestroy HUD Text(Event Player.TutHud);')
s = s[:a] + '\n'.join(beats) + '\n' + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  상세 패널 튜토리얼 중 숨김 : %d개' % n)
print('  목표 설명 제거             : %d개 남음' % s.count('Set Objective Description'))
print('  장면 수                    : %d' % s.count('Start Camera(Event Player, Ray Cast'))
print('  안내소 오프셋 4m           : %d' % s.count('Vector(0, 0, -4)'))
