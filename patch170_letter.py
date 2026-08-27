# -*- coding: utf-8 -*-
"""[파발 02] 샛길 -> 겸사겸사 편지 한 통.

샛길은 배달(표식까지 달리기) 위에 표식까지 달리기를 한 번 더 얹은 중복 구조였고
보상 $12는 우회할 값어치가 없었다. 목표를 '좌표'에서 '사람'으로 바꾼다.

- 평범한 화물(HasParcel == 1)일 때만 발동. 값나가는 화물(== 2)은 그림자 강도 담당.
- 배달 한 건당 한 번만 (Loop If 제거).
- 좌표를 새로 찍지 않으므로 배치 버그가 구조적으로 불가능하다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()

start = src.index('rule("[파발 02] 흔들리는 화물")')
end = src.index('rule("[파발 03] 그림자 강도")')

NEW = '''rule("[파발 02] 겸사겸사 편지 한 통")
{
\tevent
\t{
\t\tOngoing - Each Player;
\t\tAll;
\t\tAll;
\t}

\tconditions
\t{
\t\tIs Dummy Bot(Event Player) == False;
\t\tEvent Player.Init == 1;
\t\tEvent Player.Busy == 0;
\t\tEvent Player.HasParcel == 1;
\t\tIs Alive(Event Player) == True;
\t}

\tactions
\t{
\t\tWait(Random Real(7, 14), Ignore Condition);
\t\tIf(And(And(Event Player.HasParcel == 1, Event Player.Busy == 0), Is Alive(Event Player)));
\t\t\tSet Player Variable(Event Player, DialTgt, Random Value In Array(Filtered Array(All Players(Team 1), And(And(Current Array Element != Event Player, Is Dummy Bot(Current Array Element) == False), And(Is Alive(Current Array Element), Player Variable(Current Array Element, TutOn) == 0)))));
\t\t\tIf(Entity Exists(Event Player.DialTgt));
\t\t\t\tCreate Icon(Event Player, Event Player.DialTgt, Flag, Visible To and Position, Color(Sky Blue), True);
\t\t\t\tSet Player Variable(Event Player, DialCur, Last Created Entity());
\t\t\t\tCreate Icon(Event Player.DialTgt, Event Player, Flag, Visible To and Position, Color(Sky Blue), True);
\t\t\t\tSet Player Variable(Event Player, DialPin, Last Created Entity());
\t\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player), Custom String("겸사겸사 편지 한 통 — {0}에게 전해라", Event Player.DialTgt));
\t\t\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player), Add(Total Time Elapsed(), 3));
\t\t\t\tSet Global Variable At Index(NoticeMsg, Slot Of(Event Player.DialTgt), Custom String("{0}이(가) 네게 편지를 가져오고 있다", Event Player));
\t\t\t\tSet Global Variable At Index(NoticeEnd, Slot Of(Event Player.DialTgt), Add(Total Time Elapsed(), 3));
\t\t\t\tPlay Effect(Event Player, Buff Impact Sound, Color(Sky Blue), Position Of(Event Player), 45);
\t\t\t\tWait Until(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.DialTgt)) < 4, Not(Entity Exists(Event Player.DialTgt))), Or(Event Player.HasParcel == 0, Not(Is Alive(Event Player)))), 45);
\t\t\t\tDestroy Icon(Event Player.DialCur);
\t\t\t\tDestroy Icon(Event Player.DialPin);
\t\t\t\tIf(And(Entity Exists(Event Player.DialTgt), And(Distance Between(Position Of(Event Player), Position Of(Event Player.DialTgt)) < 4, Is Alive(Event Player))));
\t\t\t\t\tModify Player Variable(Event Player, Money, Add, 40);
\t\t\t\t\tModify Player Variable(Event Player, Earned, Add, 40);
\t\t\t\t\tSet Player Variable(Event Player, Fame, Min(100, Add(Event Player.Fame, 2)));
\t\t\t\t\tModify Player Variable(Event Player.DialTgt, Money, Add, 20);
\t\t\t\t\tModify Player Variable(Event Player.DialTgt, Earned, Add, 20);
\t\t\t\t\tSmall Message(Event Player, Custom String("편지를 건넸다 +$40 · 명성 +2"));
\t\t\t\t\tSmall Message(Event Player.DialTgt, Custom String("{0}에게서 편지를 받았다 +$20", Event Player));
\t\t\t\t\tPlay Effect(Event Player, Ring Explosion, Color(Sky Blue), Position Of(Event Player), 1.2);
\t\t\t\t\tPlay Effect(Event Player.DialTgt, Ring Explosion, Color(Sky Blue), Position Of(Event Player.DialTgt), 1.2);
\t\t\t\tElse;
\t\t\t\t\tSmall Message(Event Player, Custom String("편지는 주머니에서 구겨졌다"));
\t\t\t\tEnd;
\t\t\tEnd;
\t\tEnd;
\t}
}

'''

src = src[:start] + NEW + src[end:]
# 튜토리얼 슬라이드 문구도 함께 교체
tut_old = r"세 발로 떨쳐내라.\r\n샛길 빛기둥은 7초 안에 밟아라."
tut_new = r"세 발로 떨쳐내라.\r\n편지가 딸려오면 표식이 붙은 사람에게 건네라."
assert src.count(tut_old) == 1, '튜토리얼 문구 %d건' % src.count(tut_old)
src = src.replace(tut_old, tut_new)
print('  튜토리얼 문구 교체 (%d자 -> %d자)' % (len(tut_old), len(tut_new)))

assert '샛길' not in src, '샛길 잔여: %r' % src[src.index('샛길') - 60: src.index('샛길') + 30]
io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('[파발 02] 샛길 -> 편지 한 통 교체 완료')
