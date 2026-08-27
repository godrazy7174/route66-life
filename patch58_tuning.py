# -*- coding: utf-8 -*-
"""[1] 시온 바이크가 안 나가던 진짜 원인 + 키 충돌 해소
    원인: 캐서디 시절 Disallow Button(Ability 2)가 영웅을 바꿔도 남는다.
          시온 규칙이 스킬만 켜고 버튼 금지를 안 풀었다 -> Allow Button 추가.
    키 충돌: 시온은 손으로 육포를 안 먹는다 — 허기 35 미만이면
          안장 주머니에서 자동으로 꺼내 먹는다. E 는 온전히 바이크 전용.
          (웅크리기+E 취식과 웅크림-바이크 잠금 규칙은 폐기)

[2] 돈 버는 이벤트 빈도·금액 하향
    길 위의 발견   18초/12%(+밤10) -> 30초/8%(+밤6), 지갑 $20~70 -> $15~45
    보물 상자      150~240초, $200~500 -> 240~420초, $150~350
    채굴 연속 보너스 x6 -> x4
    월드 이벤트    160~280초 -> 220~360초

[3] 가죽 수확 하향: 기본 5~8 -> 4~6, 사냥꾼 +4 -> +3, 레벨 상한 +8 -> +5

[4] 전설 야수 체력: Set Max Health 상한(1000%)에 걸려 50배가 아니었다.
    보조 체력 풀 2500 을 얹어 실제 5000HP(기본 100의 50배)로.
    은신·처치 정리 때 풀 제거.

[5] 잡화점 4번째 행동: 원석·가죽 전량 판매 (정비소 시세의 90%, 평판 적용)
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ [1] 바이크 버튼 금지 해제 ═════════════════════════════════════
sub("'Set Ability 2 Enabled(Event Player, True)',", 'x', 0) if False else None
sub('''		Set Ability 2 Enabled(Event Player, True);
		Set Ultimate Ability Enabled(Event Player, False);
		Set Secondary Fire Enabled(Event Player, False);
		Set Ultimate Charge(Event Player, 0);
		Set Melee Enabled(Event Player, False);
		Disallow Button(Event Player, Button(Ability 1));''',
'''		Set Ability 2 Enabled(Event Player, True);
		Allow Button(Event Player, Button(Ability 2));
		Set Ultimate Ability Enabled(Event Player, False);
		Set Secondary Fire Enabled(Event Player, False);
		Set Ultimate Charge(Event Player, 0);
		Set Melee Enabled(Event Player, False);
		Disallow Button(Event Player, Button(Ability 1));''')

# ── 웅크림 취식/잠금 폐기 -> 시온은 E 를 아예 육포에 안 쓴다 ───────
sub('''		If(And(Hero Of(Event Player) == Hero(Shion), Is Button Held(Event Player, Button(Crouch)) == False));
			Abort;
		End;
''',
'''		If(Hero Of(Event Player) == Hero(Shion));
			Abort;
		End;
''')
a = s.index('rule("[코어 17-3] 시온 웅크림 — 취식 중 바이크 잠금")')
b = s.index('\nrule(', a + 5) + 1
s = s[:a] + s[b:]

# ── 시온 자동 취식 ─────────────────────────────────────────────────
AUTOEAT = ('rule("[코어 17-3] 시온 — 안장 주머니 자동 취식")' + NLC + '{' + NLC
         + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC
         + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
         + T + 'conditions' + NLC + T + '{' + NLC
         + T*2 + 'Is Dummy Bot(Event Player) == False;' + NLC
         + T*2 + 'Event Player.Init == 1;' + NLC
         + T*2 + 'Is Alive(Event Player) == True;' + NLC
         + T*2 + 'Hero Of(Event Player) == Hero(Shion);' + NLC
         + T*2 + 'Event Player.Hunger < 35;' + NLC
         + T*2 + 'Value In Array(Event Player.Inv, 0) >= 1;' + NLC
         + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
         + T*2 + 'Set Player Variable At Index(Event Player, Inv, 0, Subtract(Value In Array(Event Player.Inv, 0), 1));' + NLC
         + T*2 + 'Set Player Variable(Event Player, Hunger, Min(100, Add(Event Player.Hunger, 55)));' + NLC
         + T*2 + 'Heal(Event Player, Null, 40);' + NLC
         + T*2 + 'Small Message(Event Player, Custom String("안장 주머니에서 육포를 꺼내 먹었다 — 허기 {0}", Round To Integer(Event Player.Hunger, Down)));' + NLC
         + T*2 + 'Play Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 50);' + NLC
         + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[코어 07] 궁극기 게이지 상시 제거")', AUTOEAT + 'rule("[코어 07] 궁극기 게이지 상시 제거")')

sub('Custom String("이제 시온이다 — [E] 바이크 (쿨타임 2초) · 육포는 [웅크리기+E]")',
    'Custom String("이제 시온이다 — [E] 바이크 (쿨타임 2초) · 육포는 허기가 지면 알아서 꺼내 먹는다")')

# ══ [2] 돈 이벤트 하향 ════════════════════════════════════════════
sub('\t\tWait(18, Ignore Condition);\n\t\tIf(Random Integer(1, 100) <= Add(12, Multiply(Global Variable(IsNight), 10)));',
    '\t\tWait(30, Ignore Condition);\n\t\tIf(Random Integer(1, 100) <= Add(8, Multiply(Global Variable(IsNight), 6)));')
sub('Set Player Variable(Event Player, Loot, Random Integer(20, 70));',
    'Set Player Variable(Event Player, Loot, Random Integer(15, 45));')
sub('Wait(Random Integer(150, 240), Ignore Condition);', 'Wait(Random Integer(240, 420), Ignore Condition);')
sub('Set Player Variable(Event Player, Prize, Random Integer(200, 500));',
    'Set Player Variable(Event Player, Prize, Random Integer(150, 350));')
sub('Set Player Variable(Event Player, StreakPay, Multiply(Event Player.Streak, 6));',
    'Set Player Variable(Event Player, StreakPay, Multiply(Event Player.Streak, 4));')
sub('Wait(Random Integer(160, 280), Ignore Condition);', 'Wait(Random Integer(220, 360), Ignore Condition);')

# ══ [3] 가죽 수확 하향 ════════════════════════════════════════════
sub('Set Player Variable(Attacker, Yield, Random Integer(5, 8));',
    'Set Player Variable(Attacker, Yield, Random Integer(4, 6));')
sub('\t\t\tModify Player Variable(Attacker, Yield, Add, 4);\n', '\t\t\tModify Player Variable(Attacker, Yield, Add, 3);\n')
sub('Modify Player Variable(Attacker, Yield, Add, Min(8, Round To Integer(Divide(Value In Array(Player Variable(Attacker, JobXP), 2), 250), Down)));',
    'Modify Player Variable(Attacker, Yield, Add, Min(5, Round To Integer(Divide(Value In Array(Player Variable(Attacker, JobXP), 2), 250), Down)));')

# ══ [4] 전설 체력: 보조 풀 2500 ═══════════════════════════════════
for n in range(3):
    TGT = 'Value In Array(Event Player.Target, %d)' % n
    sub(T*4 + 'Set Max Health(%s, 1000);' % TGT,
        T*4 + 'Set Max Health(%s, 1000);' % TGT + NLC
      + T*4 + 'Remove All Health Pools From Player(%s);' % TGT + NLC
      + T*4 + 'Add Health Pool To Player(%s, Health, 2500, True, True);' % TGT)
sub('''			Set Max Health(Event Player, 40);
			Set Respawn Max Time(Event Player, 4);''',
'''			Set Max Health(Event Player, 40);
			Remove All Health Pools From Player(Event Player);
			Set Respawn Max Time(Event Player, 4);''')
sub('''		Stop Scaling Player(Victim);
		Set Max Health(Victim, 40);''',
'''		Stop Scaling Player(Victim);
		Remove All Health Pools From Player(Victim);
		Set Max Health(Victim, 40);''')

# ══ [5] 잡화점 원석·가죽 전량 판매 ════════════════════════════════
sub('Array(1, 4, 2, 3, 2, 3, 3, 1, 2, 3, 1, 3)', 'Array(1, 4, 2, 4, 2, 3, 3, 1, 2, 3, 1, 3)', 4)
sub('Custom String("육포 5개 묶음 $65"), Custom String("-")',
    'Custom String("육포 5개 묶음 $65"), Custom String("원석·가죽 전량 판매 — 시세 90%")', 2)

SHOP_SELL = ('''			Else If(Event Player.MenuIdx == 3);
				If(Add(Value In Array(Event Player.Inv, 2), Value In Array(Event Player.Inv, 3)) <= 0);
					Small Message(Event Player, Custom String("팔 원석이나 가죽이 없습니다"));
					Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);
				Else;
					Set Player Variable(Event Player, SellSum, Round To Integer(Multiply(Multiply(Multiply(Add(Multiply(Value In Array(Event Player.Inv, 2), Global Variable(OrePrice)), Multiply(Value In Array(Event Player.Inv, 3), Global Variable(HidePrice))), Global Variable(SellMult)), 0.9), Add(1, Multiply(Event Player.Rep, 0.0015))), To Nearest));
					Modify Player Variable(Event Player, Money, Add, Event Player.SellSum);
					Modify Player Variable(Event Player, Earned, Add, Event Player.SellSum);
					Set Player Variable At Index(Event Player, Inv, 2, 0);
					Set Player Variable At Index(Event Player, Inv, 3, 0);
					Small Message(Event Player, Custom String("잡화점에 전부 넘겼다 — $ {0}   (시세 90%)", Event Player.SellSum));
					Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 100);
				End;
''')
sub('''			End;
		Else If(Event Player.Zone == 3);''',
    SHOP_SELL + '''			End;
		Else If(Event Player.Zone == 3);''')

sub('Custom String("육포 $15      물통 $10      육포 5개 묶음 $65' + NL + '평판이 좋으면 싸게, 나쁘면 비싸게 판다' + NL + '")',
    'Custom String("육포 $15      물통 $10      육포 5개 묶음 $65' + NL + '원석·가죽도 받아준다 — 정비소 시세의 90%' + NL + '평판이 좋으면 싸게, 나쁘면 비싸게 판다' + NL + '")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1] Allow Button + 자동 취식 / [2] 이벤트 하향 / [3] 가죽 하향 / [4] 전설 5000HP / [5] 잡화점 매입')
