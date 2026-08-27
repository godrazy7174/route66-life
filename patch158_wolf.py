# patch158: 늑대가 너무 빠르고 보이지 않는 문제
#  속도: 0.3초당 1.4m(초당 4.67m) -> 0.7m(초당 2.33m). 20m 접근에 4.3초 -> 8.6초로 늘어
#        3발을 맞출 시간이 생긴다(12초 제한 안에는 여전히 도달).
#  시인성: 회색 구슬(반경 0.9)만 있고 아이콘이 없어 밤에 사실상 안 보였다.
#          붉은 구슬(1.4) + 해골 아이콘으로 바꿔 벽 너머에서도 위치가 보이게 한다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def one(sub):
    idx = [i for i, l in enumerate(lines) if sub in l]
    assert len(idx) == 1, f'{sub!r}: {len(idx)}'
    return idx[0]

# 빈 슬롯 96 재사용
i = one('\t\t95: PadC')
lines.insert(i + 1, '\t\t96: WolfIco')

# 1) 접근 속도
i = one('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Event Player.DialTgt, Multiply(Direction Towards(Event Player.DialTgt, Event Player.CowPos), 1.4))));')
lines[i] = lines[i].replace('), 1.4)))', '), 0.7)))')

# 2) 구슬 색·크기 + 아이콘 생성
i = one('Create Effect(All Players(All Teams), Sphere, Color(Gray), Event Player.DialTgt, 0.9, Visible To Position Radius and Color);')
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines[i] = ind + 'Create Effect(All Players(All Teams), Sphere, Color(Red), Event Player.DialTgt, 1.4, Visible To Position Radius and Color);'
j = next(k for k in range(i, i+4) if lines[k].strip() == 'Set Player Variable(Event Player, EscortFlash, Last Created Entity());')
lines[j + 1:j + 1] = [
    ind + 'Destroy Icon(Event Player.WolfIco);',
    ind + 'Create Icon(Event Player, Add(Event Player.DialTgt, Vector(0, 2.2, 0)), Skull, Visible To and Position, Color(Red), True);',
    ind + 'Set Player Variable(Event Player, WolfIco, Last Created Entity());',
]

# 3) 안내 문구
i = one('늑대다! 소에게 달려든다 — 쏴서 쫓아내라 (회색 그림자)')
lines[i] = lines[i].replace('늑대다! 소에게 달려든다 — 쏴서 쫓아내라 (회색 그림자)',
                            '늑대다! 붉은 표식을 조준해 세 발 맞혀 쫓아내라')

# 4) 종료 시 아이콘 정리 (While 루프 뒤 Destroy Effect 옆)
idx = [k for k, l in enumerate(lines) if l.strip() == 'Destroy Effect(Event Player.EscortFlash);']
assert len(idx) == 2, len(idx)          # 생성 전 정리 + 루프 후 정리
after = idx[1]
ind2 = lines[after][:len(lines[after]) - len(lines[after].lstrip('\t'))]
lines.insert(after + 1, ind2 + 'Destroy Icon(Event Player.WolfIco);')

# 사망/이탈 시에도 남지 않도록 사망 처리에 추가
d = one('Destroy Icon(Event Player.CowIco);\n') if False else None
death = [k for k, l in enumerate(lines) if l.strip() == 'Destroy Icon(Event Player.CowIco);']
last = death[-1]
ind3 = lines[last][:len(lines[last]) - len(lines[last].lstrip('\t'))]
lines.insert(last + 1, ind3 + 'Destroy Icon(Event Player.WolfIco);')

out = '\n'.join(lines)
assert out.count('96: WolfIco') == 1
assert out.count('Set Player Variable(Event Player, WolfIco, Last Created Entity());') == 1
assert out.count('Destroy Icon(Event Player.WolfIco);') == 3
assert out.count('Color(Red), Event Player.DialTgt, 1.4') == 1
assert out.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch158 ok')
