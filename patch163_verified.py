# patch163: 위치를 '계산'하지 말고 '검증된 좌표'만 쓴다
#  지금까지의 실패 원인:
#    - 건물/경로 좌표에 수평 오프셋을 주면 협곡에서는 허공이나 벽 속이 된다
#    - 그걸 Nearest Walkable Position으로 보내면 (a) 전부 같은 통로로 스냅되거나
#      (b) 벽 사이 좁은 틈을 '걸을 수 있는 곳'으로 골라 도달 불가능한 자리에 놓인다
#    - 스폰 회피도 '밀어내기'라 밀려난 지점이 또 벽 속이 된다
#  해결: 오프셋과 NWP를 전부 제거하고, 사용자가 직접 걸어 찍은 역마차 경로 13개와
#        건물 13곳의 좌표를 그대로 쓴다. 스폰 근처는 밀어내지 말고 후보에서 제외한다.
import io, re

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

POOL = 'Append To Array(Global Variable(RaidPath), Global Variable(LocPos))'
SAFE = f'Filtered Array({POOL}, Distance Between(Current Array Element, Global Variable(SpawnPos)) >= 22)'
NEAR = (f'Filtered Array({SAFE}, And(Distance Between(Current Array Element, Position Of(Event Player)) >= 11, '
        'Distance Between(Current Array Element, Position Of(Event Player)) <= 55))')

# ---------- 1) 샛길: 후보 선정 전체를 교체 ----------
s = next(i for i, l in enumerate(lines) if l.strip() == 'Set Player Variable(Event Player, Roll, Random Integer(0, 11));')
e = next(i for i in range(s, len(lines)) if 'Global Variable(SpawnPos), Multiply(Direction From Angles' in lines[i])
e = next(i for i in range(e, len(lines)) if lines[i].strip() == 'End;')
ind = lines[s][:len(lines[s]) - len(lines[s].lstrip('\t'))]
lines[s:e + 1] = [
    ind + f'If(Count Of({NEAR}) >= 1);',
    ind + f'\tSet Player Variable(Event Player, DialTgt, Random Value In Array({NEAR}));',
    ind + 'Else;',
    ind + f'\tSet Player Variable(Event Player, DialTgt, Random Value In Array({SAFE}));',
    ind + 'End;',
]

# ---------- 2) 진단: 알림 줄로 (Small Message가 안 보인다는 보고) ----------
d = next(i for i, l in enumerate(lines) if '[진단]' in l)
ind2 = lines[d][:len(lines[d]) - len(lines[d].lstrip('\t'))]
lines[d] = (ind2 + 'Set Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("[진단] 좌표 {0} · 거리 {1}", '
            'Custom String("{0}/{1}", Round To Integer(X Component Of(Event Player.DialTgt), To Nearest), '
            'Round To Integer(Z Component Of(Event Player.DialTgt), To Nearest)), '
            'Round To Integer(Distance Between(Event Player.DialTgt, Position Of(Event Player)), To Nearest)));')
lines.insert(d + 1, ind2 + 'Set Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 6));')

out = '\n'.join(lines)
assert out.count('rule("') == 131
assert 'Direction From Angles(Random Real(-180, 180), 0), Random Real(30, 55)' in out   # 다른 6곳은 아직 남아 있음
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch163 ok (shortcut rebuilt on verified coordinates)')
