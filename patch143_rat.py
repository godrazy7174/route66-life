# patch143 (작업 7): 쥐 습격
#  A) 로비: 팀1 8 / 팀2 4 (최대 8인)
#  B) 기존 야수 규칙에서 슬롯 3(쥐) 격리 — 은신/배회/표시/처치/사냥대상/급소/대사냥
#  C) 신규 규칙 4개: 습격 개시 / 이동·약탈 / 직업 보정 피해 / 퇴치·종료
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def one(sub, start=0):
    idxs = [i for i, l in enumerate(lines) if i >= start and sub in l]
    assert len(idxs) == 1, f'{sub!r}: {len(idxs)}'
    return idxs[0]

def add_cond(rule_prefix, cond):
    """해당 규칙의 conditions 블록 마지막에 조건 한 줄 추가"""
    r = next(i for i, l in enumerate(lines) if l.startswith(f'rule("{rule_prefix}'))
    c = next(i for i in range(r, len(lines)) if lines[i] == '\tconditions')
    assert lines[c + 1] == '\t{'
    e = next(i for i in range(c + 2, len(lines)) if lines[i] == '\t}')
    lines.insert(e, '\t\t' + cond)

# ---- A) 로비 ----
i = one('Max Team 1 Players: 12')
lines[i] = lines[i].replace('12', '8')
i = one('Max Team 2 Players: 0')
lines[i] = lines[i].replace('0', '4')

# ---- B) 슬롯 3 격리 ----
for pfx in ('[직업 03] 야수 은신', '[직업 03-3] 야수 배회', '[직업 03-4] 야수 위치 표시'):
    add_cond(pfx, 'Slot Of(Event Player) <= 2;')
add_cond('[직업 03-2] 야수 처치', 'Slot Of(Victim) <= 2;')

# 사냥 대상 선정에서 쥐 제외
i = one('Set Player Variable(Event Player, Target, Filtered Array(All Players(Team 2), And(And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))')
lines[i] = lines[i].replace(
    'Filtered Array(All Players(Team 2), And(And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))',
    'Filtered Array(Filtered Array(All Players(Team 2), Slot Of(Current Array Element) <= 2), And(And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))')

# 급소의 빛: 야수 3마리에만
for old in ('Set Damage Received(All Players(Team 2), 250);',
            'Set Damage Received(All Players(Team 2), 60);'):
    i = one(old)
    lines[i] = lines[i].replace('All Players(Team 2)',
        'Filtered Array(All Players(Team 2), Slot Of(Current Array Element) <= 2)')

# 대사냥 대야수 선정에서 쥐 제외
i = one('Set Global Variable(HuntBeast, First Of(Filtered Array(All Players(Team 2)')
lines[i] = lines[i].replace('First Of(Filtered Array(All Players(Team 2),',
                            'First Of(Filtered Array(Filtered Array(All Players(Team 2), Slot Of(Current Array Element) <= 2),')
lines[i] = lines[i].replace('))));', ')))));', 1) if lines[i].rstrip().endswith('))));') else lines[i]

# ---- 전역 변수 ----
i = one('\t\t70: TownStage')
lines.insert(i + 1, '\t\t71: RatOn')
lines.insert(i + 2, '\t\t72: RatNext')

# ---- C) 신규 규칙 ----
r = next(i for i, l in enumerate(lines) if l.startswith('rule("[야수 06]'))
RULES = '''rule("[쥐 01] 쥐떼의 습격")
{
\tevent
\t{
\t\tOngoing - Global;
\t}

\tconditions
\t{
\t\tGlobal Variable(Ready) == 1;
\t\tGlobal Variable(RatOn) == 0;
\t\tTotal Time Elapsed() >= Global Variable(RatNext);
\t}

\tactions
\t{
\t\tSet Global Variable(RatOn, 1);
\t\tCreate Dummy Bot(Hero(Wrecking Ball), Team 2, 3, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-6, 6), 0, Random Real(-6, 6)))), Vector(1, 0, 0));
\t\tWait(0.5, Ignore Condition);
\t\tSet Max Health(Players In Slot(3, Team 2), 1000);
\t\tSet Move Speed(Players In Slot(3, Team 2), 130);
\t\tSet Damage Received(Players In Slot(3, Team 2), 100);
\t\tBig Message(All Players(All Teams), Custom String("쥐떼가 몰려온다!! 잡화점을 노린다 — 혼자서는 못 막는다"));
\t\tCreate Icon(All Players(All Teams), Players In Slot(3, Team 2), Skull, Visible To and Position, Color(Red), True);
\t\tSet Global Variable(RatFx, Last Created Entity());
\t\tPlay Effect(All Players(All Teams), Debuff Impact Sound, Color(Red), Value In Array(Global Variable(LocPos), 2), 200);
\t\tWait(45, Ignore Condition);
\t\tIf(Global Variable(RatOn) == 1);
\t\t\tSet Global Variable(RatOn, 0);
\t\t\tDestroy Icon(Global Variable(RatFx));
\t\t\tSet Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 15)));
\t\t\tBig Message(All Players(All Teams), Custom String("쥐떼가 육포를 물고 달아났다 — 잡화점이 텅 비었다"));
\t\t\tDestroy Dummy Bot(Team 2, 3);
\t\tEnd;
\t\tSet Global Variable(RatNext, Add(Total Time Elapsed(), Random Real(240, 600)));
\t}
}

rule("[쥐 02] 쥐의 약탈")
{
\tevent
\t{
\t\tOngoing - Each Player;
\t\tTeam 2;
\t\tAll;
\t}

\tconditions
\t{
\t\tSlot Of(Event Player) == 3;
\t\tGlobal Variable(RatOn) == 1;
\t\tIs Alive(Event Player) == True;
\t}

\tactions
\t{
\t\tStart Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)), 1, To World, Replace existing throttle, None);
\t\tIf(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) < 9);
\t\t\tSet Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 2)));
\t\t\tPlay Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1);
\t\tEnd;
\t\tWait(2, Ignore Condition);
\t\tLoop If(And(Global Variable(RatOn) == 1, Is Alive(Event Player)));
\t}
}

rule("[쥐 03] 사냥꾼의 이빨")
{
\tevent
\t{
\t\tPlayer Took Damage;
\t\tTeam 2;
\t\tAll;
\t}

\tconditions
\t{
\t\tSlot Of(Event Player) == 3;
\t\tGlobal Variable(RatOn) == 1;
\t\tEntity Exists(Attacker) == True;
\t\tIs Dummy Bot(Attacker) == False;
\t\tPlayer Variable(Attacker, Job) >= 2;
\t\tPlayer Variable(Attacker, Job) <= 3;
\t}

\tactions
\t{
\t\tDamage(Event Player, Null, Multiply(Event Damage, Player Variable(Attacker, Job) == 3 ? 1 : 0.5));
\t}
}

rule("[쥐 04] 쥐떼 퇴치")
{
\tevent
\t{
\t\tPlayer Died;
\t\tTeam 2;
\t\tAll;
\t}

\tconditions
\t{
\t\tSlot Of(Victim) == 3;
\t\tGlobal Variable(RatOn) == 1;
\t}

\tactions
\t{
\t\tSet Global Variable(RatOn, 0);
\t\tDestroy Icon(Global Variable(RatFx));
\t\tIf(And(Entity Exists(Attacker), Is Dummy Bot(Attacker) == False));
\t\t\tModify Player Variable(Attacker, Money, Add, 400);
\t\t\tModify Player Variable(Attacker, Earned, Add, 400);
\t\t\tSet Player Variable(Attacker, Fame, Min(100, Add(Player Variable(Attacker, Fame), 8)));
\t\t\tBig Message(All Players(All Teams), Custom String("{0} — 쥐떼의 우두머리를 잡았다!! (+$400 · 명성 +8)", Attacker));
\t\tElse;
\t\t\tBig Message(All Players(All Teams), Custom String("쥐떼가 물러갔다"));
\t\tEnd;
\t\tPlay Effect(All Players(All Teams), Good Explosion, Color(Lime Green), Position Of(Victim), 3);
\t\tPlay Effect(All Players(All Teams), Buff Explosion Sound, Color(Lime Green), Position Of(Victim), 200);
\t\tDestroy Dummy Bot(Team 2, 3);
\t}
}

'''
lines[r:r] = RULES.split('\n')

# RatFx 전역
i = one('\t\t72: RatNext')
lines.insert(i + 1, '\t\t73: RatFx')

out = '\n'.join(lines)
assert out.count('rule("') == 129, out.count('rule("')
assert out.count('Max Team 1 Players: 8') == 1
assert out.count('Max Team 2 Players: 4') == 1
assert out.count('Slot Of(Event Player) <= 2;') == 3
assert out.count('Slot Of(Victim) <= 2;') == 1
assert out.count('Hero(Wrecking Ball)') == 1
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch143 ok rules=', out.count('rule("'))
