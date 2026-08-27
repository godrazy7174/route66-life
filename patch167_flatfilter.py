# patch167: 샛길 좌표가 (0,0,0)으로 나오는 문제
#  진단 출력 '[진단] 좌표 0/0 · 거리 0' = 후보 배열이 비어 Random Value In Array가 0을 반환했다.
#  원인: Filtered Array를 중첩하면 안팎의 Current Array Element가 충돌해 결과가 비어 버린다.
#  해결: 중첩을 없애고 조건을 하나의 And로 합친다. 그리고 3단 폴백으로 절대 비지 않게 한다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

POOL = 'Append To Array(Global Variable(RaidPath), Global Variable(LocPos))'
D_SPAWN = 'Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22'
D_NEAR = ('And(Distance Between(Current Array Element, Position Of(Event Player)) >= 11, '
          'Distance Between(Current Array Element, Position Of(Event Player)) <= 55)')
NEAR = f'Filtered Array({POOL}, And({D_SPAWN}, {D_NEAR}))'      # 단일 필터
SAFE = f'Filtered Array({POOL}, {D_SPAWN})'                      # 단일 필터

s = next(i for i, l in enumerate(lines) if l.strip().startswith('If(Count Of(Filtered Array(Filtered Array('))
assert 'DialTgt' in lines[s + 1]
e = next(i for i in range(s, len(lines)) if lines[i].strip() == 'End;')
ind = lines[s][:len(lines[s]) - len(lines[s].lstrip('\t'))]

lines[s:e + 1] = [
    ind + f'If(Count Of({NEAR}) >= 1);',
    ind + f'\tSet Player Variable(Event Player, DialTgt, Random Value In Array({NEAR}));',
    ind + f'Else If(Count Of({SAFE}) >= 1);',
    ind + f'\tSet Player Variable(Event Player, DialTgt, Random Value In Array({SAFE}));',
    ind + 'Else;',
    ind + '\tSet Player Variable(Event Player, DialTgt, Random Value In Array(Global Variable(RaidPath)));',
    ind + 'End;',
]

# 진단: 후보 개수까지 보이도록 교체
d = next(i for i, l in enumerate(lines) if '[진단]' in l)
ind2 = lines[d][:len(lines[d]) - len(lines[d].lstrip('\t'))]
lines[d] = (ind2 + 'Set Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[진단] 좌표 {0} · 거리 {1} · 후보 {2}", '
            'Custom String("{0}/{1}", Round To Integer(X Component Of(Event Player.DialTgt), To Nearest), '
            'Round To Integer(Z Component Of(Event Player.DialTgt), To Nearest)), '
            'Round To Integer(Distance Between(Event Player.DialTgt, Position Of(Event Player)), To Nearest), '
            f'Custom String("{{0}}/{{1}}", Count Of({NEAR}), Count Of({POOL}))));')

out = '\n'.join(lines)
assert 'Filtered Array(Filtered Array(' not in out.split('rule("[파발 02]')[1].split('rule("')[0]
assert out.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch167 ok')
