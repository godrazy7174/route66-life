# -*- coding: utf-8 -*-
"""그림자 강도 접근 속도 소폭 증가 (지시).

[파발 03] 의 그림자는 0.25초마다 플레이어 쪽으로 1.7m 씩 다가온다 = 6.8 m/s.
1.7 -> 2.0 으로 올린다 = 8.0 m/s (약 18% 증가).

참고 좌표계: 걷기 100% = 5.5 m/s, 질주 165% = 약 9.1 m/s.
6.8 은 걷기보다 빠르고 질주보다 느렸는데, 8.0 이면 질주에 바짝 붙는다 —
도망만으로는 못 떨치고 세 발을 쏴야 한다는 원래 설계가 더 선명해진다.
물리는 30m 안에서 조준하고 좌클릭이면 명중 판정이므로 속도와 무관하다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

OLD = "Multiply(Direction Towards(Event Player.EscortPos, Position Of(Event Player)), 1.7)"
NEW = "Multiply(Direction Towards(Event Player.EscortPos, Position Of(Event Player)), 2.0)"
assert s.count(OLD) == 1, s.count(OLD)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(OLD, NEW))
print('ok')
