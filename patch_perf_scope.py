# -*- coding: utf-8 -*-
"""패치노트 7 — "워크샵 스크립트를 과도하게 불러와 서버가 종료되었습니다" 대책.

## 무엇이 부하인가

워크샵의 프레임 예산을 먹는 것은 **룰 인스턴스 수 x 조건 평가**다.
이 모드는 `Ongoing - Each Player` 룰이 92개인데, 그중 **85개가 팀을 `All` 로 잡고 있다.**
`All` 이면 1팀 8명뿐 아니라 **2팀의 야수 3 + 쥐 1, 봇 4기에도 인스턴스가 생긴다.**

    현재: 85 x 12 = 1,020 인스턴스가 매 프레임 조건 평가

그런데 그 85개 중 **73개는 조건에 이미 `Is Dummy Bot(Event Player) == False` 또는
`Event Player.Init == 1` 이 들어 있어 봇에서는 절대 통과하지 못한다.**
(봇은 `Init` 이 0 이다 — 4장 6번) 즉 봇 4기 몫의 평가는 **처음부터 전부 헛일**이었다.

## 무엇을 하는가

그 73개의 이벤트 팀을 `All` -> `Team 1` 로 좁힌다.

    이후: 73 x 8 + 12 x 12 = 728 인스턴스 (약 29% 감소)

**동작은 한 글자도 바뀌지 않는다.** 지금도 봇에서는 조건이 통과하지 못하므로,
평가를 아예 안 하게 만들 뿐이다. 조건 줄은 그대로 둔다 —
지우면 테스트 빌드(1팀에 봇을 세운다)와 의미가 달라지고, 방어선도 사라진다.

## 남는 위험

이것으로 부족하면 다음 후보는 **대야수의 30배 크기**다. `ref/actions.ts` 의
`startScalingSize` 가 "large players placed into complex environments will severely
impact server load" 라고 명시하고 있고, 이미 `Disable Movement Collision With
Environment` 를 걸었지만 `includeFloors` 는 False 라 바닥 충돌은 남아 있다.
크기를 줄이는 것이 다음 레버다 (전설의 야수 50배도 같은 문제를 갖는다).

그래서 **서버 부하를 눈으로 보게** 진단 표시를 함께 넣는다 —
`[코어 08]` 알림 줄 아래에 평균/최고 부하를 띄워, 다음 실기에서 숫자를 가져올 수 있게 한다.
"""
import io
import re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ── 조건이 이미 봇을 배제하는 Each Player 룰을 Team 1 로 좁힌다 ──
rules = s.split('\nrule(')
changed = []
for i in range(1, len(rules)):
    r = rules[i]
    name = r.split('"')[1] if '"' in r else '?'
    head, sep, rest = r.partition('\tconditions')
    if not sep or 'Ongoing - Each Player' not in head:
        continue
    m = re.search(r'\n\tconditions\n\t\{(.*?)\n\t\}', r, re.S)
    if not m:
        continue
    cond = m.group(1)
    if ('Is Dummy Bot(Event Player) == False' not in cond
            and 'Event Player.Init == 1' not in cond):
        continue
    old_ev = 'Ongoing - Each Player;\n\t\tAll;\n\t\tAll;'
    if old_ev not in head:
        continue
    rules[i] = head.replace(old_ev, 'Ongoing - Each Player;\n\t\tTeam 1;\n\t\tAll;', 1) + sep + rest
    changed.append(name)

assert len(changed) >= 70, len(changed)
s = '\nrule('.join(rules)

# ── 서버 부하 진단 표시 (호스트에게만) ─────────────────────────
anchor = 'rule("[알림 01] 알림 줄 생성")'
assert s.count(anchor) == 1
s = s.replace(anchor, '''rule("[진단 01] 서버 부하 표시 — 호스트만")
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

''' + anchor)

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('좁힌 룰: %d개' % len(changed))
for n in changed:
    print('   ', n)
