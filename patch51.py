# -*- coding: utf-8 -*-
"""[1] '좌측 상단 칭호가 안 바뀐다'
    좌상단에 뜨던 건 칭호가 아니라 직업이었다. 그런데 무직 상태의 직업명이
    '떠돌이'이고, 재산 칭호의 첫 단계도 '떠돌이'라 같은 글자였다.
    칭호가 올라가도 좌상단은 직업(떠돌이)이니 그대로였던 것.
    -> 무직 직업명을 '뜨내기'로 바꿔 겹침을 없애고,
       좌상단에 칭호를 실제로 표시한다.

[2] 체포 패널티 강화
    지금은 현상금만 지워지고 끝이라, 오히려 $100 벌금을 안 내고
    수배가 지워지는 이득이었다.
    -> 소지금 20% 몰수 + 8초 구금 + 평판 -10

[3] 강탈 쿨타임
    성공하면 45초, 실패하면 6초. 남은 시간은 눌렀을 때 알려준다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:60], s.count(old))
    s = s.replace(old, new, cnt)

TIER = ('Add(Add(Add(Add(Local Player.Money >= 300, Local Player.Money >= 1000), '
        'Local Player.Money >= 2500), Local Player.Money >= 6000), Local Player.Money >= 15000)')
TITLES = ('Array(Custom String("떠돌이"), Custom String("일꾼"), Custom String("정착민"), '
          'Custom String("유지"), Custom String("거상"), Custom String("66번 국도의 주인"))')

sub('\t\t54: NameSig\n', '\t\t54: NameSig\n\t\t55: RobCd\n')

# ── [1] 무직 직업명 변경 + 좌상단에 칭호 추가 ──────────────────────
JOBS_OLD = ('Array(Custom String("떠돌이"), Custom String("광부"), Custom String("사냥꾼"), '
            'Custom String("현상금 사냥꾼"), Custom String("무법자"))')
JOBS_NEW = JOBS_OLD.replace('Custom String("떠돌이")', 'Custom String("뜨내기")', 1)
n = s.count(JOBS_OLD)
assert n >= 1, n
s = s.replace(JOBS_OLD, JOBS_NEW)

OLD = ('Custom String("{0}   Lv.{1}   평판 {2}", Value In Array(%s, Local Player.Job), '
       'Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 250), Down)), Local Player.Rep)'
       % JOBS_NEW)
NEW = ('Custom String("{0}   {1}", Custom String("『 {0} 』", Value In Array(%s, %s)), '
       'Custom String("{0} Lv.{1}   평판 {2}", Value In Array(%s, Local Player.Job), '
       'Add(1, Round To Integer(Divide(Value In Array(Local Player.JobXP, Local Player.Job), 250), Down)), Local Player.Rep))'
       % (TITLES, TIER, JOBS_NEW))
sub(OLD, NEW)

# ── [2] 체포 패널티 ────────────────────────────────────────────────
sub('\t\t\tSet Player Variable(Event Player.Target, Bounty, 0);\n'
    '\t\t\tTeleport(Event Player.Target, Value In Array(Global Variable(LocPos), 7));\n',
    '\t\t\tSet Player Variable(Event Player.Target, Bounty, 0);\n'
    '\t\t\tSet Player Variable(Event Player.Target, Rep, Max(-100, Subtract(Player Variable(Event Player.Target, Rep), 10)));\n'
    '\t\t\tSet Player Variable(Event Player, Amt, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.2), Down));\n'
    '\t\t\tSet Player Variable(Event Player.Target, Money, Subtract(Player Variable(Event Player.Target, Money), Event Player.Amt));\n'
    '\t\t\tTeleport(Event Player.Target, Value In Array(Global Variable(LocPos), 7));\n'
    '\t\t\tSet Status(Event Player.Target, Null, Asleep, 8);\n'
    '\t\t\tSet Status(Event Player.Target, Null, Phased Out, 8);\n'
    '\t\t\tBig Message(Event Player.Target, Custom String("유치장에 처넣어졌다 — 벌금 $ {0}, 8초 구금", Event Player.Amt));\n')

# ── [3] 강탈 쿨타임 ────────────────────────────────────────────────
sub('\t\tSet Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(Players Within Radius(Eye Position(Event Player), 9',
    '\t\tIf(Total Time Elapsed() < Event Player.RobCd);\n'
    '\t\t\tSmall Message(Event Player, Custom String("아직 몸을 사려야 한다 — {0}초 뒤에 다시", '
    'Round To Integer(Subtract(Event Player.RobCd, Total Time Elapsed()), Up)));\n'
    '\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);\n'
    '\t\t\tAbort;\n'
    '\t\tEnd;\n'
    '\t\tSet Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(Players Within Radius(Eye Position(Event Player), 9')

sub('\t\t\tSmall Message(Event Player, Custom String("놓쳤다"));\n',
    '\t\t\tSet Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 6));\n'
    '\t\t\tSmall Message(Event Player, Custom String("놓쳤다"));\n')
sub('\t\t\t\tSmall Message(Event Player, Custom String("빈털터리다"));\n',
    '\t\t\t\tSet Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 6));\n'
    '\t\t\t\tSmall Message(Event Player, Custom String("빈털터리다"));\n')
sub('\t\t\t\tSet Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 15)));\n',
    '\t\t\t\tSet Player Variable(Event Player, Rep, Max(-100, Subtract(Event Player.Rep, 15)));\n'
    '\t\t\t\tSet Player Variable(Event Player, RobCd, Add(Total Time Elapsed(), 45));\n')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[1] 무직 직업명 떠돌이 -> 뜨내기, 좌상단에 『칭호』 표시')
print('[2] 체포당하면 소지금 20% 몰수 + 8초 구금 + 평판 -10')
print('[3] 강탈 성공 45초 / 실패 6초 쿨타임, 남은 시간 안내')
