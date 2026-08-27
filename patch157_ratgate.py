# patch157: 쥐떼 난이도를 '명중률'이 아니라 '참여 인원'이 결정하도록 재설계
#  문제: 체력만으로 난이도를 잡으면 명중률 가정(60%)에 통째로 의존한다.
#        실측 결과가 45%면 3명이 붙어도 못 잡고, 75%면 2명이 잡아버려 의도가 깨진다.
#  해결: 서로 다른 공격자를 기록해, 3명 미만이면 가죽이 단단해 피해 18%만 통하고
#        3명이 모이는 순간 70%로 열린다. 체력은 4,000으로 낮춰 저명중 구간도 구제한다.
#        → 명중률 35~95% 전 구간에서 "1~2명 실패 / 3명 성공"이 성립한다.
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def one(sub):
    idx = [i for i, l in enumerate(lines) if sub in l]
    assert len(idx) == 1, f'{sub!r}: {len(idx)}'
    return idx[0]

# --- 전역: 공격자 명단 ---
i = one('\t\t74: RatTgt')
lines.insert(i + 1, '\t\t75: RatHitters')

# --- 체력 6000 -> 4000 (Max Health 1000% -> 667%) ---
i = one('Set Max Health(Players In Slot(3, Team 2), 1000);')
lines[i] = lines[i].replace('1000)', '667)')

# --- 등장 시 명단 초기화 ---
i = one('Set Player Variable(Players In Slot(3, Team 2), Roll, 0);')
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines.insert(i + 1, ind + 'Set Global Variable(RatHitters, Empty Array);')

# --- [쥐 03] 조건에서 직업 제한 제거 (모든 공격자를 기록해야 하므로) ---
s = next(k for k, l in enumerate(lines) if l.startswith('rule("[쥐 03]'))
c = next(k for k in range(s, len(lines)) if lines[k] == '\tconditions')
e = next(k for k in range(c + 2, len(lines)) if lines[k] == '\t}')
conds = [l for l in lines[c + 2:e] if 'Job)' not in l]
assert len(conds) == len(lines[c + 2:e]) - 2, (len(conds), len(lines[c + 2:e]))
lines[c + 2:e] = conds

# --- [쥐 03] actions 교체: 공격자 기록 + 직업 보정 ---
a = next(k for k in range(s, len(lines)) if lines[k] == '\tactions')
ae = next(k for k in range(a + 2, len(lines)) if lines[k] == '\t}')
BODY = [
 '\t\tIf(Not(Array Contains(Global Variable(RatHitters), Attacker)));',
 '\t\t\tModify Global Variable(RatHitters, Append To Array, Attacker);',
 '\t\t\tIf(Count Of(Global Variable(RatHitters)) == 3);',
 '\t\t\t\tBig Message(All Players(All Teams), Custom String("셋이 붙었다 — 쥐떼의 가죽이 벗겨진다!"));',
 '\t\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(Event Player), 3);',
 '\t\t\tEnd;',
 '\t\tEnd;',
 '\t\tIf(And(Player Variable(Attacker, Job) >= 2, Player Variable(Attacker, Job) <= 3));',
 '\t\t\tDamage(Event Player, Null, Multiply(Event Damage, Player Variable(Attacker, Job) == 3 ? 1 : 0.5));',
 '\t\tEnd;',
]
lines[a + 2:ae] = BODY

# --- 새 규칙 [쥐 05]: 인원에 따라 가죽 두께 조절 ---
r = next(k for k, l in enumerate(lines) if l.startswith('rule("[쥐 04]'))
RULE = '''rule("[쥐 05] 쥐떼의 가죽")
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
\t\tSet Damage Received(Event Player, Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18);
\t\tWait(0.25, Ignore Condition);
\t\tLoop If(And(Global Variable(RatOn) == 1, Is Alive(Event Player)));
\t}
}

'''
lines[r:r] = RULE.split('\n')

out = '\n'.join(lines)
assert out.count('75: RatHitters') == 1
assert out.count('rule("[쥐 05]') == 1
assert out.count('Count Of(Global Variable(RatHitters)) >= 3 ? 70 : 18') == 1
assert out.count('Set Max Health(Players In Slot(3, Team 2), 667);') == 1
assert out.count('rule("') == 131
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch157 ok rules=', out.count('rule("'))
