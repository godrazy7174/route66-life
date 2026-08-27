Differentiate the three job micro-games in this Overwatch 2 Workshop project via ONE Python patch script patch107_minigames.py: the miner keeps the sweep bar but slightly harder; the courier and the cowherd each get a brand-new, mechanically different mini-game. Work non-interactively. If the sandbox blocks Python, just WRITE the script and say so - the caller runs it. Final prints ASCII-safe (cp949).

# Project context
- ROUTE66_LIFE_EN.ow is the source of truth (~5,179 lines). Do NOT edit ROUTE66_LIFE.ow.
- Conventions per patch105_skillbar.py: sub() assert-counted, block() assembly, rule-body replacement by scanning from a unique rule header to its closing brace, one write, UTF-8 header, Korean docstring.
- Player variables are FULL: NO new variables. Reuse rules: WorkProg is a free counter whenever the player is not mid-channel; DialTgt/DialPin/DialCur (bank-dial vars) are free outside an active bank heist and may hold a position/effect-id/icon-id during a short window; CowPos already holds the live cow position.
- Validation (run if possible): python patch107_minigames.py && python lint.py ROUTE66_LIFE_EN.ow && python blockcheck.py ROUTE66_LIFE_EN.ow && python enumcheck.py ROUTE66_LIFE_EN.ow && python paircheck.py ROUTE66_LIFE_EN.ow

# Doctrine
No ternary in comparison RHS, no bare grouping parens. Custom String max 3 args. Korean as-is. Effects/icons are created once and must be destroyed on every exit path.

# Edit 1 - miner: slightly harder sweep
In rule "[스킬바 01] DoSkillBar", the cursor sweeps at 0.9s per half-sweep. Replace every `0.9` in that rule with `0.72` (there are 8 occurrences within the rule: 4 Chase durations + 4 Wait Until timeouts; scope the substitution to that rule's body and assert the count is 8). Nothing else changes (zone stays 5/17). The miner is now the only caller of DoSkillBar.

# Edit 2 - courier: 샛길 질주 (shortcut dash - a MOVEMENT game)
Replace the ENTIRE actions body of rule "[파발 02] 흔들리는 화물" (keep its event and conditions blocks exactly as they are) with:
- Wait(Random Real(7, 14), Ignore Condition);
- If(And(And(Event Player.HasParcel == 1, Event Player.Busy == 0), Is Alive(Event Player)));
  - Set Player Variable(Event Player, DialTgt, Nearest Walkable Position(Add(Position Of(Event Player), Multiply(Direction From Angles(Random Real(0, 360), 0), 17))));
  - Create Effect(All Players(All Teams), Light Shaft, Color(Yellow), Event Player.DialTgt, 1.2, None);
  - Set Player Variable(Event Player, DialPin, Last Created Entity());
  - Create Icon(Event Player, Add(Event Player.DialTgt, Vector(0, 2.5, 0)), Circle, Visible To and Position, Color(Yellow), True);
  - Set Player Variable(Event Player, DialCur, Last Created Entity());
  - Big Message(Event Player, Custom String("샛길이 보인다 — 7초 안에 빛기둥을 밟아라!"));
  - Play Effect(Event Player, Buff Impact Sound, Color(Yellow), Position Of(Event Player), 45);
  - Wait Until(Or(Or(Distance Between(Position Of(Event Player), Event Player.DialTgt) < 3, Event Player.Busy == 1), Or(Event Player.HasParcel != 1, Not(Is Alive(Event Player)))), 7);
  - Destroy Effect(Event Player.DialPin);
  - Destroy Icon(Event Player.DialCur);
  - If(And(And(Distance Between(Position Of(Event Player), Event Player.DialTgt) < 3, Event Player.HasParcel == 1), Is Alive(Event Player)));
    - Modify Player Variable(Event Player, Money, Add, 15);
    - Modify Player Variable(Event Player, Earned, Add, 15);
    - Small Message(Event Player, Custom String("샛길로 질렀다 +$15"));
    - Play Effect(Event Player, Ring Explosion, Color(Yellow), Position Of(Event Player), 1.2);
  - Else;
    - Small Message(Event Player, Custom String("샛길이 흙먼지에 묻혔다"));
  - End;
- End;
- Wait(2, Ignore Condition);
- Loop If(Event Player.HasParcel == 1);
(Do NOT set Busy - the courier must keep sprinting. The Busy == 1 abort in the Wait Until exits early if the player starts a channel, protecting the reused dial vars.)

# Edit 3 - cowherd: 눈싸움 (stare-down - a STILLNESS game)
Replace the ENTIRE actions body of rule "[목동 02] 날뛰는 소" (keep its event and conditions blocks exactly as they are) with:
- Wait(Random Real(6, 12), Ignore Condition);
- If(And(And(Event Player.CowOn == 1, Event Player.Busy == 0), Is Alive(Event Player)));
  - Set Player Variable(Event Player, WorkProg, 0);
  - Big Message(Event Player, Custom String("소가 겁먹었다 — 2초간 멈춰 서서 소를 바라봐라!"));
  - Play Effect(Event Player, Buff Impact Sound, Color(White), Position Of(Event Player), 45);
  - Wait(0.5, Ignore Condition);
  - then FOUR identical sampling blocks, each:
    If(And(Is Moving(Event Player) == False, Dot Product(Facing Direction Of(Event Player), Direction Towards(Eye Position(Event Player), Event Player.CowPos)) >= 0.85));
    	Modify Player Variable(Event Player, WorkProg, Add, 1);
    End;
    Wait(0.5, Ignore Condition);
  - after the four blocks:
  - If(And(Event Player.WorkProg >= 4, Event Player.CowOn == 1));
    - Modify Player Variable(Event Player, Money, Add, 12);
    - Modify Player Variable(Event Player, Earned, Add, 12);
    - Small Message(Event Player, Custom String("소가 진정했다 +$12"));
    - Play Effect(Event Player, Ring Explosion, Color(White), Position Of(Event Player), 1);
  - Else;
    - Small Message(Event Player, Custom String("소가 콧대를 세운다 — 눈을 피했다"));
  - End;
  - Set Player Variable(Event Player, WorkProg, 0);
- End;
- Wait(2, Ignore Condition);
- Loop If(Event Player.CowOn == 1);

# Deliverables
patch107_minigames.py (script alone suffices if execution is blocked). Verification counts for the caller: `0.72` = 8, `샛길이 보인다` = 1, `샛길로 질렀다` = 1, `샛길이 흙먼지에 묻혔다` = 1, `소가 겁먹었다` = 1, `소가 진정했다` = 1, `소가 콧대를 세운다` = 1, `화물 끈이 풀린다` = 0, `소가 날뛴다` = 0, `Call Subroutine(DoSkillBar);` = 1 (only the miner remains). Touch nothing else.
