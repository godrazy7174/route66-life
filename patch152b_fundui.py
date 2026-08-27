# patch152b (전수조사 #6~#11): 마을 금고 통합 후 남은 구 시스템 표기 전량 정리
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()
GOALS9 = 'Array(8000, 23000, 48000, 88000, 148000, 233000, 348000, 498000, 498000)'

PAIRS = [
 # 1) 상단 HUD — 단계와 다음 목표액을 상시 표시
 ('Custom String("부흥 기금 $ {0}   ({1}/3)", Global Variable(Fund), Global Variable(FundTier))',
  f'Custom String("마을 금고 {{0}}/8   $ {{1}} / {{2}}", Global Variable(TownStage), Global Variable(Fund), Value In Array({GOALS9}, Global Variable(TownStage)))'),

 # 2) 안내소 앞 이정표
 ('Custom String("마을 재건 {0} / 5", Global Variable(RebuildMax))',
  'Custom String("마을 금고 {0} / 8", Global Variable(TownStage))'),

 # 3) 안내소 표지판 설명
 (r'마을 재건 — 우물에서 기차역까지 다섯 단계, 총 $1,000,000\r\n',
  r'마을 금고 — $1,000씩 함께 보태 우물에서 기차역까지 여덟 단계\r\n'),

 # 4) 정거장 표지판 설명
 ('부흥 기금 — $1000씩 모아 쉼터·급행로·대축제를 연다',
  '마을 금고 — $1000씩 보태 우물부터 기차역까지 여덟 걸음'),

 # 5) 메뉴 라벨 2개 (같은 기능이므로 같은 이름으로)
 ('Custom String("마을 재건")', 'Custom String("마을 금고에 $1,000")'),
 ('Custom String("부흥 기금 기부 $1,000")', 'Custom String("마을 금고에 $1,000")'),

 # 6) [기금 01] 중복 공지 강등 — [금고 01]이 이미 건물 완성을 알린다
 ('Big Message(All Players(All Teams), Custom String("부흥 기금 1단계!! 길손의 쉼터가 세워졌다 — 길목의 모닥불에서 몸을 데워라"));',
  'Small Message(All Players(All Teams), Custom String("특전 — 길목의 모닥불에서 몸을 데운다"));'),
 ('Big Message(All Players(All Teams), Custom String("부흥 기금 2단계!! 역마차 급행로 개통 — 배달·금괴 호송 보수 +15%"));',
  'Small Message(All Players(All Teams), Custom String("특전 — 배달·금괴 호송 보수 +15%"));'),
 ('Big Message(All Players(All Teams), Custom String("부흥 기금 3단계!! 국도 대축제 — 오늘의 직업 1.75배 · 밤마다 불꽃놀이 · 아침마다 명성 +1"));',
  'Small Message(All Players(All Teams), Custom String("특전 — 오늘의 직업 1.75배 · 밤마다 불꽃놀이 · 아침마다 명성 +1"));'),
]

for o, n in PAIRS:
    c = t.count(o)
    assert c == 1, f'{c} matches: {o[:60]}'
    t = t.replace(o, n)

assert '부흥 기금' not in t
assert '마을 재건' not in t
assert t.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch152b ok')
