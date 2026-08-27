# -*- coding: utf-8 -*-
"""낮 조명을 지상 -> 하늘로 옮긴다.

문제: 장소마다 반경 5짜리 흰 발광을 지상에 깔았더니
      거대한 빛 덩어리가 표지판과 시야를 가렸다.
      광기둥도 반경 3이라 청록 기둥처럼 보였다.

수정: 조명을 맵 상공으로 올려 '해'처럼 만들고,
      지상 광기둥은 장소 표시 역할만 하도록 가늘게 되돌린다.
      겸사겸사 상세 패널 표시 거리를 줄여 패널끼리 겹치는 것도 완화.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 지상에 깔린 낮 발광 제거 ────────────────────────────────────
n = len(re.findall(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, Good Aura, Color\(White\), Value In Array\(Global Variable\(LocPos\), \d+\), 5, Visible To Position Radius and Color\);\n', s))
s = re.sub(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, Good Aura, Color\(White\), Value In Array\(Global Variable\(LocPos\), \d+\), 5, Visible To Position Radius and Color\);\n', '', s)

# ── 2) 광기둥을 표시용 굵기로 ──────────────────────────────────────
s = s.replace('Global Variable(IsNight) == 1 ? 0.9 : 3,', 'Global Variable(IsNight) == 1 ? 0.9 : 1.4,')

# ── 3) 하늘에 해를 띄운다 (낮에만) ─────────────────────────────────
DAY = 'Global Variable(IsNight) == 0 ? All Players(All Teams) : False'
sky = []
# 맵 양 끝(식당 / 무법자 은신처) 중간 상공에 큰 해
mid = 'Divide(Add(Value In Array(Global Variable(LocPos), 0), Value In Array(Global Variable(LocPos), 8)), 2)'
sky.append('\t\tCreate Effect(%s, Sphere, Color(Yellow), Add(%s, Vector(0, 90, 0)), 22, Visible To Position Radius and Color);' % (DAY, mid))
sky.append('\t\tCreate Effect(%s, Good Aura, Color(White), Add(%s, Vector(0, 90, 0)), 55, Visible To Position Radius and Color);' % (DAY, mid))
# 마을 위쪽에 넓은 하늘빛 몇 점
for i in (0, 4, 8):
    pos = 'Add(Value In Array(Global Variable(LocPos), %d), Vector(0, 55, 0))' % i
    sky.append('\t\tCreate Effect(%s, Good Aura, Color(White), %s, 30, Visible To Position Radius and Color);' % (DAY, pos))
_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + '\n'.join(sky) + '\n' + s[b:]

# ── 4) 상세 패널 표시 거리 22m -> 13m (패널 겹침 완화) ─────────────
m = len(re.findall(r'Value In Array\(Global Variable\(LocPos\), \d+\)\) < 22,', s))
s = re.sub(r'(Value In Array\(Global Variable\(LocPos\), \d+\)\) < )22(,)', r'\g<1>13\2', s)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  지상 발광 제거   : %d곳' % n)
print('  하늘 조명 추가   : %d개' % len(sky))
print('  광기둥 낮 굵기   : 3 -> 1.4')
print('  패널 표시 거리   : 22m -> 13m (%d곳)' % m)
