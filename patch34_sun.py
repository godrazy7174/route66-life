# -*- coding: utf-8 -*-
"""patch25의 하늘 조명 복원 — 태양 방식.

되살리는 것 (patch25)
    태양      : 맵 중앙 상공 y+90 에 Sphere(Yellow, r22) + Good Aura(White, r55)
    하늘 발광 : 상공 y+55 에 Good Aura(White, r30) 세 점

되살리지 않는 것 (patch26 — 이게 망친 원인)
    상공 5x4 격자 20개. 촘촘해서 멀리서는 점, 겹치는 곳은 과노출이었다.

바꾸는 것
    표시 방식을 조건부(IsNight == 0 ? All : False)에서
    낮/밤 전환 시 실제 생성/파괴로. 조건부는 이 스크립트에서 안 먹는다
    (광기둥이 통째로 안 보이던 원인이었고, patch25 때 "이곳에는 적용되지
     않았다"고 한 것도 같은 증상이었을 가능성이 높다).

    하늘 발광 세 점의 기준 장소도 0/4/8 -> 0/4/7 로 바꾼다.
    4(정비소)와 8(은신처)은 25m밖에 안 떨어져 있어 r30끼리 겹쳤다.
    0/4/7 은 서로 89~126m 라 겹치지 않으면서 맵을 고루 덮는다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

LOC = lambda i: 'Value In Array(Global Variable(LocPos), %d)' % i
MID = 'Divide(Add(%s, %s), 2)' % (LOC(0), LOC(8))
SUN = 'Add(%s, Vector(0, 90, 0))' % MID
SKY = lambda i: 'Add(%s, Vector(0, 55, 0))' % LOC(i)
RE  = 'Visible To Position Radius and Color'

LIGHTS = [('Light Shaft', 'Aqua' if i == 9 else 'White', LOC(i), '1.2') for i in range(10)]
LIGHTS += [('Sphere', 'Yellow', SUN, '22'), ('Good Aura', 'White', SUN, '55')]
LIGHTS += [('Good Aura', 'White', SKY(i), '30') for i in (0, 4, 7)]

on = []
for kind, col, pos, r in LIGHTS:
    on.append('\t\tCreate Effect(All Players(All Teams), %s, Color(%s), %s, %s, %s);' % (kind, col, pos, r, RE))
    on.append('\t\tModify Global Variable(SignIds, Append To Array, Last Created Entity());')
off = ['\t\tDestroy Effect(Value In Array(Global Variable(SignIds), %d));' % i for i in range(len(LIGHTS))]

def rule(name, night, body):
    return ('rule("%s")\n{\n\tevent\n\t{\n\t\tOngoing - Global;\n\t}\n\n'
            '\tconditions\n\t{\n\t\tGlobal Variable(Ready) == 1;\n'
            '\t\tGlobal Variable(IsNight) == %d;\n\t}\n\n'
            '\tactions\n\t{\n%s\n\t}\n}\n\n' % (name, night, body))

BLOCK = (rule('[월드 09] 낮 — 해가 뜬다', 0,
              '\n'.join(off) + '\n\t\tSet Global Variable(SignIds, Empty Array);\n' + '\n'.join(on))
         + rule('[월드 10] 밤 — 해가 진다', 1,
                '\n'.join(off) + '\n\t\tSet Global Variable(SignIds, Empty Array);'))

a = s.index('rule("[월드 09]')
b = s.index('rule("[월드 05] 아침 정산")')
s = s[:a] + BLOCK + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료 — 낮 조명 %d개' % len(LIGHTS))
print('  광기둥      10  (장소 표시, r1.2)')
print('  태양         2  (Sphere r22 + Good Aura r55, 상공 y+90)')
print('  하늘 발광    3  (Good Aura r30, 상공 y+55 / 식당·정비소·보안관초소)')
