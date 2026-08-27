# -*- coding: utf-8 -*-
"""세이브 코드 HUD 수정 — 발급 코드가 "0 - 0"으로 표시되는 문제.

원인
  1. 발급 HUD가 입력용 변수 EnterA/EnterB를 재평가 참조 →
     '코드 입력' 메뉴만 열어도(EnterA/B=0 초기화) 화면 코드가 0 - 0으로 덮임.
  2. 신규 캐릭터($100 미만·무직)는 인코딩 값이 실제로 0이라
     자릿수 패딩 없이는 "0 - 0"으로 보임 — 12자리 입력 형식과 불일치.
  3. 발급 HUD와 키패드 HUD가 SaveHud 한 변수를 공유 →
     입력을 열었다 취소하면 발급 코드 표시가 사라짐.

수정
  - 표시 전용 변수 SaveA/SaveB 분리(발급 스냅샷), PadA/PadB로 6자리 0 패딩.
  - 키패드 HUD는 KeyHud로 분리 — 발급 코드 HUD는 입력 중에도 유지.
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ── 1. 변수 선언 추가 ─────────────────────────────────────────────
sub(T*2 + '84: SaveOn' + N + '}',
    T*2 + '84: SaveOn' + N
  + T*2 + '85: SaveA' + N
  + T*2 + '86: SaveB' + N
  + T*2 + '87: PadA' + N
  + T*2 + '88: PadB' + N
  + T*2 + '89: KeyHud' + N + '}')

# ── 2. 발급 인코딩 → 표시 전용 SaveA/SaveB ───────────────────────
sub('Set Player Variable(Event Player, EnterA, Add(Multiply(Min(9999,',
    'Set Player Variable(Event Player, SaveA, Add(Multiply(Min(9999,')
sub('Set Player Variable(Event Player, EnterB, Add(Multiply(Add(Multiply(Add(Multiply(Add(Multiply(Event Player.Job, 10)',
    'Set Player Variable(Event Player, SaveB, Add(Multiply(Add(Multiply(Add(Multiply(Add(Multiply(Event Player.Job, 10)')
sub('Set Player Variable(Event Player, EnterB, Add(Multiply(Event Player.EnterB, 10), Modulo(Add(Event Player.EnterA, Event Player.EnterB), 9)));',
    'Set Player Variable(Event Player, SaveB, Add(Multiply(Event Player.SaveB, 10), Modulo(Add(Event Player.SaveA, Event Player.SaveB), 9)));')

# ── 3. 자릿수 인덱스 계산 (발급 시 1회) ──────────────────────────
CHK = 'Set Player Variable(Event Player, SaveB, Add(Multiply(Event Player.SaveB, 10), Modulo(Add(Event Player.SaveA, Event Player.SaveB), 9)));'
PADA = 'Set Player Variable(Event Player, PadA, Add(Add(Event Player.SaveA >= 10 ? 1 : 0, Event Player.SaveA >= 100 ? 1 : 0), Add(Event Player.SaveA >= 1000 ? 1 : 0, Add(Event Player.SaveA >= 10000 ? 1 : 0, Event Player.SaveA >= 100000 ? 1 : 0))));'
PADB = PADA.replace('SaveA', 'SaveB').replace('PadA', 'PadB')
sub(CHK + N + T*4 + 'Destroy HUD Text(Event Player.SaveHud);',
    CHK + N + T*4 + PADA + N + T*4 + PADB + N + T*4 + 'Destroy HUD Text(Event Player.SaveHud);')

# ── 4. 발급 HUD — 6자리 0 패딩 표시 ──────────────────────────────
PADS = 'Array(Custom String("00000"), Custom String("0000"), Custom String("000"), Custom String("00"), Custom String("0"), Custom String(""))'
sub('Custom String("세이브 코드   {0} - {1}", Event Player.EnterA, Event Player.EnterB)',
    'Custom String("세이브 코드   {0} - {1}", Custom String("{0}{1}", Value In Array(' + PADS + ', Event Player.PadA), Event Player.SaveA), Custom String("{0}{1}", Value In Array(' + PADS + ', Event Player.PadB), Event Player.SaveB))')

# ── 5. 입력 시작 — 발급 HUD는 유지, 키패드는 KeyHud로 ────────────
sub('Set Player Variable(Event Player, EntryCur, 0);' + N + T*4 + 'Destroy HUD Text(Event Player.SaveHud);' + N,
    'Set Player Variable(Event Player, EntryCur, 0);' + N)
sub('Color(Aqua), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);' + N + T*4 + 'Set Player Variable(Event Player, SaveHud, Last Text ID());',
    'Color(Aqua), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);' + N + T*4 + 'Set Player Variable(Event Player, KeyHud, Last Text ID());')

# ── 6. 키패드 파괴 지점 4곳 → KeyHud ─────────────────────────────
sub(N + T*3 + 'Destroy HUD Text(Event Player.SaveHud);',
    N + T*3 + 'Destroy HUD Text(Event Player.KeyHud);', 2)   # [세이브 02] 완료 + 사망 정리
sub(N + T*2 + 'Destroy HUD Text(Event Player.SaveHud);',
    N + T*2 + 'Destroy HUD Text(Event Player.KeyHud);', 2)   # [세이브 03] 취소 + [세이브 04] 이탈

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('세이브 HUD 수정 완료: SaveA/SaveB 분리 + 6자리 패딩 + KeyHud 분리')
