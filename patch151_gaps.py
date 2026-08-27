# patch151 (전수조사 #3, #4)
#  [버그 C] 정거장 갹출에 8단계 완료 게이트가 없어 완주 후에도 돈이 빨려 들어가고
#           건물명/목표액 배열이 범위를 넘어 안내가 깨진다
#  [버그 D] 환생해도 Contrib(기여 기록)이 남아, 이후 금고 단계가 오를 때 재건 진행도를 공짜로 회복한다
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

# ---- C) 정거장 갹출 게이트 ----
cands = [i for i, l in enumerate(lines) if l.strip() == 'If(Event Player.Money < 1000);']
assert len(cands) == 1, cands          # 안내소 쪽은 'Else If(' 라 구분됨
i = cands[0]
ind = lines[i][:len(lines[i]) - len(lines[i].lstrip('\t'))]
lines[i] = ind + 'If(Global Variable(TownStage) >= 8);'
lines[i + 1:i + 1] = [
    ind + '\tSmall Message(Event Player, Custom String("마을은 이미 되살아났다 — 당신의 이름과 함께"));',
    ind + '\tPlay Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 50);',
    ind + 'Else If(Event Player.Money < 1000);',
]

# ---- D) 환생 시 기여 기록 리셋 ----
j = next(k for k, l in enumerate(lines) if l.strip() == 'Set Player Variable(Event Player, Rebuild, 0);')
ind = lines[j][:len(lines[j]) - len(lines[j].lstrip('\t'))]
lines.insert(j + 1, ind + 'Set Player Variable(Event Player, Contrib, 0);')

out = '\n'.join(lines)
assert out.count('마을은 이미 되살아났다') == 2
assert out.count('Set Player Variable(Event Player, Contrib, 0);') == 1
assert out.count('rule("') == 130
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch151 ok')
