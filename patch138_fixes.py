# patch138: remove [디버그 01] survey HUD; shortcut targets from surveyed waypoints
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def find_one(sub):
    idxs = [i for i, l in enumerate(lines) if sub in l]
    assert len(idxs) == 1, f'expected 1 match for {sub!r}, got {len(idxs)}'
    return idxs[0]

# ---- Edit 1: delete [디버그 01] rule ----
i0 = find_one('rule("[디버그 01] 경로 측량 좌표")')
i1 = find_one('rule("[세금 01] 징수원 도착")')
assert 15 < i1 - i0 < 25, f'debug rule span unexpected: {i0}..{i1}'
del lines[i0:i1]

# ---- Edit 2: shortcut target = random surveyed waypoint near player ----
CONE_NWP = ('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Position Of(Event Player), '
            'Multiply(Direction From Angles(Add(Horizontal Angle From Direction(Facing Direction Of(Event Player)), '
            'Random Real(-75, 75)), 0), Random Real(11, 19)))));')
j0 = [i for i, l in enumerate(lines) if CONE_NWP in l]
assert len(j0) == 2, f'cone lines: {len(j0)}'
j0 = j0[0]
j_end = find_one('Multiply(Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), Event Player.DelDest)), 13)')
j_end += 1
assert lines[j_end].strip() == 'End;', repr(lines[j_end])
ind = lines[j0][:len(lines[j0]) - len(lines[j0].lstrip('\t'))]
CAND = ('Filtered Array(Append To Array(Global Variable(RaidPath), Global Variable(LocPos)), '
        'And(Distance Between(Current Array Element, Position Of(Event Player)) >= 12, '
        'Distance Between(Current Array Element, Position Of(Event Player)) <= 34))')
new_block = [
    ind + f'If(Count Of({CAND}) >= 1);',
    ind + f'\tSet Player Variable(Event Player, DialTgt, Random Value In Array({CAND}));',
    ind + 'Else;',
    ind + ('\tSet Player Variable(Event Player, DialTgt, Add(Position Of(Event Player), '
           'Multiply(Direction From Angles(Add(Horizontal Angle From Direction(Facing Direction Of(Event Player)), '
           'Random Real(-75, 75)), 0), Random Real(11, 19))));'),
    ind + 'End;',
    ind + ('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Event Player.DialTgt, '
           'Vector(Random Real(-4, 4), 0, Random Real(-4, 4)))));'),
]
lines[j0:j_end + 1] = new_block

out = '\n'.join(lines)
assert out.count('rule("') == 121, out.count('rule("')
assert '측량 좌표' not in out
assert out.count('Append To Array(Global Variable(RaidPath)') == 2
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch138 applied: rules =', out.count('rule("'))
