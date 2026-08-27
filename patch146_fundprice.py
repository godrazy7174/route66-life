# patch146: 마을 금고 가격 2.5배 상향 + 세이브 복원 시 TownStage/Fund 복원
import io

SRC = 'ROUTE66_LIFE_EN.ow'
t = io.open(SRC, encoding='utf-8').read()

OLD = 'Array(4000, 11000, 22000, 38000, 61000, 93000, 138000, 198000)'
NEW = 'Array(8000, 23000, 48000, 88000, 148000, 233000, 348000, 498000)'
n = t.count(OLD)
assert n == 3, f'goal array sites: {n}'
t = t.replace(OLD, NEW)

# ---- 세이브 복원: Rebuild -> TownStage / Fund ----
lines = t.split('\n')
i = next(k for k, l in enumerate(lines)
         if 'Set Player Variable(Event Player, Rebuild, Round To Integer(Divide(Event Player.EnterC, 100000), Down));' in l)
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines[i + 1:i + 1] = [
    ind + 'Set Global Variable(TownStage, Max(Global Variable(TownStage), Value In Array(Array(0, 1, 2, 4, 6, 8), Event Player.Rebuild)));',
    ind + 'Set Global Variable(Fund, Max(Global Variable(Fund), Value In Array(Array(0, 8000, 23000, 88000, 233000, 498000), Event Player.Rebuild)));',
]
t = '\n'.join(lines)

assert t.count('Value In Array(Array(0, 1, 2, 4, 6, 8), Event Player.Rebuild)') == 1
assert t.count(NEW) == 3
assert t.count('rule("') == 129
io.open(SRC, 'w', encoding='utf-8', newline='').write(t)
print('patch146 ok')
