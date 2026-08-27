import io, re, sys

OPEN = ('If(', 'For Global Variable(', 'For Player Variable(', 'While(')
CLOSE = ('End;',)

src = io.open(sys.argv[1], encoding='utf-8').read()
bad = 0
for m in re.finditer(r'rule\("([^"]+)"\)', src):
    a = m.start()
    nxt = src.find('\nrule("', a + 5)
    blk = src[a: len(src) if nxt == -1 else nxt]
    name = m.group(1)
    depth = 0
    mind = 0
    for ln, line in enumerate(blk.split('\n'), 1):
        t = line.strip()
        if t.startswith(CLOSE):
            depth -= 1
            mind = min(mind, depth)
        elif t.startswith(OPEN):
            depth += 1
    if depth != 0 or mind < 0:
        bad += 1
        print('!! %-40s 최종깊이 %d, 최소깊이 %d' % (name, depth, mind))
if bad == 0:
    print('블록 균형: 모든 룰 정상 (If/For/While <-> End)')
else:
    print('불균형 룰 %d개' % bad)
