"""1. 전량 판매 시 "0개 판매"로 표시
   원인: 메시지 문자열이 표시되는 동안 계속 재평가되는데,
         메시지를 띄운 직후 재고를 0으로 만들어서 0으로 바뀐다.
   -> 수량을 별도 변수(Amt)에 먼저 담아두고 그 값을 표시한다.
      (레퍼런스는 값 변경 전에 Wait(0.016)을 넣어 우회하지만,
       스냅샷 방식이 대기 없이 확실하다.)

2. 장소 상세 패널에 눌러야 할 키가 없다
   식당과 안내소에만 키 안내가 있었다.
   -> 10곳 전부에 키 줄을 붙인다. 행동이 하나뿐인 장소는 [F]만,
      여러 개인 장소는 [R] 행동 선택 + [F] 실행.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 판매 수량 스냅샷 ────────────────────────────────────────────
s = s.replace("\t\t37: SleepDay\n", "\t\t37: SleepDay\n\t\t38: Amt\n")

for inv_idx, price, label in ((2, 'OrePrice', '원석'), (3, 'HidePrice', '가죽')):
    old = ('\t\t\t\tSet Player Variable(Event Player, Roll, Multiply(Value In Array(Event Player.Inv, %d), Global Variable(%s)));'
           % (inv_idx, price))
    new = ('\t\t\t\tSet Player Variable(Event Player, Amt, Value In Array(Event Player.Inv, %d));\n'
           '\t\t\t\tSet Player Variable(Event Player, Roll, Multiply(Event Player.Amt, Global Variable(%s)));'
           % (inv_idx, price))
    assert old in s, '판매 계산 구간(%s)을 찾지 못함' % label
    s = s.replace(old, new)

s = s.replace('Custom String("원석 {0}개 판매 — $ {1}", Value In Array(Event Player.Inv, 2), Event Player.Roll)',
              'Custom String("원석 {0}개 판매 — $ {1}", Event Player.Amt, Event Player.Roll)')
s = s.replace('Custom String("가죽 {0}장 판매 — $ {1}", Value In Array(Event Player.Inv, 3), Event Player.Roll)',
              'Custom String("가죽 {0}장 판매 — $ {1}", Event Player.Amt, Event Player.Roll)')

# 장물 거래도 수량을 보여주도록
s = s.replace('Custom String("장물을 넘겼다 — $ {0}   (평판 -5)", Event Player.Roll)',
              'Custom String("장물을 넘겼다 — $ {0}   (평판 -5)", Event Player.Roll)')

# ── 2) 상세 패널에 키 안내 ────────────────────────────────────────
KEY_R = 'Input Binding String(Button(Reload))'
KEY_F = 'Input Binding String(Button(Interact))'
MULTI = 'Custom String("[{0}] 행동 선택      [{1}] 실행", %s, %s)' % (KEY_R, KEY_F)
SINGLE = 'Custom String("[{0}] 실행", %s)' % KEY_F

BODY = [
    ('Custom String("전직  광부 · 사냥꾼 · 현상금 사냥꾼\\r\\n식사 $12\\r\\n")', MULTI),
    ('Custom String("채굴 — 원석 획득\\r\\n정밀 탐사 $30\\r\\n오늘 원석 시세  $ {0}\\r\\n", Global Variable(OrePrice))', MULTI),
    ('Custom String("육포 $15      물통 $10      육포 5개 묶음 $65\\r\\n")', MULTI),
    ('Custom String("숙박 $60 — 하루 한 번\\r\\n피로가 완전히 회복된다\\r\\n")', SINGLE),
    ('Custom String("원석  $ {0}       가죽  $ {1}\\r\\n시세는 매일 아침 바뀐다\\r\\n", Global Variable(OrePrice), Global Variable(HidePrice))', MULTI),
    ('Custom String("위스키 $25 — 피로 회복\\r\\n카드 도박 $50\\r\\n소문 듣기\\r\\n")', MULTI),
    ('Custom String("흔적 추적 → 사냥감 출현\\r\\n좌클릭으로 직접 쏴서 잡는다\\r\\n")', SINGLE),
    ('Custom String("벌금 $100 — 수배 말소\\r\\n현상금 게시판\\r\\n무법자 1명당  $ {0}\\r\\n", Global Variable(BotBounty))', MULTI),
    ('Custom String("무법자 합류\\r\\n장물 거래 — 무법자 165% / 일반 130%\\r\\n습격 계획\\r\\n")', MULTI),
    ('Custom String("튜토리얼 — 처음이라면 여기서\\r\\n완주 보상  육포 3 · 물통 3 · $30\\r\\n")', SINGLE),
]

lines = s.split('\n')
fixed = 0
for i, line in enumerate(lines):
    m = re.match(r'(\s*)Create In-World Text\(And\(Distance Between\(Local Player, Value In Array\(Global Variable\(LocPos\), (\d+)\)\) < 22, Local Player\.TutOn == 0\) \? Local Player : False, .*?, (Add\(Value In Array\(Global Variable\(LocPos\), \d+\), Vector\(0, 1\.5, 0\)\), 0\.95, Do Not Clip, Visible To Position and String, Color\(White\), Default Visibility\);)$', line)
    if not m:
        continue
    indent, idx, tail = m.group(1), int(m.group(2)), m.group(3)
    body, keys = BODY[idx]
    txt = 'Custom String("{0}{1}", %s, %s)' % (body, keys)
    lines[i] = ('%sCreate In-World Text(And(Distance Between(Local Player, Value In Array(Global Variable(LocPos), %d)) < 22, '
                'Local Player.TutOn == 0) ? Local Player : False, %s, %s' % (indent, idx, txt, tail))
    fixed += 1
s = '\n'.join(lines)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  판매 수량 스냅샷 : %d곳' % s.count('Set Player Variable(Event Player, Amt,'))
print('  키 안내 붙인 패널: %d / 10' % fixed)
