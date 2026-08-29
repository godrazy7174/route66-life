# -*- coding: utf-8 -*-
"""[진단 01] 서버 부하 표시를 끈다 (지시).

부하 진단은 8-7 에서 "다음 실기에서 숫자를 가져오기 위해" 넣은 것이라
평상시에는 화면만 차지한다. 다시 필요해지면 아래 룰을 [알림 01] 앞에 그대로
붙이면 된다 — Host Player() 에게만 보이고 다른 액션에는 손대지 않는다.

    rule("[진단 01] 서버 부하 표시 — 호스트만")
    {
        event
        {
            Ongoing - Global;
        }

        conditions
        {
            Global Variable(Ready) == 1;
        }

        actions
        {
            Create HUD Text(Local Player == Host Player() ? Local Player : False, Null, Null, Custom String("부하 {0} · 평균 {1} · 최고 {2}", Round To Integer(Server Load(), To Nearest), Round To Integer(Server Load Average(), To Nearest), Round To Integer(Server Load Peak(), To Nearest)), Left, 12, Color(White), Color(White), Color(Green), Visible To Sort Order String and Color, Default Visibility);
        }
    }

진단 표시가 없어도 신호는 받을 수 있다 — `[코어 10] 서버 부하 보호` 가 부하 230 을
넘으면 「서버가 버겁다」를, 190 아래로 내려오면 「서버가 다시 안정됐다」를 띄운다.
크래시 직전에 이 자막이 떴는지만 봐도 부하 문제인지 아닌지 갈린다.

핸들을 변수에 담지 않았지만 룰이 한 번만 실행되고 판이 끝날 때까지 유지되는
전역 HUD 하나라 누수가 아니다 (4장 9번의 '플레이어별 HUD' 금지와는 다른 경우다).
"""
import io
import re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

m = re.search(r'rule\("\[진단 01\][^\n]*"\)\n\{.*?\n\}\n\n', s, re.S)
assert m, '[진단 01] 룰을 찾지 못했다'
assert s.count('Server Load') == 6, s.count('Server Load')  # 진단 3 + [월드 04] 1 + [코어 10] 2

s = s[:m.start()] + s[m.end():]
assert 'Server Load Peak' not in s and 'Server Load Average' not in s
assert s.count('Server Load()') == 3, '[월드 04] 의 적응 대기와 [코어 10] 의 부하 보호는 남겨야 한다'

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
