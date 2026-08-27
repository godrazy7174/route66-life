# -*- coding: utf-8 -*-
"""밀수 재수주 쿨타임 60초 -> 30초.

sim_economy.py 로 여섯 직업의 지속 수익을 재보니 밀수가 $99/분으로 꼴찌였다.
밀수는 '벌이가 나쁘지만 악명이 오르는 길'로 설계된 것이 아니라
'무법자의 안전한 벌이'로 설계됐는데, 실제로는 목동($117)보다도 못했다.
병목은 보수(2배 계수)가 아니라 인계 후 60초 동안 아무것도 못 하는 대기였다.
쿨타임만 절반으로 줄여 사이클 밀도를 올린다 (-> 약 $163/분, 목동 위).
보수 계수는 건드리지 않는다 — 한 건당 벌이가 커지면 원거리 접선의
'위험 감수' 균형이 같이 흔들린다.

쿨타임 안내 문구는 남은 시간을 계산해 띄우므로 문자열 수정은 필요 없다.
"""
import io

PATH = 'ROUTE66_LIFE_EN.ow'
OLD = '\t\t\tSet Player Variable(Event Player, SmuggleCd, Add(Total Time Elapsed(), 60));'
NEW = '\t\t\tSet Player Variable(Event Player, SmuggleCd, Add(Total Time Elapsed(), 30));'

src = io.open(PATH, encoding='utf-8').read()
assert src.count(OLD) == 1, src.count(OLD)
io.open(PATH, 'w', encoding='utf-8', newline='').write(src.replace(OLD, NEW))
print('ok')
