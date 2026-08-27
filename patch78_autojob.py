# -*- coding: utf-8 -*-
"""자동 전직 — 일을 하면 그 직업이 된다.

  - 6개 일터의 '전직' 메뉴 삭제, 수주·소몰이·습격의 직업 게이트 삭제
  - 작업 시작 시점에 자동 전직: 채굴=광부, 추적=사냥꾼, 체포=현상금 사냥꾼,
    강탈·습격=무법자, 수주=파발꾼, 소몰이=목동 (BecomeJob 서브루틴)
  - 무법자 악명 20 가입 게이트는 자연 소멸 (강탈 자체가 악명을 쌓는다)
  - Adv(승급)를 직업별 7칸 배열로 전환 — 직업을 오가도 승급 유지.
    경험치(JobXP)가 직업별로 남는 것과 같은 원리.
  - 메뉴 라벨 84칸 배열·개수 배열(x3)·승급 안내문·튜토리얼·식당 안내 갱신
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

def block(depth, *lines):
    return ''.join(T*depth + ln + N for ln in lines)

EFF_RED = 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);'
EFF_RING = 'Play Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Position Of(Event Player), 2.5);'
EFF_BUFF = 'Play Effect(Event Player, Buff Explosion Sound, Color(Sky Blue), Position Of(Event Player), 160);'

def recruit_block(job, name, already):
    return (block(3, 'If(Event Player.MenuIdx == 0);')
          + block(4, 'If(Event Player.Job == %d);' % job)
          + block(5, 'Small Message(Event Player, Custom String("%s"));' % already,
                     EFF_RED)
          + block(4, 'Else;')
          + block(5, 'Set Player Variable(Event Player, Job, %d);' % job,
                     'Set Player Variable(Event Player, Adv, 0);',
                     'Big Message(Event Player, Custom String("전직 완료 — %s"));' % name,
                     EFF_RING, EFF_BUFF)
          + block(4, 'End;'))

# ══ 1. 구역 블록 구조 변경 ═══════════════════════════════════════════

# 광산 (구역 1): 전직 삭제 → 채굴이 0번
sub(recruit_block(1, '광부', '이미 광부다')
    + block(3, 'Else If(Event Player.MenuIdx == 1);')
    + block(4, 'Call Subroutine(DoMine);'),
    block(3, 'If(Event Player.MenuIdx == 0);')
    + block(4, 'Call Subroutine(DoMine);'))
sub(block(3, 'Else If(Event Player.MenuIdx == 2);')
    + T*4 + 'Set Player Variable(Event Player, Amt, And(Event Player.Job == 1, Event Player.Adv == 1) ? 0 : 45);',
    block(3, 'Else If(Event Player.MenuIdx == 1);')
    + T*4 + 'Set Player Variable(Event Player, Amt, And(Event Player.Job == 1, Event Player.Adv == 1) ? 0 : 45);')

# 개활지 (구역 6): 전직 삭제 → 추적이 0번
sub(recruit_block(2, '사냥꾼', '이미 사냥꾼이다')
    + block(3, 'Else If(Event Player.MenuIdx == 1);')
    + block(4, 'Call Subroutine(DoHunt);'),
    block(3, 'If(Event Player.MenuIdx == 0);')
    + block(4, 'Call Subroutine(DoHunt);'))

# 초소 (구역 7): 전직 삭제 → 벌금 0, 게시판 1, 승급 2, 재산세 Else
sub(recruit_block(3, '현상금 사냥꾼', '이미 현상금 사냥꾼이다')
    + block(3, 'Else If(Event Player.MenuIdx == 1);')
    + T*4 + 'Set Player Variable(Event Player, Amt, Event Player.Fame >= 70 ? 50 : 100);',
    block(3, 'If(Event Player.MenuIdx == 0);')
    + T*4 + 'Set Player Variable(Event Player, Amt, Event Player.Fame >= 70 ? 50 : 100);')
sub(block(3, 'Else If(Event Player.MenuIdx == 2);')
    + T*4 + 'Small Message(Event Player, Custom String("현상금 게시판 — 지금 수배자 {0}명"',
    block(3, 'Else If(Event Player.MenuIdx == 1);')
    + T*4 + 'Small Message(Event Player, Custom String("현상금 게시판 — 지금 수배자 {0}명"')
sub(block(3, 'Else If(Event Player.MenuIdx == 3);')
    + block(4, 'If(Event Player.Job != 3);'),
    block(3, 'Else If(Event Player.MenuIdx == 2);')
    + block(4, 'If(Event Player.Job != 3);'))

# 은신처 (구역 8): 합류 삭제 → 장물 0, 습격 1(게이트 해제), 승급 Else
OUTLAW_JOIN = (block(3, 'If(Event Player.MenuIdx == 0);')
    + block(4, 'If(Event Player.Job == 4);')
    + block(5, 'Small Message(Event Player, Custom String("이미 무법자다"));', EFF_RED)
    + block(4, 'Else If(Event Player.Noto < 20);')
    + block(5, 'Small Message(Event Player, Custom String("은신처가 애송이는 안 받는다 — 악명 20을 쌓아 와라 (현재 {0})", Event Player.Noto));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Set Player Variable(Event Player, Job, 4);',
               'Set Player Variable(Event Player, Adv, 0);',
               'Set Player Variable(Event Player, Noto, Min(100, Add(Event Player.Noto, 5)));',
               'Big Message(Event Player, Custom String("무법자가 되었다"));',
               'Small Message(Event Player, Custom String("강탈 40%, 장물 165%. 습격 계획 3회면 역마차를 턴다"));',
               'Play Effect(Event Player, Ring Explosion, Color(Purple), Position Of(Event Player), 2);')
    + block(4, 'End;'))
sub(OUTLAW_JOIN + block(3, 'Else If(Event Player.MenuIdx == 1);'),
    block(3, 'If(Event Player.MenuIdx == 0);'))
sub(block(3, 'Else If(Event Player.MenuIdx == 2);')
    + block(4, 'If(Event Player.Job != 4);')
    + block(5, 'Small Message(Event Player, Custom String("무법자만 할 수 있다 — 먼저 합류해라"));', EFF_RED)
    + block(4, 'Else;')
    + block(5, 'Call Subroutine(DoPlan);')
    + block(4, 'End;'),
    block(3, 'Else If(Event Player.MenuIdx == 1);')
    + block(4, 'Call Subroutine(DoPlan);'))

# 정거장 (구역 11): 전직 삭제 + 수주 게이트 해제
sub(recruit_block(5, '파발꾼', '이미 파발꾼이다')
    + block(3, 'Else If(Event Player.MenuIdx == 1);')
    + block(4, 'If(Event Player.Job != 5);')
    + block(5, 'Small Message(Event Player, Custom String("파발꾼만 수주할 수 있다 — 전직은 여기 1번 게시판에서"));', EFF_RED)
    + T*4 + 'Else If(Event Player.HasParcel == 1);',
    block(3, 'If(Event Player.MenuIdx == 0);')
    + T*4 + 'If(Event Player.HasParcel == 1);')
sub(T*4 + 'Else;' + N + T*5 + 'Set Player Variable(Event Player, DelDest, Random Integer(0, 10));',
    T*4 + 'Else;' + N
    + block(5, 'Set Player Variable(Event Player, JobArg, 5);', 'Call Subroutine(BecomeJob);')
    + T*5 + 'Set Player Variable(Event Player, DelDest, Random Integer(0, 10));')

# 목장 (구역 12): 전직 삭제 + 소몰이 게이트 해제
sub(recruit_block(6, '목동', '이미 목동이다')
    + block(3, 'Else If(Event Player.MenuIdx == 1);')
    + block(4, 'If(Event Player.Job != 6);')
    + block(5, 'Small Message(Event Player, Custom String("목동만 소를 몰 수 있다 — 전직은 여기 1번 게시판에서"));', EFF_RED)
    + T*4 + 'Else If(Event Player.CowOn == 1);',
    block(3, 'If(Event Player.MenuIdx == 0);')
    + T*4 + 'If(Event Player.CowOn == 1);')
sub(T*4 + 'Else;' + N + T*5 + 'Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Add(Value In Array(Global Variable(LocPos), 12)',
    T*4 + 'Else;' + N
    + block(5, 'Set Player Variable(Event Player, JobArg, 6);', 'Call Subroutine(BecomeJob);')
    + T*5 + 'Set Player Variable(Event Player, CowPos, Nearest Walkable Position(Add(Add(Value In Array(Global Variable(LocPos), 12)')

# ══ 2. 작업 시작 지점에 자동 전직 삽입 ═══════════════════════════════
def convert2(depth, job):
    return block(depth, 'Set Player Variable(Event Player, JobArg, %d);' % job, 'Call Subroutine(BecomeJob);')

sub(T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("채굴 중..."',
    convert2(2, 1) + T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("채굴 중..."')
sub(T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("흔적 추적 중..."',
    convert2(2, 2) + T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("흔적 추적 중..."')
sub(T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("습격 계획 중..."',
    convert2(2, 4) + T*2 + 'Create Progress Bar HUD Text(Event Player, Event Player.WorkProg, Custom String("습격 계획 중..."')
sub(N + T*2 + 'If(Player Variable(Event Player.Target, Bounty) > 0);' + N,
    N + T*2 + 'If(Player Variable(Event Player.Target, Bounty) > 0);' + N + convert2(3, 3))
sub(T*2 + 'Else;' + N + T*3 + 'Big Message(Event Player.Target, Custom String("{0}이(가) 총을 겨눴다 — 도망쳐라", Event Player));',
    T*2 + 'Else;' + N + convert2(3, 4)
    + T*3 + 'Big Message(Event Player.Target, Custom String("{0}이(가) 총을 겨눴다 — 도망쳐라", Event Player));')

# ══ 3. 승급 게이트 안내문 ═══════════════════════════════════════════
sub('광부만 승급할 수 있다 — 전직은 여기 1번 게시판에서', '광부만 승급할 수 있다 — 채굴이 너를 광부로 만든다')
sub('현상금 사냥꾼만 승급할 수 있다 — 전직은 여기 1번 게시판에서', '현상금 사냥꾼만 승급할 수 있다 — 수배자 체포가 너를 현상금 사냥꾼으로 만든다')
sub('사냥꾼만 승급할 수 있다 — 전직은 여기 1번 게시판에서', '사냥꾼만 승급할 수 있다 — 흔적 추적이 너를 사냥꾼으로 만든다')
sub('무법자만 승급할 수 있다 — 합류는 여기 1번 게시판에서', '무법자만 승급할 수 있다 — 강탈과 습격이 너를 무법자로 만든다')
sub('파발꾼만 승급할 수 있다 — 전직은 여기 1번 게시판에서', '파발꾼만 승급할 수 있다 — 배달 수주가 너를 파발꾼으로 만든다')
sub('목동만 승급할 수 있다 — 전직은 여기 1번 게시판에서', '목동만 승급할 수 있다 — 소몰이가 너를 목동으로 만든다')

# ══ 4. 메뉴 라벨 84칸 배열 ══════════════════════════════════════════
CS = lambda t: 'Custom String("%s")' % t
DASH = CS('-')
sub(', '.join([CS('전직: 광부'), CS('채굴하기'), CS('정밀 탐사 $45'), CS('승급: 광산주 — Lv.4'), DASH, DASH]),
    ', '.join([CS('채굴하기'), CS('정밀 탐사 $45'), CS('승급: 광산주 — Lv.4'), DASH, DASH, DASH]))
sub(', '.join([CS('전직: 사냥꾼'), CS('흔적 추적 — 야수 몰아내기'), CS('승급: 맹수 사냥꾼 — Lv.4'), DASH, DASH, DASH]),
    ', '.join([CS('흔적 추적 — 야수 몰아내기'), CS('승급: 맹수 사냥꾼 — Lv.4'), DASH, DASH, DASH, DASH]))
sub(', '.join([CS('전직: 현상금 사냥꾼'), CS('벌금 납부 $100 — 현상금 말소'), CS('현상금 게시판'), CS('승급: 보안관 — Lv.4·명성 30'), CS('재산세 납부 — 징수 기간만'), DASH]),
    ', '.join([CS('벌금 납부 $100 — 현상금 말소'), CS('현상금 게시판'), CS('승급: 보안관 — Lv.4·명성 30'), CS('재산세 납부 — 징수 기간만'), DASH, DASH]))
sub(', '.join([CS('무법자 합류 — 악명 20'), CS('장물 거래'), CS('습격 계획 (무법자 전용)'), CS('승급: 갱단 두목 — Lv.4'), DASH, DASH]),
    ', '.join([CS('장물 거래'), CS('습격 계획'), CS('승급: 갱단 두목 — Lv.4'), DASH, DASH, DASH]))
sub(', '.join([CS('전직: 파발꾼'), CS('배달 수주'), CS('승급: 역마차장 — Lv.4'), DASH, DASH, DASH]),
    ', '.join([CS('배달 수주'), CS('승급: 역마차장 — Lv.4'), DASH, DASH, DASH, DASH]))
sub(', '.join([CS('전직: 목동'), CS('소 몰기 시작'), CS('승급: 목장주 — Lv.4'), DASH, DASH, DASH]),
    ', '.join([CS('소 몰기 시작'), CS('승급: 목장주 — Lv.4'), DASH, DASH, DASH, DASH]))

# ══ 5. 메뉴 개수 배열 (x3) ══════════════════════════════════════════
sub('Array(1, 1, 4, 4, 2, 3, 4, 3, 5, 4, 3, 4, 3, 3, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 3, 3, 4, 2, 2, 1, 1)', 3)

# ══ 6. Adv → 직업별 배열 ════════════════════════════════════════════
sub('Event Player.Adv == 1', 'Value In Array(Event Player.Adv, Event Player.Job) == 1', 13)
sub('Set Player Variable(Event Player, Adv, 1);',
    'Set Player Variable At Index(Event Player, Adv, Event Player.Job, 1);', 6)
sub('Local Player.Adv == 1 ?', 'Value In Array(Local Player.Adv, Local Player.Job) == 1 ?')
sub('Set Player Variable(Event Player, Adv, 0);',
    'Set Player Variable(Event Player, Adv, Array(0, 0, 0, 0, 0, 0, 0));')
sub('Event Player.Job == 2 ? Event Player.Adv : 0', 'Value In Array(Event Player.Adv, 2)')
sub('Subtract(3, Event Player.Adv)', 'Subtract(3, Value In Array(Event Player.Adv, 4))', 2)
sub('Multiply(0.9, Event Player.Adv)', 'Multiply(0.9, Value In Array(Event Player.Adv, 6))')
sub('Multiply(Event Player.Job, 10), Event Player.Adv)',
    'Multiply(Event Player.Job, 10), Value In Array(Event Player.Adv, Event Player.Job))')
sub(T*4 + 'Set Player Variable(Event Player, Adv, Modulo(Round To Integer(Divide(Event Player.Amt, 1000), Down), 10));',
    block(4, 'Set Player Variable(Event Player, Adv, Array(0, 0, 0, 0, 0, 0, 0));')
    + T*4 + 'Set Player Variable At Index(Event Player, Adv, Event Player.Job, Modulo(Round To Integer(Divide(Event Player.Amt, 1000), Down), 10));')

# ══ 7. 안내 문구 (튜토리얼·식당) ════════════════════════════════════
sub('직업은 각자의 일터 게시판에서 구한다. 가서 문을 두드려라.',
    '일을 하는 순간 그 직업이 된다. 경험과 승급은 직업마다 따로 남는다.')
sub('직업은 각자의 일터 게시판에서 구한다',
    '일을 하는 순간 그 직업이 된다 — 경험은 직업마다 남는다')

# ══ 8. 선언 + BecomeJob 규칙 ════════════════════════════════════════
sub(T*2 + '89: KeyHud' + N + '}',
    T*2 + '89: KeyHud' + N + T*2 + '90: JobArg' + N + '}')
sub(T + '8: DoTutorial' + N + '}',
    T + '8: DoTutorial' + N + T + '9: BecomeJob' + N + '}')

JOBNAMES = ', '.join([CS('뜨내기'), CS('광부'), CS('사냥꾼'), CS('현상금 사냥꾼'), CS('무법자'), CS('파발꾼'), CS('목동')])
RULE = ('rule("[직업 00] 일이 곧 직업 — 자동 전직")' + N + '{' + N
  + T + 'event' + N + T + '{' + N
  + T*2 + 'Subroutine;' + N + T*2 + 'BecomeJob;' + N
  + T + '}' + N + N
  + T + 'actions' + N + T + '{' + N
  + block(2, 'If(Event Player.Job != Event Player.JobArg);')
  + block(3, 'Set Player Variable(Event Player, Job, Event Player.JobArg);',
             'Big Message(Event Player, Custom String("전직 — {0}", Value In Array(Array(%s), Event Player.JobArg)));' % JOBNAMES,
             'Small Message(Event Player, Custom String("일이 곧 직업이다 — 이전 직업의 경험치와 승급은 그대로 남는다"));',
             'Play Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 70);',
             'Play Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Position Of(Event Player), 2);')
  + block(2, 'End;')
  + T + '}' + N + '}' + N + N)
sub('rule("[직업 01] DoMine")', RULE + 'rule("[직업 01] DoMine")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('자동 전직 적용: 전직 메뉴 6곳 삭제, BecomeJob 7개 진입점, Adv 배열화')
