# -*- coding: utf-8 -*-
"""배치 좌표를 Filtered Array / SpawnPos 의존에서 완전히 떼어낸다.

증상: 샛길·밀수·보물상자·금고마차·금괴호송이 전부 고정 위치 또는 (0,0,0).
공통점: 전부 Filtered Array(..., Distance Between(..., Global Variable(SpawnPos)) >= 22).
       이 필터가 빈 배열을 돌려주면 Random Value In Array(빈 배열) = 0 -> 좌표 (0,0,0).
       금괴 호송은 Current Array Element를 '인덱스'로 쓰는 형태인데도 같이 망가졌으므로
       범인은 필터 문법이 아니라 SpawnPos 쪽일 가능성이 크다. 어느 쪽이든 둘 다 제거한다.

해법: 검증된 28개 좌표(RaidPath 13 + LocPos 15)를 SpotPos에 한 번 담아두고,
      인덱스 순회(While)로 거리 조건을 만족하는 지점을 고른다.
      실패해도 반드시 SpotPos의 실제 원소를 돌려주므로 (0,0,0)이 나올 수 없다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()
orig = src


def once(old, new, tag):
    global src
    n = src.count(old)
    assert n == 1, '%s: %d건 (1건이어야 함)' % (tag, n)
    src = src.replace(old, new)
    print('  OK %s' % tag)


# 1. 전역 변수 선언
once('\t\t25: DailyGoal\n', '\t\t25: DailyGoal\n\t\t26: SpotPos\n', '전역 26 SpotPos')
once('\t\t75: RatHitters\n',
     '\t\t75: RatHitters\n'
     '\t\t76: PickPos\n\t\t77: PickRef\n\t\t78: PickMin\n'
     '\t\t79: PickMax\n\t\t80: PickIdx\n\t\t81: PickN\n',
     '전역 76~81 Pick*')

# 2. 서브루틴 선언
once('\t9: BecomeJob\n', '\t9: BecomeJob\n\t10: PickSpot\n', '서브루틴 10 PickSpot')

# 3. SpotPos 구축 (LocPos 보정이 모두 끝난 직후)
anchor = ('\t\tSet Global Variable(TrainPos, Nearest Walkable Position(Multiply(Add('
          'Value In Array(Global Variable(LocPos), 11), Value In Array(Global Variable(LocPos), 6)), 0.5)));\n')
once(anchor,
     anchor + '\t\tSet Global Variable(SpotPos, Append To Array(Global Variable(RaidPath), Global Variable(LocPos)));\n',
     'SpotPos 구축')

# 4. PickSpot 서브루틴 룰
PICKRULE = (
    'rule("[좌표 00] PickSpot — 검증된 지점 뽑기")\n'
    '{\n'
    '\tevent\n'
    '\t{\n'
    '\t\tSubroutine;\n'
    '\t\tPickSpot;\n'
    '\t}\n'
    '\n'
    '\tactions\n'
    '\t{\n'
    '\t\tSet Global Variable(PickIdx, Random Integer(0, Subtract(Count Of(Global Variable(SpotPos)), 1)));\n'
    '\t\tSet Global Variable(PickPos, Value In Array(Global Variable(SpotPos), Global Variable(PickIdx)));\n'
    '\t\tSet Global Variable(PickN, 0);\n'
    '\t\tWhile(And(Global Variable(PickN) < Count Of(Global Variable(SpotPos)), '
    'Or(Distance Between(Global Variable(PickPos), Global Variable(PickRef)) < Global Variable(PickMin), '
    'Distance Between(Global Variable(PickPos), Global Variable(PickRef)) > Global Variable(PickMax))));\n'
    '\t\t\tSet Global Variable(PickIdx, Modulo(Add(Global Variable(PickIdx), 1), Count Of(Global Variable(SpotPos))));\n'
    '\t\t\tSet Global Variable(PickPos, Value In Array(Global Variable(SpotPos), Global Variable(PickIdx)));\n'
    '\t\t\tModify Global Variable(PickN, Add, 1);\n'
    '\t\tEnd;\n'
    '\t}\n'
    '}\n'
    '\n')
once('rule("[코어 04] SetupPlayer")', PICKRULE + 'rule("[코어 04] SetupPlayer")', 'PickSpot 룰 삽입')

# 5. 샛길 — 3단 If 전체를 PickSpot 호출로 교체
lines = src.split('\n')
i = next(k for k, L in enumerate(lines)
         if L.strip().startswith('If(Count Of(Filtered Array(Append To Array(Global Variable(RaidPath)'))
assert lines[i + 6].strip() == 'End;', '샛길 블록 경계 불일치: %r' % lines[i + 6]
tab = '\t' * (len(lines[i]) - len(lines[i].lstrip('\t')))
lines[i:i + 7] = [
    tab + 'Set Global Variable(PickRef, Position Of(Event Player));',
    tab + 'Set Global Variable(PickMin, 12);',
    tab + 'Set Global Variable(PickMax, 40);',
    tab + 'Call Subroutine(PickSpot);',
    tab + 'Set Player Variable(Event Player, DialTgt, Global Variable(PickPos));',
]
# 진단 줄 2개 제거 (원래 안내 문구가 다시 살아난다)
before = len(lines)
lines = [L for L in lines if '[진단] 좌표 {0}' not in L
         and 'Set Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 6));' not in L]
assert before - len(lines) == 2, '진단 줄 제거 %d개 (2개여야 함)' % (before - len(lines))
src = '\n'.join(lines)
print('  OK 샛길 3단 If -> PickSpot, 진단 줄 제거')

# 6. 금괴 호송
old = ('\t\t\t\t\tSet Player Variable(Event Player, EscortPos, Value In Array(Global Variable(LocPos), '
       'Random Value In Array(Array Slice(Sorted Array(Filtered Array(Array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12), '
       'Distance Between(Value In Array(Global Variable(LocPos), Current Array Element), Global Variable(SpawnPos)) >= 22), '
       'Distance Between(Value In Array(Global Variable(LocPos), Current Array Element), '
       'Value In Array(Global Variable(LocPos), 11))), 4, 8))));\n')
new = ('\t\t\t\t\tSet Global Variable(PickRef, Value In Array(Global Variable(LocPos), 11));\n'
       '\t\t\t\t\tSet Global Variable(PickMin, 35);\n'
       '\t\t\t\t\tSet Global Variable(PickMax, 90);\n'
       '\t\t\t\t\tCall Subroutine(PickSpot);\n'
       '\t\t\t\t\tSet Player Variable(Event Player, EscortPos, Global Variable(PickPos));\n')
once(old, new, '금괴 호송 목적지')

# 7. 밀수
old = ('\t\t\t\tSet Player Variable(Event Player, SmugglePos, Random Value In Array(Filtered Array('
       'Append To Array(Global Variable(RaidPath), Global Variable(LocPos)), '
       'Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)));\n')
new = ('\t\t\t\tSet Global Variable(PickRef, Value In Array(Global Variable(LocPos), 8));\n'
       '\t\t\t\tSet Global Variable(PickMin, 40);\n'
       '\t\t\t\tSet Global Variable(PickMax, 999);\n'
       '\t\t\t\tCall Subroutine(PickSpot);\n'
       '\t\t\t\tSet Player Variable(Event Player, SmugglePos, Global Variable(PickPos));\n')
once(old, new, '밀수 접선지')

# 8. 남은 무제약 배치 (사냥 흔적 2 · 금고 마차 · 보물 상자)
old = ('Random Value In Array(Filtered Array(Append To Array(Global Variable(RaidPath), '
       'Global Variable(LocPos)), Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22))')
n = src.count(old)
assert n == 4, '무제약 배치 %d건 (4건이어야 함)' % n
src = src.replace(old, 'Random Value In Array(Global Variable(SpotPos))')
print('  OK 사냥 흔적 2 · 금고 마차 · 보물 상자 (4건)')

assert src != orig
io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('\n적용 완료: %s' % P)
