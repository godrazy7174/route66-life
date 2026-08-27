# patch139 (작업 1): 알림 줄 수정 유지
#  - HUD 삼항의 거짓 가지 Null -> Custom String("")  (평상시 "0" 표시 제거)
#  - 표시 시간 5초 -> 2.5초 / 6초 -> 3초
#  - NoticeMsg / TickerMsg 초기화 추가
import io

SRC = 'ROUTE66_LIFE_EN.ow'
lines = io.open(SRC, encoding='utf-8').read().split('\n')

def find_one(sub):
    idxs = [i for i, l in enumerate(lines) if sub in l]
    assert len(idxs) == 1, f'expected 1 match for {sub!r}, got {len(idxs)}'
    return idxs[0]

# ---- Edit 1: HUD false-branch Null -> empty string ----
i = find_one('Value In Array(Global Variable(NoticeEnd), Slot Of(Event Player)) ? Value In Array(Global Variable(NoticeMsg), Slot Of(Event Player)) : Null')
lines[i] = lines[i].replace(
    'Value In Array(Global Variable(NoticeMsg), Slot Of(Event Player)) : Null',
    'Value In Array(Global Variable(NoticeMsg), Slot Of(Event Player)) : Custom String("")')
j = find_one('Total Time Elapsed() < Global Variable(TickerEnd) ? Global Variable(TickerMsg) : Null')
lines[j] = lines[j].replace(
    'Global Variable(TickerMsg) : Null',
    'Global Variable(TickerMsg) : Custom String("")')

# ---- Edit 2: durations ----
n5 = n6 = 0
for k, l in enumerate(lines):
    if 'NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 5))' in l or 'NoticeEnd, Slot Of(Attacker), Add(Total Time Elapsed(), 5))' in l:
        lines[k] = l.replace('Add(Total Time Elapsed(), 5))', 'Add(Total Time Elapsed(), 2.5))'); n5 += 1
    elif 'TickerEnd, Add(Total Time Elapsed(), 6))' in l:
        lines[k] = l.replace('Add(Total Time Elapsed(), 6))', 'Add(Total Time Elapsed(), 3))'); n6 += 1
assert n5 == 22 and n6 == 22, (n5, n6)

# ---- Edit 3: initialize globals in [코어 01] ----
i3 = find_one('Disable Built-In Game Mode Announcer();')
ind = lines[i3][:len(lines[i3]) - len(lines[i3].lstrip('\t'))]
lines[i3:i3] = [
    ind + 'Set Global Variable(NoticeMsg, Empty Array);',
    ind + 'Set Global Variable(NoticeEnd, Empty Array);',
    ind + 'Set Global Variable(TickerMsg, Custom String(""));',
    ind + 'Set Global Variable(TickerEnd, 0);',
]

out = '\n'.join(lines)
assert out.count(': Null') == out.count(': Null')  # noop guard
assert 'NoticeMsg), Slot Of(Event Player)) : Custom String("")' in out
assert 'Global Variable(TickerMsg) : Custom String("")' in out
assert out.count('Add(Total Time Elapsed(), 2.5))') == 22
assert out.count('Add(Total Time Elapsed(), 3))') == 22
assert out.count('rule("') == 122
io.open(SRC, 'w', encoding='utf-8', newline='').write(out)
print('patch139 applied — notice 2.5s / ticker 3s / empty-string idle / globals initialized')
