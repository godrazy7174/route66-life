# 미검증 수치 2건을 정량 계산으로 확정
#  A) 쥐떼 체력 — "혼자·둘은 못 잡고 셋이면 잡힌다"가 성립하는가
#  B) 마을 금고 1단계 $8,000 — 인원별 도달 시간이 합리적인가
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ---------- A) 쥐떼 ----------
# 좌클릭 전투 + 무한 탄창(재장전 없음). 이 게임에서 쓰이는 영웅들의 초당 피해:
DPS = {'캐서디': 140, '애쉬(비조준)': 150, '트레이서': 220, '프레야': 140}
BASE = sum(DPS.values()) / len(DPS)          # 평균 162
ACC = 0.60                                    # 3인칭·이동표적 기준 명중률(사용자가 "맞히기 어렵다"고 실측)
EFF = BASE * ACC                              # 1인 실효 DPS
WINDOW = 45                                   # 쥐 지속 시간(초)
RAT_HP = 7000                                 # Set Max Health 1000% (레킹볼 기본 700 가정)

print('=== A) 쥐떼 처치 가능성 ===')
print(f'  1인 실효 DPS {EFF:.0f} · 제한 {WINDOW}초 · 쥐 체력 {RAT_HP}')
for dr in (100, 70):
    print(f'\n  [피해 수신 {dr}%] 실효 체력 {RAT_HP/(dr/100):.0f}')
    for n in (1, 2, 3, 4):
        dmg = EFF * n * WINDOW * (dr / 100)
        print(f'    시민 {n}명: 총 피해 {dmg:>6.0f} → {"처치" if dmg >= RAT_HP else "실패"}')
    # 현상금 사냥꾼(추가 100%) 1명 + 시민 2명
    mixed = (EFF * 2 + EFF * 2) * WINDOW * (dr / 100)
    print(f'    현상금1+시민2: {mixed:>6.0f} → {"처치" if mixed >= RAT_HP else "실패"}')

# ---------- B) 마을 금고 ----------
print('\n=== B) 마을 금고 도달 시간 ===')
PER_MIN = 215          # 사용자 실측(1일차 17시에 $1,825 = 분당 약 215)
SHARE = 0.30           # 수입 중 갹출 비율(장비·식비를 빼고 남는 몫의 현실적 추정)
GOALS = [8000, 23000, 48000, 88000, 148000, 233000, 348000, 498000]
for n in (1, 2, 3, 5, 8):
    rate = PER_MIN * n * SHARE
    t1 = GOALS[0] / rate
    t8 = GOALS[-1] / rate
    print(f'  {n}인: 갹출 분당 ${rate:>5.0f} → 1단계 {t1:>5.1f}분 · 8단계 완주 {t8/60:>4.1f}시간')
