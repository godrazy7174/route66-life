# -*- coding: utf-8 -*-
"""[1] 취침 무제한 + 집의 이점을 피로에서 재산으로 이전
[2] 야수가 30초 뒤에도 안 숨는 문제 -> 전환 감지 대신 주기 검사로
[4] 추적하면 세 마리 전부 나오게
[3] 카메라 거리/높이/블렌드 재조정
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    assert s.count(old) == cnt, (old[:50], s.count(old))
    return s.replace(old, new, cnt)

# ══ [1] 취침 무제한 ═══════════════════════════════════════════════
s = sub('''		If(Event Player.SleepCount >= Add(1, Event Player.HasHome));
			Small Message(Event Player, Custom String("오늘은 더 잘 수 없다 — 내일 아침에 다시"));
			Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
			Abort;
		End;
		If(And(Event Player.HasHome == 0, Event Player.Money < 60));''',
'''		If(Event Player.Money < 60);''')
s = sub('		Modify Player Variable(Event Player, SleepCount, Add, 1);\n'
        '		If(Event Player.HasHome == 0);\n'
        '			Modify Player Variable(Event Player, Money, Subtract, 60);\n'
        '		End;\n',
        '		Modify Player Variable(Event Player, Money, Subtract, 60);\n')
s = sub('		Set Player Variable(Event Player, SleepCount, 0);\n', '')
s = sub('\t\t44: SleepCount\n', '')
assert 'SleepCount' not in s

# 집의 이점: 사망 시 손실 15% -> 5%
s = sub('Multiply(Event Player.Money, 0.15)',
        'Multiply(Event Player.Money, Event Player.HasHome == 1 ? 0.05 : 0.15)')
s = sub('Custom String("이제 숙박이 무료이고 하루 횟수 제한도 없다")',
        'Custom String("이제 죽어도 잃는 돈이 15%%에서 5%%로 줄어든다"))'.replace('))', ')'))

# 안내 문구
s = sub('숙박 $60 — 하루 한 번' + NL + '내 방 마련 $7000 — 이후 숙박 무료, 횟수 제한 없음',
        '숙박 $60 — 피로 완전 회복, 횟수 제한 없음' + NL + '내 방 마련 $7000 — 죽어도 잃는 돈이 15%에서 5%로')
s = sub('Custom String("숙박 $60 — 하루 한 번")', 'Custom String("숙박 $60 — 피로 완전 회복")')
s = sub('Custom String("내 방 마련 $3500")', 'Custom String("내 방 마련 $7000")')
s = sub('Custom String("숙박 $40 — 피로 완전 회복")', 'Custom String("숙박 $60 — 피로 완전 회복")')

# ══ [3] 카메라 ════════════════════════════════════════════════════
A = 'Add(Position Of(Event Player), Vector(0, 1.6, 0))'
B = 'Add(Position Of(Event Player), Vector(0, 1.9, 0))'
s = s.replace(A, B)
s = s.replace('Multiply(Facing Direction Of(Event Player), -3.2)), Empty Array, All Players(All Teams), False), '
              'Add(%s, Multiply(Facing Direction Of(Event Player), 6)), 70);' % B,
              'Multiply(Facing Direction Of(Event Player), -4)), Empty Array, All Players(All Teams), False), '
              'Add(%s, Multiply(Facing Direction Of(Event Player), 6)), 50);' % B)
assert s.count('), -4)), Empty Array') == 2

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1] 취침 무제한 / 집 = 사망 손실 15%% -> 5%%')
print('[3] 카메라 거리 3.2 -> 4.0, 높이 1.6 -> 1.9, 블렌드 70 -> 50')
