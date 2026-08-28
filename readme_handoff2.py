# -*- coding: utf-8 -*-
"""README 8장 신설 — 대야수 공격과 쥐 행동 개편의 인수인계.

사용자가 세 가지를 요청했고 1번(열차 안내)만 구현을 마쳤다.
2·3번은 설계 결정과 조사 결과가 이미 나와 있으므로, 다른 기기에서
바로 이어 구현할 수 있도록 전부 남긴다.
"""
import io

P = 'README.md'
s = io.open(P, encoding='utf-8').read()

anchor = """굳이 확인한다면 **사람이 배달 중에 접속을 끊는** 쪽으로 해야 한다."""
assert s.count(anchor) == 1

s = s.replace(anchor, anchor + """

## 8. 구현 예정 — 대야수 공격 · 쥐 행동

사용자가 세 가지를 요청했고 **1번(열차 안내)만 구현이 끝났다.**
2·3번은 설계 결정과 조사가 이미 끝나 있으니 아래대로 이어서 만들면 된다.

### 8-1. 끝난 것 — 열차의 날 안내 (`patch_train_guide.py`)

증상은 "화약을 심었는데 저녁 8시에 아무 일도 없다"였다.
**`[열차 02]`의 상태 기계와 `TrainPos` 는 멀쩡했다.** 진짜 원인은 안내였다 —
`[열차 01]` 은 `TrainPos` 5m 안에서만 발동하는데 벗어나면 F 를 눌러도
**실패 메시지조차 없고**, 철길목에는 가까이 가야 보이는 작은 간판뿐이었다.
그래서 (1) 열차의 날 내내 철길목에 주황 표식(`[열차 04]`), (2) HUD 에 남은 거리(m),
(3) 8시 1분 전 예고, (4) 화약 없이 지나갈 때 Big Message,
(5) 금고 보상이 **자루**라 은신처 정산이 필요하다는 명시를 넣었다.

> 금고를 뜯으면 지갑이 아니라 `Sack` 에 담긴다. 은신처(Zone 8)에서 정산해야 현금이 되고,
> 자루를 진 동안 질주·바이크가 막히며 죽으면 전액 소실이다. 원래 메시지가 `+$` 라
> 이미 받은 것처럼 보였다.

### 8-2. 대야수가 플레이어를 공격하게 (요청 2)

**사용자 결정: 「추격 + 근접 강타」, 그리고 장애물에 걸리는 경우의 해결책도 함께.**

현재 상태:

- `[대사냥 02]` 가 Team 2 슬롯 0~2 봇 하나를 `HuntBeast` 로 잡아 8000 체력 풀을 붙이고
  `Start Scaling Player(..., 30, False)` — **30배 크기**로 만든다 (`scale` 은 배수다).
- 움직임은 `[직업 03-3] 야수 배회` 가 준다. 무작위 배회 + 개활지(`LocPos[6]`)에서
  11m 넘어가면 순간이동으로 되돌림. **공격 수단이 전혀 없다.**

만들 것:

1. **`[직업 03-3]` 조건에 `Event Player != Global Variable(HuntBeast);` 추가.**
   안 하면 새 추격 룰과 throttle 을 두고 싸우고, 개활지 밖으로 못 나간다.
   (사냥이 끝나면 `HuntBeast` 는 Null 이 되므로 평소 야수는 영향 없다)
2. **`[대사냥 06] 대야수의 추격과 강타`** 신규 룰
   (`Ongoing - Each Player` / Team 2, 조건 `HuntPhase == 4` · `Event Player == HuntBeast` · `Is Alive`).
   - 표적: `All Players(Team 1)` 중 `Is Alive` + `Init == 1` + `TutOn == 0` +
     **`Has Status(..., Phased Out) == False`** 인 사람 중 최근접.
     (Phased Out 제외는 4장 5번 — 스크립트 `Damage` 는 Phased Out 을 뚫는다)
   - `Start Throttle In Direction` + `Set Facing` 으로 추격, `Set Move Speed` 115
     (걷기 100 보다 빠르고 질주 165 보다 느리게 — 질주로 도망칠 여지를 남긴다).
   - 사거리 안이면 `Damage(표적, Event Player, 55)`, `HuntSwing` 타임스탬프로 1.6초 간격.
     **사거리는 30배 크기를 감안해 25m 안팎에서 시작해 실기로 조정할 것** —
     모델이 거대해 발밑에 서 있어도 중심까지 거리가 멀다.
   - 끝에 `Wait(0.5)` + `Loop If(And(HuntPhase == 4, Is Alive(Event Player)))`.

3. **장애물 해법 — 두 겹으로.**
   - **(공식 권고)** `ref/actions.ts` 의 `startScalingSize` 설명에 이렇게 적혀 있다:
     *"large players placed into complex environments will severely impact server load,
     so consider also applying the Disable Movement Collision With Environment action."*
     → 각성 시 `Disable Movement Collision With Environment`, 토벌·밤 종료 시
     `Enable Movement Collision With Environment` 로 되돌린다. 서버 부하 대책이기도 하다.
   - **(2차 안전장치)** 끼임 감지 — 0.5초마다 위치를 `HuntLast` 에 기록해,
     1.5m 미만 이동이 6틱(3초) 이어지고 **표적이 사거리 밖이면**
     표적에서 가장 가까운 **`SpotPos` 검증 지점**으로 순간이동시킨다.
     좌표를 계산하지 않는다는 4장 1번 원칙을 지키는 방법이다.
     연출은 붉은 링 폭발 + 티커 「대야수가 길을 질러 나타났다」로 덮어 글리치로 안 보이게.

4. **함정 — `Loop If` 는 액션 목록을 처음부터 다시 돌린다.**
   끼임 카운터(`HuntStuck`)와 `HuntLast` 초기화를 액션 맨 위에 두면 **매 틱 리셋된다.**
   초기화는 반드시 `[대사냥 02]` 의 각성 블록(`Set Global Variable(HuntPhase, 4)` 근처)에 둘 것.

5. 신규 전역 예정: `HuntTgt` · `HuntLast` · `HuntStuck` · `HuntSwing`
   (전역은 77/128 로 51칸 남아 있다. 플레이어 변수는 꽉 찼으니 쓰지 말 것 —
   대야수는 하나뿐이라 전역으로 충분하다)

### 8-3. 쥐 행동 개편 (요청 3)

**사용자 결정: 육포를 먼저 털고, 육포가 없으면 죽거나 사람을 잡을 때까지 안 사라진다.
솔로 소프트락을 막기 위해 「인원수만큼 약해지게」.**

현재 상태:

- `[쥐 01]` 이 45초 뒤 **무조건** 철수하며 육포 15 를 깎는다.
- `[쥐 02]` 는 **사람을 먼저 쫓고**, 잡화점(`LocPos[2]`) 9m 안에 있을 때만 육포를 2씩 턴다.
- `[쥐 03]` 이 `Set Damage Received(rat, Count(RatHitters) >= 3 ? 70 : 18)` 로
  **타격자 3명 이상이면** 쥐가 약해지게 한다. 쥐는 667 체력이라 18% 면 실효 3,705.

만들 것:

1. **육포 우선** — `[쥐 02]` 를 뒤집는다. `JerkyStock > 0` 이면 잡화점으로 직행하고
   (가는 길에 3.5m 안의 사람은 문다), `JerkyStock == 0` 이 되어서야 사람을 사냥한다.
2. **지속** — `[쥐 01]` 의 `Wait(45)` 뒤에 `JerkyStock == 0` 이면 물러나지 않게 한다.
   `Wait Until(Or(RatOn == 0, RatKill == 1), 99999)` 로 **죽거나 사람을 잡을 때까지** 남긴다.
   물러나지 않는다는 것을 Big Message 로 알릴 것.
3. **중복 방지** — `[쥐 01]` 의 `RatOn == 0` 조건이 **이미** 막고 있다.
   다음 일정이 와도 대기열에 쌓이지 않고 그냥 건너뛰며, 쥐가 죽을 때 `[쥐 04]` 가
   `RatNext` 를 다시 잡는다. **동작은 이미 맞으니 확인만 하고 문서화하면 된다.**
4. **인원 비례 난이도** — `[쥐 03]` 의 값을
   `Max(Count Of(RatHitters) >= 3 ? 70 : 18, Divide(54, Max(1, 접속 인원)))` 로 바꾼다.
   1명 54% / 2명 27% / 3명 이상 18%(기존값 유지). 솔로 실효 체력이 3,705 에서 1,235 로 내려온다.
   접속 인원은 `Count Of(Filtered Array(All Players(Team 1), And(Is Alive, Init == 1)))`.
5. 신규 전역 예정: `RatKill`.
   신규 룰 예정: **`[쥐 06] 쥐가 사람을 잡았다`** (`Player Died` / Team 1,
   공격자가 Team 2 슬롯 3 봇이면 `RatKill = 1`). 습격 시작 시 `RatKill = 0` 으로 초기화.
6. **같이 지울 잔재** — `[쥐 01]` 의 `Set Global Variable(RatNext, Add(Total Time Elapsed(), 240))`
   은 바로 아래 줄에서 `Random Real(240, 600)` 으로 덮어써지는 죽은 코드다.
""")

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('ok')
