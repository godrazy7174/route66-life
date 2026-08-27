# -*- coding: utf-8 -*-
"""[1] 가죽 수량 문제
    (a) 수확량이 적다 -> 2~4(사냥꾼 +2) 에서 5~8(사냥꾼 +4) 로.
    (b) '10개인데 3개 팔렸다고 뜬다'
        판매 메시지가 Amt / Roll 을 표시하는데 이 둘은 온 스크립트가
        공용으로 쓰는 임시 변수다. 메시지는 떠 있는 동안 계속 다시 읽으므로,
        F 를 한 번 더 누르거나 다른 룰이 끼어들면 숫자가 그 자리에서 바뀐다.
        예전에 '0개 판매'로 한 번 겪은 것과 같은 원인이다.
        -> 판매 전용 변수 SellQty / SellSum 을 따로 판다.
        야수 처치도 공용 Roll 을 쓰고 있어 전용 Yield 로 분리한다.
        인벤토리 갱신도 읽고-더하고-쓰기 대신 Modify ... At Index 로 바꿔
        동시에 두 마리가 죽어도 한쪽이 묻히지 않게 한다.

[2] 강도를 아무 데서나, 근접 공격 키(V)로
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    assert s.count(old) == cnt, (old[:60], s.count(old))
    return s.replace(old, new, cnt)

# ── 전용 변수 ──────────────────────────────────────────────────────
for name, idx, after in (('SellQty', 37, '\t\t38: Amt\n'), ('SellSum', 44, '\t\t45: GoalDone\n'), ('Yield', 48, '\t\t47: LastDay\n')):
    assert name not in s
    s = s.replace(after, ('\t\t%d: %s\n' % (idx, name)) + after if idx < int(after.split(':')[0].strip()) else after + ('\t\t%d: %s\n' % (idx, name)), 1)

# ── [1a] 수확량 ────────────────────────────────────────────────────
s = sub('Set Player Variable(Attacker, Roll, Random Integer(2, 4));',
        'Set Player Variable(Attacker, Yield, Random Integer(5, 8));')
s = sub('''			Modify Player Variable(Attacker, Roll, Add, 2);
			Set Player Variable At Index(Attacker, JobXP, 2,''',
        '''			Modify Player Variable(Attacker, Yield, Add, 4);
			Set Player Variable At Index(Attacker, JobXP, 2,''')
s = sub('Set Player Variable At Index(Attacker, Inv, 3, Add(Value In Array(Player Variable(Attacker, Inv), 3), Player Variable(Attacker, Roll)));',
        'Modify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));')
s = s.replace('큰 놈을 잡았다! 가죽 {1}장 + $70', '큰 놈을 잡았다! 가죽 {1}장 + $150')
s = sub('Modify Player Variable(Attacker, Money, Add, 70);', 'Modify Player Variable(Attacker, Money, Add, 150);')
s = sub('Modify Player Variable(Attacker, Earned, Add, 70);', 'Modify Player Variable(Attacker, Earned, Add, 150);')
s = s.replace('Player Variable(Attacker, Roll)', 'Player Variable(Attacker, Yield)')

# ── [1b] 판매 전용 변수 ────────────────────────────────────────────
for lo, hi in (('Else If(Event Player.Zone == 4);', 'Else If(Event Player.Zone == 5);'),
               ('Else If(Event Player.Zone == 8);', 'Else If(Event Player.Zone == 9);')):
    a, b = s.index(lo), s.index(hi)
    blk = s[a:b].replace('Event Player.Amt', 'Event Player.SellQty').replace('Event Player.Roll', 'Event Player.SellSum')
    blk = blk.replace('Set Player Variable(Event Player, Amt,', 'Set Player Variable(Event Player, SellQty,')
    blk = blk.replace('Set Player Variable(Event Player, Roll,', 'Set Player Variable(Event Player, SellSum,')
    s = s[:a] + blk + s[b:]

# ── [2] 강도: 어디서나, V 키 ───────────────────────────────────────
s = sub('\t\tEvent Player.Zone == -1;\n\t\tGlobal Variable(ArchOn) == 0;\n\t\tIs Alive(Event Player) == True;\n\t\tIs Button Held(Event Player, Button(Interact)) == True;',
        '\t\tGlobal Variable(ArchOn) == 0;\n\t\tIs Alive(Event Player) == True;\n\t\tIs Button Held(Event Player, Button(Melee)) == True;')
s = sub('Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Interact)))',
        'Custom String("대상 없음 — 9m 안의 상대를 조준하고 [{0}]", Input Binding String(Button(Melee)))')
s = sub('Custom String("황야에서 [{0}] 강도/체포", Input Binding String(Button(Interact)))',
        'Custom String("[{0}] 강도/체포", Input Binding String(Button(Melee)))')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1a] 가죽 2~4(+2) -> 5~8(+4), 큰 놈 $70 -> $150')
print('[1b] 판매/사냥 전용 변수 분리 + 인벤토리 갱신을 Modify At Index 로')
print('[2]  강도: 황야 제한 해제, F -> V(근접)')
