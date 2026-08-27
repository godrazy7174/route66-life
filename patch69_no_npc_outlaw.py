# -*- coding: utf-8 -*-
"""NPC 무법자 시스템 완전 제거 (설계 확정: 앞으로도 없음).

제거: [무법자 01/02/03] 룰 3개, 전역 7종(BotHome/BotBounty/Out*5), HuntPay,
      설계자 03 의 은신처 재배치 시 봇 정리 블록.

재배선:
  현상금 사냥꾼  NPC 수입 소멸 -> 본업은 사람 사냥(체포·처단)으로 순화.
                 명성 +2 소스도 함께 소멸 (체포 +12, 처단 +8 은 그대로)
  보안관 승급     'NPC 처치금 +$30' -> '몰수 벌금의 절반을 수수료로'
                 (체포 시 범인에게서 걷는 20% 벌금 중 절반 수령 — 발행 없음)
  무법자 습격 이벤트 -> '야수 광란' (90초간 야수 가죽 2배)
  초소 게시판     '무법자 1명당 $N' -> 실시간 수배자 수 표시
  밤 안내/튜토리얼 ' 현상금 2배' 문구 -> 실제 효과(발견 확률)만 언급
"""
import io

NL = chr(92) + 'r' + chr(92) + 'n'
P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

def droprule(name):
    global s
    a = s.index('rule("%s")' % name)
    b = s.index('\nrule(', a + 5) + 1
    s = s[:a] + s[b:]

# ══ 룰 3개 제거 ═══════════════════════════════════════════════════
droprule('[무법자 01] 무법자 스폰 관리')
droprule('[무법자 02] 무법자 사격 판정')
droprule('[무법자 03] 무법자 반격')

# ══ 변수 선언·초기화 제거 ═════════════════════════════════════════
for d in ('\t\t9: BotHome\n', '\t\t15: BotBounty\n', '\t\t18: OutPos\n', '\t\t19: OutHP\n',
          '\t\t20: OutResp\n', '\t\t21: OutFx\n', '\t\t22: OutIco\n', '\t\t52: HuntPay\n'):
    sub(d, '')
sub('\t\tSet Global Variable(BotBounty, 12);\n', '', 2)
for d in ('\t\tSet Global Variable(OutPos, Array(Vector(0, 0, 0), Vector(0, 0, 0), Vector(0, 0, 0)));\n',
          '\t\tSet Global Variable(OutHP, Array(0, 0, 0));\n',
          '\t\tSet Global Variable(OutResp, Array(0, 0, 0));\n',
          '\t\tSet Global Variable(OutFx, Array(0, 0, 0));\n',
          '\t\tSet Global Variable(OutIco, Array(0, 0, 0));\n'):
    sub(d, '')
sub('\t\tSet Global Variable(BotHome, Value In Array(Global Variable(LocPos), 8));\n', '', 3)

# ══ 설계자 03: 은신처 봇 정리 블록 제거 ═══════════════════════════
A = '''		If(Global Variable(ArchIdx) == 8);
			For Global Variable(Tmp, 0, 3, 1);
				If(Value In Array(Global Variable(OutHP), Global Variable(Tmp)) > 0);
					Destroy Effect(Value In Array(Global Variable(OutFx), Global Variable(Tmp)));
					Destroy Icon(Value In Array(Global Variable(OutIco), Global Variable(Tmp)));
					Set Global Variable At Index(OutHP, Global Variable(Tmp), 0);
					Set Global Variable At Index(OutResp, Global Variable(Tmp), 0);
				End;
			End;
		End;
'''
sub(A, '')

# ══ 이벤트 3: 무법자 습격 -> 야수 광란 ════════════════════════════
sub('''		Else If(Global Variable(EventKind) == 3);
			Set Global Variable(BotBounty, 40);
			Big Message(All Players(All Teams), Custom String("무법자 습격! 무법자 현상금이 $40으로 뛴다"));''',
'''		Else If(Global Variable(EventKind) == 3);
			Big Message(All Players(All Teams), Custom String("야수 광란! 90초 동안 야수 가죽이 2배로 벗겨진다"));''')
sub('Custom String("소문 — 무법자들이 몰려왔다")', 'Custom String("소문 — 야수들이 사납게 날뛴다")')
sub('''		If(Player Variable(Victim, Giant) == 2);
			Modify Player Variable(Attacker, Yield, Multiply, 50);''',
'''		If(Global Variable(EventKind) == 3);
			Modify Player Variable(Attacker, Yield, Multiply, 2);
		End;
		If(Player Variable(Victim, Giant) == 2);
			Modify Player Variable(Attacker, Yield, Multiply, 50);''')

# ══ 초소 패널·게시판 ══════════════════════════════════════════════
sub('Custom String("벌금 $100 — 수배 말소' + NL + '현상금 게시판' + NL + '무법자 1명당  $ {0}' + NL + '", Global Variable(BotBounty))',
    'Custom String("벌금 $100 — 수배 말소, 악명 -40' + NL + '현상금 게시판 — 수배범을 잡으면 그 목값을 갖는다' + NL + '")')
sub('Custom String("현상금 게시판 — 무법자 1명당 $ {0}", Global Variable(BotBounty))',
    'Custom String("현상금 게시판 — 지금 수배자 {0}명", Count Of(Filtered Array(All Players(All Teams), Player Variable(Current Array Element, Bounty) > 0)))')

# ══ 보안관 승급 효과 교체 ═════════════════════════════════════════
sub("Custom String(\"체포 1.2초 · 무법자 처치금 +$30\")",
    "Custom String(\"체포 1.2초 · 몰수 벌금의 절반을 수수료로\")")
sub('''			Set Player Variable(Event Player, Fine, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.2), Down));
			Set Player Variable(Event Player.Target, Money, Subtract(Player Variable(Event Player.Target, Money), Event Player.Fine));''',
'''			Set Player Variable(Event Player, Fine, Round To Integer(Multiply(Player Variable(Event Player.Target, Money), 0.2), Down));
			Set Player Variable(Event Player.Target, Money, Subtract(Player Variable(Event Player.Target, Money), Event Player.Fine));
			If(And(Event Player.Job == 3, Event Player.Adv == 1));
				Modify Player Variable(Event Player, Money, Add, Round To Integer(Multiply(Event Player.Fine, 0.5), Down));
				Small Message(Event Player, Custom String("보안관 수수료 +$ {0}", Round To Integer(Multiply(Event Player.Fine, 0.5), Down)));
			End;''')

# ══ 밤 안내·튜토리얼 문구 ═════════════════════════════════════════
sub('Custom String("어둠 속에서는 현상금이 2배. 길 위에서 뭔가 주울 확률도 오른다")',
    'Custom String("어둠 속에서는 길 위에서 뭔가 주울 확률이 오른다")')
sub('Custom String("12분이 하루다. 밤이 오면 마을의 불이 꺼지고 현상금이 두 배가 된다.' + NL + '하루 목표를 채우면 보너스가 붙는다.")',
    'Custom String("12분이 하루다. 밤이 오면 마을의 불이 꺼지고 길 위의 행운이 늘어난다.' + NL + '하루 목표를 채우면 보너스가 붙는다.")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
for gone in ('BotHome', 'BotBounty', 'OutPos', 'OutHP', 'OutResp', 'OutFx', 'OutIco', 'HuntPay', '무법자 01'):
    assert gone not in s, gone
print('NPC 무법자 완전 제거 + 재배선 완료')
