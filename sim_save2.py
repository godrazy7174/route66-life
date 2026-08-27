# -*- coding: utf-8 -*-
"""세이브 코드 발급 -> 입력 -> 복원 왕복을 현재 코드 그대로 재현해 전수 검증한다.

발급식은 [조작 03c], 검증·복원식은 [세이브 02]에서 그대로 옮겼다.
"""
import itertools
import random


def issue(money, deposit, pick, home, horse, bag, job, adv, jobxp, fame, noto,
          rebuild, rebirth, giant, earned):
    A = min(9999, (money + deposit) // 100) * 100 + pick * 10 + home * 4 + horse * 2 + bag
    Braw = ((((job * 10 + adv) * 10 + min(9, jobxp // 250)) * 10 + min(9, fame // 10)) * 10
            + min(9, noto // 10))
    B = Braw * 10 + (A + Braw) % 9
    Craw = (rebuild * 100000 + rebirth * 10000 + min(9, giant // 10) * 1000
            + min(99, earned // 2000) * 10)
    C = Craw + (A + B + Craw // 10) % 9
    return A, B, C


def restore(A, B, C):
    Amt = B // 10
    Roll = C // 10
    bad = ((B % 10 != (A + Amt) % 9)
           or (Amt // 10000 > 6)
           or ((A // 10) % 10 > 4)
           or ((Amt // 1000) % 10 > 1)
           or (C % 10 != (A + B + Roll) % 9)
           or (C // 100000 > 5)
           or ((C // 10000) % 10 > 5))
    if bad:
        return None
    return dict(
        Money=(A // 100) * 100,
        Pick=(A // 10) % 10,
        HasBag=A % 2,
        HasHorse=((A % 10) // 2) % 2,
        HasHome=(A % 10) // 4,
        Job=Amt // 10000,
        Adv=(Amt // 1000) % 10,
        JobXP=((Amt // 100) % 10) * 250,
        Fame=((Amt // 10) % 10) * 10,
        Noto=(Amt % 10) * 10,
        Rebuild=C // 100000,
        Rebirth=(C // 10000) % 10,
        Giant=((C // 1000) % 10) * 10,
        Earned=(Roll % 100) * 2000,
    )


def check(state):
    (money, deposit, pick, home, horse, bag, job, adv, jobxp,
     fame, noto, rebuild, rebirth, giant, earned) = state
    A, B, C = issue(money, deposit, pick, home, horse, bag, job, adv, jobxp,
                    fame, noto, rebuild, rebirth, giant, earned)
    if not (A < 10 ** 6 and B < 10 ** 6 and C < 10 ** 6):
        return 'OVERFLOW A=%d B=%d C=%d' % (A, B, C)
    r = restore(A, B, C)
    if r is None:
        return 'REJECTED (정상 코드인데 거부됨)'
    want = dict(
        Money=min(999900, ((money + deposit) // 100) * 100),
        Pick=pick, HasBag=bag, HasHorse=horse, HasHome=home,
        Job=job, Adv=adv, JobXP=min(9, jobxp // 250) * 250,
        Fame=min(9, fame // 10) * 10, Noto=min(9, noto // 10) * 10,
        Rebuild=rebuild, Rebirth=rebirth,
        Giant=min(9, giant // 10) * 10,
        Earned=min(99, earned // 2000) * 2000,
    )
    diff = {k: (want[k], r[k]) for k in want if want[k] != r[k]}
    return 'MISMATCH %s' % diff if diff else None


fails = 0
tested = 0
# 1) 경계값 전수 조합
grid = itertools.product(
    [0, 99, 100, 999999, 1500000],
    [0, 7777],
    range(5),
    [0, 1], [0, 1], [0, 1],
    range(7),
    [0, 1],
    [0, 250, 9999],
    [0, 100], [0, 100],
    [0, 5], [0, 5],
    [0, 180],
    [0, 2000, 198000, 500000]
)
for st in grid:
    tested += 1
    e = check(st)
    if e:
        fails += 1
        if fails <= 6:
            print('  FAIL %s :: %s' % (st, e))

# 2) 무작위 보강
rnd = random.Random(7)
for _ in range(400000):
    st = (rnd.randrange(0, 2000000), rnd.randrange(0, 200000), rnd.randrange(0, 5),
          rnd.randrange(2), rnd.randrange(2), rnd.randrange(2), rnd.randrange(7),
          rnd.randrange(2), rnd.randrange(0, 12000), rnd.randrange(0, 101),
          rnd.randrange(0, 101), rnd.randrange(0, 6), rnd.randrange(0, 6),
          rnd.randrange(0, 190), rnd.randrange(0, 600000))
    tested += 1
    e = check(st)
    if e:
        fails += 1
        if fails <= 6:
            print('  FAIL %s :: %s' % (st, e))

print('왕복 검사 %d건 / 실패 %d건' % (tested, fails))

# 3) 오탈자 1자리 검출률
rnd = random.Random(11)
caught = miss = 0
for _ in range(60000):
    st = (rnd.randrange(0, 900000), 0, rnd.randrange(0, 5), rnd.randrange(2),
          rnd.randrange(2), rnd.randrange(2), rnd.randrange(7), rnd.randrange(2),
          rnd.randrange(0, 3000), rnd.randrange(0, 101), rnd.randrange(0, 101),
          rnd.randrange(0, 6), rnd.randrange(0, 6), rnd.randrange(0, 100),
          rnd.randrange(0, 200000))
    A, B, C = issue(*st)
    digits = list('%06d%06d%06d' % (A, B, C))
    i = rnd.randrange(18)
    old = digits[i]
    digits[i] = str((int(old) + rnd.randrange(1, 10)) % 10)
    s = ''.join(digits)
    A2, B2, C2 = int(s[:6]), int(s[6:12]), int(s[12:])
    r = restore(A2, B2, C2)
    if r is None:
        caught += 1
    else:
        miss += 1
print('한 자리 오타 검출: %d / %d  (%.1f%%)' % (caught, caught + miss, 100 * caught / (caught + miss)))
