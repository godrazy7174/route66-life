# -*- coding: utf-8 -*-
"""직업 레벨에 실제 효과를 붙인다. (지금까지 광부만 효과가 있었다)

    사냥꾼        레벨당 가죽 +1 (최대 +8)
    현상금 사냥꾼  레벨당 처치금 +$10 (최대 +$100)
    무법자        레벨당 강탈 비율 +2%p (40% -> 최대 60%)
    광부          기존 유지 (레벨당 금맥 확률 +1%p, 최대 +12%p)

경험치가 안 들어오던 구멍도 막는다.
    체포는 현상금 사냥꾼의 핵심 행위인데 경험치가 0이었다 -> +25
    강탈은 무법자의 핵심 행위인데 경험치가 0이었다   -> +20

겸사겸사 이 두 룰의 금액 표시를 공용 Roll 에서 전용 변수로 뺀다.
Roll 은 도박·채굴·발견의 1~100 난수가 들어오는 변수라
메시지가 떠 있는 동안 숫자가 바뀔 수 있다 (가죽 +42 와 같은 원인).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new, cnt)

def lvl(expr, n):
    return 'Round To Integer(Divide(Value In Array(%s, %d), 250), Down)' % (expr, n)

assert 'Take' not in s and 'HuntPay' not in s
sub('\t\t50: KillPay\n', '\t\t50: KillPay\n\t\t51: Take\n\t\t52: HuntPay\n')

# ── 사냥꾼: 레벨당 가죽 +1 ─────────────────────────────────────────
sub('\t\t\tModify Player Variable(Attacker, Yield, Add, 4);\n',
    '\t\t\tModify Player Variable(Attacker, Yield, Add, 4);\n'
    '\t\t\tModify Player Variable(Attacker, Yield, Add, Min(8, %s));\n'
    % lvl('Player Variable(Attacker, JobXP)', 2))

# ── 현상금 사냥꾼: 레벨당 +$10, 전용 변수로 ────────────────────────
a = s.index('rule("[무법자 02] 무법자 사격 판정")')
b = s.index('\nrule(', a + 5)
blk = s[a:b]
blk = blk.replace('Set Player Variable(Event Player, Roll, Multiply(Global Variable(BotBounty), Add(1, Global Variable(IsNight))));',
                  'Set Player Variable(Event Player, HuntPay, Multiply(Global Variable(BotBounty), Add(1, Global Variable(IsNight))));')
blk = blk.replace('Modify Player Variable(Event Player, Roll, Add, 40);',
                  'Modify Player Variable(Event Player, HuntPay, Add, 40);\n'
                  '\t\t\t\t\t\tModify Player Variable(Event Player, HuntPay, Add, Multiply(10, Min(10, %s)));'
                  % lvl('Event Player.JobXP', 3))
blk = blk.replace('Event Player.Roll', 'Event Player.HuntPay')
s = s[:a] + blk + s[b:]

# ── 무법자: 레벨당 강탈 +2%p / 체포·강탈 경험치 / 전용 변수 ────────
a = s.index('rule("[범죄 01] 황야에서 강도 / 체포 (F)")')
b = s.index('\nrule(', a + 5)
blk = s[a:b]
blk = blk.replace('Set Player Variable(Event Player, Roll, Player Variable(Event Player.Target, Bounty));',
                  'Set Player Variable(Event Player, Take, Player Variable(Event Player.Target, Bounty));\n'
                  '\t\t\tIf(Event Player.Job == 3);\n'
                  '\t\t\t\tSet Player Variable At Index(Event Player, JobXP, 3, Add(Value In Array(Event Player.JobXP, 3), 25));\n'
                  '\t\t\tEnd;')
blk = blk.replace('Set Player Variable(Event Player, Roll, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.25), Down));',
                  'Set Player Variable(Event Player, Take, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.25), Down));')
blk = blk.replace('\t\t\t\tSet Player Variable(Event Player, Roll, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.4), Down));\n',
                  '\t\t\t\tSet Player Variable(Event Player, Take, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), '
                  'Add(0.4, Min(0.2, Multiply(0.02, %s)))), Down));\n'
                  '\t\t\t\tSet Player Variable At Index(Event Player, JobXP, 4, Add(Value In Array(Event Player.JobXP, 4), 20));\n'
                  % lvl('Event Player.JobXP', 4))
blk = blk.replace('Event Player.Roll', 'Event Player.Take')
s = s[:a] + blk + s[b:]
assert 'Event Player.Roll' not in s[a:b + 400]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('사냥꾼        레벨당 가죽 +1 (최대 +8)')
print('현상금 사냥꾼  레벨당 처치금 +$10 (최대 +$100), 체포에 경험치 +25')
print('무법자        레벨당 강탈 +2%p (40 -> 최대 60%), 강탈에 경험치 +20')
print('금액 표시     공용 Roll -> 전용 HuntPay / Take')
