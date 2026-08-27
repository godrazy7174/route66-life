# -*- coding: utf-8 -*-
"""전수 조사 1차 — 확인된 버그 수정.

1) 은행 뒷문 다이얼이 배달/소몰이 중에도 열린다.
   다이얼은 DialTgt/DialPin/DialCur를 숫자로 덮어쓰는데, 같은 세 변수를
   [파발 02] 편지가 아이콘 핸들로, [목동 04] 늑대가 좌표/카운터로 쓴다.
   결과: 편지 아이콘 2개가 파괴되지 못하고 화면에 영구히 남고(누수),
        늑대 표식이 엉뚱한 곳으로 간다.
   -> 짐(화물·소)을 진 채로는 금고를 못 열게 막고 이유를 알린다.

2) 편지 수령자가 죽어 있어도 보상이 지급된다. 생존 확인을 추가한다.

3) [쥐 04] 쥐를 잡아도 RatNext가 갱신되지 않는다. [쥐 01]이 Wait(45)를
   끝낼 때까지 '다음 습격 시각'이 과거로 남아 있어, 재진입 타이밍이
   룰 실행 상태에만 의존한다. 처치 시점에 바로 밀어준다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()


def once(old, new, tag):
    global src
    assert src.count(old) == 1, '%s: %d건' % (tag, src.count(old))
    src = src.replace(old, new)
    print('  OK %s' % tag)


# 1) 은행 다이얼 게이트
T = '\t' * 3
bank_open = ('If(And(And(Event Player.Zone == 9, Global Variable(IsNight) == 1), '
             'And(And(Global Variable(RebuildMax) >= 3, Global Variable(Day) >= Global Variable(BankLockDay)), '
             'Event Player.JailOn == 0)));\n')
assert src.count(bank_open) == 1
guard_open = (bank_open
              + T + '\tIf(Or(Event Player.HasParcel >= 1, Event Player.CowOn >= 1));\n'
              + T + '\t\tSmall Message(Event Player, Custom String("짐을 진 채로는 금고를 못 딴다 — 먼저 일을 끝내라"));\n'
              + T + '\t\tPlay Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 45);\n'
              + T + '\tElse;\n')
src = src.replace(bank_open, guard_open)

# 은행 블록의 마지막 줄 뒤에 End; 를 넣어 새 If를 닫는다
last = '\t\t\t\tSmall Message(Event Player, Custom String("아직은 조용하다 — 해정하는 순간 마을이 깬다"));\n'
assert src.count(last) == 1
src = src.replace(last, last + T + '\tEnd;\n')
# 은행 본문 10줄을 한 단계 더 들여쓴다
body = [
    'Set Player Variable(Event Player, Busy, 1);',
    'Set Player Variable(Event Player, DialOn, 1);',
    'Set Player Variable(Event Player, DialTgt, Random Integer(0, 9));',
    'Set Player Variable(Event Player, DialPin, 1);',
    'Set Player Variable(Event Player, DialCur, 0);',
    'Destroy HUD Text(Event Player.KeyHud);',
]
i = src.index(guard_open) + len(guard_open)
j = src.index(T + '\tEnd;\n', i)
seg = src[i:j]
seg2 = ''.join('\t' + ln + '\n' if ln.strip() else ln + '\n' for ln in seg.split('\n')[:-1])
src = src[:i] + seg2 + src[j:]
for b in body:
    assert '\t\t\t\t\t' + b in src, '들여쓰기 실패: %s' % b
print('  OK 은행 다이얼 — 화물·소 운반 중 차단')

# 2) 편지 수령자 생존 확인
once('If(And(Entity Exists(Event Player.DialTgt), And(Distance Between(Position Of(Event Player), '
     'Position Of(Event Player.DialTgt)) < 4, Is Alive(Event Player))));',
     'If(And(And(Entity Exists(Event Player.DialTgt), Is Alive(Event Player.DialTgt)), '
     'And(Distance Between(Position Of(Event Player), Position Of(Event Player.DialTgt)) < 4, Is Alive(Event Player))));',
     '편지 — 수령자 생존 확인')

# 3) 쥐 처치 시 다음 습격 시각 갱신
once('\t\tSet Global Variable(RatOn, 0);\n\t\tDestroy Icon(Global Variable(RatFx));\n',
     '\t\tSet Global Variable(RatOn, 0);\n'
     '\t\tSet Global Variable(RatNext, Add(Total Time Elapsed(), Random Real(240, 600)));\n'
     '\t\tDestroy Icon(Global Variable(RatFx));\n',
     '쥐 처치 — RatNext 갱신')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('done')
