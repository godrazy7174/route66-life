# -*- coding: utf-8 -*-
"""1) 대사냥 진행 중에는 일반 흔적 추적(DoHunt)을 봉인한다.
   2) 야수 배회에서 의도적으로 죽여둔 분기 두 개를 제거한다.
      (Random Integer(1, 100) <= 0 — 절대 참이 될 수 없어 예전에 봉인한 순간이동/폭주)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()

# ── 1) DoHunt 봉인 ────────────────────────────────────────────────
i = src.index('rule("[직업 02] DoHunt")')
anchor = '\tactions\n\t{\n\t\tIf(Event Player.Energy < 4);\n'
k = src.index(anchor, i)
guard = ('\tactions\n\t{\n'
         '\t\tIf(Global Variable(HuntPhase) >= 1);\n'
         '\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), '
         'Custom String("전설의 야수를 사냥하러 가야할 듯 하다..."));\n'
         '\t\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 3));\n'
         '\t\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Orange), Position Of(Event Player), 45);\n'
         '\t\t\tAbort;\n'
         '\t\tEnd;\n'
         '\t\tIf(Event Player.Energy < 4);\n')
src = src[:k] + guard + src[k + len(anchor):]
print('  OK DoHunt — 대사냥 진행 중 봉인')

# ── 2) 야수 배회의 죽은 분기 제거 ─────────────────────────────────
i = src.index('rule("[직업 03-3] 야수 배회")')
j = src.index('rule("', i + 10)
blk = src[i:j]
lines = blk.split('\n')

# (a) Else If(Random Integer(1, 100) <= 0) 분기 통째로
a = next(n for n, l in enumerate(lines) if l.strip() == 'Else If(Random Integer(1, 100) <= 0);')
b = next(n for n in range(a + 1, len(lines)) if lines[n].strip() == 'Else;')
assert b - a == 7, '분기 길이 %d (7이어야 함)' % (b - a)
del lines[a:b]

# (b) 안쪽 If(Random Integer(1, 100) <= 0) ... End;
c = next(n for n, l in enumerate(lines) if l.strip() == 'If(Random Integer(1, 100) <= 0);')
d = next(n for n in range(c + 1, len(lines)) if lines[n].strip() == 'End;')
assert d - c == 3, '내부 블록 길이 %d (3이어야 함)' % (d - c)
del lines[c:d + 1]

assert 'Random Integer(1, 100) <= 0' not in '\n'.join(lines)
src = src[:i] + '\n'.join(lines) + src[j:]
print('  OK 야수 배회 — 봉인된 죽은 분기 2개 제거')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('done')
