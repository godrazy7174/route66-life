# -*- coding: utf-8 -*-
"""등불 제거. 밤 연출은 '조명이 꺼진다'로 단순화.

  낮 : 장소마다 광기둥이 켜져 있다
  밤 : 광기둥이 전부 꺼진다. 그게 전부.

플레이어에게 붙는 이펙트는 하나도 남기지 않는다 (3인칭 시야 방해 원천 차단).
길찾기는 항상 떠 있는 장소 이름 표지판이 담당한다.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) [월드 08] 밤 — 등불 룰 통째로 제거 ──────────────────────────
a = s.index('rule("[월드 08] 밤 — 등불")')
b = s.index('\nrule(', a + 5) + 1
s = s[:a] + s[b:]

# ── 2) 이 패치로 쓸모없어진 Lantern 변수 정리 ──────────────────────
s = s.replace('\t\t19: Lantern\n', '', 1)
s = s.replace('\t\tSet Player Variable(Event Player, Lantern, 0);\n', '', 1)
assert 'Lantern' not in s

# ── 3) 광기둥: 낮에만 켜진다 ───────────────────────────────────────
DAY = 'Global Variable(IsNight) == 0 ? All Players(All Teams) : False'
pat = (r'Create Effect\(All Players\(All Teams\), Light Shaft, '
       r'Global Variable\(IsNight\) == 1 \? Color\(Orange\) : (Color\(\w+\)), '
       r'(Value In Array\(Global Variable\(LocPos\), \d+\)), '
       r'Global Variable\(IsNight\) == 1 \? 1\.8 : 1\.2, '
       r'Visible To Position Radius and Color\);')
n = len(re.findall(pat, s))
s = re.sub(pat,
           lambda m: 'Create Effect(%s, Light Shaft, %s, %s, 1.2, Visible To Position Radius and Color);'
                     % (DAY, m.group(1), m.group(2)),
           s)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  [월드 08] 등불 룰 : 제거')
print('  Lantern 변수      : 제거 (이 패치로 미사용)')
print('  광기둥 %d개       : 낮에만 표시, 반경 1.2 고정' % n)
print('  플레이어 부착 이펙트 : %d개' % s.count(', Event Player, 0.'))
