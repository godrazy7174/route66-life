# -*- coding: utf-8 -*-
"""낮 조명이 마을 위에만 있어 외곽(협곡·고지대)이 어두운 문제.

기존: 장소 3곳 상공에만 발광 -> 마을을 벗어나면 밤 맵 그대로
수정: 확정 좌표로 잰 맵 범위(X -75~44, Z -46~62)에 여유를 두고
      상공 격자로 은은한 발광을 깐다. 넓고 약하게 여러 개 겹쳐
      한 덩어리로 뭉쳐 보이지 않게 한다.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
DAY = 'Global Variable(IsNight) == 0 ? All Players(All Teams) : False'

# ── 기존 장소 기준 하늘 발광 3개 제거 ──────────────────────────────
n = len(re.findall(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, Good Aura, Color\(White\), Add\(Value In Array\(Global Variable\(LocPos\), \d+\), Vector\(0, 55, 0\)\), 30, Visible To Position Radius and Color\);\n', s))
s = re.sub(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, Good Aura, Color\(White\), Add\(Value In Array\(Global Variable\(LocPos\), \d+\), Vector\(0, 55, 0\)\), 30, Visible To Position Radius and Color\);\n', '', s)

# ── 맵 전체 상공 격자 ──────────────────────────────────────────────
XS = [-95, -55, -15, 25, 60]
ZS = [-65, -20, 25, 75]
grid = []
for x in XS:
    for z in ZS:
        grid.append('\t\tCreate Effect(%s, Good Aura, Color(White), Vector(%d, 50, %d), 34, Visible To Position Radius and Color);' % (DAY, x, z))

_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + '\n'.join(grid) + '\n' + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  장소 기준 발광 제거 : %d개' % n)
print('  상공 격자 발광      : %d개  (%dx%d, 높이 50, 반경 34)' % (len(grid), len(XS), len(ZS)))
print('  덮는 범위           : X %d~%d  Z %d~%d' % (XS[0], XS[-1], ZS[0], ZS[-1]))
