# -*- coding: utf-8 -*-
"""야수를 숨기지 않는다 + 훨씬 더 날뛰게 만든다 + 등장 문구 교체.

[1] 은신 폐지
    투명·Phased Out·이동정지를 전부 걷어낸다. 야수는 항상 보이고 항상 돌아다닌다.
    다만 예전에 "추적 안 해도 잡히면 사냥 성공이 되는 건 버그"라고 했었다.
    숨기지 않으면 그건 필연이므로, 대신 추적한 야수는 가죽을 더 주도록 했다.
    추적이 '보이게 만드는 수단'에서 '보상을 키우는 수단'으로 바뀐다.

[2] 이동
    전환 0.3~1.1초 -> 0.15~0.5초
    속도 115~165%  -> 130~210%, 20% 확률로 240~300% 폭주
    추력 0.55~1    -> 0.3~1 (가다 서다가 더 심해짐)
    점프 30%       -> 55%
    시선도 매번 무작위로 홱홱 돌린다

[3] 문구 교체
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
C6 = 'Value In Array(Global Variable(LocPos), 6)'

def head(name, extra=''):
    return ('rule("%s")\n{\n\tevent\n\t{\n\t\tOngoing - Each Player;\n\t\tTeam 2;\n\t\tAll;\n\t}\n\n'
            '\tconditions\n\t{\n\t\tIs Dummy Bot(Event Player) == True;\n'
            '\t\tGlobal Variable(Ready) == 1;\n\t\tIs Alive(Event Player) == True;\n%s\t}\n\n'
            '\tactions\n\t{\n' % (name, extra))

NEW = head('[직업 03] 야수 준비') + '''		Set Max Health(Event Player, 40);
		Set Ability 1 Enabled(Event Player, False);
		Set Ability 2 Enabled(Event Player, False);
		Set Ultimate Ability Enabled(Event Player, False);
		Set Primary Fire Enabled(Event Player, False);
		Set Secondary Fire Enabled(Event Player, False);
		Clear Status(Event Player, Phased Out);
		Set Invisible(Event Player, None);
	}
}

''' + head('[직업 03-3] 야수 배회') + '''		If(Distance Between(Position Of(Event Player), %(c6)s) > 22);
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
		Loop();
	}
}

''' % {'c6': C6} + head('[직업 03-4] 야수 위치 표시') + '''		Destroy Icon(Event Player.IcoId);
		Create Icon(All Players(All Teams), Add(Position Of(Event Player), Vector(0, 1.8, 0)), Eye, Visible To and Position, Color(Orange), True);
		Set Player Variable(Event Player, IcoId, Last Created Entity());
		Wait Until(Not(Is Alive(Event Player)), 99999);
		Destroy Icon(Event Player.IcoId);
		Set Player Variable(Event Player, IcoId, 0);
	}
}

'''
a = s.index('rule("[직업 03] 야수 은신")')
b = s.index('rule("[직업 03-2] 야수 처치")')
s = s[:a] + NEW + s[b:]

# ── DoHunt: 숨김 해제 동작 제거, 문구 교체 ─────────────────────────
for old, new in [
    ('And(Is Alive(Current Array Element), Has Status(Current Array Element, Phased Out) == True)',
     'Is Alive(Current Array Element)'),
    ('\t\tClear Status(Event Player.Target, Phased Out);\n', ''),
    ('\t\tSet Invisible(Event Player.Target, None);\n', ''),
    ('Custom String("야수를 몰아냈다 — 30초 안에 쏴라")',
     'Custom String("크아앙! 엄청 무서운 야수가 나타났다!")'),
]:
    assert s.count(old) == 1, old[:45]
    s = s.replace(old, new, 1)

# ── 추적한 야수는 가죽을 더 준다 ───────────────────────────────────
OLDK = '\t\tSet Player Variable At Index(Attacker, Inv, 3,'
assert s.count(OLDK) == 1
s = s.replace(OLDK, '\t\tIf(Player Variable(Victim, RevealEnd) > Total Time Elapsed());\n'
                    '\t\t\tModify Player Variable(Attacker, Roll, Add, 3);\n'
                    '\t\tEnd;\n' + OLDK, 1)

# ── 개활지 패널 문구 ───────────────────────────────────────────────
OLDP = ('Custom String("이 일대에 야수 {0}마리 — 숨어 있어 눈에 띄지 않는다' + NL
        + '추적하면 30초 동안 모습을 드러낸다' + NL + '", ')
assert s.count(OLDP) == 1
NEWP = ('Custom String("이 일대를 야수 {0}마리가 돌아다닌다' + NL
        + '추적하면 한 마리를 코앞으로 몰아온다 — 몰아낸 야수는 가죽을 더 준다' + NL + '", ')
s = s.replace(OLDP, NEWP, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  은신 폐지   : 투명·Phased Out·이동정지 전부 제거, 항상 보이고 항상 배회')
print('  추적 의미   : 코앞으로 끌어옴 + 30초 안에 잡으면 가죽 +3')
print('  이동        : 0.15~0.5초 전환 / 130~210%% (20%% 확률 240~300%%) / 점프 55%% / 시선 무작위')
print('  등장 문구   : 크아앙! 엄청 무서운 야수가 나타났다!')
