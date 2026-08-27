# -*- coding: utf-8 -*-
"""전 품목 가격 인상 (+50~60%) — 돈이 너무 빨리 벌린다는 피드백.

  소모품   식사 12->18 · 육포 15->22 · 물통 10->15 · 묶음 65->95
          위스키 25->38 · 숙박 60->90 · 정밀 탐사 30->45
  도박     판돈 50->75 · 승리 90->135 · 잭팟 300->450 (배율 유지)
  장비     곡괭이 500/1200/2500/5000 -> 800/2000/4000/8000
          배낭 1800->2800 · 말 3500->5500 · 내 방 7000->11000
  사치     불꽃놀이 3000->5000 · 황금 동상 25000->40000
  부동산   식당 15000 · 술집 18000 · 모텔 21000 · 잡화점 24000
          정비소 27000 · 대장간 30000 (+50%)
  판매가(원석·가죽·배달 보수 등 수입)는 그대로 — 회수만 키운다.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ── 소모품 로직 (평판 공식 기준가) ─────────────────────────────────
sub('Multiply(12, Subtract', 'Multiply(18, Subtract')
sub('Multiply(15, Subtract', 'Multiply(22, Subtract')
sub('Multiply(10, Subtract', 'Multiply(15, Subtract')
sub('Multiply(65, Subtract', 'Multiply(95, Subtract')
sub('Multiply(25, Subtract', 'Multiply(38, Subtract', 3)
sub('Multiply(60, Subtract', 'Multiply(90, Subtract')
sub('? 0 : 30);', '? 0 : 45);')

# ── 도박 ───────────────────────────────────────────────────────────
sub('If(Event Player.Money >= 50);', 'If(Event Player.Money >= 75);')
sub('Modify Player Variable(Event Player, Money, Subtract, 50);', 'Modify Player Variable(Event Player, Money, Subtract, 75);')
sub("Rent, Max(1, Round To Integer(Multiply(50, 0.1), To Nearest)));", "Rent, Max(1, Round To Integer(Multiply(75, 0.1), To Nearest)));")
sub('Modify Player Variable(Event Player, Money, Add, 90);', 'Modify Player Variable(Event Player, Money, Add, 135);')
sub('Modify Player Variable(Event Player, Earned, Add, 90);', 'Modify Player Variable(Event Player, Earned, Add, 135);')
sub('Modify Player Variable(Event Player, Money, Add, 300);', 'Modify Player Variable(Event Player, Money, Add, 450);')
sub('Modify Player Variable(Event Player, Earned, Add, 300);', 'Modify Player Variable(Event Player, Earned, Add, 450);')
sub('술집에서 잭팟! $300', '술집에서 잭팟! $450')
sub('이겼다 — $90 획득', '이겼다 — $135 획득')
sub('판돈이 부족합니다 ($50 필요)', '판돈이 부족합니다 ($75 필요)')

# ── 장비 ───────────────────────────────────────────────────────────
sub('Array(500, 1200, 2500, 5000)', 'Array(800, 2000, 4000, 8000)', 3)
sub('Modify Player Variable(Event Player, Money, Subtract, 1800);', 'Modify Player Variable(Event Player, Money, Subtract, 2800);')
sub('Else If(Event Player.Money >= 1800);', 'Else If(Event Player.Money >= 2800);')
sub('돈이 부족합니다 ($1800 필요)', '돈이 부족합니다 ($2800 필요)')
sub("Rent, Max(1, Round To Integer(Multiply(1800, 0.1), To Nearest)));", "Rent, Max(1, Round To Integer(Multiply(2800, 0.1), To Nearest)));")
sub('Modify Player Variable(Event Player, Money, Subtract, 3500);', 'Modify Player Variable(Event Player, Money, Subtract, 5500);')
sub('Else If(Event Player.Money >= 3500);', 'Else If(Event Player.Money >= 5500);')
sub('돈이 부족합니다 ($3500 필요)', '돈이 부족합니다 ($5500 필요)')
sub("Rent, Max(1, Round To Integer(Multiply(3500, 0.1), To Nearest)));", "Rent, Max(1, Round To Integer(Multiply(5500, 0.1), To Nearest)));")
sub('Modify Player Variable(Event Player, Money, Subtract, 7000);', 'Modify Player Variable(Event Player, Money, Subtract, 11000);')
sub('Else If(Event Player.Money >= 7000);', 'Else If(Event Player.Money >= 11000);')
sub('돈이 부족합니다 ($7000 필요)', '돈이 부족합니다 ($11000 필요)')
sub("Rent, Max(1, Round To Integer(Multiply(7000, 0.1), To Nearest)));", "Rent, Max(1, Round To Integer(Multiply(11000, 0.1), To Nearest)));")

# ── 사치 ───────────────────────────────────────────────────────────
sub('If(Event Player.Money >= 3000);', 'If(Event Player.Money >= 5000);')
sub('Modify Player Variable(Event Player, Money, Subtract, 3000);', 'Modify Player Variable(Event Player, Money, Subtract, 5000);')
sub("Rent, Max(1, Round To Integer(Multiply(3000, 0.1), To Nearest)));", "Rent, Max(1, Round To Integer(Multiply(5000, 0.1), To Nearest)));")
sub('돈이 부족합니다 ($3000 필요)', '돈이 부족합니다 ($5000 필요)')
sub('If(Event Player.Money >= 25000);', 'If(Event Player.Money >= 40000);')
sub('Modify Player Variable(Event Player, Money, Subtract, 25000);', 'Modify Player Variable(Event Player, Money, Subtract, 40000);')
sub("Rent, Max(1, Round To Integer(Multiply(25000, 0.1), To Nearest)));", "Rent, Max(1, Round To Integer(Multiply(40000, 0.1), To Nearest)));")
sub('돈이 부족합니다 ($25000 필요)', '돈이 부족합니다 ($40000 필요)')
sub('황금 동상을 세웠다!! ($25,000)', '황금 동상을 세웠다!! ($40,000)')

# ── 부동산 ─────────────────────────────────────────────────────────
sub('Array(10000, 0, 16000, 14000, 18000, 12000, 0, 0, 0, 0, 20000)',
    'Array(15000, 0, 24000, 21000, 27000, 18000, 0, 0, 0, 0, 30000)')

# ── 패널·라벨·안내 문구 ────────────────────────────────────────────
sub('식사 $12 — 허기·갈증 회복', '식사 $18 — 허기·갈증 회복', 3)
sub('따뜻한 식사 $12 — 허기와 갈증을 한 번에 채운다', '따뜻한 식사 $18 — 허기와 갈증을 한 번에 채운다', 3)
sub('육포 $15 (재고 {0})      물통 $10      묶음 $65', '육포 $22 (재고 {0})      물통 $15      묶음 $95')
sub('육포 구매 $15', '육포 구매 $22')
sub('물통 구매 $10', '물통 구매 $15')
sub('육포 5개 묶음 $65', '육포 5개 묶음 $95')
sub('숙박 $60 — 피로 40 회복', '숙박 $90 — 피로 40 회복')
sub('숙박 $60 — 피로 회복', '숙박 $90 — 피로 회복')
sub('내 방 마련 $7000 — 숙박 회복 80', '내 방 마련 $11000 — 숙박 회복 80')
sub('내 방 마련 $7000', '내 방 마련 $11000')
sub('위스키 $25 — 피로 회복', '위스키 $38 — 피로 회복', 2)
sub('카드 도박 $50', '카드 도박 $75', 2)
sub('정밀 탐사 $30', '정밀 탐사 $45', 2)
sub('가죽 배낭 $1800 — 트레이서 변신', '가죽 배낭 $2800 — 트레이서 변신')
sub('가죽 배낭 $1800', '가죽 배낭 $2800')
sub('말 $3500 — 시온 변신', '말 $5500 — 시온 변신')
sub('말 $3500', '말 $5500')
sub('황금 동상 $25000 — 식당 앞', '황금 동상 $40000 — 식당 앞')
sub('황금 동상 $25,000', '황금 동상 $40,000')
sub('불꽃놀이 $3000 — 전 서버', '불꽃놀이 $5000 — 전 서버')
sub('불꽃놀이 $3,000', '불꽃놀이 $5,000')
sub('하룻밤 $60에 피로를 40 되찾는다', '하룻밤 $90에 피로를 40 되찾는다')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('전 품목 가격 인상 완료')
