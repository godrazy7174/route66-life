# -*- coding: utf-8 -*-
"""[2] 30초가 지나도 안 숨는 문제
    은신 룰이 '조건이 거짓 -> 참으로 바뀌는 순간'에만 도는 구조였다.
    이 전환을 놓치면 영영 안 숨는다. 확실하게 주기 검사로 바꾼다.
    이미 숨은 상태면 아무 것도 하지 않으므로 반복해도 무해하다.

[4] 추적하면 세 마리 전부 나오게
    한 마리만 고르던 것을 살아있는 야수 전부로 바꾼다.
    한 자리에 겹치지 않도록 조금씩 흩어서 내려놓는다.
    반복문 대신 0/1/2 를 펼쳐 쓴다 — 이 스크립트에서 반복 변수는
    다른 룰과 공유돼 여러 번 사고를 냈다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

# ══ [2] 은신을 주기 검사로 ════════════════════════════════════════
a = s.index('rule("[직업 03] 야수 은신")')
b = s.index('rule("[직업 03-3] 야수 배회")')
HIDE = '''rule("[직업 03] 야수 은신")
{
	event
	{
		Ongoing - Each Player;
		Team 2;
		All;
	}

	conditions
	{
		Is Dummy Bot(Event Player) == True;
		Global Variable(Ready) == 1;
		Is Alive(Event Player) == True;
	}

	actions
	{
		If(And(Total Time Elapsed() >= Event Player.RevealEnd, Has Status(Event Player, Phased Out) == False));
			Set Max Health(Event Player, 40);
			Set Ability 1 Enabled(Event Player, False);
			Set Ability 2 Enabled(Event Player, False);
			Set Ultimate Ability Enabled(Event Player, False);
			Set Primary Fire Enabled(Event Player, False);
			Set Secondary Fire Enabled(Event Player, False);
			Destroy Icon(Event Player.IcoId);
			Set Player Variable(Event Player, IcoId, 0);
			Stop Throttle In Direction(Event Player);
			Set Move Speed(Event Player, 0);
			Set Invisible(Event Player, All);
			Set Status(Event Player, Null, Phased Out, 9999);
			Teleport(Event Player, Nearest Walkable Position(Add(Value In Array(Global Variable(LocPos), 6), Vector(Random Real(-7, 7), 0, Random Real(-7, 7)))));
		End;
		Wait(0.4, Ignore Condition);
		Loop();
	}
}

'''
s = s[:a] + HIDE + s[b:]

# ══ [4] 추적하면 전부 ═════════════════════════════════════════════
def one(n):
    t = 'Value In Array(Event Player.Target, %d)' % n
    return ('\t\tIf(Count Of(Event Player.Target) > %d);\n'
            '\t\t\tSet Player Variable(%s, RevealEnd, Add(Total Time Elapsed(), 30));\n'
            '\t\t\tClear Status(%s, Phased Out);\n'
            '\t\t\tSet Invisible(%s, None);\n'
            '\t\t\tTeleport(%s, Nearest Walkable Position(Add(Add(Position Of(Event Player), '
            'Multiply(Facing Direction Of(Event Player), 7)), Vector(Random Real(-4, 4), 0, Random Real(-4, 4)))));\n'
            '\t\t\tPlay Effect(All Players(All Teams), Ring Explosion, Color(Orange), Position Of(%s), 3);\n'
            '\t\tEnd;\n' % (n, t, t, t, t, t))

OLDSEL = s[s.index('\t\tSet Player Variable(Event Player, Target, First Of(Sorted Array(Filtered Array(All Players(Team 2)'):]
OLDSEL = OLDSEL[:OLDSEL.index(chr(10)) + 1]
NEWSEL = ('\t\tSet Player Variable(Event Player, Target, Filtered Array(All Players(Team 2), '
          'And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))));\n')
s = s.replace(OLDSEL, NEWSEL, 1)

s = s.replace('\t\tIf(Not(Entity Exists(Event Player.Target)));\n\t\t\tSmall Message(Event Player, Custom String("흔적이 끊겼다 — 잠시 뒤 다시 시도해라"));',
              '\t\tIf(Count Of(Event Player.Target) == 0);\n\t\t\tSmall Message(Event Player, Custom String("흔적이 끊겼다 — 잠시 뒤 다시 시도해라"));', 1)

# 기존 단일 대상 처리 5줄을 세 마리 전개로 교체
i = s.index('\t\tSet Player Variable(Event Player.Target, RevealEnd, Add(Total Time Elapsed(), 30));')
j = s.index('\t\tPlay Effect(Event Player, Explosion Sound, Color(Orange), Position Of(Event Player.Target), 190);')
s = s[:i] + one(0) + one(1) + one(2) + s[j:]
s = s.replace('Play Effect(Event Player, Explosion Sound, Color(Orange), Position Of(Event Player.Target), 190);',
              'Play Effect(Event Player, Explosion Sound, Color(Orange), Position Of(Event Player), 190);', 1)
s = s.replace('Custom String("크아앙! 엄청 무서운 야수가 나타났다!")',
              'Custom String("크아앙! 엄청 무서운 야수가 나타났다!")', 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('[2] 은신 : 전환 감지 -> 0.4초 주기 검사 (이미 숨었으면 무시)')
print('[4] 추적 : 살아있는 야수 전부를 눈앞에 흩어 소환')
