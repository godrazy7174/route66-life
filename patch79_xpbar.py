# -*- coding: utf-8 -*-
"""현직 경험치 바 — 좌측 스탯 아래 상시 표시.

  - HUD 텍스트(Left 3): "경험치 {레벨 내} / 250   누적 {총}" — 문자열 재평가로 실시간
  - 진행 바(Left 4): 레벨 내 진행률 0~100 (250 XP = 한 레벨), 텍스트 없음
    (진행 바는 문자열 재평가 옵션이 없어 숫자를 못 얹는다 — 위 텍스트가 담당)
  - 무직(Job 0)·튜토리얼 중에는 숨김 (Local Player 조건부 — 검증된 패턴)
  - 세이브 코드/키패드 HUD는 Left 4 → 5로 이동 (자리 양보)
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

XPCUR = 'Modulo(Value In Array(Local Player.JobXP, Local Player.Job), 250)'
XPTOT = 'Value In Array(Local Player.JobXP, Local Player.Job)'
VIS = 'And(Local Player.TutOn == 0, Local Player.Job > 0) ? Local Player : False'

XPTEXT = (T*2 + 'Create HUD Text(' + VIS + ', Null, Null, '
  + 'Custom String("경험치 {0} / 250   누적 {1}", ' + XPCUR + ', ' + XPTOT + '), '
  + 'Left, 3, Color(White), Color(White), Color(Sky Blue), Visible To Sort Order String and Color, Default Visibility);' + N)
XPBAR = (T*2 + 'Create Progress Bar HUD Text(' + VIS + ', '
  + 'Multiply(0.4, ' + XPCUR + '), Null, Left, 4, Color(Sky Blue), Null, '
  + 'Visible To Values and Color, Default Visibility);' + N)

ANCHOR = T*2 + 'Create HUD Text(Local Player.TutOn == 0 ? Local Player : False, Value In Array(Array(Custom String("황야")'
sub(ANCHOR, XPTEXT + XPBAR + ANCHOR)

# 세이브 코드·키패드 HUD 자리 이동 (Left 4 -> 5)
sub('Custom String("적어두세요 — 방이 닫히면 이 코드만 남습니다"), Left, 4,',
    'Custom String("적어두세요 — 방이 닫히면 이 코드만 남습니다"), Left, 5,')
sub('Custom String("[R] +1      [F] 자리 확정      [웅크리기] 취소"), Left, 4,',
    'Custom String("[R] +1      [F] 자리 확정      [웅크리기] 취소"), Left, 5,')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('경험치 바 추가: 텍스트(Left 3) + 진행 바(Left 4), 세이브 HUD는 5로')
