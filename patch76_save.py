# -*- coding: utf-8 -*-
"""세이브 코드 시스템 (수동 — 워크샵에 저장소가 없어 코드 적기/입력 방식).

코드 형식: A(6자리) - B(6자리)
  A = 소지금/100 (4자리, 상한 $999,900) · 곡괭이(1) · 장비비트(집4+말2+배낭1)(1)
  B = 직업(1) · 승급(1) · 현직 레벨(1) · 명성/10(1) · 악명/10(1) · 체크섬(1)
  체크섬 = (A + B상위5자리) mod 9 — 오타 방어용 (위조 방어는 포기, 공지된 한계)

안내소 메뉴: [튜토리얼 / 세이브 코드 발급 / 코드 입력]
  발급: 코드가 HUD 에 상시 표시 (적어두라는 안내)
  입력: R = 숫자 +1, F = 자리 확정 (12자리), 웅크리기 = 취소
       완료 시 검증 -> 소지금·장비·직업·승급·레벨·명성·악명 복원, 영웅 변신 재적용
미저장 항목(설계): 인벤토리 소모품·건물 소유(서버 상태)·현직 외 경험치.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
T = chr(9)
NLC = chr(10)

def sub(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (old[:70], s.count(old))
    s = s.replace(old, new, cnt)

# ══ 변수 ══════════════════════════════════════════════════════════
for v in ('SaveHud', 'EnterA', 'EnterB', 'EntryIdx', 'EntryCur', 'SaveOn'):
    assert v not in s
sub('\t\t78: CowIco\n',
    '\t\t78: CowIco\n\t\t79: SaveHud\n\t\t80: EnterA\n\t\t81: EnterB\n\t\t82: EntryIdx\n\t\t83: EntryCur\n\t\t84: SaveOn\n')
sub('\t\tSet Player Variable(Event Player, JailOn, 0);\n\t\tSet Player Variable(Event Player, Zone, -1);\n',
    '\t\tSet Player Variable(Event Player, JailOn, 0);\n\t\tSet Player Variable(Event Player, SaveOn, 0);\n\t\tSet Player Variable(Event Player, Zone, -1);\n', 0) if False else None
i = s.index('Set Player Variable(Event Player, TaxPaidRound, 0);')
j = s.index(chr(10), i) + 1
s = s[:j] + '\t\tSet Player Variable(Event Player, SaveOn, 0);\n' + s[j:]

# ══ 안내소 메뉴 1 -> 3 ════════════════════════════════════════════
sub('Array(1, 1, 4, 4, 2, 3, 4, 3, 5, 4, 1, 4, 3, 3, 1, 1)', 'Array(1, 1, 4, 4, 2, 3, 4, 3, 5, 4, 3, 4, 3, 3, 1, 1)', 3)
sub('Custom String("튜토리얼 보기"), Custom String("-"), Custom String("-")',
    'Custom String("튜토리얼 보기"), Custom String("세이브 코드 발급"), Custom String("코드 입력 — 저장 복원")')

FLOOR = lambda e: 'Round To Integer(%s, Down)' % e
LVL = FLOOR('Divide(Value In Array(Event Player.JobXP, Event Player.Job), 250)')

ISSUE = (T*3 + 'Else If(Event Player.MenuIdx == 1);' + NLC
 + T*4 + 'Set Player Variable(Event Player, EnterA, Add(Multiply(Min(9999, %s), 100), Add(Multiply(Event Player.Pick, 10), Add(Multiply(Event Player.HasHome, 4), Add(Multiply(Event Player.HasHorse, 2), Event Player.HasBag)))));' % FLOOR('Divide(Event Player.Money, 100)') + NLC
 + T*4 + 'Set Player Variable(Event Player, EnterB, Add(Multiply(Add(Multiply(Add(Multiply(Add(Multiply(Event Player.Job, 10), Event Player.Adv), 10), Min(9, %s)), 10), Min(9, %s)), 10), Min(9, %s)));' % (LVL, FLOOR('Divide(Event Player.Fame, 10)'), FLOOR('Divide(Event Player.Noto, 10)')) + NLC
 + T*4 + 'Set Player Variable(Event Player, EnterB, Add(Multiply(Event Player.EnterB, 10), Modulo(Add(Event Player.EnterA, Event Player.EnterB), 9)));' + NLC
 + T*4 + 'Destroy HUD Text(Event Player.SaveHud);' + NLC
 + T*4 + 'Create HUD Text(Event Player, Null, Custom String("세이브 코드   {0} - {1}", Event Player.EnterA, Event Player.EnterB), Custom String("적어두세요 — 방이 닫히면 이 코드만 남습니다"), Left, 4, Color(White), Color(Yellow), Color(Gray), Visible To Sort Order String and Color, Default Visibility);' + NLC
 + T*4 + 'Set Player Variable(Event Player, SaveHud, Last Text ID());' + NLC
 + T*4 + 'Big Message(Event Player, Custom String("세이브 코드 발급 — 화면 왼쪽에 표시됩니다"));' + NLC
 + T*4 + 'Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 60);' + NLC)

ENTRY = (T*3 + 'Else;' + NLC
 + T*4 + 'Set Player Variable(Event Player, Busy, 1);' + NLC
 + T*4 + 'Set Player Variable(Event Player, EnterA, 0);' + NLC
 + T*4 + 'Set Player Variable(Event Player, EnterB, 0);' + NLC
 + T*4 + 'Set Player Variable(Event Player, EntryIdx, 0);' + NLC
 + T*4 + 'Set Player Variable(Event Player, EntryCur, 0);' + NLC
 + T*4 + 'Destroy HUD Text(Event Player.SaveHud);' + NLC
 + T*4 + 'Create HUD Text(Event Player, Custom String("코드 입력   {0}", Custom String("A {0}   B {1}", Event Player.EnterA, Event Player.EnterB)), Custom String("자리 {0}/12   현재 숫자 [ {1} ]", Event Player.EntryIdx, Event Player.EntryCur), Custom String("[R] +1      [F] 자리 확정      [웅크리기] 취소"), Left, 4, Color(Aqua), Color(White), Color(Gray), Visible To Sort Order String and Color, Default Visibility);' + NLC
 + T*4 + 'Set Player Variable(Event Player, SaveHud, Last Text ID());' + NLC
 + T*4 + 'Wait Until(Not(Is Button Held(Event Player, Button(Interact))), 5);' + NLC
 + T*4 + 'Set Player Variable(Event Player, SaveOn, 1);' + NLC
 + T*4 + 'Small Message(Event Player, Custom String("주의 — 복원하면 현재 진행이 덮어써집니다"));' + NLC)

sub('''		If(Event Player.Zone == 9);
			Call Subroutine(DoTutorial);''',
'''		If(Event Player.Zone == 9);
			If(Event Player.MenuIdx == 0);
				Call Subroutine(DoTutorial);
''' + ISSUE + ENTRY + '''			End;''')

# ══ 입력 규칙 ═════════════════════════════════════════════════════
DIV = lambda a, b: 'Round To Integer(Divide(%s, %s), Down)' % (a, b)
RAWB = 'Event Player.Amt'
DEC = (
   T*3 + 'Set Player Variable(Event Player, Amt, %s);' % DIV('Event Player.EnterB', '10') + NLC
 + T*3 + 'If(Or(Or(Modulo(Event Player.EnterB, 10) != Modulo(Add(Event Player.EnterA, Event Player.Amt), 9), %s > 6), Or(Modulo(%s, 10) > 4, Modulo(%s, 10) > 1)));' % (DIV(RAWB, '10000'), DIV('Event Player.EnterA', '10'), DIV(RAWB, '1000')) + NLC
 + T*4 + 'Big Message(Event Player, Custom String("코드가 올바르지 않습니다 — 다시 확인하세요"));' + NLC
 + T*4 + 'Play Effect(Event Player, Debuff Impact Sound, Color(Red), Position Of(Event Player), 70);' + NLC
 + T*3 + 'Else;' + NLC
 + T*4 + 'Set Player Variable(Event Player, Money, Multiply(%s, 100));' % DIV('Event Player.EnterA', '100') + NLC
 + T*4 + 'Set Player Variable(Event Player, Pick, Modulo(%s, 10));' % DIV('Event Player.EnterA', '10') + NLC
 + T*4 + 'Set Player Variable(Event Player, HasBag, Modulo(Event Player.EnterA, 2));' + NLC
 + T*4 + 'Set Player Variable(Event Player, HasHorse, Modulo(%s, 2));' % DIV('Modulo(Event Player.EnterA, 10)', '2') + NLC
 + T*4 + 'Set Player Variable(Event Player, HasHome, %s);' % DIV('Modulo(Event Player.EnterA, 10)', '4') + NLC
 + T*4 + 'Set Player Variable(Event Player, Job, %s);' % DIV(RAWB, '10000') + NLC
 + T*4 + 'Set Player Variable(Event Player, Adv, Modulo(%s, 10));' % DIV(RAWB, '1000') + NLC
 + T*4 + 'Set Player Variable At Index(Event Player, JobXP, Event Player.Job, Multiply(Modulo(%s, 10), 250));' % DIV(RAWB, '100') + NLC
 + T*4 + 'Set Player Variable(Event Player, Fame, Multiply(Modulo(%s, 10), 10));' % DIV(RAWB, '10') + NLC
 + T*4 + 'Set Player Variable(Event Player, Noto, Multiply(Modulo(Event Player.Amt, 10), 10));' + NLC
 + T*4 + 'If(Event Player.HasHorse == 1);' + NLC
 + T*5 + 'Start Forcing Player To Be Hero(Event Player, Hero(Shion));' + NLC
 + T*4 + 'Else If(Event Player.HasBag == 1);' + NLC
 + T*5 + 'Start Forcing Player To Be Hero(Event Player, Hero(Tracer));' + NLC
 + T*4 + 'End;' + NLC
 + T*4 + 'Big Message(Event Player, Custom String("복원 완료 — 66번 국도에 돌아온 것을 환영합니다"));' + NLC
 + T*4 + 'Play Effect(All Players(All Teams), Ring Explosion, Color(Yellow), Position Of(Event Player), 4);' + NLC
 + T*4 + 'Play Effect(Event Player, Buff Explosion Sound, Color(Yellow), Position Of(Event Player), 180);' + NLC
 + T*3 + 'End;' + NLC)

SAVERULES = ('rule("[세이브 01] 숫자 +1 (R)")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.SaveOn == 1;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Reload)) == True;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, EntryCur, Modulo(Add(Event Player.EntryCur, 1), 10));' + NLC
 + T*2 + 'Play Effect(Event Player, Debuff Impact Sound, Color(White), Position Of(Event Player), 40);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC
 + 'rule("[세이브 02] 자리 확정 (F)")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.SaveOn == 1;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Interact)) == True;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'If(Event Player.EntryIdx < 6);' + NLC
 + T*3 + 'Set Player Variable(Event Player, EnterA, Add(Multiply(Event Player.EnterA, 10), Event Player.EntryCur));' + NLC
 + T*2 + 'Else;' + NLC
 + T*3 + 'Set Player Variable(Event Player, EnterB, Add(Multiply(Event Player.EnterB, 10), Event Player.EntryCur));' + NLC
 + T*2 + 'End;' + NLC
 + T*2 + 'Modify Player Variable(Event Player, EntryIdx, Add, 1);' + NLC
 + T*2 + 'Set Player Variable(Event Player, EntryCur, 0);' + NLC
 + T*2 + 'Play Effect(Event Player, Buff Impact Sound, Color(Aqua), Position Of(Event Player), 45);' + NLC
 + T*2 + 'If(Event Player.EntryIdx >= 12);' + NLC
 + T*3 + 'Set Player Variable(Event Player, SaveOn, 0);' + NLC
 + T*3 + 'Destroy HUD Text(Event Player.SaveHud);' + NLC
 + T*3 + 'Set Player Variable(Event Player, Busy, 0);' + NLC
 + DEC
 + T*2 + 'End;' + NLC
 + T*2 + 'Wait Until(Not(Is Button Held(Event Player, Button(Interact))), 3);' + NLC
 + T + '}' + NLC + '}' + NLC + NLC
 + 'rule("[세이브 03] 입력 취소 (웅크리기)")' + NLC + '{' + NLC
 + T + 'event' + NLC + T + '{' + NLC + T*2 + 'Ongoing - Each Player;' + NLC + T*2 + 'All;' + NLC + T*2 + 'All;' + NLC + T + '}' + NLC + NLC
 + T + 'conditions' + NLC + T + '{' + NLC
 + T*2 + 'Event Player.SaveOn == 1;' + NLC
 + T*2 + 'Is Button Held(Event Player, Button(Crouch)) == True;' + NLC
 + T + '}' + NLC + NLC + T + 'actions' + NLC + T + '{' + NLC
 + T*2 + 'Set Player Variable(Event Player, SaveOn, 0);' + NLC
 + T*2 + 'Destroy HUD Text(Event Player.SaveHud);' + NLC
 + T*2 + 'Set Player Variable(Event Player, Busy, 0);' + NLC
 + T*2 + 'Small Message(Event Player, Custom String("입력을 취소했다"));' + NLC
 + T + '}' + NLC + '}' + NLC + NLC)
sub('rule("[코어 10] 서버 부하 보호")', SAVERULES + 'rule("[코어 10] 서버 부하 보호")')

# ══ 입력 중 R 커서·취식 충돌 방지 ═════════════════════════════════
sub('''		Global Variable(ArchOn) == 0;
		Is Button Held(Event Player, Button(Reload)) == True;''',
'''		Global Variable(ArchOn) == 0;
		Event Player.SaveOn == 0;
		Is Button Held(Event Player, Button(Reload)) == True;''')

# == 사망 시 입력 상태 정리 ==
i = s.index(chr(9)*2 + 'Set Player Variable(Event Player, Hunger, Max(Event Player.Hunger, 40));')
CLEAN = (chr(9)*2 + 'If(Event Player.SaveOn == 1);' + chr(10)
       + chr(9)*3 + 'Set Player Variable(Event Player, SaveOn, 0);' + chr(10)
       + chr(9)*3 + 'Destroy HUD Text(Event Player.SaveHud);' + chr(10)
       + chr(9)*2 + 'End;' + chr(10))
s = s[:i] + CLEAN + s[i:]

# ══ 안내소 패널 갱신 ══════════════════════════════════════════════
NL = chr(92) + 'r' + chr(92) + 'n'
sub('Custom String("튜토리얼 — 처음이라면 여기서' + NL + '완주 보상  육포 3 · 물통 3 · $30' + NL + '")',
    'Custom String("튜토리얼 — 처음이라면 여기서 (완주 보상 육포 3 · 물통 3 · $30)' + NL + '세이브 코드 — 발급받아 적어두면 다음 방에서 복원할 수 있다' + NL + '")')

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('세이브 코드 시스템 완료 — 발급 / 12자리 입력 / 검증·복원')
