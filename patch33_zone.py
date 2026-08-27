# -*- coding: utf-8 -*-
"""식당 자리에 서면 튜토리얼이 뜨는 문제.

구역 감지가 '반경 안에 들어온 것 중 마지막 인덱스'를 채택하고 있었다.
    for Idx in 0..10: if 반경 안 -> Zone = Idx
그래서 겹치는 구간에서는 항상 인덱스가 큰 쪽이 이긴다.

실제 겹침 (좌표로 확인)
    식당(r7)   <-> 안내소(r9, r5)   4.0m
    정비소(r4) <-> 대장간(r10, r6)  6.0m

식당 표지판은 LocPos[0]에 있는데 그 지점은 안내소 중심에서 4m,
즉 안내소 반경(5) 안이다. 인덱스 9가 0을 이기므로
'식당 표지판 앞 = 안내소' 가 되어 F를 누르면 튜토리얼이 시작됐다.
식당으로 인식되는 건 표지판에서 오히려 멀어져야 했다.

수정: 마지막 인덱스가 아니라 '가장 가까운 중심'을 채택한다.
      표지판 바로 앞에 서면 그 표지판의 장소가 잡힌다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# 전용 변수 (Lantern 제거로 비어 있던 19번)
assert 'ZoneDist' not in s
s = s.replace('\t\t20: Init\n', '\t\t19: ZoneDist\n\t\t20: Init\n', 1)

D = ('Distance Between(Position Of(Event Player), '
     'Value In Array(Global Variable(LocPos), Event Player.Idx))')

OLD = '''		Set Player Variable(Event Player, Tmp, -1);
		For Player Variable(Event Player, Idx, 0, 11, 1);
			If(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), Event Player.Idx)) <= Value In Array(Global Variable(LocRad), Event Player.Idx));
				Set Player Variable(Event Player, Tmp, Event Player.Idx);
			End;
		End;
'''
NEW = '''		Set Player Variable(Event Player, Tmp, -1);
		Set Player Variable(Event Player, ZoneDist, 9999);
		For Player Variable(Event Player, Idx, 0, 11, 1);
			If(And(%s <= Value In Array(Global Variable(LocRad), Event Player.Idx), %s < Event Player.ZoneDist));
				Set Player Variable(Event Player, Tmp, Event Player.Idx);
				Set Player Variable(Event Player, ZoneDist, %s);
			End;
		End;
''' % (D, D, D)

assert s.count(OLD) == 1
s = s.replace(OLD, NEW, 1)
s = s.replace('\t\tSet Player Variable(Event Player, Sprinting, 0);\n',
              '\t\tSet Player Variable(Event Player, Sprinting, 0);\n'
              '\t\tSet Player Variable(Event Player, ZoneDist, 9999);\n', 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료 — 구역 판정: 마지막 인덱스 -> 가장 가까운 중심')
