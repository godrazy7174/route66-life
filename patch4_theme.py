"""장소를 실제 66번 국도 랜드마크에 맞춰 재설계 (8곳 -> 9곳).

실제 맵 랜드마크(확인됨): 다이너, 대형 주유소, 모텔, 살룬, 정비소, 상점,
서부 마을 복합 건물, 종점 열차, 데드락 협곡.

동시에 버그 수정: 표지판/광기둥이 루프 변수 Global.Idx를 재평가하는
재평가 모드로 생성돼 있어서, 루프가 끝나면 Idx가 범위를 벗어나
이름과 위치가 전부 깨진다. -> 재평가를 'Visible To'로 바꿔
생성 시점 값으로 고정한다(장소를 옮길 땐 어차피 파괴 후 재생성).
"""
import io, re

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()

NAMES = ['파노라마 다이너', '협곡 광산', '주유소 잡화점', '모텔', '정비소 고물상',
         '살룬', '협곡 개활지', '보안관 초소', '데드락 은신처']
ZONE_NAMES = ['황야'] + NAMES

ACTIONS = [
    ['행동 없음 — 마을로 이동하세요', '-', '-', '-'],
    ['전직: 광부', '전직: 사냥꾼', '전직: 현상금 사냥꾼', '식사 $12 — 허기 회복'],
    ['채굴하기', '정밀 탐사 $30', '-', '-'],
    ['육포 구매 $15', '물통 구매 $10', '육포 5개 묶음 $65', '-'],
    ['숙박 $40 — 피로 완전 회복', '-', '-', '-'],
    ['원석 전량 판매', '가죽 전량 판매', '오늘의 시세', '-'],
    ['위스키 $20 — 피로 회복', '카드 도박 $50', '소문 듣기', '-'],
    ['흔적 추적 — 사냥감 출현', '-', '-', '-'],
    ['벌금 납부 $100 — 현상금 말소', '현상금 게시판', '-', '-'],
    ['장물 거래 — 시세 130%, 평판 -5', '-', '-', '-'],
]
COUNTS = [1, 4, 2, 3, 1, 3, 3, 1, 2, 1]


def arr(items):
    return 'Array(' + ', '.join('Custom String("%s")' % x for x in items) + ')'


FLAT = arr([a for grp in ACTIONS for a in grp])
ZONEARR = arr(ZONE_NAMES)
NAMEARR = arr(NAMES)


def replace_rule(src, name, new):
    a = src.index('rule("%s")' % name)
    nxt = src.find('\nrule("', a)
    b = len(src) if nxt == -1 else nxt + 1
    return src[:a] + new + src[b:]


# ── BuildWorld: 9곳 링 배치 + 재평가 고정 ───────────────────────────
s = replace_rule(s, '[코어 02] BuildWorld', '''rule("[코어 02] BuildWorld")
{
	event
	{
		Subroutine;
		BuildWorld;
	}

	actions
	{
		Set Global Variable(Anchor, Nearest Walkable Position(Position Of(Host Player())));
		Set Global Variable(LocPos, Empty Array);
		For Global Variable(Idx, 0, 9, 1);
			Modify Global Variable(LocPos, Append To Array, Nearest Walkable Position(Add(Global Variable(Anchor), Vector(Multiply(34, Cosine From Degrees(Multiply(Global Variable(Idx), 40))), 0, Multiply(34, Sine From Degrees(Multiply(Global Variable(Idx), 40)))))));
		End;
		Set Global Variable(LocRad, Array(7, 7, 7, 6, 6, 6, 10, 6, 8));
		Set Global Variable(BotHome, Value In Array(Global Variable(LocPos), 8));
		Set Global Variable(SignIds, Empty Array);
		For Global Variable(Idx, 0, 9, 1);
			Create In-World Text(All Players(All Teams), Value In Array(''' + NAMEARR + ''', Global Variable(Idx)), Add(Value In Array(Global Variable(LocPos), Global Variable(Idx)), Vector(0, 2.4, 0)), 1.7, Do Not Clip, Visible To, Color(Yellow), Default Visibility);
			Modify Global Variable(SignIds, Append To Array, Last Text ID());
			Create Effect(All Players(All Teams), Light Shaft, Color(Yellow), Value In Array(Global Variable(LocPos), Global Variable(Idx)), 1.2, Visible To);
		End;
	}
}
''')

# ── 구역 감지: 0..9 ─────────────────────────────────────────────────
s = s.replace('For Player Variable(Event Player, Idx, 0, 8, 1);',
              'For Player Variable(Event Player, Idx, 0, 9, 1);')

# ── 행동 커서: 액션 수 배열 ─────────────────────────────────────────
s = re.sub(r'Value In Array\(Array\(1, 4, 2, 3, 1, 3, 3, 1, 1\), Add\(Event Player\.Zone, 1\)\)',
           'Value In Array(Array(%s), Add(Event Player.Zone, 1))' % ', '.join(str(c) for c in COUNTS), s)

# ── HUD: 구역 이름/행동 라벨 배열 교체 ──────────────────────────────
old_zone = s[s.index('Value In Array(Array(Custom String("황야")'):s.index(', Add(Local Player.Zone, 1))')]
s = s.replace(old_zone, 'Value In Array(' + ZONEARR)
old_flat = s[s.index('Value In Array(Array(Custom String("행동 없음'):s.index(', Add(Multiply(Add(Local Player.Zone, 1), 4), Local Player.MenuIdx))')]
s = s.replace(old_flat, 'Value In Array(' + FLAT)

# ── 무법자: 캠프 인덱스 7 -> 8 ──────────────────────────────────────
s = s.replace('Or(Player Variable(Current Array Element, Zone) == -1, Player Variable(Current Array Element, Zone) == 7)',
              'Or(Player Variable(Current Array Element, Zone) == -1, Player Variable(Current Array Element, Zone) == 8)')
s = s.replace('If(Global Variable(ArchIdx) == 7);', 'If(Global Variable(ArchIdx) == 8);')

# ── 체포된 사람은 보안관 초소로 ─────────────────────────────────────
s = s.replace('Teleport(Event Player.Target, Value In Array(Global Variable(LocPos), 0));',
              'Teleport(Event Player.Target, Value In Array(Global Variable(LocPos), 7));')

# ── 설계자 모드: 9곳 ────────────────────────────────────────────────
s = s.replace('Set Global Variable(ArchIdx, Modulo(Add(Global Variable(ArchIdx), 1), 8));',
              'Set Global Variable(ArchIdx, Modulo(Add(Global Variable(ArchIdx), 1), 9));')
old_arch = s[s.index('Value In Array(Array(Custom String("시청"), Custom String("광산")'):]
old_arch = old_arch[:old_arch.index(', Global Variable(ArchIdx))')]
while 'Value In Array(Array(Custom String("시청"), Custom String("광산")' in s:
    a = s.index('Value In Array(Array(Custom String("시청"), Custom String("광산")')
    b = s.index(', Global Variable(ArchIdx))', a)
    s = s[:a] + 'Value In Array(' + NAMEARR + s[b:]
# 설계자가 다시 만드는 표지판도 재평가 고정
s = s.replace('Vector(0, 2.4, 0)), 1.7, Do Not Clip, Visible To Position and String, Color(Yellow), Default Visibility);',
              'Vector(0, 2.4, 0)), 1.7, Do Not Clip, Visible To, Color(Yellow), Default Visibility);')
# 좌표 패널 9줄
panel = []
for i, n in enumerate(NAMES):
    panel.append(
        '\t\t\tCreate HUD Text(Host Player(), Null, Custom String("{0}   {1}", Custom String("%d %s"), '
        'Custom String("X {0}   Y {1}   Z {2}", X Component Of(Value In Array(Global Variable(LocPos), %d)), '
        'Y Component Of(Value In Array(Global Variable(LocPos), %d)), '
        'Z Component Of(Value In Array(Global Variable(LocPos), %d)))), Null, Left, %d, Color(White), Color(Aqua), '
        'Color(White), Visible To Sort Order String and Color, Default Visibility);' % (i, n, i, i, i, 10 + i))
    panel.append('\t\t\tModify Global Variable(ArchHud, Append To Array, Last Text ID());')
a = s.index('\t\t\tSet Global Variable(ArchHud, Array(Last Text ID()));')
b = s.index('\t\t\tBig Message(Host Player(), Custom String("설계자 모드 ON')
s = s[:a] + '\t\t\tSet Global Variable(ArchHud, Array(Last Text ID()));\n' + '\n'.join(panel) + '\n' + s[b:]

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('테마 재설계 완료')
print('  장소 수        : 9')
print('  파노라마 다이너: %d' % s.count('파노라마 다이너'))
print('  보안관 초소    : %d' % s.count('보안관 초소'))
print('  데드락 은신처  : %d' % s.count('데드락 은신처'))
print('  좌표 패널 줄   : %d' % s.count('Modify Global Variable(ArchHud, Append To Array'))
print('  깨진 재평가 잔존: %d' % s.count('Visible To Position and String, Color(Yellow)'))
