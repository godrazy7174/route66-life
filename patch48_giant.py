# -*- coding: utf-8 -*-
"""[1] 거대 야수 이벤트 — 몰아낼 때마다 마리당 10% 확률
       체력 5배(40% -> 200%), 몸집 2.4배, 가죽 5배.
[2] '가죽 +42' 같은 말도 안 되는 수치
       메시지는 떠 있는 동안 변수를 계속 다시 읽는다.
       Yield 를 [범죄 02] 살해와 처단이 같이 쓰고 있어서,
       야수를 잡은 뒤 수배범을 처단하면 앞 메시지의 숫자가 현상금으로 바뀐다.
       (그 전 빌드에서는 공용 Roll 이라 1~100 난수까지 튀어나왔다 — 42가 그것)
       -> 살해·처단에 전용 KillPay 를 주고 Yield 는 사냥 전용으로 남긴다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new, cnt)

# ── 전용 변수 ──────────────────────────────────────────────────────
assert 'Giant' not in s and 'KillPay' not in s
sub('\t\t48: Yield\n', '\t\t48: Yield\n\t\t49: Giant\n\t\t50: KillPay\n')

# ── [2] 살해·처단을 Yield 에서 분리 ───────────────────────────────
sub('Set Player Variable(Attacker, Yield, Player Variable(Victim, Bounty));',
    'Set Player Variable(Attacker, KillPay, Player Variable(Victim, Bounty));')
a = s.index('rule("[범죄 02] 살해와 처단")')
b = s.index('\nrule(', a + 5)
s = s[:a] + s[a:b].replace('Player Variable(Attacker, Yield)', 'Player Variable(Attacker, KillPay)') + s[b:]

# ── [1] 소환 시 거대 판정 ──────────────────────────────────────────
for n in (0, 1, 2):
    T = 'Value In Array(Event Player.Target, %d)' % n
    old = '\t\t\tSet Player Variable(%s, RevealEnd, Add(Total Time Elapsed(), 30));\n' % T
    new = old + (
        '\t\t\tSet Player Variable(%s, Giant, Random Integer(1, 100) <= 10 ? 1 : 0);\n'
        '\t\t\tIf(Player Variable(%s, Giant) == 1);\n'
        '\t\t\t\tSet Max Health(%s, 200);\n'
        '\t\t\t\tStart Scaling Player(%s, 2.4, False);\n'
        '\t\t\t\tBig Message(All Players(All Teams), Custom String("거대한 야수다! 체력 5배 — 가죽도 5배"));\n'
        '\t\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(%s), 6);\n'
        '\t\t\t\tPlay Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(%s), 200);\n'
        '\t\t\tElse;\n'
        '\t\t\t\tSet Max Health(%s, 40);\n'
        '\t\t\t\tStop Scaling Player(%s);\n'
        '\t\t\tEnd;\n' % (T, T, T, T, T, T, T, T))
    sub(old, new)

# ── [1] 처치 보상 5배 ──────────────────────────────────────────────
sub('\t\tModify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));\n'
    '\t\tIf(Random Integer(1, 100) <= 15);',
    '\t\tIf(Player Variable(Victim, Giant) == 1);\n'
    '\t\t\tModify Player Variable(Attacker, Yield, Multiply, 5);\n'
    '\t\tEnd;\n'
    '\t\tModify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));\n'
    '\t\tIf(Player Variable(Victim, Giant) == 1);\n'
    '\t\t\tModify Player Variable(Attacker, Money, Add, 400);\n'
    '\t\t\tModify Player Variable(Attacker, Earned, Add, 400);\n'
    '\t\t\tBig Message(All Players(All Teams), Custom String("{0} — 거대한 야수를 쓰러뜨렸다! 가죽 {1}장 + $400", Attacker, Player Variable(Attacker, Yield)));\n'
    '\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(Attacker), 6);\n'
    '\t\t\tPlay Effect(All Players(All Teams), Buff Explosion Sound, Color(Red), Position Of(Attacker), 200);\n'
    '\t\tElse If(Random Integer(1, 100) <= 15);')

# ── [1] 죽거나 다시 숨을 때 원래대로 ───────────────────────────────
sub('\t\tSet Player Variable(Victim, RevealEnd, 0);',
    '\t\tSet Player Variable(Victim, Giant, 0);\n'
    '\t\tStop Scaling Player(Victim);\n'
    '\t\tSet Max Health(Victim, 40);\n'
    '\t\tSet Player Variable(Victim, RevealEnd, 0);')
sub('\t\t\tSet Max Health(Event Player, 40);\n',
    '\t\t\tSet Max Health(Event Player, 40);\n'
    '\t\t\tStop Scaling Player(Event Player);\n'
    '\t\t\tSet Player Variable(Event Player, Giant, 0);\n')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1] 거대 야수 : 마리당 10%, 체력 200%(=5배), 몸집 2.4배, 가죽 x5 + $400')
print('[2] 살해·처단을 KillPay 로 분리 — Yield 는 사냥 전용')
