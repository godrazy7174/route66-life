# patch137: courier rework
# 1) valuable cargo = random 25% on accept (no server-wide announce, no re-accept)
# 2) new rule [파발 03] shadow bandit chaser while HasParcel==2 (borrows Escort* vars)
#    -> requires mutual exclusion gates: parcel accept blocks Escort, escort accept blocks HasParcel
# 3) shortcut (샛길) target: forward cone + retries instead of 360-degree NWP snap
import io, sys

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def find_one(sub):
    idxs = [i for i, l in enumerate(lines) if sub in l]
    assert len(idxs) == 1, f'expected 1 match for {sub!r}, got {len(idxs)}'
    return idxs[0]

def indent_of(i):
    l = lines[i]
    return l[:len(l) - len(l.lstrip('\t'))]

# ---- Edit 1: replace re-accept conversion branches with gates ----
i0 = find_one('Else If(Event Player.HasParcel == 2);')
cand = [i for i in range(i0 + 1, i0 + 7)
        if 'Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 3);' in lines[i]]
assert len(cand) == 1, f'block shape unexpected near {i0}: {cand}'
i_end = cand[0]
ind = indent_of(i0)
new_block = [
    ind + 'Else If(Event Player.Escort == 1);',
    ind + '\tSmall Message(Event Player, Custom String("금괴를 나르는 손으로 화물까지는 못 든다"));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
    ind + 'Else If(Event Player.HasParcel >= 1);',
    ind + '\tSmall Message(Event Player, Custom String("이미 화물을 지고 있다 — 배달부터 끝내라"));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
]
lines[i0:i_end + 1] = new_block

# ---- Edit 2+3: hint line replacement + random valuable roll ----
ih = find_one('한 번 더 수주하면 값진 화물')
ind = indent_of(ih)
lines[ih:ih + 1] = [
    ind + 'Small Message(Event Player, Custom String("노란 화살표를 따라가라 · 이따금 값진 화물(보수 2.5배)이 걸린다"));',
    ind + 'If(Random Integer(1, 100) <= 25);',
    ind + '\tSet Player Variable(Event Player, HasParcel, 2);',
    ind + '\tBig Message(Event Player, Custom String("값진 화물이다! 보수 2.5배 — 어둠 속에서 그림자가 냄새를 맡았다"));',
    ind + '\tPlay Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 2);',
    ind + 'End;',
]

# ---- Edit 4: settlement message no longer server-wide ----
i4 = find_one('값진 화물을 지켜냈다!')
ind = indent_of(i4)
lines[i4] = ind + 'Big Message(Event Player, Custom String("값진 화물을 지켜냈다! +$ {0}", Event Player.RunPay));'

# ---- Edit 5: escort accept blocks HasParcel (mutual exclusion for Escort* borrow) ----
i5 = find_one('Else If(Event Player.Bounty > 0);')
ind = indent_of(i5)
lines[i5:i5] = [
    ind + 'Else If(Event Player.HasParcel >= 1);',
    ind + '\tSmall Message(Event Player, Custom String("화물을 진 채로 금괴까지는 못 맡는다"));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
]

# ---- Edit 6: shortcut target = forward cone + retries ----
i6 = find_one('Multiply(Direction From Angles(Random Real(0, 360), 0), 17)')
ind = indent_of(i6)
CONE = ('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Position Of(Event Player), '
        'Multiply(Direction From Angles(Add(Horizontal Angle From Direction(Facing Direction Of(Event Player)), '
        'Random Real(-75, 75)), 0), Random Real(11, 19)))));')
BAD = ('If(Or(Distance Between(Event Player.DialTgt, Position Of(Event Player)) < 7, '
       'Distance Between(Event Player.DialTgt, Position Of(Event Player)) > 26));')
FALLBACK = ('Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Position Of(Event Player), '
            'Multiply(Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), '
            'Event Player.DelDest)), 13))));')
lines[i6:i6 + 1] = [
    ind + CONE,
    ind + BAD,
    ind + '\t' + CONE,
    ind + 'End;',
    ind + BAD,
    ind + '\t' + FALLBACK,
    ind + 'End;',
]

# ---- Edit 7: new rule [파발 03] shadow bandit ----
i7 = find_one('rule("[목동 02] 날뛰는 소")')
R = '''rule("[파발 03] 그림자 강도")
{
\tevent
\t{
\t\tOngoing - Each Player;
\t\tAll;
\t\tAll;
\t}

\tconditions
\t{
\t\tIs Dummy Bot(Event Player) == False;
\t\tEvent Player.Init == 1;
\t\tEvent Player.HasParcel == 2;
\t\tIs Alive(Event Player) == True;
\t}

\tactions
\t{
\t\tWait(Random Real(8, 14), Ignore Condition);
\t\tIf(And(And(Event Player.HasParcel == 2, Event Player.Busy == 0), Is Alive(Event Player)));
\t\t\tSet Player Variable(Event Player, EscortPay, 0);
\t\t\tSet Player Variable(Event Player, EscortPos, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Facing Direction Of(Event Player), -22))));
\t\t\tDestroy Effect(Event Player.EscortFx);
\t\t\tCreate Effect(All Players(All Teams), Sphere, Color(Red), Event Player.EscortPos, 0.9, Visible To Position Radius and Color);
\t\t\tSet Player Variable(Event Player, EscortFx, Last Created Entity());
\t\t\tDestroy Icon(Event Player.EscortIco);
\t\t\tCreate Icon(All Players(All Teams), Add(Event Player.EscortPos, Vector(0, 2.2, 0)), Skull, Visible To and Position, Color(Red), True);
\t\t\tSet Player Variable(Event Player, EscortIco, Last Created Entity());
\t\t\tBig Message(Event Player, Custom String("그림자 강도가 따라붙었다 — 쏴서 떨쳐내라! (붉은 그림자)"));
\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 80);
\t\t\tWhile(And(And(Event Player.HasParcel == 2, Is Alive(Event Player)), Event Player.EscortPay < 3));
\t\t\t\tSet Player Variable(Event Player, EscortPos, Add(Event Player.EscortPos, Multiply(Direction Towards(Event Player.EscortPos, Position Of(Event Player)), 1.7)));
\t\t\t\tIf(And(Is Button Held(Event Player, Button(Primary Fire)), And(Distance Between(Position Of(Event Player), Event Player.EscortPos) < 30, Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Event Player.EscortPos)) >= 0.96)));
\t\t\t\t\tModify Player Variable(Event Player, EscortPay, Add, 1);
\t\t\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Orange), Event Player.EscortPos, 40);
\t\t\t\tEnd;
\t\t\t\tIf(Distance Between(Event Player.EscortPos, Position Of(Event Player)) < 2.5);
\t\t\t\t\tSet Player Variable(Event Player, EscortPay, 99);
\t\t\t\t\tDamage(Event Player, Null, 40);
\t\t\t\t\tSmall Message(Event Player, Custom String("그림자 강도에게 물어뜯겼다 — 놈이 어둠으로 사라졌다"));
\t\t\t\t\tPlay Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1.5);
\t\t\t\tEnd;
\t\t\t\tWait(0.25, Ignore Condition);
\t\t\tEnd;
\t\t\tDestroy Effect(Event Player.EscortFx);
\t\t\tDestroy Icon(Event Player.EscortIco);
\t\t\tIf(And(Event Player.EscortPay >= 3, Event Player.EscortPay < 99));
\t\t\t\tSmall Message(Event Player, Custom String("그림자 강도를 쫓아냈다!"));
\t\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Lime Green), Position Of(Event Player), 60);
\t\t\tEnd;
\t\tEnd;
\t\tWait(Random Real(16, 24), Ignore Condition);
\t\tLoop If(Event Player.HasParcel == 2);
\t}
}
'''
lines[i7:i7] = R.split('\n')

out = '\n'.join(lines)
assert out.count('rule("') == 122, out.count('rule("')
assert '한 번 더 수주하면' not in out
assert out.count('그림자 강도') == 4
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch137 applied: rules =', out.count('rule("'))
