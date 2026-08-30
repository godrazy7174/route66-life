# -*- coding: utf-8 -*-
"""원석·가죽 시세 변동성 대폭 증가 (지시).

매일 아침 [월드 01] 이 뽑는 시세를 넓힌다. **평균은 그대로 두고 폭만 키운다** —
평균까지 오르면 광부·사냥꾼의 기대 수입 자체가 변해 경제 균형(sim_economy.py)이
같이 움직이기 때문이다.

    원석: 2~5 (평균 3.5, 폭 3) -> 1~6 (평균 3.5, 폭 5)
    가죽: 3~6 (평균 4.5, 폭 3) -> 1~8 (평균 4.5, 폭 7)

최저가가 1 이 되면서 "오늘은 헐값이라 파는 게 손해" 인 날이 생기고,
최고가 6/8 인 날은 몰아 파는 날이 된다 — "시세를 보고 팔아라" 는 튜토리얼 문구가
실제 의사결정이 된다. 1일차 개장가(원석 2 / 가죽 5)는 그대로 둔다.

창고 상한(원석·가죽 보관)은 없으므로 몰아 팔기에 걸림돌은 없다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new):
    global s
    assert s.count(old) == 1, (old, s.count(old))
    s = s.replace(old, new)


sub("Set Global Variable(OrePrice, Random Integer(2, 5));",
    "Set Global Variable(OrePrice, Random Integer(1, 6));")
sub("Set Global Variable(HidePrice, Random Integer(3, 6));",
    "Set Global Variable(HidePrice, Random Integer(1, 8));")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
