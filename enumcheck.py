"""인자 자리에 들어간 상수(enum) 값이 그 자리에서 유효한지 검사한다.

붙여넣기 실패의 상당수가 이 부류였다.
예: Visible To and Position 은 인월드 텍스트(WorldTextReeval)에는 있지만
    이펙트(EffectReeval)에는 없다. 이름이 비슷해서 눈으로는 안 걸린다.
"""
import json, re, io, sys, os

REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ref')


def load(fn):
    s = io.open(os.path.join(REF, fn), encoding='utf-8').read()
    a = s.index('//begin-json') + len('//begin-json')
    b = s.index('//end-json')
    t = s[a:b]
    t = re.sub(r'([\n{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)', r'\1"\2"\3', t)
    t = re.sub(r',(\s*[}\]])', r'\1', t)
    return json.loads(t)


# 상수 그룹 -> 멤버 이름 집합
GROUPS = {}
for grp, node in load('constants.ts').items():
    vals = node.get('values', node) if isinstance(node, dict) else {}
    if isinstance(vals, dict):
        members = set()
        for k, v in vals.items():
            if isinstance(v, dict) and v.get('en-US'):
                members.add(v['en-US'])
                if v.get('ko-KR'):
                    members.add(v['ko-KR'])
        if members:
            GROUPS[grp] = members

# 함수 -> 인자 타입 목록
FUNCS = {}
for fn in ('actions.ts', 'values.ts'):
    for k, v in load(fn).items():
        if isinstance(v, dict) and v.get('en-US'):
            args = v.get('args') or []
            FUNCS.setdefault(v['en-US'], [a.get('type') for a in args])


def strip_strings(text):
    out, i, n = [], 0, len(text)
    while i < n:
        if text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 1
            out.append('"S"')
            i = j + 1
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)


def split_args(inner):
    args, depth, cur = [], 0, ''
    for ch in inner:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == ',' and depth == 0:
            args.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


NAMECHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-:'")

raw = io.open(sys.argv[1], encoding='utf-8').read()
text = strip_strings(raw)
problems = []

for ln, line in enumerate(text.split('\n'), 1):
    for m in re.finditer(r'\(', line):
        p = m.start()
        j = p - 1
        while j >= 0 and line[j] in NAMECHARS:
            j -= 1
        cand = line[j + 1:p].strip()
        name = None
        words = cand.split(' ')
        for k in range(len(words)):
            trial = ' '.join(words[k:])
            if trial in FUNCS:
                name = trial
                break
        if name is None:
            continue
        depth, q = 0, p
        while q < len(line):
            if line[q] == '(':
                depth += 1
            elif line[q] == ')':
                depth -= 1
                if depth == 0:
                    break
            q += 1
        if depth != 0:
            continue
        args = split_args(line[p + 1:q])
        types = FUNCS[name]
        for idx, arg in enumerate(args):
            if idx >= len(types):
                break
            t = types[idx]
            if not isinstance(t, str) or t not in GROUPS:
                continue
            if '(' in arg or arg == '' or arg[0].isdigit() or arg[0] == '-':
                continue
            if arg.startswith(('Event Player', 'Local Player', 'Global', 'Value In Array', 'All Players')):
                continue
            if arg not in GROUPS[t]:
                near = [x for x in GROUPS[t] if x.split()[0] == arg.split()[0]]
                problems.append('L%d  %s 인자%d: "%s" 는 %s 에 없음%s'
                                % (ln, name, idx + 1, arg, t,
                                   ('  → ' + ' / '.join(sorted(near)[:3])) if near else ''))

if problems:
    print('=== 상수 오용 %d건 ===' % len(problems))
    for p in problems:
        print('  ' + p)
else:
    print('상수 검사: 모든 인자 정상')
