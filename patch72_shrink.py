# -*- coding: utf-8 -*-
"""요소 수 감축 (기능 무손실) — '설정 크기' 한도는 바이트가 아니라 요소 수다.

A. 튜토리얼 카메라 15블록 -> For 루프 1블록 (장면 배열 참조)
   TutStep 은 튜토리얼 전용 플레이어 변수라 루프 변수로 안전.
   루프 종료 후 TutStep=15 가 HUD 배열을 벗어나므로 조회에 Min(14, ...) 클램프.
B. 낮/밤 광기둥 파괴 19줄 x 2룰 -> For 루프 (내부에 Wait 없음 = 원자적, 공용 Idx 안전)
C. DoHunt 야수 3중 전개 -> For 루프 (내부에 Wait 없음 = 안전)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ A. 튜토리얼 루프화 ════════════════════════════════════════════
SEQ = 'Array(0, 2, 3, 0, 1, 6, 8, 7, 11, 12, 4, 10, 0, 5, 9)'
POS = 'Value In Array(Global Variable(LocPos), Value In Array(%s, Event Player.TutStep))' % SEQ
a = s.index('\t\tStart Camera(Event Player, Ray Cast Hit Position(Add(Value In Array(Global Variable(LocPos), 0), Vector(0, 2, 0))')
end_key = '\t\tWait Until(Event Player.TutSkip == 1, 7);\n\t\tDestroy HUD Text(Event Player.TutHud);'
b = s.index(end_key) + len('\t\tWait Until(Event Player.TutSkip == 1, 7);\n')
LOOP = (T*2 + 'For Player Variable(Event Player, TutStep, 0, 15, 1);' + NLC
      + T*3 + 'Set Player Variable(Event Player, TutSkip, 0);' + NLC
      + T*3 + 'Start Camera(Event Player, Ray Cast Hit Position(Add(%s, Vector(0, 2, 0)), Add(%s, Vector(0, 6, 9)), Empty Array, All Players(All Teams), False), %s, 0);' % (POS, POS, POS) + NLC
      + T*3 + 'Wait Until(Event Player.TutSkip == 1, 7);' + NLC
      + T*2 + 'End;' + NLC)
s = s[:a] + LOOP + s[b:]
# HUD 조회 클램프 (제목/본문 2곳)
n = s.count('), Event Player.TutStep), ')
assert n == 2, n
s = s.replace('), Event Player.TutStep), ', '), Min(14, Event Player.TutStep)), ')

# ══ B. 광기둥 파괴 루프화 (낮·밤 2룰) ═════════════════════════════
DESTROYS = ''.join(T*2 + 'Destroy Effect(Value In Array(Global Variable(SignIds), %d));' % i + NLC for i in range(19))
LOOPD = (T*2 + 'For Global Variable(Idx, 0, 19, 1);' + NLC
       + T*3 + 'Destroy Effect(Value In Array(Global Variable(SignIds), Global Variable(Idx)));' + NLC
       + T*2 + 'End;' + NLC)
n = s.count(DESTROYS)
assert n == 2, n
s = s.replace(DESTROYS, LOOPD)

# ══ C. DoHunt 3중 전개 루프화 ═════════════════════════════════════
a = s.index('\t\tIf(Count Of(Event Player.Target) > 0);')
b = s.index('\t\tPlay Effect(Event Player, Explosion Sound, Color(Orange), Position Of(Event Player), 190);')
TGT = 'Value In Array(Event Player.Target, Event Player.Idx)'
BODY = (T*2 + 'For Player Variable(Event Player, Idx, 0, Count Of(Event Player.Target), 1);' + NLC
 + T*3 + 'Set Player Variable(%s, RevealEnd, Add(Total Time Elapsed(), 30));' % TGT + NLC
 + T*3 + 'Set Player Variable(%s, Roll, Random Integer(1, 100));' % TGT + NLC
 + T*3 + 'Set Player Variable(%s, Giant, Player Variable(%s, Roll) <= Add(11, Multiply(10, Event Player.Roll)) ? 1 : 0);' % (TGT, TGT) + NLC
 + T*3 + 'If(Player Variable(%s, Roll) <= Add(1, Event Player.Roll));' % TGT + NLC
 + T*4 + 'Set Player Variable(%s, Giant, 2);' % TGT + NLC
 + T*3 + 'End;' + NLC
 + T*3 + 'If(Player Variable(%s, Giant) == 2);' % TGT + NLC
 + T*4 + 'Set Max Health(%s, 1000);' % TGT + NLC
 + T*4 + 'Remove All Health Pools From Player(%s);' % TGT + NLC
 + T*4 + 'Add Health Pool To Player(%s, Health, 2500, True, True);' % TGT + NLC
 + T*4 + 'Start Scaling Player(%s, 50, False);' % TGT + NLC
 + T*4 + 'Big Message(All Players(All Teams), Custom String("전설의 야수가 깨어났다!! 보상 50배"));' + NLC
 + T*4 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(%s), 14);' % TGT + NLC
 + T*4 + 'Play Effect(All Players(All Teams), Explosion Sound, Color(Red), Position Of(%s), 250);' % TGT + NLC
 + T*3 + 'Else If(Player Variable(%s, Giant) == 1);' % TGT + NLC
 + T*4 + 'Set Max Health(%s, 200);' % TGT + NLC
 + T*4 + 'Start Scaling Player(%s, 2.4, False);' % TGT + NLC
 + T*4 + 'Big Message(All Players(All Teams), Custom String("거대한 야수다! 체력 5배 — 가죽도 5배"));' + NLC
 + T*4 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Red), Position Of(%s), 6);' % TGT + NLC
 + T*3 + 'Else;' + NLC
 + T*4 + 'Set Max Health(%s, 40);' % TGT + NLC
 + T*4 + 'Stop Scaling Player(%s);' % TGT + NLC
 + T*3 + 'End;' + NLC
 + T*3 + 'Clear Status(%s, Phased Out);' % TGT + NLC
 + T*3 + 'Set Invisible(%s, None);' % TGT + NLC
 + T*3 + 'Teleport(%s, Nearest Walkable Position(Add(Add(Position Of(Event Player), Multiply(Facing Direction Of(Event Player), 7)), Vector(Random Real(-4, 4), 0, Random Real(-4, 4)))));' % TGT + NLC
 + T*3 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(%s), 3);' % TGT + NLC
 + T*2 + 'End;' + NLC)
s = s[:a] + BODY + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('요소 감축: 튜토리얼 루프 / 파괴 루프 x2 / 야수 소환 루프')
