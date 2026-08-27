# -*- coding: utf-8 -*-
"""전수 조사 2차 — 승인된 제안 (가)·(다)·(라) 구현.

(가) 쥐떼 보상 분배
     "셋이 붙어야 잡힌다"고 해놓고 막타 1인이 $400+명성8을 독식했다.
     RatHitters 전원에게 $200·명성4, 막타에 +$200·명성4를 얹는다.
     막타는 반드시 RatHitters에 들어 있으므로(피격이 사망보다 먼저 발생)
     막타의 총합은 전과 동일한 $400·명성8이고, 조력자만 새로 받는다.

(다) 서버 부하 보호에서 Set Slow Motion 제거
     슬로우모션은 게임 시간만 늦출 뿐 스크립트 부하를 전혀 줄이지 않는다.
     부하 대응이 아니라 그냥 렉처럼 느껴지는 부작용이었다.
     대신 실제로 무거운 [월드 04] 구역 감지(플레이어당 0.35초마다 15회
     거리 비교)의 주기를 부하가 높을 때만 늦춘다.

(라) 마스터리는 9까지만 세이브 코드에 담긴다 — 코드 HUD에 명시.
"""
import io

P = 'ROUTE66_LIFE_EN.ow'
src = io.open(P, encoding='utf-8').read()


def once(old, new, tag):
    global src
    assert src.count(old) == 1, '%s: %d건' % (tag, src.count(old))
    src = src.replace(old, new)
    print('  OK %s' % tag)


# ── (가) 쥐떼 보상 분배 ───────────────────────────────────────────
old = (
    '\t\tIf(And(Entity Exists(Attacker), Is Dummy Bot(Attacker) == False));\n'
    '\t\t\tModify Player Variable(Attacker, Money, Add, 400);\n'
    '\t\t\tModify Player Variable(Attacker, Earned, Add, 400);\n'
    '\t\t\tSet Player Variable(Attacker, Fame, Min(100, Add(Player Variable(Attacker, Fame), 8)));\n'
    '\t\t\tBig Message(All Players(All Teams), Custom String("{0} — 쥐떼의 우두머리를 잡았다!! (+$400 · 명성 +8)", Attacker));\n'
    '\t\tElse;\n')
new = (
    '\t\tFor Global Variable(Idx, 0, Count Of(Global Variable(RatHitters)), 1);\n'
    '\t\t\tModify Player Variable(Value In Array(Global Variable(RatHitters), Global Variable(Idx)), Money, Add, 200);\n'
    '\t\t\tModify Player Variable(Value In Array(Global Variable(RatHitters), Global Variable(Idx)), Earned, Add, 200);\n'
    '\t\t\tSet Player Variable(Value In Array(Global Variable(RatHitters), Global Variable(Idx)), Fame, '
    'Min(100, Add(Player Variable(Value In Array(Global Variable(RatHitters), Global Variable(Idx)), Fame), 4)));\n'
    '\t\t\tSmall Message(Value In Array(Global Variable(RatHitters), Global Variable(Idx)), '
    'Custom String("쥐떼를 몰아내는 데 힘을 보탰다 +$200 · 명성 +4"));\n'
    '\t\tEnd;\n'
    '\t\tIf(And(Entity Exists(Attacker), Is Dummy Bot(Attacker) == False));\n'
    '\t\t\tModify Player Variable(Attacker, Money, Add, 200);\n'
    '\t\t\tModify Player Variable(Attacker, Earned, Add, 200);\n'
    '\t\t\tSet Player Variable(Attacker, Fame, Min(100, Add(Player Variable(Attacker, Fame), 4)));\n'
    '\t\t\tBig Message(All Players(All Teams), Custom String("{0} — 쥐떼의 우두머리를 잡았다!! (막타 +$200 · 몫은 {1}명이 나눈다)", '
    'Attacker, Count Of(Global Variable(RatHitters))));\n'
    '\t\tElse;\n')
once(old, new, '쥐떼 보상 — 참여자 전원 분배')

# ── (다) 슬로우모션 제거 + 구역 감지 적응형 주기 ──────────────────
once('\t\tSmall Message(All Players(All Teams), Custom String("서버가 버겁다 — 일부 처리를 늦춘다"));\n'
     '\t\tSet Slow Motion(85);\n'
     '\t\tWait Until(Server Load() < 190, 120);\n'
     '\t\tSet Slow Motion(100);\n',
     '\t\tSmall Message(All Players(All Teams), Custom String("서버가 버겁다 — 구역 감지를 잠시 늦춘다"));\n'
     '\t\tWait Until(Server Load() < 190, 120);\n'
     '\t\tSmall Message(All Players(All Teams), Custom String("서버가 다시 안정됐다"));\n',
     '서버 부하 — 슬로우모션 제거')
assert 'Set Slow Motion' not in src

once('\t\tSet Player Variable(Event Player, Zone, Event Player.Tmp);\n'
     '\t\t\tSet Player Variable(Event Player, MenuIdx, 0);\n'
     '\t\tEnd;\n'
     '\t\tWait(0.35, Ignore Condition);\n',
     '\t\tSet Player Variable(Event Player, Zone, Event Player.Tmp);\n'
     '\t\t\tSet Player Variable(Event Player, MenuIdx, 0);\n'
     '\t\tEnd;\n'
     '\t\tWait(Server Load() > 200 ? 0.8 : 0.35, Ignore Condition);\n',
     '구역 감지 — 부하 200 초과 시 0.35s -> 0.8s')

# ── (라) 마스터리 상한 명시 ───────────────────────────────────────
once('Custom String("적어둬라 — 방이 닫히면 이 코드만 남는다")',
     'Custom String("적어둬라 — 방이 닫히면 이 코드만 남는다 (마스터리는 9까지 담긴다)")',
     '세이브 코드 HUD — 마스터리 9 상한 명시')

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('done')
