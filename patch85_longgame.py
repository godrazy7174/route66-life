# -*- coding: utf-8 -*-
"""장기화 1차 배치 — 마을 재건 사다리 + 오늘의 직업 + 세이브 코드 A-B-C.

  재건 사다리 (안내소 4번 메뉴, 누적 $1,000,000):
    ①우물 $60k(갈증 -20%) ②전신국 $100k(목표 보너스 2배)
    ③은행 $160k(재산세 절반·사망 손실 3%) ④오페라 $260k(피로 회복 +25%)
    ⑤기차역 $420k(칭호 『66번 국도의 재건자』) — 환생은 2차 배치
  오늘의 직업: 매일 아침 직업 1개 보수 +50% (시계 HUD 상시 표시)
  세이브 코드: 12자리 -> 18자리 (C블록 = 재건단계·환생·예비3·검증)
"""
import io

T = chr(9)
N = chr(10)
RN = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

def block(depth, *lines):
    return ''.join(T*depth + ln + N for ln in lines)

CS = lambda t: 'Custom String("%s")' % t
JOBN7 = 'Array(%s)' % ', '.join(CS(x) for x in ['뜨내기', '광부', '사냥꾼', '현상금 사냥꾼', '무법자', '파발꾼', '목동'])
LANDMARKS = 'Array(%s)' % ', '.join(CS(x) for x in ['마을 우물', '전신국', '마을 은행', '오페라 하우스', '기차역'])
PERKS = 'Array(%s)' % ', '.join(CS(x) for x in ['갈증이 20% 느리게 마른다', '오늘 목표 보너스 $400', '재산세 절반 · 사망 손실 3%', '숙박·위스키 회복 +25%', '칭호 획득 — 66번 국도의 재건자'])
PADS = 'Array(Custom String("00000"), Custom String("0000"), Custom String("000"), Custom String("00"), Custom String("0"), Custom String(""))'

# ══ 1. 변수 선언 ═════════════════════════════════════════════════
sub(T*2 + '36: JerkyStock' + N,
    T*2 + '36: JerkyStock' + N + T*2 + '37: TodayJob' + N + T*2 + '38: RebuildMax' + N + T*2 + '39: RebuildFxN' + N)
sub(T*2 + '90: JobArg' + N + '}',
    T*2 + '90: JobArg' + N + T*2 + '91: Rebuild' + N + T*2 + '92: Rebirth' + N
    + T*2 + '93: EnterC' + N + T*2 + '94: SaveC' + N + T*2 + '95: PadC' + N + '}')

# ══ 2. 초기화 + 하루 전환 ════════════════════════════════════════
sub(T*2 + 'Set Global Variable(DailyGoal, 480);' + N,
    T*2 + 'Set Global Variable(DailyGoal, 480);' + N
    + block(2, 'Set Global Variable(TodayJob, Random Integer(1, 6));',
               'Set Global Variable(RebuildMax, 0);',
               'Set Global Variable(RebuildFxN, 0);'))
sub(T*3 + 'Set Global Variable(DailyGoal, Add(400, Multiply(Global Variable(Day), 80)));' + N,
    T*3 + 'Set Global Variable(DailyGoal, Add(400, Multiply(Global Variable(Day), 80)));' + N
    + block(3, 'Set Global Variable(TodayJob, Random Integer(1, 6));',
               'Big Message(All Players(All Teams), Custom String("새 아침 — 오늘은 {0}의 날! 해당 직업 보수 1.5배", Value In Array(%s, Global Variable(TodayJob))));' % JOBN7))

# ══ 3. HUD — 시계에 오늘의 직업, 칭호에 재건자 ═══════════════════
sub('Value In Array(Array(Custom String("낮"), Custom String("밤")), Global Variable(IsNight))',
    'Custom String("{0} · {1}의 날", Value In Array(Array(Custom String("낮"), Custom String("밤")), Global Variable(IsNight)), Value In Array(%s, Global Variable(TodayJob)))' % JOBN7)
MONEYTITLE = 'Value In Array(Array(Custom String("떠돌이"), Custom String("일꾼"), Custom String("정착민"), Custom String("유지"), Custom String("거상"), Custom String("66번 국도의 주인")), Add(Add(Add(Add(Local Player.Money >= 300, Local Player.Money >= 1000), Local Player.Money >= 2500), Local Player.Money >= 6000), Local Player.Money >= 15000))'
sub(MONEYTITLE, 'Local Player.Rebuild >= 5 ? Custom String("66번 국도의 재건자") : ' + MONEYTITLE)

# ══ 4. 재건 특전 ═════════════════════════════════════════════════
sub('Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 1.5)));',
    'Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, Event Player.Rebuild >= 1 ? 1.2 : 1.5)));')
sub(T*2 + 'Modify Player Variable(Event Player, Money, Add, 200);' + N,
    T*2 + 'Modify Player Variable(Event Player, Money, Add, Event Player.Rebuild >= 2 ? 400 : 200);' + N)
sub('오늘의 목표 달성 — 보너스 $200"))',
    '오늘의 목표 달성 — 보너스 $ {0}", Event Player.Rebuild >= 2 ? 400 : 200))')
sub(T*5 + 'Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, Event Player.Fame >= 70 ? 0.025 : 0.05), Down));' + N,
    T*5 + 'Set Player Variable(Event Player, Amt, Round To Integer(Multiply(Event Player.Money, Event Player.Fame >= 70 ? 0.025 : 0.05), Down));' + N
    + block(5, 'If(Event Player.Rebuild >= 3);')
    + block(6, 'Set Player Variable(Event Player, Amt, Max(1, Round To Integer(Multiply(Event Player.Amt, 0.5), To Nearest)));')
    + block(5, 'End;'))
sub(T*2 + 'Set Player Variable(Event Player, DeathLoss, Round To Integer(Multiply(Event Player.Money, Event Player.HasHome == 1 ? 0.05 : 0.15), Down));' + N,
    T*2 + 'Set Player Variable(Event Player, DeathLoss, Round To Integer(Multiply(Event Player.Money, Event Player.HasHome == 1 ? 0.05 : 0.15), Down));' + N
    + block(2, 'If(Event Player.Rebuild >= 3);')
    + block(3, 'Set Player Variable(Event Player, DeathLoss, Round To Integer(Multiply(Event Player.Money, 0.03), Down));')
    + block(2, 'End;'))
sub('Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, Event Player.HasHome == 1 ? 80 : 40)));',
    'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, Multiply(Event Player.HasHome == 1 ? 80 : 40, Event Player.Rebuild >= 4 ? 1.25 : 1))));')
sub('Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 30)));',
    'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, Event Player.Rebuild >= 4 ? 38 : 30)));')

# ══ 5. 오늘의 직업 보너스 (+50%) ═════════════════════════════════
def bonus(depth, var, owner='Event Player'):
    return (block(depth, 'If(Global Variable(TodayJob) == %d);' % JOB)
          + block(depth+1, 'Set Player Variable(%s, %s, Round To Integer(Multiply(%s(%s, %s), 1.5), To Nearest));'
                  % (owner, var, 'Player Variable' if owner == 'Attacker' else 'Player Variable', owner, var))
          + block(depth, 'End;'))

JOB = 1
sub(T*3 + 'Set Player Variable(Event Player, MineGain, Random Integer(50, 130));' + N,
    T*3 + 'Set Player Variable(Event Player, MineGain, Random Integer(50, 130));' + N + bonus(3, 'MineGain'))
sub(T*3 + 'Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), Event Player.MineGain));' + N,
    bonus(3, 'MineGain') + T*3 + 'Set Player Variable At Index(Event Player, Inv, 2, Add(Value In Array(Event Player.Inv, 2), Event Player.MineGain));' + N)
JOB = 2
sub(T*2 + 'Modify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));' + N,
    bonus(2, 'Yield', 'Attacker') + T*2 + 'Modify Player Variable At Index(Attacker, Inv, 3, Add, Player Variable(Attacker, Yield));' + N)
sub(T*3 + 'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 12)));' + N,
    T*3 + 'Set Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 12)));' + N
    + block(3, 'If(Global Variable(TodayJob) == 3);')
    + block(4, 'Set Player Variable(Event Player, Prize, Round To Integer(Multiply(Event Player.Take, 0.5), To Nearest));',
               'Modify Player Variable(Event Player, Money, Add, Event Player.Prize);',
               'Modify Player Variable(Event Player, Earned, Add, Event Player.Prize);',
               'Small Message(Event Player, Custom String("오늘의 직업 포상 +$ {0}", Event Player.Prize));')
    + block(3, 'End;'))
JOB = 4
sub(T*3 + 'Set Player Variable(Event Player, PlanPay, Random Integer(65, 125));' + N,
    T*3 + 'Set Player Variable(Event Player, PlanPay, Random Integer(65, 125));' + N + bonus(3, 'PlanPay'))
sub(T*3 + 'Set Player Variable(Event Player, PlanPay, Random Integer(8, 15));' + N,
    T*3 + 'Set Player Variable(Event Player, PlanPay, Random Integer(8, 15));' + N + bonus(3, 'PlanPay'))
JOB = 5
sub(T*2 + 'Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 3)));' + N + T*2 + 'Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);',
    T*2 + 'Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, 3)));' + N
    + bonus(2, 'RunPay') + T*2 + 'Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);')
JOB = 6
sub(T*3 + 'End;' + N + T*3 + 'Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);',
    T*3 + 'End;' + N + bonus(3, 'RunPay') + T*3 + 'Modify Player Variable(Event Player, Money, Add, Event Player.RunPay);')

# ══ 6. 안내소 — 메뉴 확장 + 재건 블록 ════════════════════════════
sub('Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 3, 3, 4, 2, 2, 1, 1)',
    'Array(1, 1, 3, 4, 2, 3, 4, 2, 4, 3, 4, 4, 2, 2, 1, 1)', 3)
sub(', '.join([CS('튜토리얼 보기'), CS('세이브 코드 발급'), CS('코드 입력 — 저장 복원'), CS('-'), CS('-'), CS('-')]),
    ', '.join([CS('튜토리얼 보기'), CS('세이브 코드 발급'), CS('코드 입력 — 저장 복원'), CS('마을 재건'), CS('-'), CS('-')]))
sub(T*3 + 'Else;' + N + T*4 + 'Set Player Variable(Event Player, Busy, 1);' + N + T*4 + 'Set Player Variable(Event Player, EnterA, 0);' + N,
    T*3 + 'Else If(Event Player.MenuIdx == 2);' + N + T*4 + 'Set Player Variable(Event Player, Busy, 1);' + N + T*4 + 'Set Player Variable(Event Player, EnterA, 0);' + N)
REBUILD_BLOCK = (block(3, 'Else;')
    + block(4, 'If(Event Player.Rebuild >= 5);')
    + block(5, 'Small Message(Event Player, Custom String("마을은 이미 되살아났다 — 당신의 이름과 함께"));',
               'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 50);')
    + block(4, 'Else;')
    + block(5, 'Set Player Variable(Event Player, Amt, Value In Array(Array(60000, 100000, 160000, 260000, 420000), Event Player.Rebuild));')
    + block(5, 'If(Event Player.Money >= Event Player.Amt);')
    + block(6, 'Modify Player Variable(Event Player, Money, Subtract, Event Player.Amt);',
               'Modify Player Variable(Event Player, Rebuild, Add, 1);',
               'Set Global Variable(RebuildMax, Max(Global Variable(RebuildMax), Event Player.Rebuild));',
               'Big Message(All Players(All Teams), Custom String("{0} — {1} 재건!! ({2}/5)", Event Player, Value In Array(%s, Subtract(Event Player.Rebuild, 1)), Event Player.Rebuild));' % LANDMARKS,
               'Small Message(Event Player, Custom String("특전 — {0}", Value In Array(%s, Subtract(Event Player.Rebuild, 1))));' % PERKS,
               'Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 6);',
               'Play Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 220);')
    + block(6, 'If(Event Player.Rebuild >= 5);')
    + block(7, 'Big Message(All Players(All Teams), Custom String("기차역이 복원되었다 — {0}, 66번 국도의 재건자!", Event Player));')
    + block(6, 'End;')
    + block(5, 'Else;')
    + block(6, 'Small Message(Event Player, Custom String("다음 단계: {0} — $ {1} 필요", Value In Array(%s, Event Player.Rebuild), Event Player.Amt));' % LANDMARKS,
               'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);')
    + block(5, 'End;')
    + block(4, 'End;'))
sub(T*4 + 'Small Message(Event Player, Custom String("주의 — 복원하면 현재 진행이 덮어써집니다"));' + N + T*3 + 'End;',
    T*4 + 'Small Message(Event Player, Custom String("주의 — 복원하면 현재 진행이 덮어써집니다"));' + N
    + REBUILD_BLOCK + T*3 + 'End;')

# 간판·게이지·오브
sub('세이브 코드 — 발급받아 적어두면 다음 방에서 복원할 수 있다' + RN,
    '세이브 코드 — 발급받아 적어두면 다음 방에서 복원할 수 있다' + RN
    + '마을 재건 — 우물에서 기차역까지 다섯 단계, 총 $1,000,000' + RN)
ANCHOR_INFO = 'Create In-World Text(All Players(All Teams), Custom String("안내소"), Add(Value In Array(Global Variable(LocPos), 9), Vector(0, 2.1, 0)), 1.5, Do Not Clip, Visible To and Position, Color(Yellow), Default Visibility);'
sub(ANCHOR_INFO,
    ANCHOR_INFO + N + T*2 + 'Create In-World Text(All Players(All Teams), Custom String("마을 재건 {0} / 5", Global Variable(RebuildMax)), Add(Value In Array(Global Variable(LocPos), 9), Vector(0, 3, 0)), 1.2, Do Not Clip, Visible To Position and String, Color(Yellow), Default Visibility);')
ORB_RULE = ('rule("[재건 01] 랜드마크 오브")' + N + '{' + N
    + T + 'event' + N + T + '{' + N + T*2 + 'Ongoing - Global;' + N + T + '}' + N + N
    + T + 'conditions' + N + T + '{' + N + T*2 + 'Global Variable(RebuildMax) > Global Variable(RebuildFxN);' + N + T + '}' + N + N
    + T + 'actions' + N + T + '{' + N
    + block(2, 'Create Effect(All Players(All Teams), Sphere, Color(Yellow), Add(Value In Array(Global Variable(LocPos), 9), Value In Array(Array(Vector(2.5, 2, 0), Vector(1.2, 2.6, 2.2), Vector(-1.2, 3.2, 2.2), Vector(-2.5, 3.8, 0), Vector(0, 4.6, 1)), Global Variable(RebuildFxN))), 0.4, None);',
               'Modify Global Variable(RebuildFxN, Add, 1);',
               'Wait(0.1, Ignore Condition);',
               'Loop If(Global Variable(RebuildMax) > Global Variable(RebuildFxN));')
    + T + '}' + N + '}' + N + N)
sub('rule("[코어 10] 서버 부하 보호")', ORB_RULE + 'rule("[코어 10] 서버 부하 보호")')

# ══ 7. 세이브 코드 A-B-C (18자리) ════════════════════════════════
PADB_LINE = 'Set Player Variable(Event Player, PadB, Add(Add(Event Player.SaveB >= 10 ? 1 : 0, Event Player.SaveB >= 100 ? 1 : 0), Add(Event Player.SaveB >= 1000 ? 1 : 0, Add(Event Player.SaveB >= 10000 ? 1 : 0, Event Player.SaveB >= 100000 ? 1 : 0))));'
PADC_LINE = PADB_LINE.replace('SaveB', 'SaveC').replace('PadB', 'PadC')
sub(T*4 + PADB_LINE + N,
    T*4 + PADB_LINE + N
    + block(4, 'Set Player Variable(Event Player, SaveC, Add(Multiply(Event Player.Rebuild, 100000), Multiply(Event Player.Rebirth, 10000)));',
               'Set Player Variable(Event Player, SaveC, Add(Event Player.SaveC, Modulo(Add(Add(Event Player.SaveA, Event Player.SaveB), Round To Integer(Divide(Event Player.SaveC, 10), Down)), 9)));',
               PADC_LINE))
OLD_HUD = 'Custom String("세이브 코드   {0} - {1}", Custom String("{0}{1}", Value In Array(%s, Event Player.PadA), Event Player.SaveA), Custom String("{0}{1}", Value In Array(%s, Event Player.PadB), Event Player.SaveB))' % (PADS, PADS)
NEW_HUD = 'Custom String("세이브 코드   {0} - {1} - {2}", Custom String("{0}{1}", Value In Array(%s, Event Player.PadA), Event Player.SaveA), Custom String("{0}{1}", Value In Array(%s, Event Player.PadB), Event Player.SaveB), Custom String("{0}{1}", Value In Array(%s, Event Player.PadC), Event Player.SaveC))' % (PADS, PADS, PADS)
sub(OLD_HUD, NEW_HUD)
sub(T*4 + 'Set Player Variable(Event Player, EnterB, 0);' + N,
    T*4 + 'Set Player Variable(Event Player, EnterB, 0);' + N + T*4 + 'Set Player Variable(Event Player, EnterC, 0);' + N)
sub('Custom String("A {0}   B {1}", Event Player.EnterA, Event Player.EnterB)',
    'Custom String("A {0}   B {1}   C {2}", Event Player.EnterA, Event Player.EnterB, Event Player.EnterC)')
sub('자리 {0}/12', '자리 {0}/18')
sub(T*2 + 'Else;' + N + T*3 + 'Set Player Variable(Event Player, EnterB, Add(Multiply(Event Player.EnterB, 10), Event Player.EntryCur));' + N,
    T*2 + 'Else If(Event Player.EntryIdx < 12);' + N + T*3 + 'Set Player Variable(Event Player, EnterB, Add(Multiply(Event Player.EnterB, 10), Event Player.EntryCur));' + N
    + T*2 + 'Else;' + N + T*3 + 'Set Player Variable(Event Player, EnterC, Add(Multiply(Event Player.EnterC, 10), Event Player.EntryCur));' + N)
sub('If(Event Player.EntryIdx >= 12);', 'If(Event Player.EntryIdx >= 18);')
sub(T*3 + 'Set Player Variable(Event Player, Amt, Round To Integer(Divide(Event Player.EnterB, 10), Down));' + N,
    T*3 + 'Set Player Variable(Event Player, Amt, Round To Integer(Divide(Event Player.EnterB, 10), Down));' + N
    + T*3 + 'Set Player Variable(Event Player, Roll, Round To Integer(Divide(Event Player.EnterC, 10), Down));' + N)
OLD_VALID = 'If(Or(Or(Modulo(Event Player.EnterB, 10) != Modulo(Add(Event Player.EnterA, Event Player.Amt), 9), Round To Integer(Divide(Event Player.Amt, 10000), Down) > 6), Or(Modulo(Round To Integer(Divide(Event Player.EnterA, 10), Down), 10) > 4, Modulo(Round To Integer(Divide(Event Player.Amt, 1000), Down), 10) > 1)));'
NEW_VALID = ('If(Or(Or(Or(Modulo(Event Player.EnterB, 10) != Modulo(Add(Event Player.EnterA, Event Player.Amt), 9), Round To Integer(Divide(Event Player.Amt, 10000), Down) > 6), Or(Modulo(Round To Integer(Divide(Event Player.EnterA, 10), Down), 10) > 4, Modulo(Round To Integer(Divide(Event Player.Amt, 1000), Down), 10) > 1)), '
    + 'Or(Or(Modulo(Event Player.EnterC, 10) != Modulo(Add(Add(Event Player.EnterA, Event Player.EnterB), Event Player.Roll), 9), Round To Integer(Divide(Event Player.EnterC, 100000), Down) > 5), '
    + 'Or(Modulo(Round To Integer(Divide(Event Player.EnterC, 10000), Down), 10) > 5, Modulo(Event Player.Roll, 1000) != 0))));')
sub(OLD_VALID, NEW_VALID)
sub(T*4 + 'Set Player Variable(Event Player, Noto, Multiply(Modulo(Event Player.Amt, 10), 10));' + N,
    T*4 + 'Set Player Variable(Event Player, Noto, Multiply(Modulo(Event Player.Amt, 10), 10));' + N
    + block(4, 'Set Player Variable(Event Player, Rebuild, Round To Integer(Divide(Event Player.EnterC, 100000), Down));',
               'Set Player Variable(Event Player, Rebirth, Modulo(Round To Integer(Divide(Event Player.EnterC, 10000), Down), 10));',
               'Set Global Variable(RebuildMax, Max(Global Variable(RebuildMax), Event Player.Rebuild));'))

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('장기화 1차 배치 적용 완료')
