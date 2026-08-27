# -*- coding: utf-8 -*-
"""메뉴 라벨 평면 배열 정렬 검사 — (Zone+1)*6 인덱싱 전제.

총 96개(16구역 x 6칸)인지, 각 구역 첫 칸이 기대 라벨로 시작하는지 검사.
patch90/91이 '-' 소진 없이 라벨을 삽입해 off-by-two가 났던 사고(2026-08-26)의 재발 방지.
사용: python labelcheck.py ROUTE66_LIFE_EN.ow
"""
import io, re, sys

P = sys.argv[1] if len(sys.argv) > 1 else 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
p = s.index('Custom String("행동 없음')  # 행동 없음
astart = s.rfind('Array(', 0, p)
j = astart + 6; depth = 1; start = j; top = []
while depth > 0:
    c = s[j]
    if c == '(':
        depth += 1
    elif c == ')':
        depth -= 1
        if depth == 0:
            top.append(s[start:j].strip())
    elif c == ',' and depth == 1:
        top.append(s[start:j].strip()); start = j + 1
    j += 1

errors = []
if len(top) != 96:
    errors.append('label count %d != 96' % len(top))

first_expect = {2: '채굴하기', 6: '위스키', 7: '흔적 추적',
                8: '벌금 납부', 9: '장물 거래', 10: '튜토리얼',
                12: '배달 수주', 13: '소 몰기'}
for z, exp in first_expect.items():
    e = top[z * 6] if z * 6 < len(top) else ''
    m = re.search(r'Custom String\("([^"]*)"', e)
    name = m.group(1) if m else '<dyn>'
    if not name.startswith(exp):
        errors.append('zone %d slot0 = %r (expect %r...)' % (z - 1, name[:14], exp))

if errors:
    for e in errors:
        try:
            print('LABEL FAIL:', e)
        except Exception:
            print('LABEL FAIL (non-ascii detail)')
    sys.exit(1)
print('LABEL OK: 96 entries, zones aligned')
