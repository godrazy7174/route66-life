# -*- coding: utf-8 -*-
"""[1a] 사냥 메시지 숫자가 0이 되거나 부풀어 보이는 문제
      메시지는 떠 있는 동안 값을 계속 다시 읽는다. 야수가 셋이라
      3초 안에 두 마리를 잡으면 앞 메시지가 뒤 값으로 덮인다.
      -> 증감(+N) 대신 '지금 보유량'을 띄운다. 다시 읽혀도 늘 참이다.

[1b] 고양이가 한 마리만 나오는 문제
      소환 코드는 세 마리 전부 처리하지만, 잡힌 야수가 죽어 있으면
      살아있는 것만 골라진다. 봇 부활 시간을 따로 안 정해 놔서
      한 번 사냥한 뒤에는 한동안 한두 마리만 살아 있었다.
      -> 야수 부활 시간을 4초로 고정. 처치 룰 끝의 25초 대기 후
         복귀 이동은 은신 룰이 대신하므로 지운다.

[2]  머리 위 칭호가 안 바뀌는 문제
      문자열 재평가에만 기대고 있었다. 칭호나 수배 여부가 바뀌면
      이름표를 실제로 부수고 새로 만든다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new, cnt)

TIER = ('Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), '
        'Event Player.Money >= 2500), Event Player.Money >= 6000), Event Player.Money >= 15000)')
SIG = 'Add(Multiply(%s, 2), Event Player.Bounty > 0)' % TIER

# ── 변수 ───────────────────────────────────────────────────────────
assert 'NameId' not in s
sub('\t\t52: HuntPay\n', '\t\t52: HuntPay\n\t\t53: NameId\n\t\t54: NameSig\n')

# ── [1a] 보유량 표시 ───────────────────────────────────────────────
HELD = 'Value In Array(Player Variable(Attacker, Inv), 3)'
sub('Custom String("사냥 성공 — 가죽 +{0}", Player Variable(Attacker, Yield))',
    'Custom String("사냥 성공 — 가죽 {0}장", %s)' % HELD)
sub('Custom String("{0} — 큰 놈을 잡았다! 가죽 {1}장 + $150", Attacker, Player Variable(Attacker, Yield))',
    'Custom String("{0} — 큰 놈을 잡았다! 가죽 {1}장 + $150", Attacker, %s)' % HELD)
sub('Custom String("{0} — 거대한 야수를 쓰러뜨렸다! 가죽 {1}장 + $400", Attacker, Player Variable(Attacker, Yield))',
    'Custom String("{0} — 거대한 야수를 쓰러뜨렸다! 가죽 {1}장 + $400", Attacker, %s)' % HELD)

# ── [1b] 야수 부활 ─────────────────────────────────────────────────
sub('\t\t\tSet Max Health(Event Player, 40);\n\t\t\tStop Scaling Player(Event Player);',
    '\t\t\tSet Max Health(Event Player, 40);\n'
    '\t\t\tSet Respawn Max Time(Event Player, 4);\n'
    '\t\t\tStop Scaling Player(Event Player);')
i = s.index('\t\tSet Player Variable(Victim, RevealEnd, 0);')
j = s.index('\t}\n}', i)
tail = s[i:j]
assert 'Wait(25, Ignore Condition);' in tail
s = s[:i] + '\t\tSet Player Variable(Victim, RevealEnd, 0);\n' + s[j:]

# ── [2] 이름표 갱신 ────────────────────────────────────────────────
k = s.index('\t\tCreate In-World Text(All Players(All Teams), Custom String("『 {0} 』 {1}"')
e = s.index(';\n', k) + 2
NAME = s[k:e]
s = s[:e] + ('\t\tSet Player Variable(Event Player, NameId, Last Text ID());\n'
             '\t\tSet Player Variable(Event Player, NameSig, %s);\n' % SIG) + s[e:]

RULE = ('rule("[코어 15] 머리 위 이름표 갱신")\n{\n\tevent\n\t{\n\t\tOngoing - Each Player;\n\t\tAll;\n\t\tAll;\n\t}\n\n'
        '\tconditions\n\t{\n\t\tEvent Player.Init == 1;\n\t\t%s != Event Player.NameSig;\n\t}\n\n'
        '\tactions\n\t{\n'
        '\t\tSet Player Variable(Event Player, NameSig, %s);\n'
        '\t\tDestroy In-World Text(Event Player.NameId);\n'
        '%s'
        '\t\tSet Player Variable(Event Player, NameId, Last Text ID());\n'
        '\t}\n}\n\n' % (SIG, SIG, NAME))
s = s.replace('rule("[튜토리얼 01] DoTutorial")', RULE + 'rule("[튜토리얼 01] DoTutorial")', 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1a] 사냥 메시지를 증감에서 보유량 표시로')
print('[1b] 야수 부활 4초 고정, 처치 룰의 25초 복귀 대기 제거')
print('[2]  칭호/수배 상태가 바뀌면 이름표를 부수고 새로 생성')
