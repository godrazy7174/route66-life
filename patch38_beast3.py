# -*- coding: utf-8 -*-
"""야수 아이콘이 여전히 안 뜨는 문제 — 의심 두 가지를 한꺼번에 제거.

  (1) 아이콘 위치를 플레이어 엔티티로 줬다.
      이 스크립트에서 실제로 화면에 뜬 아이콘(보물·무법자)은 전부 벡터 위치다.
      -> 머리 위 벡터로 통일.

  (2) 표시 조건이 BeastTimer[Slot Of(...)] 에 물려 있다.
      Slot Of 가 봇에서 기대대로 안 나오면 조건 자체가 성립하지 않는다.
      -> '숨은 상태 = Phased Out' 을 직접 본다. 은신 룰이 걸고 DoHunt 가 푼다.

배회 조건과 DoHunt 사냥감 선별도 같은 이유로 Phased Out 기준으로 바꾼다.
덤: 숨은 야수는 투명이라 몇 마리인지 알 길이 없었다 -> 개활지 패널에 수를 띄운다.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

SHOWN   = 'Has Status(Event Player, Phased Out) == False'
HIDDEN  = 'Has Status(Event Player, Phased Out) == True'
OLDCOND = 'Value In Array(Global Variable(BeastTimer), Slot Of(Event Player)) > Total Time Elapsed()'

n = s.count(OLDCOND)
assert n == 4, n            # 배회 조건 + 배회 Loop If + 표시 조건 + 표시 Wait Until
s = s.replace(OLDCOND, SHOWN)
s = s.replace('Not(%s)' % SHOWN, HIDDEN, 1)

OLDI = 'Create Icon(All Players(All Teams), Event Player, Eye, Visible To and Position, Color(Orange), True);'
NEWI = ('Create Icon(All Players(All Teams), Add(Position Of(Event Player), Vector(0, 1.8, 0)), '
        'Eye, Visible To and Position, Color(Orange), True);')
assert s.count(OLDI) == 1
s = s.replace(OLDI, NEWI, 1)

OLDT = 'Value In Array(Global Variable(BeastTimer), Slot Of(Current Array Element)) <= Total Time Elapsed()'
assert s.count(OLDT) == 1
s = s.replace(OLDT, 'Has Status(Current Array Element, Phased Out) == True', 1)

OLDP = ('Custom String("야수는 숨어 있다 — 추적해야 모습을 드러낸다' + NL
        + '드러난 30초 안에 좌클릭으로 잡아라' + NL + '")')
assert s.count(OLDP) == 1, s.count(OLDP)
NEWP = ('Custom String("이 일대에 야수 {0}마리 — 숨어 있어 눈에 띄지 않는다' + NL
        + '추적하면 30초 동안 모습을 드러낸다' + NL + '", '
        'Count Of(Filtered Array(All Players(Team 2), And(Is Dummy Bot(Current Array Element), '
        'Is Alive(Current Array Element)))))')
s = s.replace(OLDP, NEWP, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  표시/배회 조건 : BeastTimer[Slot Of] -> Phased Out 직접 확인')
print('  아이콘 위치    : 플레이어 엔티티 -> 머리 위 벡터')
print('  사냥감 선별    : 슬롯 의존 제거')
print('  개활지 패널    : 살아있는 야수 수 표시')
