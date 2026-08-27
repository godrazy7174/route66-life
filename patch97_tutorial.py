# -*- coding: utf-8 -*-
"""튜토리얼을 18쪽으로 확장하고 모든 플레이어 영웅에게 무한 탄창을 적용한다."""
import io
import os
import tempfile

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
    return ''.join(T * depth + line + N for line in lines)


# ── 1. 튜토리얼 제목과 본문 ──────────────────────────────────────
sub('Custom String("사건"), Custom String("긴 여정")',
    'Custom String("사건"), Custom String("사흘의 리듬"), Custom String("두 갈래 큰 길"), Custom String("긴 여정")', 1)

BODY14 = ('밤마다 금고 마차가 어둠 속 어딘가에 멈춘다 — 먼저 터는 자가 임자, 대신 악명이 붙는다.' + RN
    + '사흘에 한 번 저녁이면 열차가 선다 — 대장간의 화약 $200이 금고를 연다.' + RN
    + '그다음 날 아침엔 대야수의 흔적이 나타난다 — 함께 쫓고, 기여한 만큼 나눈다.')
BODY15 = ('명성 30이면 목장에서 소를 치고, 악명 30이면 뒷골목에서 밀주를 담근다.' + RN
    + '은신처의 밀수, 정거장의 금괴 호송 — 나르는 동안 질주할 수 없고, 죽거나 털리면 끝이다.' + RN
    + '마을이 되살아나면(재건 3단계) 밤의 은행이 간 큰 자를 기다린다.')
sub('소문은 여기서 듣는다."), Custom String("돈이 쌓이면',
    '소문은 여기서 듣는다."), Custom String("' + BODY14 + '"), Custom String("' + BODY15
    + '"), Custom String("돈이 쌓이면', 1)

sub('목값 $300이면 전단이 돌고, $800이면 마을이 문을 걸어 잠근다.")',
    '목값 $300이면 전단이 돌고, $800이면 마을이 문을 걸어 잠근다.' + RN
    + '습격의 장물은 자루에 담긴다 — 은신처에서 정산하고, 진 채로 죽으면 흘린다.")', 1)

# ── 2. 튜토리얼 쪽수·순회·카메라 ────────────────────────────────
sub('Min(15, Event Player.TutStep)', 'Min(17, Event Player.TutStep)', 2)
sub('({1}/16)', '({1}/18)', 1)
sub('For Player Variable(Event Player, TutStep, 0, 16, 1);',
    'For Player Variable(Event Player, TutStep, 0, 18, 1);', 1)
CAMERA_OLD = 'Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 9, 9)'
CAMERA_NEW = 'Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 11, 12, 9, 9)'
CAMERA_TAIL = ('Value In Array(Global Variable(LocPos), Value In Array(' + CAMERA_OLD
    + ', Event Player.TutStep)), 0);')
CAMERA_MARK = 'Value In Array(Global Variable(LocPos), Value In Array(__PATCH97_CAMERA_TAIL__, Event Player.TutStep)), 0);'
assert s.count(CAMERA_TAIL) == 1, (CAMERA_TAIL[:80], s.count(CAMERA_TAIL))
s = s.replace(CAMERA_TAIL, CAMERA_MARK, 1)
sub(CAMERA_OLD, CAMERA_NEW, 2)
assert s.count(CAMERA_MARK) == 1, (CAMERA_MARK[:80], s.count(CAMERA_MARK))
s = s.replace(CAMERA_MARK, CAMERA_TAIL, 1)

# ── 3. 모든 플레이어 영웅 무한 탄창 ──────────────────────────────
AMMO_RULE = ('rule("[코어 18] 무한 탄창")' + N + '{' + N
    + T + 'event' + N + T + '{' + N
    + block(2, 'Ongoing - Each Player;', 'All;', 'All;')
    + T + '}' + N + N
    + T + 'conditions' + N + T + '{' + N
    + block(2, 'Is Dummy Bot(Event Player) == False;',
               'Event Player.Init == 1;',
               'Is Alive(Event Player) == True;',
               'Ammo(Event Player, 0) < Max Ammo(Event Player, 0);')
    + T + '}' + N + N
    + T + 'actions' + N + T + '{' + N
    + block(2, 'Set Ammo(Event Player, 0, Max Ammo(Event Player, 0));',
               'Wait(0.25, Ignore Condition);',
               'Loop If(Ammo(Event Player, 0) < Max Ammo(Event Player, 0));')
    + T + '}' + N + '}' + N + N)
sub('rule("[코어 07] 궁극기 게이지 상시 제거")',
    AMMO_RULE + 'rule("[코어 07] 궁극기 게이지 상시 제거")', 1)

# 같은 디렉터리의 임시 파일을 완성한 뒤 원자적으로 교체한다.
target = os.path.abspath(P)
fd, temp_path = tempfile.mkstemp(prefix='.patch97_', suffix='.tmp', dir=os.path.dirname(target))
try:
    with os.fdopen(fd, 'w', encoding='utf-8', newline=N) as out:
        out.write(s)
    os.replace(temp_path, target)
except BaseException:
    try:
        os.remove(temp_path)
    except OSError:
        pass
    raise

print('튜토리얼 18쪽 확장 및 무한 탄창 적용')
