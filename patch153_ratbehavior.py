# patch153 (전수조사 #12): 쥐떼 행동을 사용자가 고른 (라) '사람을 공격한다'로 교정
#  - 가장 가까운 플레이어를 추격하고 근접하면 물어뜯는다
#  - 주변에 사람이 없을 때만 잡화점으로 가 육포를 갉는다 (공동 동기 유지)
#  - 지형에 낀 채 시간만 흘리지 않도록 12초마다 위치 점검 후 복귀
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# 전역 RatTgt
i = next(k for k, l in enumerate(lines) if l.strip() == '73: RatFx')
lines.insert(i + 1, '\t\t74: RatTgt')

# [쥐 02] actions 교체
s = next(k for k, l in enumerate(lines) if l.startswith('rule("[쥐 02]'))
d = 0
for k in range(s, len(lines)):
    d += lines[k].count('{') - lines[k].count('}')
    if d == 0 and k > s:
        e = k
        break
a = next(k for k in range(s, e) if lines[k] == '\tactions')
assert lines[a + 1] == '\t{' and lines[e - 1] == '\t}'

BODY = '''\t\tSet Global Variable(RatTgt, First Of(Sorted Array(Filtered Array(All Players(Team 1), And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1)), Distance Between(Position Of(Current Array Element), Position Of(Event Player)))));
\t\tIf(And(Entity Exists(Global Variable(RatTgt)), Distance Between(Position Of(Global Variable(RatTgt)), Position Of(Event Player)) < 40));
\t\t\tStart Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Position Of(Global Variable(RatTgt))), 1, To World, Replace existing throttle, None);
\t\t\tIf(Distance Between(Position Of(Event Player), Position Of(Global Variable(RatTgt))) < 3.5);
\t\t\t\tDamage(Global Variable(RatTgt), Event Player, 20);
\t\t\t\tPlay Effect(All Players(All Teams), Bad Explosion, Color(Red), Position Of(Event Player), 1.5);
\t\t\tEnd;
\t\tElse;
\t\t\tStart Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)), 1, To World, Replace existing throttle, None);
\t\tEnd;
\t\tIf(Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) < 9);
\t\t\tSet Global Variable(JerkyStock, Max(0, Subtract(Global Variable(JerkyStock), 2)));
\t\t\tPlay Effect(All Players(All Teams), Bad Explosion, Color(Orange), Position Of(Event Player), 1));
\t\tEnd;
\t\tModify Player Variable(Event Player, Roll, Add, 1);
\t\tIf(And(Modulo(Event Player.Roll, 12) == 0, Distance Between(Position Of(Event Player), Value In Array(Global Variable(LocPos), 2)) > 34));
\t\t\tTeleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 2), Vector(Random Real(-5, 5), 0, Random Real(-5, 5)))));
\t\tEnd;
\t\tWait(1, Ignore Condition);
\t\tLoop If(And(Global Variable(RatOn) == 1, Is Alive(Event Player)));'''.replace('Position Of(Event Player), 1));', 'Position Of(Event Player), 1);')

lines[a + 2:e - 1] = BODY.split('\n')

# [쥐 01] 생성 시 카운터 초기화
j = next(k for k, l in enumerate(lines) if 'Set Move Speed(Players In Slot(3, Team 2), 130);' in l)
ind = lines[j][:len(lines[j]) - len(lines[j].lstrip('\t'))]
lines.insert(j + 1, ind + 'Set Player Variable(Players In Slot(3, Team 2), Roll, 0);')

out = '\n'.join(lines)
assert out.count('74: RatTgt') == 1
assert out.count('Damage(Global Variable(RatTgt), Event Player, 20);') == 1
assert out.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch153 ok')
