# -*- coding: utf-8 -*-
"""낮/밤 연출을 뒤집는다 — 밤 맵을 바탕으로 낮에 불을 켠다.

근거: 워크샵으로 화면을 어둡게 만들 수단은 없지만, 발광 이펙트를 더하는 건 된다.
      그래서 '밝은 맵 + 밤에 어둡게'는 원리상 불가능하고,
      '어두운 맵 + 낮에 밝게'는 가능하다.

  맵    : 66번 국도 밤 변형으로 고정
  낮    : 장소마다 흰 광주 + 넓은 발광, 굵고 밝게
  밤    : 불을 끄고 작은 주황 등불만. 맵 본래의 어둠이 그대로 드러난다.
  이동  : 밤에는 각자 등불을 들고 다닌다 (기존 유지)
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 1) 광기둥: 낮=흰색 굵게 / 밤=주황 가늘게 ───────────────────────
n = len(re.findall(r'Light Shaft, Global Variable\(IsNight\) == 1 \? Color\(Orange\) : Color\(Yellow\)', s))
s = re.sub(r'Light Shaft, Global Variable\(IsNight\) == 1 \? Color\(Orange\) : Color\(Yellow\)(, Value In Array\(Global Variable\(LocPos\), \d+\), )Global Variable\(IsNight\) == 1 \? 2\.2 : 1\.2',
           r'Light Shaft, Global Variable(IsNight) == 1 ? Color(Orange) : Color(White)\1Global Variable(IsNight) == 1 ? 0.9 : 3',
           s)

# ── 2) 낮에만 켜지는 장소 발광 추가 ────────────────────────────────
extra = []
for i in range(11):
    pos = 'Value In Array(Global Variable(LocPos), %d)' % i
    extra.append('\t\tCreate Effect(Global Variable(IsNight) == 0 ? All Players(All Teams) : False, Good Aura, Color(White), %s, 5, Visible To Position Radius and Color);' % pos)
_bw = s.index('rule("[코어 02] BuildWorld")')
b = s.index('\t}\n}', _bw)
s = s[:b] + '\n'.join(extra) + '\n' + s[b:]

# ── 3) 밤 등불을 조금 더 또렷하게 ──────────────────────────────────
s = s.replace('Create Effect(All Players(All Teams), Orb, Color(Orange), Event Player, 0.35, Visible To Position and Radius);',
              'Create Effect(All Players(All Teams), Orb, Color(Orange), Event Player, 0.5, Visible To Position and Radius);')
s = s.replace('Create Effect(All Players(All Teams), Good Aura, Color(Orange), Event Player, 1.4, Visible To Position and Radius);',
              'Create Effect(All Players(All Teams), Good Aura, Color(Orange), Event Player, 2.2, Visible To Position and Radius);')

# ── 4) 안내 문구를 뒤집힌 연출에 맞게 ──────────────────────────────
s = s.replace('Custom String("밤이 내려앉았다 — 마을에 등불이 켜진다")',
              'Custom String("해가 졌다 — 마을의 불이 꺼진다"))'.replace('))', ')'))
s = s.replace('Custom String("현상금 2배. 길 위에서 뭔가 주울 확률도 오른다")',
              'Custom String("어둠 속에서는 현상금이 2배. 길 위에서 뭔가 주울 확률도 오른다")')
s = s.replace('Custom String("동이 텄다")', 'Custom String("동이 텄다 — 마을에 다시 불이 들어온다")')
s = s.replace('Custom String("12분이 하루다. 아침마다 시세가 바뀌고, 밤이 되면 현상금이 두 배가 된다.\\r\\n하루 목표를 채우면 보너스가 붙는다.")',
              'Custom String("12분이 하루다. 밤이 오면 마을의 불이 꺼지고 현상금이 두 배가 된다.\\r\\n하루 목표를 채우면 보너스가 붙는다.")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# ── 5) 맵을 밤 변형으로 ────────────────────────────────────────────
t = io.open('to_korean.py', encoding='utf-8').read()
t = t.replace('66번 국도 972777519512068154', '66번 국도 972777519512068153')
io.open('to_korean.py', 'w', encoding='utf-8', newline='\n').write(t)

print('패치 완료')
print('  광기둥 낮/밤 반전 : %d곳' % n)
print('  낮 전용 발광      : %d곳' % s.count('Good Aura, Color(White)'))
print('  맵 변형           : 밤(972777519512068153)')
