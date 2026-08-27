"""생성한 요소를 '같은 종류'의 파괴 액션으로 지우는지 검사한다.

워크샵은 텍스트 종류마다 파괴 액션이 따로다.
  Create HUD Text                  -> Destroy HUD Text
  Create In-World Text             -> Destroy In-World Text
  Create Progress Bar HUD Text     -> Destroy Progress Bar HUD Text
  Create Progress Bar In-World Text-> Destroy Progress Bar In-World Text
종류를 틀리면 오류 없이 조용히 실패하고, 요소가 화면에 계속 쌓인다.
(실기에서 진행바 6개가 겹쳐 뜬 원인이 이것이었다.)
"""
import io, re, sys

TYPES = ['Progress Bar In-World Text', 'Progress Bar HUD Text', 'In-World Text', 'HUD Text']

src = io.open(sys.argv[1], encoding='utf-8').read()
lines = src.split('\n')

owner = {}   # 변수 이름 -> 생성 종류
for i, line in enumerate(lines):
    t = line.strip()
    for ty in TYPES:
        if t.startswith('Create ' + ty + '('):
            for j in range(i + 1, min(i + 3, len(lines))):
                nxt = lines[j].strip()
                m = re.search(r'Set (?:Player|Global) Variable(?: At Index)?\([^;]*?,\s*(\w+),\s*(?:\d+,\s*)?Last Text ID\(\)\)', nxt)
                if not m:
                    m = re.search(r'Modify Global Variable\((\w+), Append To Array, Last Text ID\(\)\)', nxt)
                if not m:
                    m = re.search(r'Set Global Variable\((\w+), Array\(Last Text ID\(\)\)\)', nxt)
                if m:
                    owner.setdefault(m.group(1), set()).add(ty)
                    break
            break

problems = []
for i, line in enumerate(lines, 1):
    t = line.strip()
    m = re.match(r'Destroy (' + '|'.join(re.escape(x) for x in TYPES) + r')\((.*)\);$', t)
    if not m:
        continue
    used_ty, arg = m.group(1), m.group(2)
    for var, kinds in owner.items():
        if re.search(r'\b' + re.escape(var) + r'\b', arg):
            if used_ty not in kinds:
                problems.append('L%d  %s 는 "Destroy %s" 로 지워야 함 (현재 "Destroy %s")'
                                % (i, var, sorted(kinds)[0], used_ty))
            break

print('=== 생성/파괴 종류 대조 ===')
for var, kinds in sorted(owner.items()):
    print('  %-10s <- %s' % (var, ' / '.join(sorted(kinds))))
if problems:
    print('\n!! 불일치 %d건' % len(problems))
    for p in problems:
        print('  ' + p)
else:
    print('\n불일치 없음')
