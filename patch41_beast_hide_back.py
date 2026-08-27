# -*- coding: utf-8 -*-
"""은신을 되살린다. 원래 요청은 '추적하면 풀리게 하라'였다.

되돌리는 것
    야수는 다시 숨는다 (투명 + Phased Out + 정지).
    추적해야 풀리고, 30초 뒤 다시 숨는다.

되돌리지 않는 것 (이것들이 원인이었다)
    Slot Of / BeastTimer  -> 봇 자신의 RevealEnd 변수. 슬롯이 어긋나
                             '풀자마자 다시 숨는' 상태였을 가능성이 높다.
    아이콘 조건부 표시     -> 드러난 동안 생성, 숨으면 파괴.
    아이콘 위치           -> 머리 위 벡터 (실제로 뜨는 게 확인된 형태).

같이 정리
    상시 노출 전제로 넣었던 '추적한 야수 가죽 +3' 보너스는 제거한다.
    숨기면 어차피 추적한 야수만 잡을 수 있어 항상 붙는 보너스가 된다.
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
C6 = 'Value In Array(Global Variable(LocPos), 6)'
SHOWN = 'Event Player.RevealEnd > Total Time Elapsed()'
HIDE  = 'Total Time Elapsed() >= Event Player.RevealEnd'

def head(name, extra):
    return ('rule("%s")\n{\n\tevent\n\t{\n\t\tOngoing - Each Player;\n\t\tTeam 2;\n\t\tAll;\n\t}\n\n'
            '\tconditions\n\t{\n\t\tIs Dummy Bot(Event Player) == True;\n'
            '\t\tGlobal Variable(Ready) == 1;\n\t\tIs Alive(Event Player) == True;\n'
            '\t\t%s;\n\t}\n\n\tactions\n\t{\n' % (name, extra))

NEW = head('[직업 03] 야수 은신', HIDE) + '''		Set Max Health(Event Player, 40);
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
		Teleport(Event Player, Nearest Walkable Position(Add(%(c6)s, Vector(Random Real(-14, 14), 0, Random Real(-14, 14)))));
	}
}

''' % {'c6': C6} + head('[직업 03-3] 야수 배회', SHOWN) + '''		If(Distance Between(Position Of(Event Player), %(c6)s) > 22);
			Set Move Speed(Event Player, 200);
			Start Throttle In Direction(Event Player, Direction Towards(Position Of(Event Player), %(c6)s), 1, To World, Replace existing throttle, Direction and Magnitude);
		Else;
			Set Move Speed(Event Player, Random Integer(1, 100) <= 20 ? Random Integer(240, 300) : Random Integer(130, 210));
			Start Throttle In Direction(Event Player, Vector(Random Real(-1, 1), 0, Random Real(-1, 1)), Random Real(0.3, 1), To World, Replace existing throttle, Direction and Magnitude);
			Set Facing(Event Player, Vector(Random Real(-1, 1), Random Real(-0.25, 0.25), Random Real(-1, 1)), To World);
			If(Random Integer(1, 100) <= 55);
				Press Button(Event Player, Button(Jump));
			End;
		End;
		Wait(Random Real(0.15, 0.5), Ignore Condition);
		Loop If(%(shown)s);
		Stop Throttle In Direction(Event Player);
	}
}

''' % {'c6': C6, 'shown': SHOWN} + head('[직업 03-4] 야수 위치 표시', SHOWN) + '''		Destroy Icon(Event Player.IcoId);
		Create Icon(All Players(All Teams), Add(Position Of(Event Player), Vector(0, 1.8, 0)), Eye, Visible To and Position, Color(Orange), True);
		Set Player Variable(Event Player, IcoId, Last Created Entity());
		Wait Until(Or(%(hide)s, Not(Is Alive(Event Player))), 99999);
		Destroy Icon(Event Player.IcoId);
		Set Player Variable(Event Player, IcoId, 0);
	}
}

''' % {'hide': HIDE}

a = s.index('rule("[직업 03] 야수 준비")')
b = s.index('rule("[직업 03-2] 야수 처치")')
s = s[:a] + NEW + s[b:]

# ── DoHunt: 숨은 야수만 노리고, 추적하면 실제로 푼다 ───────────────
OLDF = 'And(Is Dummy Bot(Current Array Element), Is Alive(Current Array Element))'
assert s.count(OLDF) == 2      # DoHunt 대상 + 개활지 패널 야수 수
s = s.replace(OLDF, 'And(Is Dummy Bot(Current Array Element), And(Is Alive(Current Array Element), '
                    'Total Time Elapsed() >= Player Variable(Current Array Element, RevealEnd)))', 1)

OLDT = '\t\tTeleport(Event Player.Target, Nearest Walkable Position(Add(Position Of(Event Player)'
i = s.index(OLDT)
s = s[:i] + ('\t\tClear Status(Event Player.Target, Phased Out);\n'
             '\t\tSet Invisible(Event Player.Target, None);\n') + s[i:]

# ── 상시 노출 전제로 넣었던 보너스 제거 ────────────────────────────
BONUS = ('\t\tIf(Player Variable(Victim, RevealEnd) > Total Time Elapsed());\n'
         '\t\t\tModify Player Variable(Attacker, Roll, Add, 3);\n\t\tEnd;\n')
assert s.count(BONUS) == 1
s = s.replace(BONUS, '', 1)

# ── 개활지 패널 문구 ───────────────────────────────────────────────
OLDP = ('Custom String("이 일대를 야수 {0}마리가 돌아다닌다' + NL
        + '추적하면 한 마리를 코앞으로 몰아온다 — 몰아낸 야수는 가죽을 더 준다' + NL + '", ')
assert s.count(OLDP) == 1
NEWP = ('Custom String("이 일대에 야수 {0}마리 — 숨어 있어 눈에 띄지 않는다' + NL
        + '추적하면 한 마리가 튀어나온다. 30초 안에 잡아라' + NL + '", ')
s = s.replace(OLDP, NEWP, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  은신 복구   : 평소엔 투명·정지, 추적해야 풀림, 30초 뒤 재은신')
print('  추적 동작   : Phased Out 해제 + 투명 해제 + 눈 아이콘 생성')
print('  대상 선별   : 아직 숨어 있는 야수만')
print('  보너스 제거 : 상시 노출 전제였던 가죽 +3')
