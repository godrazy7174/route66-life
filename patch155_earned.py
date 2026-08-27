# patch155 (전수조사 #18): 수입인데 누적 수입(Earned)에 반영되지 않던 지점 보정
#  칭호가 누적 수입 기준이 된 뒤로 생긴 일관성 결함.
#  제외: 예금 인출(이미 번 돈), 송금 수령(상대의 수입에서 나온 돈 — 이중 계상 방지)
import io, re

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

EXCLUDE_SNIPPETS = [
    'Money, Add, Event Player.Deposit)',        # 예금 인출
    'Target, Money, Add, 100)',                 # 송금 수령
]

targets = []
for i, l in enumerate(lines):
    m = re.search(r'Modify Player Variable\((Event Player|Attacker), Money, Add, (.+)\);$', l.strip())
    if not m:
        continue
    if any(s in l for s in EXCLUDE_SNIPPETS):
        continue
    who, amt = m.group(1), m.group(2)
    near = ' '.join(x.strip() for x in lines[max(0, i-2):i+4])
    if re.search(rf'Modify Player Variable\({who}, Earned, Add', near):
        continue
    targets.append((i, who, amt))

assert 14 <= len(targets) <= 18, len(targets)
for i, who, amt in reversed(targets):
    ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
    lines.insert(i + 1, f'{ind}Modify Player Variable({who}, Earned, Add, {amt});')

out = '\n'.join(lines)
assert out.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch155 ok — Earned added at', len(targets), 'sites')
