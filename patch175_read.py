# -*- coding: utf-8 -*-
"""남은 룰 정독에서 나온 수정 2건.

A) 은행 다이얼 HUD가 핀 개수를 하나 앞서 표시한다.
   DialPin은 1에서 시작해 정답마다 +1 되고 >3이면 열린다(= 정답 3회).
   그런데 HUD는 DialPin을 그대로 찍어 아직 하나도 못 맞혔는데 "핀 1 / 3"으로 뜬다.
   맞힌 뒤 뜨는 Small Message는 Subtract(DialPin, 1)이라 제대로 세고 있어서
   둘이 어긋나 보인다. HUD를 메시지 쪽에 맞춘다.

B) 대사냥 3단계에서 대야수를 못 고르면 사냥이 조용히 죽는다.
   후보 필터가 Is Alive를 요구하는데, 야수 3마리가 동시에 죽어 있는 순간
   (리스폰 최대 4초) 흔적을 조사하면 First Of가 0을 돌려준다.
   그대로 HuntPhase만 4로 올라가 "대야수가 깨어났다"는 공지가 뜨지만
   실제 야수가 없어 그날 대사냥이 통째로 무산된다.
   -> 야수를 못 잡으면 3단계를 유지하고 흔적을 다시 세운다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()

# A) 다이얼 HUD 핀 표시
old = 'Custom String("핀 {0} / 3", Event Player.DialPin)'
assert src.count(old) == 1, src.count(old)
src = src.replace(old, 'Custom String("핀 {0} / 3", Subtract(Event Player.DialPin, 1))')
print('  OK 은행 다이얼 HUD — 핀 표시 보정')

# B) 대야수 부재 가드
a = src.index('\t\t\tSet Global Variable(HuntPhase, 4);')
b = src.index('\t\tEnd;', a)
body = src[a:b]
pick = [ln for ln in body.split('\n') if 'Set Global Variable(HuntBeast, First Of(' in ln][0]
rest = [ln for ln in body.split('\n')
        if ln.strip() and ln != pick and 'Set Global Variable(HuntPhase, 4);' not in ln]

T = '\t\t\t'
new = (pick + '\n'
       + T + 'If(Not(Entity Exists(Global Variable(HuntBeast))));\n'
       + T + '\tCreate Effect(All Players(All Teams), Light Shaft, Color(Orange), Global Variable(HuntTrackPos), 1.5, Visible To Position Radius and Color);\n'
       + T + '\tSet Global Variable(HuntTrackFx, Last Created Entity());\n'
       + T + '\tCreate Icon(All Players(All Teams), Add(Global Variable(HuntTrackPos), Vector(0, 3, 0)), Circle, Visible To and Position, Color(Orange), True);\n'
       + T + '\tSet Global Variable(HuntTrackIco, Last Created Entity());\n'
       + T + '\tSmall Message(Event Player, Custom String("기척이 흐트러졌다 — 잠시 뒤 다시 조사해라"));\n'
       + T + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Gray), Position Of(Event Player), 45);\n'
       + T + 'Else;\n'
       + T + '\tSet Global Variable(HuntPhase, 4);\n'
       + ''.join('\t' + ln + '\n' for ln in rest)
       + T + 'End;\n')
src = src[:a] + new + src[b:]
print('  OK 대사냥 — 대야수 부재 시 3단계 유지, 흔적 재설치')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('done')
