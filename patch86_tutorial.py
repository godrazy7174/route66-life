# -*- coding: utf-8 -*-
"""튜토리얼 갱신 — 15 -> 16단계 + 완주 보상 $30 -> $50.

  4 직업       + 오늘의 직업 한 줄
  11 돈으로 바꾸기 + 명성·악명 물가 한 줄
  12 장비      + 부동산 [Ctrl+F] 한 줄
  13 하루와 밤  + 징수원 한 줄
  15 긴 여정(신규, 카메라 안내소) — 마을 재건 + 세이브 코드
  완주 보상    $30 -> $50 (물가 인상 후 구매력 복원)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
RN = chr(92) + 'r' + chr(92) + 'n'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

# ── 단계 수 확장 ───────────────────────────────────────────────────
sub('Custom String("사건"), Custom String("시작")',
    'Custom String("사건"), Custom String("긴 여정"), Custom String("시작")')
sub('Min(14, Event Player.TutStep)', 'Min(15, Event Player.TutStep)', 2)
sub('[{0}] 다음      ({1}/15)', '[{0}] 다음      ({1}/16)')
sub('For Player Variable(Event Player, TutStep, 0, 15, 1);',
    'For Player Variable(Event Player, TutStep, 0, 16, 1);')
sub('Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 9)',
    'Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 9, 9)', 3)

# ── 본문 보강 ──────────────────────────────────────────────────────
sub('일을 하는 순간 그 직업이 된다. 경험과 승급은 직업마다 따로 남는다."',
    '일을 하는 순간 그 직업이 된다. 경험과 승급은 직업마다 따로 남는다.' + RN
    + "매일 아침 '오늘의 직업'이 뽑힌다 — 그날 그 직업은 보수 1.5배.\"")
sub('시세는 매일 아침 바뀌니 값을 보고 팔아라."',
    '시세는 매일 아침 바뀌니 값을 보고 팔아라.' + RN
    + '명성은 값을 깎아주고, 악명은 바가지를 부른다."')
sub('번 돈은 결국 여기로 돌아온다."',
    '번 돈은 결국 여기로 돌아온다.' + RN
    + '건물 앞에서 [Ctrl+F] — 통째로 사서 임대료를 걷는 길도 있다."')
sub('하루 목표를 채우면 보너스가 붙는다."',
    '하루 목표를 채우면 보너스가 붙는다.' + RN
    + '이틀에 한 번, 아침이면 징수원이 재산세를 걷으러 온다."')

# ── 신규 15단계 본문 (사건 뒤, 시작 앞) ────────────────────────────
sub('소문은 여기서 듣는다."), Custom String("[R] 행동 선택',
    '소문은 여기서 듣는다."), Custom String("돈이 쌓이면 안내소에서 마을을 재건해라 — 우물부터 기차역까지 다섯 걸음.' + RN
    + '떠나기 전엔 세이브 코드를 받아라. 방이 닫히면 그 코드만 남는다."), Custom String("[R] 행동 선택')

# ── 완주 보상 $30 -> $50 ───────────────────────────────────────────
sub('Set Player Variable At Index(Event Player, Inv, 1, Add(Value In Array(Event Player.Inv, 1), 3));\n\t\t\tModify Player Variable(Event Player, Money, Add, 30);',
    'Set Player Variable At Index(Event Player, Inv, 1, Add(Value In Array(Event Player.Inv, 1), 3));\n\t\t\tModify Player Variable(Event Player, Money, Add, 50);')
sub('안내를 마쳤다 — 육포 3, 물통 3, $30', '안내를 마쳤다 — 육포 3, 물통 3, $50')
sub('튜토리얼 — 처음이라면 여기서 (완주 보상 육포 3 · 물통 3 · $30)',
    '튜토리얼 — 처음이라면 여기서 (완주 보상 육포 3 · 물통 3 · $50)')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('튜토리얼 16단계 + 보상 $50 적용')
