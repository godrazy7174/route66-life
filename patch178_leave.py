# -*- coding: utf-8 -*-
"""축 5 — 플레이어 이탈 처리.

이 게임에는 Player Left Match 룰이 하나도 없다. 그래서 사람이 나가면
그가 만든 표식·효과·HUD 핸들이 전부 주인 없이 남는다.

머리 위 이름표는 플레이어 엔티티에 붙어 있고, 소 표식(CowFx/CowIco)이나
밀수·호송 표식은 저장된 좌표에 붙어 있어서 그 자리에 영영 떠 있게 된다.
사람이 드나드는 공개 방에서는 이게 계속 쌓인다(워크샵 엔티티 총량 제한도 있다).

추가로, 강탈/체포는 3~5초 채널 뒤에 상대를 조작하는데 그 사이 상대가
나가버리면 Position Of 가 (0,0,0)이 되어 판정이 좌표 우연에 좌우된다.
Entity Exists 를 실패 조건에 명시한다.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()

# ── A) 이탈 정리 룰 ───────────────────────────────────────────────
RULE = '''rule("[코어 11] 떠난 자의 흔적 정리")
{
\tevent
\t{
\t\tPlayer Left Match;
\t\tAll;
\t\tAll;
\t}

\tactions
\t{
\t\tDestroy In-World Text(Event Player.NameId);
\t\tDestroy HUD Text(Event Player.KeyHud);
\t\tDestroy HUD Text(Event Player.SaveHud);
\t\tDestroy HUD Text(Event Player.TutHud);
\t\tDestroy Progress Bar HUD Text(Event Player.WorkBar);
\t\tDestroy Icon(Event Player.DelIcon);
\t\tDestroy Icon(Event Player.SmuggleIco);
\t\tDestroy Icon(Event Player.SmuggleFlash);
\t\tDestroy Icon(Event Player.EscortIco);
\t\tDestroy Icon(Event Player.CowIco);
\t\tDestroy Icon(Event Player.WolfIco);
\t\tDestroy Icon(Event Player.DialCur);
\t\tDestroy Icon(Event Player.DialPin);
\t\tDestroy Icon(Event Player.EscortFlash);
\t\tDestroy Effect(Event Player.EscortFlash);
\t\tDestroy Effect(Event Player.EscortFx);
\t\tDestroy Effect(Event Player.CowFx);
\t}
}

'''
anchor = 'rule("[코어 15] 머리 위 이름표 갱신")'
assert src.count(anchor) == 1
src = src.replace(anchor, RULE + anchor)
print('  OK 이탈 정리 룰 추가 (표식 12 · HUD 4 · 효과 3)')

# ── B) 강탈/체포 실패 판정에 상대 존재 확인 ───────────────────────
old = ('\t\tIf(Or(Or(Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 10, '
       'Health(Event Player) < Event Player.Take), Not(Is Alive(Event Player))));\n')
assert src.count(old) == 1, src.count(old)
new = ('\t\tIf(Or(Or(Not(Entity Exists(Event Player.Target)), '
       'Distance Between(Position Of(Event Player), Position Of(Event Player.Target)) > 10), '
       'Or(Health(Event Player) < Event Player.Take, Not(Is Alive(Event Player)))));\n')
src = src.replace(old, new)
print('  OK 강탈·체포 — 채널 도중 상대 이탈 시 확실히 실패 처리')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('done')
