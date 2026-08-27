# patch154 (전수조사 #13, #14)
#  [의도불일치 H] 역마차 습격 보상 $80~140 — 24초 추격에 현상금 +200·악명 +15까지 지는데
#                 위험 없는 소몰이($220)·보물 상자($150~350)보다 낮다. 금고 마차($250~450)급으로 조정
#  [불일치 I] 쥐떼 등장 공지가 아직 '잡화점을 노린다' — 이제 사람을 문다
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

PAIRS = [
 ('Set Player Variable(Event Player, PlanPay, Random Integer(80, 140));',
  'Set Player Variable(Event Player, PlanPay, Random Integer(260, 420));'),
 ('쥐떼가 몰려온다!! 잡화점을 노린다 — 혼자서는 못 막는다',
  '쥐떼가 몰려온다!! 사람을 물고 육포를 노린다 — 혼자서는 못 막는다'),
]
for o, n in PAIRS:
    assert t.count(o) == 1, o[:40]
    t = t.replace(o, n)

assert t.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch154 ok')
