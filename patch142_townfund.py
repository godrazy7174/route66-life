# patch142 (작업 6): 재건 + 부흥 기금 -> "마을 금고" 하나로 통합 (갹출제 8단계)
#  - 전역 TownStage(70) 추가, 개인 Contrib(14, 회수 슬롯 재사용) 추가
#  - 안내소 재건 버튼($60,000 개인 부담) -> 마을 금고 $1,000 갹출로 교체
#  - 정거장 기금 버튼도 같은 금고/문구로 통일 (Contrib 기록)
#  - 새 규칙 [금고 01]: 누적액이 단계 목표를 넘으면 건물 완성 + 기여자에게 Rebuild 부여
#  - 기존 [기금 01] 조건을 TownStage 기반으로 (특전·이펙트 본문은 그대로 보존)
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

GOALS = 'Array(4000, 11000, 22000, 38000, 61000, 93000, 138000, 198000)'
NAMES = ('Array(Custom String("마을 우물"), Custom String("전신국"), Custom String("길손의 쉼터"), '
         'Custom String("마을 은행"), Custom String("역마차 급행로"), Custom String("오페라 극장"), '
         'Custom String("국도 대축제"), Custom String("기차역"))')
RB = 'Array(0, 1, 2, 0, 3, 0, 4, 0, 5)'   # TownStage -> Rebuild 값 (0 = 해당 없음)

def find_one(sub):
    idxs = [i for i, l in enumerate(lines) if sub in l]
    assert len(idxs) == 1, f'{sub!r}: {len(idxs)}'
    return idxs[0]

# ---- 1) 변수 선언 ----
i = find_one('\t\t69: TickerEnd')
lines.insert(i + 1, '\t\t70: TownStage')
i = find_one('\t\t13: WorkBar')
lines.insert(i + 1, '\t\t14: Contrib')

# ---- 2) 안내소 재건 버튼 교체 ----
s = [i for i,l in enumerate(lines) if l.strip()=='If(Event Player.Rebuild >= 5);' and lines[i-1].strip()=='Else If(Event Player.MenuIdx == 3);'][0]
assert lines[s - 1].strip() == 'Else If(Event Player.MenuIdx == 3);'
d = 0
for k in range(s, len(lines)):                       # find matching End; of this If
    st = lines[k].strip()
    if st.startswith('If(') or st.startswith('While(') or st.startswith('For '):
        d += 1
    elif st == 'End;':
        d -= 1
        if d == 0:
            e = k
            break
ind = lines[s][:len(lines[s]) - len(lines[s].lstrip('\t'))]
give = [
    ind + 'If(Global Variable(TownStage) >= 8);',
    ind + '\tSmall Message(Event Player, Custom String("마을은 이미 되살아났다 — 당신의 이름과 함께"));',
    ind + '\tPlay Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 50);',
    ind + 'Else If(Event Player.Money < 1000);',
    ind + '\tSmall Message(Event Player, Custom String("돈이 모자란다 ($1000 필요)"));',
    ind + '\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);',
    ind + 'Else;',
    ind + '\tModify Player Variable(Event Player, Money, Subtract, 1000);',
    ind + '\tModify Global Variable(Fund, Add, 1000);',
    ind + '\tSet Player Variable(Event Player, Contrib, 1);',
    ind + '\tSet Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));',
    ind + f'\tSet Player Variable(Event Player, Amt, Max(0, Subtract(Value In Array({GOALS}, Global Variable(TownStage)), Global Variable(Fund))));',
    ind + f'\tBig Message(All Players(All Teams), Custom String("{{0}} — 마을 금고에 $1,000 · {{1}}까지 $ {{2}}", Event Player, Value In Array({NAMES}, Global Variable(TownStage)), Event Player.Amt));',
    ind + '\tPlay Effect(All Players(All Teams), Buff Impact Sound, Color(Yellow), Position Of(Event Player), 90);',
    ind + 'End;',
]
lines[s:e + 1] = give

# ---- 3) 정거장 기금 버튼 통일 ----
j = find_one('Modify Global Variable(Fund, Add, 1000);\n') if False else None
idxs = [k for k, l in enumerate(lines) if l.strip() == 'Modify Global Variable(Fund, Add, 1000);']
assert len(idxs) == 2, len(idxs)
j = max(idxs)                                        # 정거장 쪽 (뒤에 위치)
jnd = lines[j][:len(lines[j]) - len(lines[j].lstrip('\t'))]
assert lines[j + 1].strip() == 'Set Player Variable(Event Player, Amt, Global Variable(Fund));'
assert '부흥 기금에 $1,000' in lines[j + 3]
lines[j + 1] = jnd + f'Set Player Variable(Event Player, Amt, Max(0, Subtract(Value In Array({GOALS}, Global Variable(TownStage)), Global Variable(Fund))));'
lines[j + 3] = jnd + f'Big Message(All Players(All Teams), Custom String("{{0}} — 마을 금고에 $1,000 · {{1}}까지 $ {{2}}", Event Player, Value In Array({NAMES}, Global Variable(TownStage)), Event Player.Amt));'
lines.insert(j + 1, jnd + 'Set Player Variable(Event Player, Contrib, 1);')

# ---- 4) [기금 01] 조건을 TownStage 기반으로 ----
c = find_one('Global Variable(Fund) >= Value In Array(Array(60000, 180000, 400000), Global Variable(FundTier));')
cnd = lines[c][:len(lines[c]) - len(lines[c].lstrip('\t'))]
lines[c] = cnd + 'Global Variable(TownStage) >= Value In Array(Array(3, 5, 7), Global Variable(FundTier));'

# ---- 5) 새 규칙 [금고 01] ----
r = find_one('rule("[기금 01] 부흥의 불")')
RULE = f'''rule("[금고 01] 마을 금고 — 단계 달성")
{{
\tevent
\t{{
\t\tOngoing - Global;
\t}}

\tconditions
\t{{
\t\tGlobal Variable(Ready) == 1;
\t\tGlobal Variable(TownStage) <= 7;
\t\tGlobal Variable(Fund) >= Value In Array({GOALS}, Global Variable(TownStage));
\t}}

\tactions
\t{{
\t\tModify Global Variable(TownStage, Add, 1);
\t\tBig Message(All Players(All Teams), Custom String("마을 금고 {{0}}/8 — {{1}}이(가) 세워졌다!!", Global Variable(TownStage), Value In Array({NAMES}, Subtract(Global Variable(TownStage), 1))));
\t\tIf(Value In Array({RB}, Global Variable(TownStage)) > 0);
\t\t\tSet Player Variable(Filtered Array(All Players(Team 1), Player Variable(Current Array Element, Contrib) >= 1), Rebuild, Value In Array({RB}, Global Variable(TownStage)));
\t\t\tSet Global Variable(RebuildMax, Max(Global Variable(RebuildMax), Value In Array({RB}, Global Variable(TownStage))));
\t\t\tSmall Message(Filtered Array(All Players(Team 1), Player Variable(Current Array Element, Contrib) >= 1), Custom String("재건 기여가 기록됐다 — 네 이름이 마을에 남는다"));
\t\tEnd;
\t\tIf(Global Variable(TownStage) >= 8);
\t\t\tBig Message(All Players(All Teams), Custom String("기차역이 복원되었다 — 66번 국도가 되살아났다!"));
\t\tEnd;
\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Value In Array(Global Variable(LocPos), 9), 7);
\t\tPlay Effect(All Players(All Teams), Buff Explosion Sound, Color(Yellow), Value In Array(Global Variable(LocPos), 9), 220);
\t}}
}}
'''
lines[r:r] = RULE.split('\n')

out = '\n'.join(lines)
assert out.count('rule("') == 125, out.count('rule("')
assert out.count('70: TownStage') == 1 and out.count('14: Contrib') == 1
assert out.count('마을 금고에 $1,000') == 2
assert '부흥 기금에 $1,000' not in out
assert out.count('Array(60000, 100000, 160000, 260000, 420000)') == 0
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch142 ok rules=', out.count('rule("'))
