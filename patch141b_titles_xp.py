# patch141b (작업 3·4·5)
#  3) 변수 회수: HudIds / WantedIco / Tier 선언 제거 (+ 환생 시 Tier 리셋 줄 제거)
#  4) 칭호 기준: 소지금(Money) -> 누적 수입(Earned), [도파민 04] 껍데기 규칙 삭제
#  5) XP: 승급 750 -> 1000, 채굴 12 -> 20, 사냥 15 -> 20
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# ---- 4a) [도파민 04] 삭제 ----
s = next(i for i, l in enumerate(lines) if l.startswith('rule("[도파민 04]'))
d = 0
for k in range(s, len(lines)):
    d += lines[k].count('{') - lines[k].count('}')
    if d == 0 and k > s:
        e = k
        break
assert 18 < e - s < 26, (s, e)
while e + 1 < len(lines) and lines[e + 1] == '':
    e += 1
del lines[s:e + 1]

# ---- 3) 선언 + 환생 리셋 줄 제거 ----
DROP_DECL = {'14: HudIds', '15: Tier', '96: WantedIco'}
RESET = 'Set Player Variable(Event Player, Tier, 0);'
n_decl = n_reset = 0
kept = []
for l in lines:
    st = l.strip()
    if st in DROP_DECL:
        n_decl += 1
        continue
    if st == RESET:
        n_reset += 1
        continue
    kept.append(l)
assert n_decl == 3, n_decl
assert n_reset == 1, n_reset
text = '\n'.join(kept)

# ---- 4b) 칭호 기준 Money -> Earned ----
OLD = ('Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), '
       'Event Player.Money >= 2500), Event Player.Money >= 6000), Event Player.Money >= 15000)')
NEW = ('Add(Add(Add(Add(Event Player.Earned >= 1000, Event Player.Earned >= 5000), '
       'Event Player.Earned >= 20000), Event Player.Earned >= 60000), Event Player.Earned >= 150000)')
assert text.count(OLD) == 5, text.count(OLD)
text = text.replace(OLD, NEW)

# ---- 5) XP ----
assert text.count('< 750);') == 6
text = text.replace('< 750);', '< 1000);')
assert text.count('{0} / 750') == 6
text = text.replace('{0} / 750', '{0} / 1000')
MINE = 'Set Player Variable At Index(Event Player, JobXP, 1, Add(Value In Array(Event Player.JobXP, 1), 12));'
assert text.count(MINE) == 1
text = text.replace(MINE, MINE.replace(', 12));', ', 20));'))
HUNT = 'Set Player Variable At Index(Attacker, JobXP, 2, Add(Value In Array(Player Variable(Attacker, JobXP), 2), 15));'
assert text.count(HUNT) == 1
text = text.replace(HUNT, HUNT.replace(', 15));', ', 20));'))

assert 'Event Player.Tier' not in text
assert ', Tier,' not in text
assert 'HudIds' not in text and 'WantedIco' not in text
assert text.count('rule("') == 124, text.count('rule("')
io.open(SRC, 'w', encoding='utf-8', newline='').write(text)
print('patch141b ok rules=', text.count('rule("'))
