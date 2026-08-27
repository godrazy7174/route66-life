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

FUNCS = {}
CONSTS = set()
for fn in ('actions.ts', 'values.ts'):
    for k, v in load(fn).items():
        if isinstance(v, dict) and v.get('en-US'):
            args = v.get('args')
            n_req = 0 if args is None else len([a for a in args if 'default' not in a])
            n_max = 0 if args is None else len(args)
            FUNCS.setdefault(v['en-US'], (n_req, n_max))
for grp, node in load('constants.ts').items():
    vals = node.get('values', node) if isinstance(node, dict) else {}
    if isinstance(vals, dict):
        for k, v in vals.items():
            if isinstance(v, dict) and v.get('en-US'):
                CONSTS.add(v['en-US'])
for fn in ('heroes.ts', 'maps.ts', 'gamemodes.ts'):
    try:
        for k, v in load(fn).items():
            if isinstance(v, dict) and v.get('en-US'):
                CONSTS.add(v['en-US'])
    except Exception:
        pass

VARIADIC = {'Custom String', 'Array', 'String'}
KEYWORDS = {'rule', 'event', 'conditions', 'actions', 'settings', 'variables',
            'subroutines', 'global', 'player', 'disabled', 'main', 'lobby',
            'modes', 'heroes', 'enabled maps', 'enabled heroes', 'General'}

NAMECHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .-:'")

def strip_strings(text):
    """Replace string literal contents with placeholders so they aren't parsed."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 1
            out.append('"S"')
            i = j + 1
        else:
            out.append(c)
            i += 1
    return ''.join(out)

def split_args(inner):
    """Split a call's argument list on top-level commas."""
    args, depth, cur = [], 0, ''
    for ch in inner:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == ',' and depth == 0:
            args.append(cur.strip()); cur = ''
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args

def main(path):
    raw = io.open(path, encoding='utf-8').read()
    body_start = raw.index('rule(')
    header = raw[:body_start]
    text = strip_strings(raw)

    problems = []

    # 1. brace / paren balance per line-run
    if text.count('(') != text.count(')'):
        problems.append('PAREN MISMATCH: %d "(" vs %d ")"' % (text.count('('), text.count(')')))
    if text.count('{') != text.count('}'):
        problems.append('BRACE MISMATCH: %d "{" vs %d "}"' % (text.count('{'), text.count('}')))

    # 2. declared variables
    gvars, pvars, subs = set(), set(), set()
    mg = re.search(r'variables\s*\{(.*?)\n\}', raw, re.S)
    if mg:
        blk = mg.group(1)
        gsec = re.search(r'global:(.*?)(player:|$)', blk, re.S)
        psec = re.search(r'player:(.*)', blk, re.S)
        if gsec:
            gvars = set(re.findall(r'\d+:\s*(\w+)', gsec.group(1)))
        if psec:
            pvars = set(re.findall(r'\d+:\s*(\w+)', psec.group(1)))
    ms = re.search(r'subroutines\s*\{(.*?)\n\}', raw, re.S)
    if ms:
        subs = set(re.findall(r'\d+:\s*(\w+)', ms.group(1)))

    # 3. function names + arg counts
    unknown = {}
    argwarn = []
    lines = text.split('\n')
    for ln, line in enumerate(lines, 1):
        for m in re.finditer(r'\(', line):
            p = m.start()
            j = p - 1
            while j >= 0 and line[j] in NAMECHARS:
                j -= 1
            cand = line[j + 1:p].strip()
            if not cand:
                continue
            # longest matching suffix that is a known element
            name = None
            words = cand.split(' ')
            for wk in range(len(words)):
                trial = ' '.join(words[wk:])
                if trial in FUNCS:
                    name = trial
                    break
            if name is None:
                if cand.split(' ')[-1] in KEYWORDS or cand in KEYWORDS:
                    continue
                unknown.setdefault(cand, []).append(ln)
                continue
            # 접미사만 일치하고 바로 앞 단어가 이름 형태(대문자 시작, 순수 알파벳)면
            # "Players On Team"처럼 존재하지 않는 긴 이름일 가능성 — 미확인으로 경고.
            # ("Anchor - Vector(" 같은 연산자/숫자 접두어는 이름 형태가 아니라 제외)
            if wk > 0:
                j2 = wk
                while j2 > 0 and words[j2 - 1].isalpha() and words[j2 - 1][0].isupper():
                    j2 -= 1
                full = ' '.join(words[j2:])
                if j2 < wk and full not in FUNCS and full not in CONSTS:
                    unknown.setdefault('%s  (known suffix: "%s")' % (full, name), []).append(ln)
                    continue
            if name in VARIADIC:
                continue
            # extract inner text for arg count
            depth, k = 0, p
            while k < len(line):
                if line[k] == '(':
                    depth += 1
                elif line[k] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            if depth != 0:
                continue
            inner = line[p + 1:k]
            got = len(split_args(inner))
            n_req, n_max = FUNCS[name]
            if got < n_req or got > n_max:
                argwarn.append('L%d  %s: got %d args, expected %d..%d' % (ln, name, got, n_req, n_max))

    # 4. variable usage
    used_g = set(re.findall(r'Global Variable\((\w+)\)', raw)) | set(re.findall(r'Global\.(\w+)', raw))
    used_g |= set(re.findall(r'Set Global Variable\((\w+),', raw))
    used_g |= set(re.findall(r'Set Global Variable At Index\((\w+),', raw))
    used_g |= set(re.findall(r'Modify Global Variable\((\w+),', raw))
    used_g |= set(re.findall(r'For Global Variable\((\w+),', raw))
    used_p = set(re.findall(r'\.(\w+)\b(?!\s*\()', raw))
    used_p |= set(re.findall(r'Set Player Variable\([^,]+,\s*(\w+),', raw))
    used_p |= set(re.findall(r'Set Player Variable At Index\([^,]+,\s*(\w+),', raw))
    used_p |= set(re.findall(r'Modify Player Variable\([^,]+,\s*(\w+),', raw))
    used_p |= set(re.findall(r'Player Variable\([^,]+,\s*(\w+)\)', raw))
    used_p |= set(re.findall(r'For Player Variable\([^,]+,\s*(\w+),', raw))
    used_subs = set(re.findall(r'Call Subroutine\((\w+)\)', raw)) | set(re.findall(r'Start Rule\((\w+),', raw))

    bad_g = sorted(used_g - gvars)
    known_words = {'Player','Target'}
    bad_p = sorted(x for x in used_p if x not in pvars and x not in gvars and x[0].isascii() and x[0].isupper() and x not in ('Player',))
    bad_s = sorted(used_subs - subs)
    declared_sub_rules = set(re.findall(r'Subroutine;\s*\n\s*(\w+);', raw))

    print('=== ROUTE66 LINT ===')
    print('rules: %d   lines: %d' % (raw.count('\nrule('), raw.count('\n') + 1))
    print('globals declared: %d   player vars: %d   subroutines: %d' % (len(gvars), len(pvars), len(subs)))
    for pr in problems:
        print('!! ' + pr)
    if unknown:
        print('\n-- UNKNOWN ELEMENT NAMES --')
        for k in sorted(unknown):
            print('   %-40s lines %s' % (k, unknown[k][:6]))
    else:
        print('\n-- element names: all recognized --')
    if argwarn:
        print('\n-- ARG COUNT MISMATCH --')
        for w in argwarn:
            print('   ' + w)
    else:
        print('-- arg counts: OK --')
    if bad_g:
        print('\n!! undeclared globals: ' + ', '.join(bad_g))
    if bad_p:
        print('!! possibly undeclared player vars: ' + ', '.join(bad_p))
    if bad_s:
        print('!! undeclared subroutines: ' + ', '.join(bad_s))
    missing_sub_impl = sorted(subs - declared_sub_rules)
    if missing_sub_impl:
        print('!! subroutines declared but never implemented: ' + ', '.join(missing_sub_impl))
    unused_sub = sorted(subs - used_subs)
    if unused_sub:
        print('   (note) subroutines never called: ' + ', '.join(unused_sub))

main(sys.argv[1])

# --- 변수 인덱스 중복 검사 (추가) ---
def dup_check(path):
    raw = io.open(path, encoding='utf-8').read()
    m = re.search(r'variables\s*\{(.*?)\n\}', raw, re.S)
    if not m:
        return
    blk = m.group(1)
    for scope, sec in (('global', re.search(r'global:(.*?)(player:|$)', blk, re.S)),
                       ('player', re.search(r'player:(.*)', blk, re.S))):
        if not sec:
            continue
        pairs = re.findall(r'(\d+):\s*(\w+)', sec.group(1))
        seen = {}
        bad = []
        for idx, name in pairs:
            if idx in seen:
                bad.append('%s 인덱스 %s: %s / %s' % (scope, idx, seen[idx], name))
            seen[idx] = name
        for b in bad:
            print('!! 중복 변수 — ' + b)
    print('변수 인덱스 중복 검사 완료')

dup_check(sys.argv[1])

# --- 전역 변수 초기화 누락 검사 (추가) ---
def globaluse_check(path):
    """전역 변수의 읽기/쓰기 균형.

    이전 판은 [코어 01] 안에서만 대입을 찾아, BuildWorld 나 각 시스템이
    직접 초기화하는 전역 27개를 매번 오탐으로 뱉었다. 그 노이즈 때문에
    진짜 '!!' 가 묻혔다. 정확한 불변식 두 가지로 바꾼다.
    """
    raw = io.open(path, encoding='utf-8').read()
    blk = re.search(r'variables\s*\{(.*?)\n\}', raw, re.S).group(1)
    gsec = re.search(r'global:(.*?)(player:|$)', blk, re.S)
    gvars = [n for _, n in re.findall(r'(\d+):\s*(\w+)', gsec.group(1))]
    body = raw[raw.index(chr(10) + 'rule('):]
    written = set()
    for pat in (r'Set Global Variable\((\w+),',
                r'Set Global Variable At Index\((\w+),',
                r'Modify Global Variable\((\w+),',
                r'For Global Variable\((\w+),'):
        written |= set(re.findall(pat, body))
    read = set(re.findall(r'Global Variable\((\w+)\)', body))
    no_write = [g for g in gvars if g in read and g not in written]
    no_read = [g for g in gvars if g in written and g not in read]
    if no_write:
        print('!! 읽기만 하고 아무도 쓰지 않는 전역: ' + ', '.join(no_write))
    if no_read:
        print('!! 쓰기만 하고 아무도 읽지 않는 전역(죽은 상태): ' + ', '.join(no_read))
    if not no_write and not no_read:
        print('전역 읽기/쓰기 균형: OK')


globaluse_check(sys.argv[1])


# --- 액션/조건 한 줄 완결성 검사 (추가) ---
# patch31 회귀 대응: 문자열 안에 진짜 개행이 들어가면 액션 한 줄이
# 여러 줄로 쪼개져 붙여넣기가 실패한다. 이름 기반 검사는 이걸 못 잡는다.
def line_check(path):
    bad = []
    inside = False
    for i, ln in enumerate(io.open(path, encoding='utf-8'), 1):
        t = ln.rstrip('\n')
        if re.match(r'\t(actions|conditions)$', t):
            inside = True
            continue
        if inside and t == '\t}':
            inside = False
            continue
        if not inside or t.strip() in ('', '{', '}'):
            continue
        if not t.startswith('\t\t'):
            bad.append((i, '들여쓰기', t[:60]))
        elif not t.endswith(';'):
            bad.append((i, '세미콜론 없음', t[:60]))
    for i, why, txt in bad:
        print('!! %d행 %s: %s' % (i, why, txt))
    if not bad:
        print('액션 줄 완결성 검사 완료')

line_check(sys.argv[1])

# --- 생성 없는 파괴 검사 (추가) ---
# patch22 회귀 대응: TutHud가 Destroy만 되고 Create가 사라졌는데
# Destroy는 조용히 no-op이라 아무 증상 없이 튜토리얼 자막만 증발했다.
def orphan_check(path):
    raw = io.open(path, encoding='utf-8').read()
    made = set(re.findall(r'Variable\((?:Event Player, )?(\w+), Last (?:Text ID|Created Entity)\(\)', raw))
    made |= set(re.findall(r'Variable\((\w+), Append To Array, Last Created Entity', raw))
    made |= set(re.findall(r'Variable At Index\((\w+), [^,]+, Last Created Entity', raw))
    killed = set(re.findall(r'Destroy (?:Progress Bar )?HUD Text\(\w+(?:\.| Variable\()(\w+)', raw))
    killed |= set(re.findall(r'Destroy (?:Effect|Icon)\(Value In Array\(Global Variable\((\w+)\)', raw))
    orphan = sorted(killed - made)
    if orphan:
        print('!! 생성 없이 파괴만 하는 변수: ' + ', '.join(orphan))
    else:
        print('생성/파괴 고아 검사 완료')

orphan_check(sys.argv[1])

# --- Busy 플래그 잠금 검사 (추가) ---
# DoHunt 회귀 대응: Busy를 1로 올려놓고 0으로 내리지 않으면
# 달리기·상호작용이 그 플레이어에게서 영구히 막힌다. 오류는 안 난다.
def busy_check(path):
    raw = io.open(path, encoding="utf-8").read()
    bad = []
    for p in raw.split(chr(10) + "rule(")[1:]:
        name = p.split(chr(34))[1]
        if name.startswith("[조작 03c]"):
            continue   # 세이브 입력 시작 — 해제는 세이브 02/03/04 와 사망 정리가 담당
        if p.count("Busy, 1)") and not p.count("Busy, 0)"):
            bad.append(name)
    if bad:
        print("!! Busy를 올리고 내리지 않는 룰: " + ", ".join(bad))
    else:
        print("Busy 플래그 검사 완료")

busy_check(sys.argv[1])

# --- 전역 기준 조건부 표시 검사 (추가) ---
# 광기둥·하늘 조명·야수 아이콘이 세 번 연속 이 패턴으로 죽었다.
#   Create Effect(Global Variable(X) == 0 ? All Players(All Teams) : False, ...)
# 전역 값으로 "보이는 대상"을 조건부로 두면 이 스크립트에서 렌더되지 않는다.
# (Local Player 기준 조건부는 정상 작동하므로 대상이 아니다.)
# 낮/밤 같은 전역 상태로 켜고 끌 때는 실제로 생성/파괴할 것.
def cond_vis_check(path):
    bad = []
    for i, ln in enumerate(io.open(path, encoding="utf-8"), 1):
        m = re.match(r"\s*Create (Effect|Icon|In-World Text)\((.*?), (?:Light Shaft|Sphere|Good Aura|Orb|Cloud|Ring|Eye|Skull|Diamond|Custom String)", ln)
        arg = m.group(2) if m else ""
        # Local Player 기준 조건부는 정상 작동한다 (장소 상세 패널 등) — 제외
        if m and "?" in arg and "Global Variable(" in arg and "Local Player" not in arg:
            bad.append((i, m.group(1), m.group(2)[:56]))
    for i, kind, arg in bad:
        print("!! %d행 %s 조건부 표시(전역 기준): %s" % (i, kind, arg))
    if not bad:
        print("조건부 표시 검사 완료")

cond_vis_check(sys.argv[1])

# --- 대기 낀 공용 루프 변수 검사 (추가) ---
# BuildWorld 봇 생성 회귀 대응: For 가 전역 변수(Idx/Tmp)를 쓰는데 몸통에
# Wait 가 있으면, 대기 중 다른 룰이 그 변수를 덮어 루프가 조기 종료된다.
def loopwait_check(path):
    bad = []
    rule = ''
    depth = 0
    var = ''
    for i, ln in enumerate(io.open(path, encoding='utf-8'), 1):
        t = ln.strip()
        if t.startswith('rule('):
            rule = t.split('"')[1]
        m = re.match(r'For Global Variable\((\w+),', t)
        if m:
            depth, var, start = 1, m.group(1), i
            continue
        if depth:
            if t.startswith('For '):
                depth += 1
            elif t == 'End;':
                depth -= 1
                if depth == 0:
                    var = ''
            elif var and t.startswith('Wait'):
                bad.append((start, rule, var))
                var = ''
    for i, r, v in bad:
        print('!! %d행 %s: 전역 %s 루프 안에 Wait — 다른 룰이 %s를 덮을 수 있음' % (i, r, v, v))
    if not bad:
        print('전역 루프 대기 검사 완료')

loopwait_check(sys.argv[1])

# --- 인자 접합 검사 (추가) ---
# patch67 회귀: 문자열 조립 실수로 인자 사이 쉼표가 빠지면
# Custom String("-")Custom String(...) 처럼 붙는다. 게임에서만 터진다.
# 문자열 리터럴 내부의 괄호는 제외한다.
def glue_check(path):
    bad = []
    for i, ln in enumerate(io.open(path, encoding="utf-8"), 1):
        instr = False
        for j, ch in enumerate(ln[:-1]):
            if ch == chr(34):
                instr = not instr
            elif ch == ")" and not instr:
                nxt = ln[j + 1]
                if nxt.isalnum() or nxt == chr(34):
                    bad.append((i, ln[max(0, j - 20):j + 20].strip()))
                    break
    for i, ctx in bad:
        print("!! %d행 쉼표 없는 접합: ...%s..." % (i, ctx))
    if not bad:
        print("인자 접합 검사 완료")

glue_check(sys.argv[1])

# --- 규칙 크기 검사 (추가) ---
# 워크샵 한도: 규칙당 내부 98KB. 인게임 진단으로 실측한 환산비는
# 텍스트 약 2.1배(46KB 텍스트 = 99KB 내부). 텍스트 40KB 초과를 차단한다.
def rulesize_check(path):
    raw = io.open(path, encoding="utf-8").read()
    bad = []
    for p in raw.split(chr(10) + "rule(")[1:]:
        name = p.split(chr(34))[1]
        kb = len(p.encode("utf-8")) / 1024.0
        if kb > 40:
            bad.append((kb, name))
    for kb, name in sorted(bad, reverse=True):
        print("!! 규칙 %.0fKB (내부 약 %.0fKB, 한도 98): %s" % (kb, kb * 2.1, name))
    if not bad:
        print("규칙 크기 검사 완료")

rulesize_check(sys.argv[1])

_sp = [i + 1 for i, l in enumerate(io.open(sys.argv[1], encoding='utf-8').read().split(chr(10))) if l.startswith(' ')]
print('space-indent lines:', _sp[:10] if _sp else 'OK')


def strlen_check(path):
    import re as _re
    _ls = io.open(path, encoding='utf-8').read().split(chr(10))
    _pat = _re.compile('Custom String' + chr(92) + '("([^"]*)"')
    _over = []
    for _i, _l in enumerate(_ls, 1):
        for _m in _pat.finditer(_l):
            _s = _m.group(1)
            _eff = len(_s.replace(chr(92) + 'r' + chr(92) + 'n', 'XX'))
            if _eff > 128:
                _over.append((_i, _eff, _s[:40]))
    if _over:
        print('!! Custom String over 128 chars (render truncated):')
        for _i, _eff, _s in _over[:10]:
            print('   L%d %dch %s...' % (_i, _eff, _s))
    else:
        print('string length check: OK')

strlen_check(sys.argv[1])


def fmtarg_check(path):
    import re as _re
    _ls = io.open(path, encoding='utf-8').read().split(chr(10))
    _bad = []
    for _i, _l in enumerate(_ls, 1):
        for _m in _re.finditer('Custom String' + chr(92) + '("([^"]*)"', _l):
            _s = _m.group(1)
            _n = set(_re.findall(r'{(' + chr(92) + 'd)}', _s))
            if _n and max(int(x) for x in _n) > 2:
                _bad.append((_i, sorted(_n), _s[:40]))
    if _bad:
        print('!! Custom String format slot > {2} (max 3 args):')
        for _i, _n, _s in _bad[:10]:
            print('   L%d slots=%s %s...' % (_i, _n, _s))
    else:
        print('format arg check: OK')

fmtarg_check(sys.argv[1])


def nested_filter_check(path):
    _ls = io.open(path, encoding='utf-8').read().split(chr(10))
    _bad = []
    for _i, _l in enumerate(_ls, 1):
        if 'Filtered Array(Filtered Array(' in _l:
            _bad.append(_i)
    if _bad:
        print('!! nested Filtered Array (Current Array Element collides -> empty result):')
        print('   lines: %s' % _bad[:10])
    else:
        print('nested filter check: OK')

nested_filter_check(sys.argv[1])

def emptypick_check(path):
    _ls = io.open(path, encoding='utf-8').read().split(chr(10))
    _bad = []
    for _i, _l in enumerate(_ls, 1):
        if 'Random Value In Array(Filtered Array(' in _l and 'Pos,' in _l:
            _bad.append(_i)
    if _bad:
        print('!! position from Random Value In Array(Filtered Array(...)):')
        print('   empty filter silently yields 0 -> coordinate (0,0,0). lines: %s' % _bad[:10])
    else:
        print('empty-pick check: OK')

emptypick_check(sys.argv[1])


def slotcount_check(path):
    """Custom String의 {N} 슬롯 개수와 실제로 넘긴 인자 개수가 맞는지."""
    src = io.open(path, encoding='utf-8').read()

    def split_args(t):
        depth = 0
        cur = ''
        out = []
        inq = False
        for ch in t:
            if ch == '"':
                inq = not inq
            if not inq:
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    if depth == 0:
                        break
                    depth -= 1
                if ch == ',' and depth == 0:
                    out.append(cur)
                    cur = ''
                    continue
            cur += ch
        out.append(cur)
        return out

    bad = []
    for m in re.finditer(r'Custom String\("([^"]*)"(,|\))', src):
        lit = m.group(1)
        slots = set(int(x) for x in re.findall(r'\{(\d)\}', lit))
        n = 0 if m.group(2) == ')' else len([a for a in split_args(src[m.end():]) if a.strip()])
        need = max(slots) + 1 if slots else 0
        if need != n:
            bad.append((src[:m.start()].count(chr(10)) + 1, sorted(slots), n, lit[:36]))
    if bad:
        print('!! Custom String slot/arg count mismatch:')
        for ln, sl, n, t in bad[:10]:
            print('   L%d slots=%s args=%d %s' % (ln, sl, n, t))
    else:
        print('slot/arg count check: OK')


slotcount_check(sys.argv[1])


def deadelse_check(path):
    """같은 If 블록에서 빈 Else 뒤에 오는 Else If는 절대 실행되지 않는다."""
    lines = io.open(path, encoding='utf-8').read().split(chr(10))
    stack = []
    bad = []
    for idx, ln in enumerate(lines, 1):
        t = ln.strip()
        ind = len(ln) - len(ln.lstrip(chr(9)))
        if t.startswith('If(') or t.startswith('While(') or t.startswith('For '):
            stack.append([ind, False])
        elif t == 'Else;':
            if stack and stack[-1][0] == ind:
                stack[-1][1] = True
        elif t.startswith('Else If('):
            if stack and stack[-1][0] == ind and stack[-1][1]:
                bad.append((idx, t[:50]))
        elif t == 'End;':
            if stack and stack[-1][0] == ind:
                stack.pop()
    if bad:
        print('!! unreachable Else If after a bare Else:')
        for ln, t in bad[:10]:
            print('   L%d %s' % (ln, t))
    else:
        print('dead-else check: OK')


deadelse_check(sys.argv[1])




def payoutmsg_check(path):
    """지급하는 상수 금액과, 같은 대상에게 보내는 메시지의 $금액이 어긋나는지.

    수신자가 다른 메시지(파발꾼 편지처럼 두 사람에게 각각 다른 금액을 알리는 경우)는
    비교 대상에서 제외한다.
    """
    lines = io.open(path, encoding='utf-8').read().split(chr(10))
    pay = re.compile(r'Modify Player Variable\(([^,]+), Money, Add, (\d+)\)')
    msg = re.compile(r'(?:Small|Big) Message\(([^,]+), Custom String\("([^"]*)"')
    notice = re.compile(r'Set Global Variable At Index\(NoticeMsg, Slot Of\(([^)]+)\), Custom String\("([^"]*)"')
    money = re.compile(r'\$ ?([0-9][0-9,]*)')
    bad = []
    for i, l in enumerate(lines):
        m = pay.search(l)
        if not m:
            continue
        who, paid = m.group(1).strip(), int(m.group(2))
        for j in range(i, min(i + 7, len(lines))):
            mm = msg.search(lines[j]) or notice.search(lines[j])
            if not mm:
                continue
            if mm.group(1).strip() != who:
                continue
            hit = money.search(mm.group(2))
            if not hit:
                continue
            said = int(hit.group(1).replace(',', ''))
            if said != paid and said > 1:
                bad.append((j + 1, paid, said, mm.group(2)[:34]))
            break
    if bad:
        print('!! payout vs message mismatch:')
        for ln, paid, said, t in bad[:10]:
            print('   L%d pays %d says %d  %s' % (ln, paid, said, t))
    else:
        print('payout message check: OK')


payoutmsg_check(sys.argv[1])


def zonename_check(path):
    """구역/건물 이름 배열이 실제 간판 이름과 어긋나지 않는지.

    같은 이름 목록이 HUD·정거장 배달지·부동산 등 여러 곳에 복제되어 있다.
    LocPos 순서가 바뀌거나 건물명을 고칠 때 한 곳만 고치면 조용히 어긋난다.
    """
    raw = io.open(path, encoding='utf-8').read()
    truth = {}
    for m in re.finditer(
            r'Create In-World Text\(All Players\(All Teams\), Custom String\("([^"]+)"\), '
            r'Add\(Value In Array\(Global Variable\(LocPos\), (\d+)\)', raw):
        truth[int(m.group(2))] = m.group(1)
    if not truth:
        print('zone name check: 간판 이름을 찾지 못함')
        return

    def close_paren(s, i):
        d = 0
        for j in range(i, len(s)):
            if s[j] == '(':
                d += 1
            elif s[j] == ')':
                d -= 1
                if d == 0:
                    return j
        return -1

    bad = []
    for m in re.finditer(r'Value In Array\(Array\(', raw):
        o = m.end() - 1
        c = close_paren(raw, o)
        if c < 0:
            continue
        names = re.findall(r'Custom String\("([^"]*)"\)', raw[o + 1:c])
        if not names or truth.get(0) not in names:
            continue
        idx = raw[c + 1:c + 80]
        off = 1 if ('Zone, 1)' in idx or names[0] != truth.get(0)) else 0
        for i, n in enumerate(names):
            z = i - off
            if z in truth and truth[z] != n:
                ln = raw[:m.start()].count(chr(10)) + 1
                bad.append('L%d idx%d "%s" != 간판 "%s"' % (ln, i, n, truth[z]))
    if bad:
        print('!! zone name array mismatch:')
        for b in bad[:10]:
            print('   ' + b)
    else:
        print('zone name check: OK')


zonename_check(sys.argv[1])


EVENT_ARITY = {
    'Ongoing - Global': 1,
    'Ongoing - Each Player': 3,
    'Player Died': 3,
    'Player Left Match': 3,
    'Player Joined Match': 3,
    'Player Dealt Damage': 3,
    'Player Took Damage': 3,
    'Player Dealt Final Blow': 3,
    'Player Earned Elimination': 3,
    'Subroutine': 2,
}


def event_check(path):
    """이벤트 이름이 실재하고, event 블록 줄 수가 그 이벤트에 맞는지.

    이름 오타나 줄 수 부족은 게임에서 임포트가 거부되는데
    지금까지 어떤 검사기도 이걸 보지 않았다.
    """
    raw = io.open(path, encoding='utf-8').read()
    bad = []
    for m in re.finditer(r'rule\("([^"]+)"\)\s*\{\s*event\s*\{\n(.*?)\n\t\}', raw, re.S):
        lines = [l.strip() for l in m.group(2).split(chr(10)) if l.strip()]
        if not lines:
            bad.append('%s: event 블록이 비었다' % m.group(1))
            continue
        ev = lines[0].rstrip(';')
        if ev not in EVENT_ARITY:
            bad.append('%s: 알 수 없는 이벤트 "%s"' % (m.group(1), ev))
        elif len(lines) != EVENT_ARITY[ev]:
            bad.append('%s: %s 는 %d줄이어야 하는데 %d줄'
                       % (m.group(1), ev, EVENT_ARITY[ev], len(lines)))
    if bad:
        print('!! event block problems:')
        for b in bad[:10]:
            print('   ' + b)
    else:
        print('event block check: OK')


def retrigger_check(path):
    """버튼을 누른 채로 액션이 반복 발동할 수 있는 룰.

    Ongoing 룰은 조건이 false->true 로 바뀔 때만 발동한다. 그래서 액션이
    자기 조건 변수를 1로 켰다가 0으로 되돌리면, 버튼을 계속 누르고 있는 동안
    연타처럼 재발동한다(모텔 숙박이 F 홀드로 $90씩 반복되던 사고).
    서브루틴 호출까지 따라가 디바운스 유무를 본다.
    """
    raw = io.open(path, encoding='utf-8').read()
    blocks = re.split(r'(?=^rule\(")', raw, flags=re.M)
    R = {}
    for b in blocks:
        m = re.match(r'rule\("([^"]+)"\)', b)
        if not m:
            continue
        cd = re.search(r'conditions\n\t\{\n(.*?)\t\}', b, re.S)
        ac = b[b.index('actions'):] if 'actions' in b else ''
        sn = re.search(r'Subroutine;\s*\n\s*(\w+);', b)
        R[m.group(1)] = (cd.group(1) if cd else '', ac, sn.group(1) if sn else None)
    SUB = {v[2]: k for k, v in R.items() if v[2]}

    def own_toggles(name):
        ac = R[name][1]
        return {v for v in re.findall(r'Set Player Variable\(Event Player, (\w+), 0\)', ac)
                if re.search(r'Set Player Variable\(Event Player, %s, 1\)' % v, ac)}

    def own_debounce(name):
        return 'Wait Until(Not(Is Button Held' in R[name][1]

    def sources(name, seen=None):
        """(토글하는 변수, 그 토글이 일어나는 룰) 쌍. 경로별로 따진다."""
        seen = seen or set()
        if name in seen:
            return set()
        seen.add(name)
        out = {(v, name) for v in own_toggles(name)}
        for c in set(re.findall(r'Call Subroutine\((\w+)\)', R[name][1])):
            if c in SUB:
                out |= sources(SUB[c], seen)
        return out

    # 이미 검토해 안전하다고 판단한 룰 (성공 시 조건 자체가 꺼지거나 쿨타임이 막는다)
    REVIEWED = {'[조작 03e] 행동 실행 — 정거장', '[범죄 01] 황야에서 강도 / 체포 (F)',
                '[열차 01] 화약 설치 (F 8초)', '[열차 03] 금고 개방 (F 5초)',
                '[밀수 02] 접선 인계 (F 3초)', '[호송 02] 금괴 인계 (F 3초)',
                '[밤 02] 금고 마차 털기 (F 5초)'}
    bad = []
    for n, (cond, ac, sn) in R.items():
        if 'Is Button Held' not in cond or n in REVIEWED:
            continue
        cvars = set(re.findall(r'Event Player\.(\w+)', cond))
        for v, src in sorted(sources(n)):
            if v not in cvars:
                continue
            # 그 토글이 일어나는 곳 자신이나 호출한 룰이 디바운스를 가져야 한다
            if own_debounce(src) or own_debounce(n):
                continue
            bad.append('%s -> %s 가 %s 를 토글' % (n, src, v))
    if bad:
        print('!! 버튼 홀드 재발동 위험 (디바운스 없음):')
        for b in bad[:10]:
            print('   ' + b)
    else:
        print('retrigger check: OK')


event_check(sys.argv[1])
retrigger_check(sys.argv[1])
