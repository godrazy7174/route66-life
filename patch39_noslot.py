# -*- coding: utf-8 -*-
"""야수 시스템에서 Slot Of 를 완전히 제거한다.

남아 있던 곳
    DoHunt      BeastTimer[Slot Of(Target)] = now + 30
    은신 조건    Total Time Elapsed() >= BeastTimer[Slot Of(Event Player)]
    처치        BeastTimer[Slot Of(Victim)] = 0

Slot Of 가 봇에서 기대대로 안 나오면 Value In Array 가 0을 돌려주고,
은신 조건이 늘 참이 되어 '드러나자마자 다시 숨는다'. 아이콘도 뜰 틈이 없다.
전역 배열 대신 봇 자신의 변수에 해제 시각을 적으면 인덱스가 아예 필요 없다.

BeastTimer 전역은 이 변경으로 쓸모가 없어져 함께 지운다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

assert 'RevealEnd' not in s
s = s.replace('\t\t28: Target\n', '\t\t27: RevealEnd\n\t\t28: Target\n', 1)

PAIRS = [
    ('Set Global Variable At Index(BeastTimer, Slot Of(Event Player.Target), Add(Total Time Elapsed(), 30));',
     'Set Player Variable(Event Player.Target, RevealEnd, Add(Total Time Elapsed(), 30));'),
    ('Total Time Elapsed() >= Value In Array(Global Variable(BeastTimer), Slot Of(Event Player));',
     'Total Time Elapsed() >= Event Player.RevealEnd;'),
    ('Set Global Variable At Index(BeastTimer, Slot Of(Victim), 0);',
     'Set Player Variable(Victim, RevealEnd, 0);'),
]
for old, new in PAIRS:
    assert s.count(old) == 1, old[:40]
    s = s.replace(old, new, 1)

# 이 변경으로 쓸모없어진 전역 정리
s = s.replace('\t\t26: BeastTimer\n', '', 1)
s = s.replace('\t\tSet Global Variable(BeastTimer, Array(0, 0, 0));\n', '', 1)
assert 'BeastTimer' not in s and 'Slot Of' not in s

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료 — 야수 시스템에서 Slot Of / BeastTimer 제거')
