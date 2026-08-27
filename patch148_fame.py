# patch148: 명성 감소 경로
#  ① 악명이 오르면 그 절반만큼 명성이 깎인다 — 개별 16곳 대신 단일 감시 규칙으로 (LastNoto 변수 1개)
#  ② 아침마다 명성 -1 (악명 -2는 이미 존재)
#  ③ 세금 체납은 악명 +10을 주므로 ①에 자동 포함 — 별도 작업 없음
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def one(sub):
    idxs = [i for i, l in enumerate(lines) if sub in l]
    assert len(idxs) == 1, f'{sub!r}: {len(idxs)}'
    return idxs[0]

# ---- 변수 선언 (빈 슬롯 15 재사용) ----
i = one('\t\t14: Contrib')
lines.insert(i + 1, '\t\t15: LastNoto')

# ---- ② 아침 정산: 명성 -1 (악명 -2 줄 옆에) ----
i = one('Set Player Variable(Event Player, Noto, Max(0, Subtract(Event Player.Noto, 2)));')
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines.insert(i + 1, ind + 'Set Player Variable(Event Player, Fame, Max(0, Subtract(Event Player.Fame, 1)));')

# ---- 세이브 복원 시 LastNoto 동기화 (복원 직후 명성이 깎이지 않도록) ----
i = one('Set Player Variable(Event Player, Noto, Multiply(Modulo(Event Player.Amt, 10), 10));')
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines.insert(i + 1, ind + 'Set Player Variable(Event Player, LastNoto, Event Player.Noto);')

# ---- ① 감시 규칙 ----
r = next(i for i, l in enumerate(lines) if l.startswith('rule("[월드 05]'))
RULE = '''rule("[평판 01] 죄는 이름을 갉는다")
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
\t\tEvent Player.Noto != Event Player.LastNoto;
\t}

\tactions
\t{
\t\tIf(Event Player.Noto > Event Player.LastNoto);
\t\t\tSet Player Variable(Event Player, Amt, Round To Integer(Divide(Subtract(Event Player.Noto, Event Player.LastNoto), 2), Up));
\t\t\tSet Player Variable(Event Player, Fame, Max(0, Subtract(Event Player.Fame, Event Player.Amt)));
\t\t\tIf(Event Player.Amt >= 3);
\t\t\t\tSmall Message(Event Player, Custom String("소문이 퍼진다 — 명성 {0} (-{1})", Event Player.Fame, Event Player.Amt));
\t\t\tEnd;
\t\tEnd;
\t\tSet Player Variable(Event Player, LastNoto, Event Player.Noto);
\t}
}

'''
lines[r:r] = RULE.split('\n')

out = '\n'.join(lines)
assert out.count('15: LastNoto') == 1
assert out.count('rule("[평판 01]') == 1
assert out.count('Set Player Variable(Event Player, Fame, Max(0, Subtract(Event Player.Fame, 1)));') == 1
assert out.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch148 ok rules=', out.count('rule("'))
