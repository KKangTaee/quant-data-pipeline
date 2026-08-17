# Recommendation

Status: 1~3차 complete; confirmed state READY; required extended forecast NO_GO
Last Updated: 2026-08-17

## Recommended Direction

현재 observed-state는 유지하고 fixed adjacent monitor를 미래 예측으로 간주하지 않는다.
사용자가 승인한 forecast target은 다음 두 개다.

1. `P(next confirmed phase = destination | current information)`
2. `P(any confirmed transition within next 3 official monthly releases | current information)`

첫 번째는 다음 전환 목적지, 두 번째는 `전환 임박도`를 위한 별도 event다. 정확한
3·6개월 뒤 phase classification은 반려됐다.

## 2026-08-17 Final 1~3 Phase Decision

이전 raw quadrant의 one-month episode 문제는 임계값을 낮추지 않고 official phase의
정의 자체를 바꿔 해결했다. 최초 국면과 모든 다음 국면은 동일 raw 후보가 2 usable
release 연속 확인될 때 두 번째 release에서 확정되며, 전환을 과거로 소급하지 않는다.

### Current-state result — `READY`

| Evidence | Actual | Gate | Result |
| --- | ---: | ---: | --- |
| Usable confirmed origins | 587 | >= 180 | Pass |
| Independent confirmed transitions | 116 | >= 48 | Pass |
| Recovery / expansion / slowdown / contraction destinations | 25 / 32 / 20 / 39 | each >= 8 | Pass |
| Final 25% destination support | 6 / 8 / 5 / 10 | each >= 2 | Pass |
| Four-phase occupancy | 12.78%~39.35% | each 8%~50% | Pass |
| Official one-month episode share | 0.85% | <= 25% | Pass |
| Three-release exact / level-side revision | 68.60% / 86.18% | 60% / 80% | Pass |
| NBER peak / trough capture | 85.71% / 85.71% | 70% / 70% | Pass |

고정 순환 순서는 강제하지 않았다. actual route에는 `contraction -> expansion`,
`recovery -> contraction`, `slowdown -> expansion` 같은 비인접 전환이 포함된다.

### Required transition-driver result — `SHADOW_ONLY`

| Evidence | Actual | Gate | Result |
| --- | ---: | ---: | --- |
| Complete required-driver origins | 27 | >= 180 | Fail |
| Independent transitions in common period | 5 | >= 48 | Fail |
| Destination support | recovery 3 / expansion 0 / slowdown 0 / contraction 2 | each >= 8 | Fail |
| Final 25% destination support | recovery 1 / expansion 0 / slowdown 0 / contraction 1 | each >= 2 | Fail |

ANFCI와 PERMIT는 stored ALFRED `realtime_start`를 conservative known-at fallback으로
해석한 뒤 각각 2011-05, 1999-08부터 정상 평가됐다. 지배적 병목은
`BAMLH0A0HYM2`가 현재 DB에서 2023-08 이후만 재현되고 3개월 변화는 2023-11부터만
가능하다는 점이다. 따라서 model fit, baseline 비교와 calibration을 실행하지 않았다.

최종 판정은 **`NO_GO`**다. 이것은 current-state 실패가 아니다. current-state는 4차의
관측 국면 후보가 될 수 있지만, 사용자가 원한 전환압력·주경로·대안경로 확률은 아직
제품화할 수 없다. production snapshot/service/React와 자산별 확인 포인트는 변경하지
않았다. fiscal은 `NOT_TESTABLE`, market block은 optional `SHADOW_ONLY`다.

### Resume condition

4·5차 전에 `BAMLH0A0HYM2`의 2023년 이전 공식 PIT history를 보강하거나, actual 결과와
독립적으로 사전 승인한 장기 credit spread 대체 source를 확정해야 한다. 그 뒤 같은
target·confirmation·support·skill threshold로 2차 coverage부터 재실행한다. BAML을
사후 제거하거나 48-event/목적지 support gate를 낮추는 방식은 허용하지 않는다.

## Prior FRED-only Feasibility Gate (Superseded)

현재 DB의 strict PIT data를 1959-01~2026-07 origin으로 다시 구성하고, unavailable
월을 보존한 채 두 번 연속 관측으로 모든 destination 전환 사건을 추출했다.

| Evidence | Actual | Minimum experiment gate | Result |
| --- | ---: | ---: | --- |
| Usable PIT monthly origins | 148 | 180 | Fail |
| Independent transitions | 32 | 48 | Fail |
| Recovery destination | 7 | 8 | Fail |
| Expansion destination | 9 | 8 | Pass |
| Slowdown destination | 5 | 8 | Fail |
| Contraction destination | 11 | 8 | Pass |
| Chronological holdout events | 8 | 12 | Fail |
| Holdout destination support | recovery 4 / expansion 0 / slowdown 0 / contraction 4 | each 2 | Fail |

Decision: **`NO_GO_DATA`**.

이는 threshold를 보수적으로 잡아서 화면을 비우는 문제가 아니다. 2014-04 이전의
strict PIT current-state가 대부분 unavailable이고, 최근 25% holdout에는 확장과 둔화
전환 사건이 한 건도 없다. 이 상태에서 4-class probability를 만들면 동일 episode의
월별 행을 반복 학습하거나 recent shock에 과적합하게 된다.

## Current Product Decision

- 현재 국면과 최근 변화: 유지
- fixed adjacent monitor를 미래 예측처럼 표현: No-Go
- 현재 데이터로 next-phase probability model fitting: No-Go
- hardcoded 조건부 scenario 문구 또는 임의 확률 fallback: No-Go
- production DB/service/React probability UI: 중단
- 자산별 확인 포인트: 현행 계산·payload·디자인 유지

## What Can Resolve The Data Gate

표본 부족은 완전히 구조적인 한계로 확정되지는 않았다. 공식 realtime dataset을
추가하면 usable history를 1960년대까지 확장할 가능성이 있다.

### Primary candidate — Philadelphia Fed RTDSM

- monthly vintages of nonfarm payroll employment, unemployment, weekly hours,
  industrial production과 capacity utilization을 제공한다.
- nonfarm payroll employment monthly vintages는 1964-12부터 존재한다.
- 현재 FRED/ALFRED table에서 2009~2011 이후에만 재현되는 일부 core series를 장기
  realtime indicator로 교체하거나 보강할 수 있다.

### Secondary candidate — Philadelphia Fed ADS vintages

- payroll, industrial production, real income, real manufacturing/trade sales, claims와
  GDP를 mixed-frequency business-conditions index로 결합한다.
- assessed-in-real-time vintage file을 제공한다.
- 단독 정답이 아니라 current-state robustness reference 또는 reduced model 후보로
  검증해야 한다.

## Prior RTDSM Expansion

공식 `IPT/H/EMPLOY/RUC` vintage를 source-isolated 공용 ledger에 저장하고 strict PIT 장기
shadow state를 재구성했다.

| Evidence | Actual | Gate | Result |
| --- | ---: | ---: | --- |
| Stored unique vintage rows | 1,334,818 | source complete | Pass |
| Usable origins | 589 | 180 | Pass |
| Independent transitions | 117 | 48 | Pass |
| Holdout transitions | 30 | 12 | Pass |
| Common-period months | 142 | 96 | Pass |
| Exact phase agreement | 54.2% | 60% | Fail |
| Cohen's kappa | 0.368 | 0.40 | Fail |
| Level-side agreement | 83.1% | 75% | Pass |

Combined decision: **`NO_GO_PARITY`**.

표본 부족은 해결됐지만 장기 state와 현행 product state가 같은 label이라는 전제가
성립하지 않았다. 따라서 이 결과로 destination/imminence 확률을 fit하거나 UI를 만드는
것은 올바르지 않다.

## Prior Raw Canonical Core-State Experiment

현행 8지표와 parity를 맞추는 접근은 폐기하고, RTDSM 4지표를 과거와 현재에 동일하게
적용하는 canonical core 후보를 구현했다. 다음 목적지는 고정 순환을 강제하지 않으며,
전환압력은 다음 3번의 공식 발표 안에 two-release 전환이 확정되는 사건이다.

| Evidence | Actual | Gate | Result |
| --- | ---: | ---: | --- |
| Usable origins / confirmed transitions | 589 / 117 | 180 / 48 | Pass |
| Four-phase occupancy | 15.11%~36.84% | each 8%~50% | Pass |
| Raw one-month episode share | 27.12% (48/177) | at most 25% | **Fail** |
| Three-release exact / level-side revision | 62.41% / 85.88% | 60% / 80% | Pass |
| NBER recession below-side | 100% | 65% | Pass |
| NBER peak / trough capture | 85.71% / 85.71% | 70% / 70% | Pass |

Combined decision: **`NO_GO_CORE_STATE`**, sole reason `ONE_MONTH_EPISODES`.

Dataset, deterministic weighted binary/multinomial model, prior-OOF calibration,
episode-block chronological validation과 strongest-baseline publication gate까지 구현·단위
검증했지만, actual experiment는 core gate에서 멈췄다. 따라서 actual probability,
baseline 비교나 calibration 성과는 존재하지 않으며 임의로 표시하지 않는다.

## Superseded Prior Decision

다음 선택지는 둘뿐이다.

1. raw quadrant가 아니라 two-release confirmation까지 포함한 canonical core label과
   새로운 episode 안정성 gate를 결과와 독립적으로 사전 설계한 뒤 처음부터 재검증한다.
2. 경제사이클 forecast 개발을 중단하고 현행 관측 국면·조건부 확인 기능만 유지한다.

25%를 27.2%로 사후 완화하기, 월별 행을 독립 표본으로 부풀리기, 결과를 본 뒤 지표 조합을 선택하는
방식은 사용하지 않는다. 자산별 확인 포인트는 어느 선택에서도 현행 그대로 유지한다.

## Event And Publication Boundary

data gate 통과는 probability 공개 승인이 아니다. 이후 모델은 strongest expanding
baseline보다 destination log loss / Brier가 좋아야 하며, imminence calibration과
episode-block holdout을 별도로 통과해야 한다. 조건부 scenario는 검증된 model
sensitivity에서만 생성한다.

## Prior Evidence Summary

- actual current read model: 2026-07-31 READY, 위축, 8/8 series
- all focused economic-cycle tests: 226 passed
- next-transition feasibility tests: 6 passed (included above)
- actual sample report: `NO_GO_DATA`, 148 usable origins, 32 events
- RTDSM actual sample report: `GO_EXPERIMENT`, 589 usable origins, 117 events
- RTDSM actual parity report: `NO_GO_PARITY`, 142 overlap, agreement 54.2%, kappa 0.368
- canonical core actual report: `NO_GO_CORE_STATE`, raw one-month episodes 27.12%;
  revision/NBER/sample/occupancy checks passed
- transition research implementation: core/dataset/model/OOS/experiment 29 focused tests passed;
  actual model fit was correctly not run
- current code: fixed next-phase selection, historical destination comparison 없음
