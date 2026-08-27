"""실기 테스트에서 드러난 버그 2건 수정.

버그 1 — 스폰 직후 계속 피해를 입음
  무법자 반격 반경이 20m인데, 장소 8곳이 반경 24m 링에 배치돼
  인접 지점 간 거리가 2*24*sin(22.5도) = 18.4m 밖에 안 된다.
  시청(0번)과 무법자 캠프(7번)가 인접이라, 시청에 스폰하면
  캠프의 무법자 사거리 안에 그대로 들어간다.
  -> 반경 14m로 축소 + 황야/캠프에 있는 사람만 공격 + 링 반경 30m로 확대.

버그 2 — 설계자 모드가 전역 Tmp를 HUD ID 저장에 쓰는데
  무법자 반격 규칙이 1.8초마다 같은 Tmp를 덮어쓴다.
  -> 설계자 전용 전역 ArchHud 배열로 분리.
  겸사겸사 8곳 좌표를 한 화면에 전부 띄우도록 패널을 만든다
  (스크린샷 한 장으로 좌표를 전부 넘길 수 있게).
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
s = io.open(P, encoding='utf-8').read()
NAMES = ['시청', '광산', '식료품점', '여관', '잡화상', '술집', '사냥터', '무법자 캠프']

# ── 1) 전역 변수 추가 ────────────────────────────────────────────────
s = s.replace("\t\t22: OutIco\n", "\t\t22: OutIco\n\t\t23: ArchHud\n")

# ── 2) 링 반경 24 -> 30, 구역 반경 겹침 제거 ────────────────────────
s = s.replace("Vector(Multiply(24, Cosine From Degrees", "Vector(Multiply(30, Cosine From Degrees")
s = s.replace("Multiply(24, Sine From Degrees", "Multiply(30, Sine From Degrees")
s = s.replace("Set Global Variable(LocRad, Array(7, 7, 6, 6, 6, 6, 14, 10));",
              "Set Global Variable(LocRad, Array(7, 7, 6, 6, 6, 6, 10, 8));")

# ── 3) 무법자: 사거리 축소 + 마을 안 사람은 쏘지 않음 ───────────────
old_aggro = ('Players Within Radius(Value In Array(Global Variable(OutPos), Global Variable(Idx)), 20, All Teams, Surfaces), '
             'And(Is Alive(Current Array Element), Player Variable(Current Array Element, Init) == 1))')
new_aggro = ('Players Within Radius(Value In Array(Global Variable(OutPos), Global Variable(Idx)), 14, All Teams, Surfaces), '
             'And(Is Alive(Current Array Element), And(Player Variable(Current Array Element, Init) == 1, '
             'Or(Player Variable(Current Array Element, Zone) == -1, Player Variable(Current Array Element, Zone) == 7))))')
assert old_aggro in s, '무법자 반격 조건을 찾지 못함'
s = s.replace(old_aggro, new_aggro)

# ── 4) 설계자 모드: 전용 전역 + 좌표 패널 8줄 ───────────────────────
panel_on = []
for i, n in enumerate(NAMES):
    panel_on.append(
        '\t\t\tCreate HUD Text(Host Player(), Null, Custom String("{0}   {1}", Custom String("%d %s"), '
        'Custom String("X {0}   Y {1}   Z {2}", X Component Of(Value In Array(Global Variable(LocPos), %d)), '
        'Y Component Of(Value In Array(Global Variable(LocPos), %d)), '
        'Z Component Of(Value In Array(Global Variable(LocPos), %d)))), Null, Left, %d, Color(White), Color(Aqua), '
        'Color(White), Visible To Sort Order String and Color, Default Visibility);' % (i, n, i, i, i, 10 + i))
    panel_on.append('\t\t\tModify Global Variable(ArchHud, Append To Array, Last Text ID());')

s = s.replace("""			Set Global Variable(Tmp, Last Text ID());
			Big Message(Host Player(), Custom String("설계자 모드 ON"));
		Else;
			Destroy HUD Text(Global Variable(Tmp));
			Big Message(Host Player(), Custom String("설계자 모드 OFF"));
		End;""",
"""			Set Global Variable(ArchHud, Array(Last Text ID()));
""" + '\n'.join(panel_on) + """
			Big Message(Host Player(), Custom String("설계자 모드 ON — 8곳 좌표가 왼쪽에 표시됩니다"));
		Else;
			For Global Variable(Idx, 0, Count Of(Global Variable(ArchHud)), 1);
				Destroy HUD Text(Value In Array(Global Variable(ArchHud), Global Variable(Idx)));
			End;
			Set Global Variable(ArchHud, Empty Array);
			Big Message(Host Player(), Custom String("설계자 모드 OFF"));
		End;""")

# ── 5) 설계자 모드 중에는 무법자를 멈춘다 (배치 방해 방지) ──────────
s = s.replace("""	conditions
	{
		Global Variable(Ready) == 1;
	}

	actions
	{
		For Global Variable(Idx, 0, 3, 1);
			If(Value In Array(Global Variable(OutHP), Global Variable(Idx)) > 0);
				Set Global Variable(Tmp,""",
"""	conditions
	{
		Global Variable(Ready) == 1;
		Global Variable(ArchOn) == 0;
	}

	actions
	{
		For Global Variable(Idx, 0, 3, 1);
			If(Value In Array(Global Variable(OutHP), Global Variable(Idx)) > 0);
				Set Global Variable(Tmp,""")

io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('패치 완료')
print('  링 반경 30m       : %d' % s.count('Multiply(30, Cosine From Degrees'))
print('  무법자 사거리 14m : %d' % s.count(', 14, All Teams, Surfaces)'))
print('  ArchHud 사용      : %d' % s.count('ArchHud'))
print('  좌표 패널 줄 수   : %d' % s.count('Modify Global Variable(ArchHud, Append To Array'))
