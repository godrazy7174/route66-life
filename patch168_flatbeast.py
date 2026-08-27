# patch168: 쥐 격리 때 만든 '중첩 Filtered Array' 3곳을 단일 필터로 평탄화
#  중첩하면 안팎의 Current Array Element가 충돌해 결과가 비어 버린다(샛길에서 실측).
#  이 셋은 각각 숨은 야수 카운트 / 사냥 대상 선정 / 대야수 선정이라,
#  비면 야수를 아예 찾지 못하는 치명적 결과가 된다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

SLOT = 'Slot Of(Current Array Element) <= 2'
PAIRS = [
 # 1) 숨은 야수 카운트
 ('Filtered Array(Filtered Array(All Players(Team 2), ' + SLOT + '), And(Is Dummy Bot(Current Array Element), '
  'And(Is Alive(Current Array Element), Total Time Elapsed() >= Player Variable(Current Array Element, RevealEnd))))',
  'Filtered Array(All Players(Team 2), And(' + SLOT + ', And(Is Dummy Bot(Current Array Element), '
  'And(Is Alive(Current Array Element), Total Time Elapsed() >= Player Variable(Current Array Element, RevealEnd)))))'),
 # 2) 사냥 대상 선정
 ('Filtered Array(Filtered Array(All Players(Team 2), ' + SLOT + '), And(And(Is Dummy Bot(Current Array Element), '
  'Is Alive(Current Array Element)), Current Array Element != Global Variable(HuntBeast)))',
  'Filtered Array(All Players(Team 2), And(' + SLOT + ', And(And(Is Dummy Bot(Current Array Element), '
  'Is Alive(Current Array Element)), Current Array Element != Global Variable(HuntBeast))))'),
 # 3) 대야수 선정
 ('Filtered Array(Filtered Array(All Players(Team 2), ' + SLOT + '), And(Is Dummy Bot(Current Array Element), '
  'Is Alive(Current Array Element)))',
  'Filtered Array(All Players(Team 2), And(' + SLOT + ', And(Is Dummy Bot(Current Array Element), '
  'Is Alive(Current Array Element))))'),
]
for o, n in PAIRS:
    c = t.count(o)
    assert c == 1, (c, o[:80])
    t = t.replace(o, n)

assert 'Filtered Array(Filtered Array(' not in t
assert t.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch168 ok - all nested filters flattened')
