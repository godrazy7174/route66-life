# -*- coding: utf-8 -*-
"""전역 조명 시도를 걷어낸다.

결론: 워크샵 이펙트는 광원이 아니라 발광 스프라이트다.
      멀리서는 점, 반경 안에서는 과노출, 겹치면 가산.
      어느 방향으로도 '조명'이 되지 않는다.

되돌리는 것
  - 맵을 아침 변형으로 (낮이 플레이 시간의 60%이고, 표지판·사냥·전투 품질에 직결)
  - 상공 격자 20개 + 해 2개 전부 제거
밤은 조명이 아니라 다른 채널로만 알린다
  - 장소 광기둥 색 (노랑 -> 주황) 과 굵기
  - 플레이어 등불
  - HUD 색
  - 게임플레이 (현상금 2배, 발견 확률 2배)
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 상공 격자 제거 ─────────────────────────────────────────────────
grid = len(re.findall(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, Good Aura, Color\(White\), Vector\(-?\d+, 50, -?\d+\), 34, Visible To Position Radius and Color\);\n', s))
s = re.sub(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, Good Aura, Color\(White\), Vector\(-?\d+, 50, -?\d+\), 34, Visible To Position Radius and Color\);\n', '', s)

# ── 해 제거 ────────────────────────────────────────────────────────
sun = len(re.findall(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, (?:Sphere|Good Aura), Color\((?:Yellow|White)\), Add\(Divide\(Add\(Value In Array\(Global Variable\(LocPos\), 0\), Value In Array\(Global Variable\(LocPos\), 8\)\), 2\), Vector\(0, 90, 0\)\), \d+, Visible To Position Radius and Color\);\n', s))
s = re.sub(r'\t\tCreate Effect\(Global Variable\(IsNight\) == 0 \? All Players\(All Teams\) : False, (?:Sphere|Good Aura), Color\((?:Yellow|White)\), Add\(Divide\(Add\(Value In Array\(Global Variable\(LocPos\), 0\), Value In Array\(Global Variable\(LocPos\), 8\)\), 2\), Vector\(0, 90, 0\)\), \d+, Visible To Position Radius and Color\);\n', '', s)

# ── 광기둥: 표시 역할, 밤에만 주황으로 ─────────────────────────────
s = s.replace('Global Variable(IsNight) == 1 ? 0.9 : 1.4,', 'Global Variable(IsNight) == 1 ? 1.8 : 1.2,')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# ── 맵을 아침 변형으로 되돌림 ──────────────────────────────────────
t = io.open('to_korean.py', encoding='utf-8').read()
t = t.replace('66번 국도 972777519512068153', '66번 국도 972777519512068154')
io.open('to_korean.py', 'w', encoding='utf-8', newline='\n').write(t)

print('정리 완료')
print('  상공 격자 제거 : %d개' % grid)
print('  해 제거        : %d개' % sun)
print('  맵            : 아침 변형(972777519512068154)')
print('  남은 밤 신호   : 광기둥 색/굵기, 플레이어 등불, HUD 색, 현상금 2배, 발견 2배')
