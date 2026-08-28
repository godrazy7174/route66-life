# -*- coding: utf-8 -*-
"""쥐떼 첫 습격이 게임 시작과 동시에 터지던 문제 — RatNext 를 초기화한다.

증상: 월드 구축이 끝나 Ready 가 1 이 되는 그 프레임에 쥐떼가 몰려온다.
환영 메시지("66번 국도에 오신 것을 환영합니다")와 같은 프레임이다.

원인: RatNext 와 RatOn 이 어디서도 초기화되지 않는다. 워크샵 전역의 기본값은 0 이라
[쥐 01] 의 세 조건이 Ready = 1 이 되는 순간 동시에 참이 된다.

    Global Variable(Ready) == 1;                        <- [코어 01] 이 방금 켬
    Global Variable(RatOn) == 0;                        <- 기본값 0
    Total Time Elapsed() >= Global Variable(RatNext);   <- 0 >= 0

RatNext 를 쓰는 곳은 [쥐 01] 꼬리와 [쥐 04] 퇴치뿐인데, 둘 다 첫 습격이 끝난 뒤에야
실행되므로 첫 발동을 막지 못한다. 이 동작 자체는 8-3 이전부터 있었다.

8-3(육포 우선 · 버티기)이 이 결함의 대가를 키웠기 때문에 지금 고친다.
JerkyStock 은 15 로 시작하고 [쥐 02] 가 잡화점 9m 안에서 초당 2 씩 깎으므로 약 8초면
0 이 된다. 그러면 8-3 의 지속 규칙이 발동해 쥐가 "죽거나 사람을 잡을 때까지" 남는데,
시작 직후에는 전원이 [튜토리얼 01] 로 TutOn == 1 이고 RatTgt 필터가 TutOn == 0 을
요구하므로 표적이 없다. RatKill 이 영원히 서지 않아 쥐가 무한정 상주하게 된다.
즉 매 판 시작 10초 만에 육포가 비고, 튜토리얼을 마친 첫 사람이 물려 죽을 때까지
쥐가 마을에 남는다.

해결: [코어 01] 에서 RatNext 를 습격 간격과 같은 Random Real(240, 600) 으로 잡는다.
새 규칙을 만드는 것이 아니라 첫 발동에도 같은 간격을 적용하는 것이다.
튜토리얼이 끝날 시간이 생긴다.

RatOn 은 건드리지 않는다 — 기본값 0 이 이미 의도한 값이고, 여기서 0 을 다시 넣어도
동작이 달라지지 않는다. 최소 수정으로 둔다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()


def sub(old, new, n=1):
    global s
    assert s.count(old) == n, (old[:60], s.count(old))
    s = s.replace(old, new)


# JerkyStock 초기화 바로 옆에 둔다 — 쥐가 노리는 것이 육포라 같은 자리가 읽기 좋다.
sub("""		Set Global Variable(JerkyStock, 15);
""", """		Set Global Variable(JerkyStock, 15);
		Set Global Variable(RatNext, Add(Total Time Elapsed(), Random Real(240, 600)));
""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
