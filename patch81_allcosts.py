# -*- coding: utf-8 -*-
"""무소모 작업에 소모 부여 — 배달·소몰이·강탈·체포.

  배달 완료   허기 2 · 갈증 3 · 피로 4   (역마차장 특전 +5와 합산 → 실질 +1)
  소몰이 성공 허기 3 · 갈증 2.5 · 피로 5 (소를 잃으면 무소모)
  강탈·체포   허기 1 · 갈증 1 · 피로 3   (놓쳐도 시도 비용 — 채굴과 같은 원칙)
  게이트      수주 피로<4 · 소몰이 피로<5 · V시도 피로<3 거부
  간판        정거장·목장 '소모 없음' 교체, 초소·은신처에 시도 비용 추가
"""
import io

T = chr(9)
N = chr(10)
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
RN = chr(92) + 'r' + chr(92) + 'n'

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

def cost(depth, e, h, t):
    return (T*depth + 'Set Player Variable(Event Player, Energy, Max(0, Subtract(Event Player.Energy, %s)));' % e + N
          + T*depth + 'Set Player Variable(Event Player, Hunger, Max(0, Subtract(Event Player.Hunger, %s)));' % h + N
          + T*depth + 'Set Player Variable(Event Player, Thirst, Max(0, Subtract(Event Player.Thirst, %s)));' % t + N)

TIRED = 'Small Message(Event Player, Custom String("너무 지쳤다 — 자거나 한잔 걸쳐야 한다"));'
EFF_RED = 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);'

# ── 1. 배달 도착 정산에 소모 (특전 +5 다음에 차감) ─────────────────
sub('Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 5)));' + N + T*2 + 'End;' + N,
    'Set Player Variable(Event Player, Energy, Min(100, Add(Event Player.Energy, 5)));' + N + T*2 + 'End;' + N
    + cost(2, 4, 2, 3))

# ── 2. 소몰이 성공에 소모 ──────────────────────────────────────────
sub('Set Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 6)));' + N,
    'Set Global Variable(JerkyStock, Min(60, Add(Global Variable(JerkyStock), 6)));' + N
    + cost(3, 5, 3, 2.5))

# ── 3. 강탈/체포 — 게이트 + 시도 비용 ──────────────────────────────
sub(T*2 + 'End;' + N + T*2 + 'Set Player Variable(Event Player, Target, First Of(Sorted Array(',
    T*2 + 'End;' + N
    + T*2 + 'If(Event Player.Energy < 3);' + N
    + T*3 + TIRED + N + T*3 + EFF_RED + N + T*3 + 'Abort;' + N
    + T*2 + 'End;' + N
    + T*2 + 'Set Player Variable(Event Player, Target, First Of(Sorted Array(')
sub('Destroy Progress Bar HUD Text(Event Player.WorkBar);' + N + T*2 + 'If(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12',
    'Destroy Progress Bar HUD Text(Event Player.WorkBar);' + N
    + cost(2, 3, 1, 1)
    + T*2 + 'If(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 12')

# ── 4. 수주 게이트 (피로 4) ────────────────────────────────────────
sub('If(Event Player.MenuIdx == 0);' + N + T*4 + 'If(Event Player.HasParcel == 1);',
    'If(Event Player.MenuIdx == 0);' + N
    + T*4 + 'If(Event Player.Energy < 4);' + N
    + T*5 + TIRED + N + T*5 + EFF_RED + N
    + T*4 + 'Else If(Event Player.HasParcel == 1);')

# ── 5. 소몰이 게이트 (피로 5) ──────────────────────────────────────
sub('If(Event Player.MenuIdx == 0);' + N + T*4 + 'If(Event Player.CowOn == 1);',
    'If(Event Player.MenuIdx == 0);' + N
    + T*4 + 'If(Event Player.Energy < 5);' + N
    + T*5 + TIRED + N + T*5 + EFF_RED + N
    + T*4 + 'Else If(Event Player.CowOn == 1);')

# ── 6. 간판 갱신 ───────────────────────────────────────────────────
sub('털리면 빼앗긴다' + RN + '허기·갈증·피로 소모 없음' + RN,
    '털리면 빼앗긴다' + RN + '배달 완료 — 허기 2 · 갈증 3 · 피로 4' + RN)
sub('120초 제한' + RN + '허기·갈증·피로 소모 없음' + RN,
    '120초 제한' + RN + '몰이 성공 — 허기 3 · 갈증 2.5 · 피로 5' + RN)
sub('수배범을 잡으면 그 목값을 갖는다' + RN,
    '수배범을 잡으면 그 목값을 갖는다' + RN + '체포 시도 — 허기 1 · 갈증 1 · 피로 3' + RN)
sub('강탈과 습격이 너를 무법자로 만든다' + RN,
    '강탈과 습격이 너를 무법자로 만든다' + RN + '강탈 시도 — 허기 1 · 갈증 1 · 피로 3' + RN, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('전 작업 소모 부여 완료: 배달·소몰이·강탈·체포 + 게이트 + 간판')
