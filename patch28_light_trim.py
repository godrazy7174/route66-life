# -*- coding: utf-8 -*-
"""조명 개수를 줄인다. 코드 구조는 그대로 둔다.

1) 광기둥 11 -> 9
   식당(0)과 안내소(9)는 4m, 정비소(4)와 대장간(10)은 6m 거리다.
   붙어 있는 쌍은 기둥 두 개가 한 덩어리로 뭉쳐 보이므로 한쪽만 남긴다.
   - 식당 기둥 제거   (안내소의 청록 기둥이 그 자리를 함께 표시)
   - 대장간 기둥 제거 (정비소 기둥이 그 자리를 함께 표시)
   이름 표지판은 그대로라 위치는 여전히 보인다.

2) 밤 등불 2개 -> 1개 (플레이어당)
   Orb(0.5) + Good Aura(2.2) 중 넓게 번지는 Good Aura를 뺀다.
   마을에 사람이 모이면 반경 2.2 오라가 겹쳐 흰 덩어리가 되던 원인.

3) 등불이 사라지지 않던 버그
   기존 코드는 등불 ID를 Tmp / Amt에 담았는데,
     Tmp -> [월드 04] 구역 감지가 0.35초마다 덮어씀
     Amt -> 판매·발견 처리가 덮어씀
   그래서 아침이 와도 Destroy Effect가 엉뚱한 값을 지웠고 등불이 남았다.
   밤이 반복될수록 이펙트가 쌓여 128개 한도에 닿는다.
   전용 변수 Lantern(19)으로 옮겨 해결.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
before_fx = s.count('Create Effect(')

# ── 1) 붙어 있는 장소의 광기둥 제거 ────────────────────────────────
shaft = (r'\t\tCreate Effect\(All Players\(All Teams\), Light Shaft, '
         r'Global Variable\(IsNight\) == 1 \? Color\(Orange\) : Color\(White\), '
         r'Value In Array\(Global Variable\(LocPos\), %d\), '
         r'Global Variable\(IsNight\) == 1 \? 1\.8 : 1\.2, '
         r'Visible To Position Radius and Color\);\n')
removed = 0
for i in (0, 10):
    pat = shaft % i
    n = len(re.findall(pat, s))
    assert n == 1, '광기둥 %d: %d개 매칭' % (i, n)
    s = re.sub(pat, '', s)
    removed += n

# ── 2) 전용 변수 선언 ──────────────────────────────────────────────
assert '19: Lantern' not in s
s = s.replace('\t\t20: Init\n', '\t\t19: Lantern\n\t\t20: Init\n', 1)

# ── 3) 밤 등불: 오라 제거 + 전용 변수 사용 ─────────────────────────
OLD = '''		Create Effect(All Players(All Teams), Orb, Color(Orange), Event Player, 0.5, Visible To Position and Radius);
		Set Player Variable(Event Player, Tmp, Last Created Entity());
		Create Effect(All Players(All Teams), Good Aura, Color(Orange), Event Player, 2.2, Visible To Position and Radius);
		Set Player Variable(Event Player, Amt, Last Created Entity());
		Wait Until(Or(Global Variable(IsNight) == 0, Not(Is Alive(Event Player))), 99999);
		Destroy Effect(Event Player.Tmp);
		Destroy Effect(Event Player.Amt);
'''
NEW = '''		Destroy Effect(Event Player.Lantern);
		Create Effect(All Players(All Teams), Orb, Color(Orange), Event Player, 0.5, Visible To Position and Radius);
		Set Player Variable(Event Player, Lantern, Last Created Entity());
		Wait Until(Or(Global Variable(IsNight) == 0, Not(Is Alive(Event Player))), 99999);
		Destroy Effect(Event Player.Lantern);
		Set Player Variable(Event Player, Lantern, 0);
'''
assert OLD in s
s = s.replace(OLD, NEW, 1)

# ── 4) 최초 설정에 초기값 ──────────────────────────────────────────
s = s.replace('\t\tSet Player Variable(Event Player, Sprinting, 0);\n',
              '\t\tSet Player Variable(Event Player, Sprinting, 0);\n'
              '\t\tSet Player Variable(Event Player, Lantern, 0);\n', 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

shafts = len(re.findall(r'Light Shaft', s))
print('패치 완료')
print('  광기둥        : %d -> %d  (식당·대장간 제거, 각각 4m/6m 옆 기둥과 중복)' % (shafts + removed, shafts))
print('  밤 등불       : 2개/인 -> 1개/인 (Good Aura 2.2 제거)')
print('  등불 누수 수정 : Tmp/Amt 공용 변수 -> 전용 Lantern(19)')
print('  Create Effect : %d -> %d' % (before_fx, s.count('Create Effect(')))
print()
print('  9인 밤 기준 동시 이펙트  %d개 -> %d개' % (11 + 9 * 2, shafts + 9 * 1))
