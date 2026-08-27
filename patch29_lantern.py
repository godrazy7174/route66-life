# -*- coding: utf-8 -*-
"""등불이 자기 시야를 가리는 문제.

원인: 이펙트가 Event Player 에 붙어 있는데 3인칭 고정이라
      플레이어가 항상 화면 정중앙이다. 즉 자기 등불을 정면으로 들여다본다.
      반경 0.5 Orb + 블룸이면 화면 절반이 노랗게 탄다.

수정: 등불을 '남이 보는 표시'로 바꾼다.
      - 보이는 대상에서 본인 제외 -> 내 시야는 완전히 깨끗
      - 반경 0.5 -> 0.3 (남의 등불도 가까이서 안 타게)
      밤에 멀리서 사람이 오는 걸 알아보는 기능은 그대로 남는다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

OLD = ('\t\tCreate Effect(All Players(All Teams), Orb, Color(Orange), '
       'Event Player, 0.5, Visible To Position and Radius);')
NEW = ('\t\tCreate Effect(Remove From Array(All Players(All Teams), Event Player), Orb, '
       'Color(Orange), Event Player, 0.3, Visible To Position and Radius);')
assert s.count(OLD) == 1
s = s.replace(OLD, NEW, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  등불 보이는 대상 : 전원 -> 본인 제외')
print('  등불 반경        : 0.5 -> 0.3')
