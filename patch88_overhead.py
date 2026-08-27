# -*- coding: utf-8 -*-
"""머리 위 표기 확장 — 칭호·이름 + 직업 Lv·명성·악명 2줄, 전원에게 표시.

  - 기존: 『칭호』 이름 1줄, 타인 전용 -> 2줄, 본인 포함 전원
  - 칭호 우선순위: 수배 중(붉음) > 66번 국도의 재건자 > 소지금 칭호
  - 직업명은 승급 반영(보안관 등), 레벨·명성·악명 실시간 재평가
  - 좌측 상단 HUD의 칭호·직업·명성 줄은 머리 위로 이전 (날짜·소지금 유지)
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
RN = chr(92) + 'r' + chr(92) + 'n'
CS = lambda t: 'Custom String("%s")' % t

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:80], s.count(old))
    s = s.replace(old, new, cnt)

MONEYTIER = ('Value In Array(Array(%s), Add(Add(Add(Add(Event Player.Money >= 300, Event Player.Money >= 1000), '
    'Event Player.Money >= 2500), Event Player.Money >= 6000), Event Player.Money >= 15000))'
    % ', '.join(CS(x) for x in ['떠돌이', '일꾼', '정착민', '유지', '거상', '66번 국도의 주인']))
TITLE = ('Event Player.Bounty > 0 ? Custom String("수배 중") : Custom String("{0}", '
    'Event Player.Rebuild >= 5 ? Custom String("66번 국도의 재건자") : ' + MONEYTIER + ')')
JOBNAME = ('Value In Array(Event Player.Adv, Event Player.Job) == 1 ? Value In Array(Array(%s), Event Player.Job) : Value In Array(Array(%s), Event Player.Job)'
    % (', '.join(CS(x) for x in ['뜨내기', '광산주', '맹수 사냥꾼', '보안관', '갱단 두목', '역마차장', '목장주']),
       ', '.join(CS(x) for x in ['뜨내기', '광부', '사냥꾼', '현상금 사냥꾼', '무법자', '파발꾼', '목동'])))
LEVEL = 'Add(1, Round To Integer(Divide(Value In Array(Event Player.JobXP, Event Player.Job), 250), Down))'

OLD_CREATE = ('Create In-World Text(Remove From Array(All Players(All Teams), Event Player), '
    'Custom String("『 {0} 』 {1}", Event Player.Bounty > 0 ? Custom String("수배 중") : ' + MONEYTIER
    + ', Event Player), Event Player, 1.1, Clip Against Surfaces, Visible To Position String and Color, '
    'Event Player.Bounty > 0 ? Color(Red) : Color(White), Default Visibility);')
NEW_CREATE = ('Create In-World Text(All Players(All Teams), '
    'Custom String("{0}' + RN + '{1}", '
    'Custom String("『 {0} 』 {1}", ' + TITLE + ', Event Player), '
    'Custom String("{0} Lv.{1}   {2}", ' + JOBNAME + ', ' + LEVEL + ', '
    'Custom String("명성 {0} · 악명 {1}", Event Player.Fame, Event Player.Noto))), '
    'Event Player, 1, Clip Against Surfaces, Visible To Position String and Color, '
    'Event Player.Bounty > 0 ? Color(Red) : Color(White), Default Visibility);')
sub(OLD_CREATE, NEW_CREATE, 2)

# 좌측 상단 HUD의 세 번째 텍스트(칭호·직업·명성 줄) 제거 -> Null
START = 'Custom String("{0}   {1}", Custom String("『 {0} 』"'
END = 'Custom String("명성 {0} · 악명 {1}", Local Player.Fame, Local Player.Noto)))'
assert s.count(START) == 1 and s.count(END) == 1
a = s.index(START)
b = s.index(END) + len(END)
s = s[:a] + 'Null' + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('머리 위 2줄 표기 적용, HUD 이전 완료')
