# -*- coding: utf-8 -*-
"""모든 행동에 소리와 이펙트를 붙인다.

원칙
  실패/거절  둔탁한 소리, 붉은색       (돈 부족, 이미 있음, 지쳤다)
  구매/소액  가벼운 소리, 초록·노랑
  큰 사건    링 폭발 + 큰 소리, 전체 공개 (전직, 잭팟, 체포, 살해)
  정보 조회  아주 작은 소리            (시세, 소문, 게시판)
  위험 경고  대상에게 큰 경고음        (강도·체포 당하는 쪽)

카드 도박은 결과가 즉시 나와서 허무했다 -> 1.4초 뜸을 들이고 결과를 터뜨린다.
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
L = io.open(P, encoding='utf-8').read().split(chr(10))

def E(vis, kind, col, pos, r):
    return 'Play Effect(%s, %s, Color(%s), %s, %s);' % (vis, kind, col, pos, r)

EP, POS = 'Event Player', 'Position Of(Event Player)'
TGT, TPOS = 'Event Player.Target', 'Position Of(Event Player.Target)'
ALL = 'All Players(All Teams)'

FAIL  = [E(EP, 'Debuff Impact Sound', 'Red', POS, 45)]
BUY   = [E(EP, 'Buff Impact Sound', 'Lime Green', POS, 55), E(EP, 'Good Pickup Effect', 'Lime Green', POS, 1)]
JOB   = [E(ALL, 'Ring Explosion', 'Sky Blue', POS, 2.5), E(EP, 'Buff Explosion Sound', 'Sky Blue', POS, 160)]
INFO  = [E(EP, 'Debuff Impact Sound', 'Sky Blue', POS, 25)]
GAIN  = [E(EP, 'Buff Impact Sound', 'Yellow', POS, 50)]

TABLE = [
    (FAIL, ['돈이 부족합니다 ($30', '돈이 부족합니다 ($15', '돈이 부족합니다 ($10',
            '돈이 부족합니다 ($65', '돈이 부족합니다 ($25', '판돈이 부족합니다',
            '숙박비가 부족합니다', '이미 내 방이 있다', '이미 무법자다', '이미 가죽 배낭이 있다',
            '이미 말이 있다', '곡괭이가 이미 최고 등급이다', '무법자만 할 수 있다',
            '오늘은 그만 마셔라', '오늘은 더 잘 수 없다', '너무 지쳤다', '흔적이 끊겼다',
            '대상 없음 —', '빈털터리다', '놓쳤다']),
    (BUY,  ['육포를 샀다', '물통을 샀다', '육포 5개 묶음 구매']),
    (JOB,  ['전직 완료 — 광부', '전직 완료 — 사냥꾼', '전직 완료 — 현상금 사냥꾼']),
    (INFO, ['오늘 시세 — 원석', '소문 — 원석', '소문 — 오늘은 조용하다',
            '현상금 게시판 — 무법자', '밤에는 2배.']),
    (GAIN, ['정밀 탐사 —', '위스키 한 잔', '원석 +{0}', '계획 {0}/3']),
    ([E(EP, 'Good Explosion', 'Sky Blue', POS, 2), E(EP, 'Buff Explosion Sound', 'Sky Blue', POS, 130)],
           ['푹 잤다']),
    ([E(EP, 'Debuff Explosion Sound', 'Red', POS, 80)], ['치료비와 분실']),
    ([E(EP, 'Debuff Impact Sound', 'Red', POS, 60)], ['탈진 — 음식이나']),
    ([E(TGT, 'Debuff Explosion Sound', 'Sky Blue', TPOS, 160)], ['당신을 체포하려 한다']),
    ([E(TGT, 'Debuff Explosion Sound', 'Red', TPOS, 160)], ['총을 겨눴다']),
    ([E(TGT, 'Buff Impact Sound', 'Lime Green', TPOS, 90)], ['도망쳤다!']),
    ([E(ALL, 'Ring Explosion', 'Sky Blue', POS, 3), E(ALL, 'Buff Explosion Sound', 'Sky Blue', POS, 180)],
           ['을(를) 체포했다']),
    ([E(ALL, 'Ring Explosion', 'Yellow', 'Position Of(Attacker)', 3),
      E('Attacker', 'Buff Explosion Sound', 'Yellow', 'Position Of(Attacker)', 180)], ['처단했다']),
    ([E(ALL, 'Ring Explosion', 'Red', 'Position Of(Attacker)', 3),
      E(ALL, 'Debuff Explosion Sound', 'Red', 'Position Of(Attacker)', 180)], ['을(를) 살해했다']),
    ([E('Global Variable(Tmp)', 'Debuff Explosion Sound', 'Red',
        'Position Of(Global Variable(Tmp))', 170)], ['억울하지만 쫓기게 됐다']),
    ([E(EP, 'Buff Impact Sound', 'Yellow', POS, 70)], ['Set Player Variable(Event Player, DayStart']),
]

hits = 0
out = []
for ln in L:
    out.append(ln)
    for fx, keys in TABLE:
        if any(k in ln for k in keys):
            pad = ln[:len(ln) - len(ln.lstrip('\t'))]
            out.extend(pad + f for f in fx)
            hits += len(fx)
            break
L = out

# ── 카드 도박: 뜸 들이기 + 결과 연출 ───────────────────────────────
j = next(i for i, x in enumerate(L) if '술집에서 잭팟' in x)
r = max(i for i in range(j) if 'Random Integer(1, 100)' in L[i])
pad = L[r][:len(L[r]) - len(L[r].lstrip('\t'))]
L[r:r] = [pad + 'Set Player Variable(Event Player, Busy, 1);',
          pad + 'Small Message(Event Player, Custom String("카드를 돌린다..."));',
          pad + E(EP, 'Debuff Impact Sound', 'White', POS, 70),
          pad + 'Wait(1.4, Ignore Condition);']
j += 4
L[j+1:j+1] = [L[j+1][:len(L[j+1]) - len(L[j+1].lstrip('\t'))] + E(ALL, 'Buff Explosion Sound', 'Yellow', POS, 200)]
w = next(i for i in range(j, j + 12) if '이겼다 — $90' in L[i])
padw = L[w][:len(L[w]) - len(L[w].lstrip('\t'))]
L[w+1:w+1] = [padw + E(EP, 'Good Explosion', 'Lime Green', POS, 2),
              padw + E(EP, 'Buff Explosion Sound', 'Lime Green', POS, 130)]
o = next(i for i in range(w, w + 12) if '잃었다 — 다음 판은' in L[i])
pado = L[o][:len(L[o]) - len(L[o].lstrip('\t'))]
L[o+1:o+1] = [pado + E(EP, 'Bad Explosion', 'Red', POS, 1.5),
              pado + E(EP, 'Debuff Explosion Sound', 'Red', POS, 110)]
e = next(i for i in range(o, o + 8) if L[i].strip() == 'End;')
L[e+1:e+1] = [L[e][:len(L[e]) - len(L[e].lstrip('\t'))] + 'Set Player Variable(Event Player, Busy, 0);']

# ── 월드 이벤트 알림 (전역 룰이라 소리가 안 닿는다) ────────────────
EVT = '''rule("[이벤트 04] 사건 알림")
{
	event
	{
		Ongoing - Each Player;
		All;
		All;
	}

	conditions
	{
		Event Player.Init == 1;
		Global Variable(EventKind) != 0;
	}

	actions
	{
		Play Effect(Event Player, Ring Explosion Sound, Color(Yellow), Position Of(Event Player), 200);
		Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 2.5);
		Wait Until(Global Variable(EventKind) == 0, 200);
		Play Effect(Event Player, Debuff Impact Sound, Color(Gray), Position Of(Event Player), 60);
	}
}

'''
s = chr(10).join(L).replace('rule("[이벤트 03] 모래폭풍 효과")', EVT + 'rule("[이벤트 03] 모래폭풍 효과")', 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  효과 추가   : %d줄 (%d개 지점)' % (hits, sum(len(k) for _, k in TABLE)))
print('  카드 도박   : 1.4초 뜸 + 잭팟/승/패 각각 다른 연출')
print('  사건 알림   : 플레이어별 룰로 추가 (전역 룰은 소리가 안 닿음)')
