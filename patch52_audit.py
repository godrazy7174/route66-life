# -*- coding: utf-8 -*-
"""전수 조사 패치 — 표기 불일치·공용 변수 오표시·논리 구멍 일괄 수정.

A. 메시지 오표시 (메시지는 떠 있는 동안 변수를 다시 읽는다)
   A1 채굴: 금맥/원석 메시지의 Roll 을 몇 줄 아래 연속 보너스가 덮는다
      -> 5번째 채굴마다 "원석 +30" 같은 오표시가 반드시 발생. MineGain/StreakPay 분리
   A2 습격: 역마차/정찰비 금액이 공용 Roll -> PlanPay
   A3 발견/보물/사망: 지갑·보물·치료비 금액이 공용 Amt/Roll -> Loot/Prize/DeathLoss

B. 표기 불일치
   B1 R키 미리보기(다음 →) 배열이 본 배열과 다르다:
      모텔 '내 방 마련'이 '-', 위스키 $20(실제 $25), 대장간 3항목 통째 누락(범위 밖)
      -> 본 배열 복사로 통일
   B2 튜토리얼 '피로': "하루 한 번뿐" — 제한 폐지됨. 회복 40/80 반영
   B3 튜토리얼 '시작': [V] 강도/체포 누락
   B4 무법자 습격: "현상금 3배" — 실제 $12->$40. 금액으로 표기
   B5 개활지 패널: 드러난 뒤 "야수 0마리 — 숨어 있어"가 됨 -> "숨은 야수 {0}마리"

C. 논리 구멍
   C1 벌금 납부: 수배 중이 아니어도 $100 받고 "풀렸다" -> 가드
   C2 전직: 이미 그 직업이어도 전직 연출 반복 -> 가드
   C3 튜토리얼 중 몸이 안내소에 무방비로 서 있다(강도·사격 표적, F 재진입 가능)
      -> 시작 시 Busy·Rooted·Phased Out·투명 (끝의 해제 코드와 짝 맞춤)
   C4 강도 대상에 야수(봇)·튜토리얼 중·수감 중인 사람이 잡힌다 -> 필터
   C5 죽은 채로 E/Q 누르면 육포·물이 소모된다 -> Is Alive
   C6 도박 잭팟·승리금이 '오늘 목표'에 안 잡힌다 -> Earned 반영
   C7 자기 머리 위 이름표가 3인칭 화면 정중앙을 가린다 -> 본인 제외
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ── 변수 ───────────────────────────────────────────────────────────
for v in ('MineGain', 'StreakPay', 'Prize', 'Loot', 'DeathLoss', 'PlanPay'):
    assert v not in s
sub('\t\t56: Fine\n', '\t\t56: Fine\n\t\t57: MineGain\n\t\t58: StreakPay\n'
    '\t\t59: Prize\n\t\t60: Loot\n\t\t61: DeathLoss\n\t\t62: PlanPay\n')

# ── A1 채굴 ────────────────────────────────────────────────────────
a = s.index('rule("[직업 01] DoMine")')
b = s.index('\nrule(', a + 5)
blk = s[a:b]
g0 = blk.index('If(Event Player.Roll <= 3);')
g1 = blk.index('If(Modulo(Event Player.MineCount, 10) == 0);')
mid = blk[g0:g1].replace('Event Player, Roll,', 'Event Player, MineGain,').replace('Event Player.Roll', 'Event Player.MineGain')
mid = mid.replace('If(Event Player.MineGain <= 3);', 'If(Event Player.Roll <= 3);', 1)   # 분기 판정은 원래 Roll
blk = blk[:g0] + mid + blk[g1:]
st = blk.index('If(Modulo(Event Player.Streak, 5) == 0);')
tail = blk[st:].replace('Event Player, Roll, Multiply(Event Player.Streak, 6)', 'Event Player, StreakPay, Multiply(Event Player.Streak, 6)').replace('Event Player.Roll', 'Event Player.StreakPay')
blk = blk[:st] + tail
s = s[:a] + blk + s[b:]

# ── A2 습격 ────────────────────────────────────────────────────────
a = s.index('rule("[직업 04] DoPlan")')
b = s.index('\nrule(', a + 5)
s = s[:a] + s[a:b].replace('Event Player, Roll,', 'Event Player, PlanPay,').replace('Event Player.Roll', 'Event Player.PlanPay') + s[b:]

# ── A3 발견/보물/사망 ──────────────────────────────────────────────
a = s.index('rule("[도파민 01] 길 위의 발견")')
b = s.index('\nrule(', a + 5)
s = s[:a] + s[a:b].replace('Event Player, Amt,', 'Event Player, Loot,').replace('Event Player.Amt', 'Event Player.Loot') + s[b:]
a = s.index('rule("[도파민 03] 보물 획득")')
b = s.index('\nrule(', a + 5)
s = s[:a] + s[a:b].replace('Event Player, Amt,', 'Event Player, Prize,').replace('Event Player.Amt', 'Event Player.Prize') + s[b:]
a = s.index('rule("[생활 02] 사망 처리")')
b = s.index('\nrule(', a + 5)
s = s[:a] + s[a:b].replace('Event Player, Roll,', 'Event Player, DeathLoss,').replace('Event Player.Roll', 'Event Player.DeathLoss') + s[b:]

# ── B1 미리보기 배열 = 본 배열 ─────────────────────────────────────
KEY = 'Array(Custom String("행동 없음 — 마을로 이동하세요")'
i1 = s.index(KEY)

def span(src, start):
    d, j = 0, start
    while True:
        c = src[j]
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0:
                return j + 1
        j += 1

e1 = span(s, i1 + 5)          # Array 뒤 여는 괄호부터 짝 맞춤
main_arr = s[i1:e1]
i2 = s.index(KEY, e1)
e2 = span(s, i2 + 5)
s = s[:i2] + main_arr + s[e2:]

# ── B2/B3 튜토리얼 문구 ────────────────────────────────────────────
sub('Custom String("피로가 바닥나면 아무 일도 할 수 없다.' + NL + '하룻밤 $60, 하루 한 번뿐이다. 잘 곳을 마련하는 게 첫 목표다.")',
    'Custom String("피로가 바닥나면 아무 일도 할 수 없다.' + NL + '하룻밤 $60에 피로를 40 되찾는다. 내 방을 마련하면 80으로 늘어난다.")')
sub('Custom String("[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기' + NL,
    'Custom String("[R] 행동 선택 · [F] 실행 · [E] 육포 · [Q] 물 · [Shift] 달리기 · [V] 강도/체포' + NL)

# ── B4 무법자 습격 표기 ────────────────────────────────────────────
sub('Custom String("무법자 습격! 현상금 3배")', 'Custom String("무법자 습격! 무법자 현상금이 $40으로 뛴다")')

# ── B5 개활지 패널 ─────────────────────────────────────────────────
sub('Custom String("이 일대에 야수 {0}마리 — 숨어 있어 눈에 띄지 않는다' + NL + '추적하면 전부 튀어나온다. 30초 안에 잡아라' + NL + '", ',
    'Custom String("숨은 야수 {0}마리 — 추적하면 전부 튀어나온다' + NL + '드러난 30초 안에 잡아라' + NL + '", ')

# ── C1 벌금 가드 ───────────────────────────────────────────────────
T4, T5 = chr(9) * 4, chr(9) * 5
OLD_FINE = (T4 + 'If(Event Player.Money >= 100);' + chr(10)
            + T5 + 'Modify Player Variable(Event Player, Money, Subtract, 100);' + chr(10)
            + T5 + 'Set Player Variable(Event Player, Bounty, 0);')
NEW_FINE = (T4 + 'If(Event Player.Bounty <= 0);' + chr(10)
            + T5 + 'Small Message(Event Player, Custom String("수배 중이 아니다 — 낼 벌금이 없다"));' + chr(10)
            + T5 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);' + chr(10)
            + T4 + 'Else If(Event Player.Money >= 100);' + chr(10)
            + T5 + 'Modify Player Variable(Event Player, Money, Subtract, 100);' + chr(10)
            + T5 + 'Set Player Variable(Event Player, Bounty, 0);')
sub(OLD_FINE, NEW_FINE)

# ── C2 전직 가드 ───────────────────────────────────────────────────
for idx, job, name in ((0, 1, '광부'), (1, 2, '사냥꾼'), (2, 3, '현상금 사냥꾼')):
    cond = ('If(Event Player.MenuIdx == %d);' if idx == 0 else 'Else If(Event Player.MenuIdx == %d);') % idx
    old = '%s\n\t\t\t\tSet Player Variable(Event Player, Job, %d);' % (cond, job)
    new = ('%s\n\t\t\t\tIf(Event Player.Job == %d);\n'
           '\t\t\t\t\tSmall Message(Event Player, Custom String("이미 %s다"));\n'
           '\t\t\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);\n'
           '\t\t\t\tElse;\n'
           '\t\t\t\t\tSet Player Variable(Event Player, Job, %d);' % (cond, job, name, job))
    sub(old, new)
# 전직 세 분기의 몸통을 If/Else 로 감쌌으니 각 분기 끝에 End 를 닫아준다
for job in (1, 2, 3):
    name = {1: '광부', 2: '사냥꾼', 3: '현상금 사냥꾼'}[job]
    old = ('\t\t\t\t\tBig Message(Event Player, Custom String("전직 완료 — %s"));\n'
           '\t\t\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Position Of(Event Player), 2.5);\n'
           '\t\t\t\t\tPlay Effect(Event Player, Buff Explosion Sound, Color(Sky Blue), Position Of(Event Player), 160);\n' % name)
    assert s.count(old) == 0
    old = ('\t\t\t\tBig Message(Event Player, Custom String("전직 완료 — %s"));\n'
           '\t\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Sky Blue), Position Of(Event Player), 2.5);\n'
           '\t\t\t\tPlay Effect(Event Player, Buff Explosion Sound, Color(Sky Blue), Position Of(Event Player), 160);\n' % name)
    new = old.replace('\t\t\t\t', '\t\t\t\t\t') + '\t\t\t\tEnd;\n'
    sub(old, new)

# ── C3 튜토리얼 보호 ───────────────────────────────────────────────
sub('\t\tSet Player Variable(Event Player, TutOn, 1);\n\t\tSet Player Variable(Event Player, TutSkip, 0);',
    '\t\tSet Player Variable(Event Player, TutOn, 1);\n'
    '\t\tSet Player Variable(Event Player, Busy, 1);\n'
    '\t\tSet Status(Event Player, Null, Rooted, 9999);\n'
    '\t\tSet Status(Event Player, Null, Phased Out, 9999);\n'
    '\t\tSet Invisible(Event Player, All);\n'
    '\t\tSet Player Variable(Event Player, TutSkip, 0);')

# ── C4 강도 대상 필터 ──────────────────────────────────────────────
OLD_F = 'And(Current Array Element != Event Player, And(Is Alive(Current Array Element), Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Eye Position(Current Array Element))) >= 0.93))'
NEW_F = 'And(Current Array Element != Event Player, And(Is Dummy Bot(Current Array Element) == False, And(Player Variable(Current Array Element, TutOn) == 0, And(Has Status(Current Array Element, Asleep) == False, And(Is Alive(Current Array Element), Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Eye Position(Current Array Element))) >= 0.93)))))'
sub(OLD_F, NEW_F)

# ── C5 죽은 채 취식 방지 ───────────────────────────────────────────
for btn in ('Ability 2', 'Ultimate'):
    old = ('\tconditions\n\t{\n\t\tEvent Player.Init == 1;\n'
           '\t\tIs Button Held(Event Player, Button(%s)) == True;' % btn)
    new = ('\tconditions\n\t{\n\t\tEvent Player.Init == 1;\n'
           '\t\tIs Alive(Event Player) == True;\n'
           '\t\tIs Button Held(Event Player, Button(%s)) == True;' % btn)
    sub(old, new)

# ── C6 도박 수익 -> 오늘 목표 ──────────────────────────────────────
sub('\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 300);\n\t\t\t\t\t\tBig Message',
    '\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 300);\n\t\t\t\t\t\tModify Player Variable(Event Player, Earned, Add, 300);\n\t\t\t\t\t\tBig Message')
sub('\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 90);\n\t\t\t\t\t\tSmall Message',
    '\t\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 90);\n\t\t\t\t\t\tModify Player Variable(Event Player, Earned, Add, 90);\n\t\t\t\t\t\tSmall Message')

# ── C7 이름표 본인 제외 ────────────────────────────────────────────
OLDN = 'Create In-World Text(All Players(All Teams), Custom String("『 {0} 』 {1}"'
NEWN = 'Create In-World Text(Remove From Array(All Players(All Teams), Event Player), Custom String("『 {0} 』 {1}"'
n = s.count(OLDN)
assert n == 2, n
s = s.replace(OLDN, NEWN)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료 — A(오표시) 5곳 / B(표기) 5곳 / C(논리) 7곳')
