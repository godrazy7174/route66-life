# -*- coding: utf-8 -*-
"""장비 소유를 눈에 보이게 + 전설 야수.

[1] 가죽 배낭 -> 트레이서로 변신 (배낭 멘 영웅). 피로 절반 효과 유지.
[2] 말 -> 시온으로 변신. 이동속도 +25% 는 제거하고
    대신 시온의 바이크(Ability 2, Joyride)를 쿨타임 2초로 해금.
    말이 곧 바이크가 되는 셈.
    E키 충돌 처리: E 는 육포 키인데 시온의 바이크도 E 다.
      - 시온은 [웅크리기+E] 로 육포를 먹는다
      - 웅크리는 동안 바이크가 잠겨 취식과 탑승이 겹치지 않는다
    우선순위: 말(시온) > 배낭(트레이서). 배낭을 사도 말이 있으면 시온 유지.
[3] 전설 야수: 몰아낼 때 마리당 1% — 크기 50배, 보상 50배(가죽 x50 + $2000).
    기존 거대(10%, 5배)는 유지. 판정: 1 <= 전설 / 2~11 <= 거대.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ [2a] 말 이동속도 보너스 제거 ══════════════════════════════════
sub('Set Move Speed(Event Player, Add(100, Multiply(Event Player.HasHorse, 25)));',
    'Set Move Speed(Event Player, 100);', 2)
sub('Set Move Speed(Event Player, Add(165, Multiply(Event Player.HasHorse, 25)));',
    'Set Move Speed(Event Player, 165);')

# ══ [1][2b] 구매 시 변신 ══════════════════════════════════════════
sub('''					Set Player Variable(Event Player, HasBag, 1);
					Big Message(Event Player, Custom String("가죽 배낭 — 달리기 피로 소모 절반"));''',
'''					Set Player Variable(Event Player, HasBag, 1);
					If(Event Player.HasHorse == 0);
						Start Forcing Player To Be Hero(Event Player, Hero(Tracer));
					End;
					Big Message(Event Player, Custom String("가죽 배낭 — 달리기 피로 소모 절반"));
					Small Message(Event Player, Custom String("배낭을 멘 트레이서가 되었다"));''')

sub('''					Set Player Variable(Event Player, HasHorse, 1);
					Big Message(All Players(All Teams), Custom String("{0} — 말을 샀다", Event Player));''',
'''					Set Player Variable(Event Player, HasHorse, 1);
					Start Forcing Player To Be Hero(Event Player, Hero(Shion));
					Big Message(All Players(All Teams), Custom String("{0} — 말을 샀다", Event Player));
					Small Message(Event Player, Custom String("이제 시온이다 — [E] 바이크 (쿨타임 2초) · 육포는 [웅크리기+E]"));''')

# ══ [2c] 시온/트레이서 스킬 규칙 ══════════════════════════════════
def lockrule(name, hero, body):
    return ('rule("%s")' % name + NLC + '{' + NLC
            + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC
            + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
            + T + 'conditions' + NLC + T + '{' + NLC
            + T*2 + 'Is Dummy Bot(Event Player) == False;' + NLC
            + T*2 + 'Hero Of(Event Player) == Hero(%s);' % hero + NLC
            + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
            + body + T + '}' + NLC + '}' + NLC + NLC)

TRACER = ''.join(T*2 + x + ';' + NLC for x in (
    'Set Ability 1 Enabled(Event Player, False)',
    'Set Ability 2 Enabled(Event Player, False)',
    'Set Ultimate Ability Enabled(Event Player, False)',
    'Set Secondary Fire Enabled(Event Player, False)',
    'Set Ultimate Charge(Event Player, 0)',
    'Set Melee Enabled(Event Player, False)',
    'Disallow Button(Event Player, Button(Ability 1))',
    'Disallow Button(Event Player, Button(Ability 2))',
    'Disallow Button(Event Player, Button(Ultimate))',
    'Disallow Button(Event Player, Button(Secondary Fire))'))

SHION = ''.join(T*2 + x + ';' + NLC for x in (
    'Set Ability 1 Enabled(Event Player, False)',
    'Set Ability 2 Enabled(Event Player, True)',
    'Set Ultimate Ability Enabled(Event Player, False)',
    'Set Secondary Fire Enabled(Event Player, False)',
    'Set Ultimate Charge(Event Player, 0)',
    'Set Melee Enabled(Event Player, False)',
    'Disallow Button(Event Player, Button(Ability 1))',
    'Disallow Button(Event Player, Button(Ultimate))',
    'Disallow Button(Event Player, Button(Secondary Fire))'))

CD = (T*2 + 'Wait Until(Is Using Ability 2(Event Player) == False, 30);' + NLC
    + T*2 + 'Set Ability Cooldown(Event Player, Button(Ability 2), 2);' + NLC)

CROUCH = (T*2 + 'Set Ability 2 Enabled(Event Player, False);' + NLC
        + T*2 + 'Wait Until(Not(Is Button Held(Event Player, Button(Crouch))), 60);' + NLC
        + T*2 + 'Set Ability 2 Enabled(Event Player, True);' + NLC)

RULES = (lockrule('[코어 16] 트레이서 설정 (배낭)', 'Tracer', TRACER)
       + lockrule('[코어 17] 시온 설정 (말) — 바이크만 해금', 'Shion', SHION))

CDRULE = ('rule("[코어 17-2] 바이크 쿨타임 2초")' + NLC + '{' + NLC
        + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC
        + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
        + T + 'conditions' + NLC + T + '{' + NLC
        + T*2 + 'Is Dummy Bot(Event Player) == False;' + NLC
        + T*2 + 'Hero Of(Event Player) == Hero(Shion);' + NLC
        + T*2 + 'Is Using Ability 2(Event Player) == True;' + NLC
        + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
        + CD + T + '}' + NLC + '}' + NLC + NLC)

CRRULE = ('rule("[코어 17-3] 시온 웅크림 — 취식 중 바이크 잠금")' + NLC + '{' + NLC
        + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC
        + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
        + T + 'conditions' + NLC + T + '{' + NLC
        + T*2 + 'Is Dummy Bot(Event Player) == False;' + NLC
        + T*2 + 'Hero Of(Event Player) == Hero(Shion);' + NLC
        + T*2 + 'Is Button Held(Event Player, Button(Crouch)) == True;' + NLC
        + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
        + CROUCH + T + '}' + NLC + '}' + NLC + NLC)

anchor = 'rule("[코어 07] 궁극기 게이지 상시 제거")'
sub(anchor, RULES + CDRULE + CRRULE + anchor)

# ══ [2d] 시온은 웅크려야 육포 (E 충돌) ════════════════════════════
sub('''		If(Value In Array(Event Player.Inv, 0) >= 1);
			Set Player Variable At Index(Event Player, Inv, 0, Subtract(Value In Array(Event Player.Inv, 0), 1));''',
'''		If(And(Hero Of(Event Player) == Hero(Shion), Is Button Held(Event Player, Button(Crouch)) == False));
			Abort;
		End;
		If(Value In Array(Event Player.Inv, 0) >= 1);
			Set Player Variable At Index(Event Player, Inv, 0, Subtract(Value In Array(Event Player.Inv, 0), 1));''')

# ══ [3] 전설 야수 (1%, 50배) ══════════════════════════════════════
for n in range(3):
    TGT = 'Value In Array(Event Player.Target, %d)' % n
    sub(T*3 + 'Set Player Variable(%s, Giant, Random Integer(1, 100) <= 10 ? 1 : 0);' % TGT,
        T*3 + 'Set Player Variable(%s, Roll, Random Integer(1, 100));' % TGT + NLC
      + T*3 + 'Set Player Variable(%s, Giant, Player Variable(%s, Roll) <= 1 ? 2 : (Player Variable(%s, Roll) <= 11 ? 1 : 0));' % (TGT, TGT, TGT))
    sub(T*3 + 'If(Player Variable(%s, Giant) == 1);' % TGT,
        T*3 + 'If(Player Variable(%s, Giant) == 2);' % TGT + NLC
      + T*4 + 'Set Max Health(%s, 1000);' % TGT + NLC
      + T*4 + 'Start Scaling Player(%s, 50, False);' % TGT + NLC
      + T*4 + 'Big Message(All Players(All Teams), Custom String("전설의 야수가 깨어났다!! 보상 50배"));' + NLC
      + T*4 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(%s), 14);' % TGT + NLC
      + T*4 + 'Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(%s), 250);' % TGT + NLC
      + T*3 + 'Else If(Player Variable(%s, Giant) == 1);' % TGT)

sub('''		If(Player Variable(Victim, Giant) == 1);
			Modify Player Variable(Attacker, Yield, Multiply, 5);
		End;''',
'''		If(Player Variable(Victim, Giant) == 2);
			Modify Player Variable(Attacker, Yield, Multiply, 50);
		Else If(Player Variable(Victim, Giant) == 1);
			Modify Player Variable(Attacker, Yield, Multiply, 5);
		End;''')
sub('''		If(Player Variable(Victim, Giant) == 1);
			Modify Player Variable(Attacker, Money, Add, 400);''',
'''		If(Player Variable(Victim, Giant) == 2);
			Modify Player Variable(Attacker, Money, Add, 2000);
			Modify Player Variable(Attacker, Earned, Add, 2000);
			Big Message(All Players(All Teams), Custom String("{0} — 전설의 야수를 쓰러뜨렸다!! 가죽 +{1}장 + $2000", Attacker, Player Variable(Attacker, Yield)));
			Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Attacker), 14);
			Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Red), Position Of(Attacker), 250);
		Else If(Player Variable(Victim, Giant) == 1);
			Modify Player Variable(Attacker, Money, Add, 400);''')

# ══ 안내 문구 ═════════════════════════════════════════════════════
NL = chr(92) + 'r' + chr(92) + 'n'
sub('Custom String("가죽 배낭 $1800  ·  말 $3500' + NL + '")',
    'Custom String("가죽 배낭 $1800 — 트레이서 변신, 달리기 피로 절반' + NL + '말 $3500 — 시온 변신, 바이크 해금' + NL + '")')
sub('Custom String("가죽 배낭 — 달리기 피로 소모 절반. 등에 멘 배낭이 보인다")', 'x', 0) if False else None
sub('Custom String("곡괭이를 벼리면 캘 때마다 더 나오고, 말을 사면 더 빨리 움직인다.' + NL,
    'Custom String("곡괭이를 벼리면 캘 때마다 더 나오고, 말을 사면 바이크를 몬다.' + NL)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)

# ══ 한글 변환기에 영웅 추가 ═══════════════════════════════════════
t = io.open('to_korean.py', encoding='utf-8').read()
K = "    ('Hero(Jetpack Cat)', 'Hero(제트팩 캣)'),"
assert K in t and 'Tracer' not in t
t = t.replace(K, K + NLC + "    ('Hero(Tracer)', 'Hero(트레이서)')," + NLC + "    ('Hero(Shion)', 'Hero(시온)'),", 1)
io.open('to_korean.py', 'w', encoding='utf-8', newline='\n').write(t)

print('[1] 배낭 -> 트레이서 (말 없을 때만)')
print('[2] 말 -> 시온, 속도 보너스 제거, 바이크 쿨 2초, 육포=웅크리기+E')
print('[3] 전설 야수 1% — 크기 50배, 가죽 x50 + $2000')
