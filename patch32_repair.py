# -*- coding: utf-8 -*-
"""patch31의 자막 삽입이 깨진 것 수정.

원인: 힙독을 거치며 소스의 이스케이프가 한 겹 벗겨져
      파이썬이 "\r\n"을 진짜 개행으로 해석했다.
      그래서 Create HUD Text 한 줄이 물리적으로 13줄로 쪼개졌다.
      워크샵은 한 액션이 한 줄이어야 하므로 붙여넣기 자체가 실패한다.

수정: 소스에 역슬래시를 아예 쓰지 않는다 (chr(92)로 조립).
      깨진 블록을 통째로 다시 만든다.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'          # 워크샵 문자열용 개행 (역슬래시 r 역슬래시 n)

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

BEATS = [
    ("66번 국도", "이기는 게임이 아니다. 서부에서 하루하루를 버티고, 자기 삶을 쌓아 올리는 게임이다."),
    ("굶주림과 목마름", "허기와 갈증은 쉬지 않고 줄어든다. 여기서 육포와 물통을 사서~[E]로 먹고 [Q]로 마신다. 0이 되면 피를 흘린다."),
    ("피로", "피로가 바닥나면 아무 일도 할 수 없다.~하룻밤 $60, 하루 한 번뿐이다. 잘 곳을 마련하는 게 첫 목표다."),
    ("직업", "광부 · 사냥꾼 · 현상금 사냥꾼 · 무법자, 그리고 아무것도 아닌 떠돌이.~여기 구인 게시판에서 언제든 바꿀 수 있다."),
    ("광부", "캘 때마다 원석이 나오고 가끔 금맥이 터진다.~쉬지 않고 이어 캐면 연속 보너스가 붙는다."),
    ("사냥꾼", "야수는 숨어 있어 흔적을 쫓아야 모습을 드러낸다.~드러난 30초 안에 좌클릭으로 직접 맞혀야 한다."),
    ("무법자", "강탈과 습격으로 크게 번다. 대신 그만큼 목에 값이 붙는다.~훔친 물건은 여기서 제값보다 비싸게 넘길 수 있다."),
    ("현상금 사냥꾼", "현상금이 붙은 자는 누구든 잡을 수 있다.~쫓기는 쪽이라면 여기서 벌금을 내고 수배를 지운다."),
    ("돈으로 바꾸기", "캔 원석과 잡은 가죽은 여기서 현금이 된다.~시세는 매일 아침 바뀌니 값을 보고 팔아라."),
    ("장비", "곡괭이를 벼리면 캘 때마다 더 나오고, 말을 사면 더 빨리 움직인다.~번 돈은 결국 여기로 돌아온다."),
    ("하루와 밤", "12분이 하루다. 밤이 오면 마을의 불이 꺼지고 현상금이 두 배가 된다.~하루 목표를 채우면 보너스가 붙는다."),
    ("사건", "몇 분에 한 번씩 세상에 일이 생긴다. 금맥 소동, 모래폭풍, 역마차 도착, 누명.~보물 상자가 떨어지면 먼저 닿는 사람이 임자다. 소문은 여기서 듣는다."),
    ("시작", "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기~가진 건 $60과 육포 둘, 물 둘. 어디서 무엇으로 살아갈지는 네가 정한다."),
]
TITLES = 'Array(' + ', '.join('Custom String("%s")' % t for t, _ in BEATS) + ')'
BODIES = 'Array(' + ', '.join('Custom String("%s")' % b.replace('~', NL) for _, b in BEATS) + ')'

BLOCK = ('\t\tDestroy HUD Text(Event Player.TutHud);\n'
         '\t\tCreate HUD Text(Event Player, Value In Array(%s, Event Player.TutStep), '
         'Value In Array(%s, Event Player.TutStep), '
         'Custom String("[{0}] 다음      ({1}/13)", Input Binding String(Button(Jump)), '
         'Add(Event Player.TutStep, 1)), Top, 0, Color(White), Color(White), Color(White), '
         'Visible To Sort Order String and Color, Default Visibility);\n'
         '\t\tSet Player Variable(Event Player, TutHud, Last Text ID());\n' % (TITLES, BODIES))

a = s.index('\t\tDestroy HUD Text(Event Player.TutHud);\n\t\tCreate HUD Text(Event Player,')
tail = '\t\tSet Player Variable(Event Player, TutHud, Last Text ID());\n'
b = s.index(tail, a) + len(tail)
s = s[:a] + BLOCK + s[b:]

assert NL in s
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('수정 완료 — 자막 블록을 한 줄짜리 액션으로 재작성')
