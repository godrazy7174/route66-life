# -*- coding: utf-8 -*-
"""이동형 작업 보상 소폭 인상 (+9~10%) — 소모 3종 + 이동 리스크 프리미엄.

  배달   거리 계수 2 -> 2.2 (기본 15 유지) — 수주 미리보기·도착 정산 2곳
  소몰이 기본 55 -> 60 (레벨당 +3 유지)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

sub('Add(15, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Value In Array(Global Variable(LocPos), Event Player.DelDest)), 2))',
    'Add(15, Multiply(Distance Between(Value In Array(Global Variable(LocPos), 11), Value In Array(Global Variable(LocPos), Event Player.DelDest)), 2.2))', 2)

sub('Set Player Variable(Event Player, RunPay, Add(55, Multiply(3, Min(10,',
    'Set Player Variable(Event Player, RunPay, Add(60, Multiply(3, Min(10,')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('이동형 작업 보상 인상: 배달 거리 x2.2, 소몰이 기본 60')
