# Recommendation

Status: feasibility data gate completed; data expansion decision required
Last Updated: 2026-08-12

## Recommended Direction

현재 observed-state는 유지하고 fixed adjacent monitor를 미래 예측으로 간주하지 않는다.
사용자가 승인한 forecast target은 다음 두 개다.

1. `P(next confirmed phase = destination | current information)`
2. `P(any confirmed transition within next 3 official monthly releases | current information)`

첫 번째는 다음 전환 목적지, 두 번째는 `전환 임박도`를 위한 별도 event다. 정확한
3·6개월 뒤 phase classification은 반려됐다.

## Completed Feasibility Gate

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

## Required Next Decision

다음 작업은 모델이나 UI가 아니라 **RTDSM/ADS data expansion feasibility**다. 승인 시:

1. 공식 파일의 vintage/date/variable contract를 감사한다.
2. 기존 `macro_series_vintage_observation`과 충돌하지 않는 provider schema를 정한다.
3. 1960년대 이후 usable origin과 independent transition support가 gate를 통과하는지
   먼저 dry-run한다.
4. current observed-state와 신규 long-history state의 최근 공통기간 parity를 검증한다.
5. gate 통과 후에만 destination/imminence model을 chronological OOS로 평가한다.

신규 provider를 넣어도 사건 gate 또는 parity가 실패하면 기능 개발을 최종 중단한다.

## Event And Publication Boundary

data gate 통과는 probability 공개 승인이 아니다. 이후 모델은 strongest expanding
baseline보다 destination log loss / Brier가 좋아야 하며, imminence calibration과
episode-block holdout을 별도로 통과해야 한다. 조건부 scenario는 검증된 model
sensitivity에서만 생성한다.

## Evidence Summary

- actual current read model: 2026-07-31 READY, 위축, 8/8 series
- all focused economic-cycle tests: 226 passed
- next-transition feasibility tests: 6 passed (included above)
- actual sample report: `NO_GO_DATA`, 148 usable origins, 32 events
- current code: fixed next-phase selection, historical destination comparison 없음
