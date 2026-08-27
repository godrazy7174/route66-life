# -*- coding: utf-8 -*-
"""두 가지 회귀 수정.

[1] 낮인데 광기둥이 안 보인다
    patch30에서 표시 여부를 삼항식으로 바꿨다:
        Create Effect(IsNight == 0 ? All Players(All Teams) : False, Light Shaft, ...)
    '보이는 대상'을 조건부로 두는 방식은 이 스크립트에서 신뢰할 수 없다
    (patch24의 낮 전용 발광도 같은 방식이었고 "이곳에는 적용되지 않았다"는
     보고를 받았다 — 그때는 다른 원인으로 넘겼는데 같은 증상이었다).
    -> 조건부 표시를 버리고 낮/밤 전환 때 실제로 생성/파괴한다.
       보이는 대상은 항상 All Players(All Teams) 고정.
    -> 겸사겸사 식당 광기둥을 되살린다. 스폰 지점에 불이 하나도 없으면
       "조명이 아예 없다"고 느끼는 게 당연하다. (대장간만 계속 제외)

[2] 튜토리얼 자막이 통째로 없다
    patch22가 자기 발등을 찍었다. 먼저 Create HUD Text의 제목/본문 배열을
    갈아끼운 다음, 두 번째 치환에서
        a = 첫 'TutSkip, 0' 줄   b = 'Destroy HUD Text(TutHud)' 줄
        s[:a] + beats + s[b:]
    로 잘라냈는데, 방금 고친 Create HUD Text가 a와 b 사이에 있었다.
    그래서 TutStep은 13번 설정되지만 그걸 읽는 곳이 어디에도 없었다.
    -> Create HUD Text 복원.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ══ [1] 광기둥 ════════════════════════════════════════════════════
pat = (r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, '
       r'Light Shaft, Color\(\w+\), Value In Array\(Global Variable\(LocPos\), \d+\), 1\.2, '
       r'Visible To Position Radius and Color\);\n')
old_n = len(re.findall(pat, s))
assert old_n == 9, old_n
s = re.sub(pat, '', s)

LOCS = [(i, 'Aqua' if i == 9 else 'White') for i in range(10)]   # 10(대장간) 제외
REEVAL = 'Visible To Position Radius and Color'

on, off = [], []
for slot, (loc, col) in enumerate(LOCS):
    on.append('\t\tCreate Effect(All Players(All Teams), Light Shaft, Color(%s), '
              'Value In Array(Global Variable(LocPos), %d), 1.2, %s);' % (col, loc, REEVAL))
    on.append('\t\tModify Global Variable(SignIds, Append To Array, Last Created Entity());')
    off.append('\t\tDestroy Effect(Value In Array(Global Variable(SignIds), %d));' % slot)

RULES = '''rule("[월드 09] 낮 — 마을 불 켜기")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Global Variable(Ready) == 1;
		Global Variable(IsNight) == 0;
	}

	actions
	{
%s
		Set Global Variable(SignIds, Empty Array);
%s
	}
}

rule("[월드 10] 밤 — 마을 불 끄기")
{
	event
	{
		Ongoing - Global;
	}

	conditions
	{
		Global Variable(Ready) == 1;
		Global Variable(IsNight) == 1;
	}

	actions
	{
%s
		Set Global Variable(SignIds, Empty Array);
	}
}

''' % ('\n'.join(off), '\n'.join(on), '\n'.join(off))

anchor = 'rule("[월드 05] 아침 정산")'
s = s.replace(anchor, RULES + anchor, 1)

# ══ [2] 튜토리얼 자막 복원 ════════════════════════════════════════
BEATS = [
    (0, "66번 국도", "이기는 게임이 아니다. 서부에서 하루하루를 버티고, 자기 삶을 쌓아 올리는 게임이다."),
    (2, "굶주림과 목마름", "허기와 갈증은 쉬지 않고 줄어든다. 여기서 육포와 물통을 사서\r\n[E]로 먹고 [Q]로 마신다. 0이 되면 피를 흘린다."),
    (3, "피로", "피로가 바닥나면 아무 일도 할 수 없다.\r\n하룻밤 $60, 하루 한 번뿐이다. 잘 곳을 마련하는 게 첫 목표다."),
    (0, "직업", "광부 · 사냥꾼 · 현상금 사냥꾼 · 무법자, 그리고 아무것도 아닌 떠돌이.\r\n여기 구인 게시판에서 언제든 바꿀 수 있다."),
    (1, "광부", "캘 때마다 원석이 나오고 가끔 금맥이 터진다.\r\n쉬지 않고 이어 캐면 연속 보너스가 붙는다."),
    (6, "사냥꾼", "야수는 숨어 있어 흔적을 쫓아야 모습을 드러낸다.\r\n드러난 30초 안에 좌클릭으로 직접 맞혀야 한다."),
    (8, "무법자", "강탈과 습격으로 크게 번다. 대신 그만큼 목에 값이 붙는다.\r\n훔친 물건은 여기서 제값보다 비싸게 넘길 수 있다."),
    (7, "현상금 사냥꾼", "현상금이 붙은 자는 누구든 잡을 수 있다.\r\n쫓기는 쪽이라면 여기서 벌금을 내고 수배를 지운다."),
    (4, "돈으로 바꾸기", "캔 원석과 잡은 가죽은 여기서 현금이 된다.\r\n시세는 매일 아침 바뀌니 값을 보고 팔아라."),
    (10, "장비", "곡괭이를 벼리면 캘 때마다 더 나오고, 말을 사면 더 빨리 움직인다.\r\n번 돈은 결국 여기로 돌아온다."),
    (0, "하루와 밤", "12분이 하루다. 밤이 오면 마을의 불이 꺼지고 현상금이 두 배가 된다.\r\n하루 목표를 채우면 보너스가 붙는다."),
    (5, "사건", "몇 분에 한 번씩 세상에 일이 생긴다. 금맥 소동, 모래폭풍, 역마차 도착, 누명.\r\n보물 상자가 떨어지면 먼저 닿는 사람이 임자다. 소문은 여기서 듣는다."),
    (9, "시작", "[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기\r\n가진 건 $60과 육포 둘, 물 둘. 어디서 무엇으로 살아갈지는 네가 정한다."),
]
TITLES = 'Array(' + ', '.join('Custom String("%s")' % b[1] for b in BEATS) + ')'
BODIES = 'Array(' + ', '.join('Custom String("%s")' % b[2] for b in BEATS) + ')'

assert 'Set Player Variable(Event Player, TutHud' not in s
HEAD = ('\t\tSet Player Variable(Event Player, TutStep, 0);\n'
        '\t\tStart Camera(Event Player, Ray Cast Hit Position(Add(Value In Array(Global Variable(LocPos), 0)')
assert s.count(HEAD) == 1
HUD = ('\t\tSet Player Variable(Event Player, TutStep, 0);\n'
       '\t\tDestroy HUD Text(Event Player.TutHud);\n'
       '\t\tCreate HUD Text(Event Player, Value In Array(%s, Event Player.TutStep), '
       'Value In Array(%s, Event Player.TutStep), '
       'Custom String("[{0}] 다음      ({1}/13)", Input Binding String(Button(Jump)), '
       'Add(Event Player.TutStep, 1)), Top, 0, Color(White), Color(White), Color(White), '
       'Visible To Sort Order String and Color, Default Visibility);\n'
       '\t\tSet Player Variable(Event Player, TutHud, Last Text ID());\n'
       '\t\tStart Camera(Event Player, Ray Cast Hit Position(Add(Value In Array(Global Variable(LocPos), 0)'
       % (TITLES, BODIES))
s = s.replace(HEAD, HUD, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  광기둥      : 조건부 표시 폐기 -> 낮/밤 전환 시 생성·파괴 (%d개, 식당 복원)' % len(LOCS))
print('  튜토리얼 자막 : 복원 (%d장면, TutStep으로 제목·본문 전환)' % len(BEATS))
print('  Custom String 총 %d개' % s.count('Custom String('))
