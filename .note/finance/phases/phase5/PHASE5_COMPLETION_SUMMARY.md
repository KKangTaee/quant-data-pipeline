# Phase 5 Completion Summary

## 목적

- Phase 5 첫 챕터에서 구현·검증된 strict family / risk overlay 작업을 마감 관점에서 정리한다.
- 다음 phase를 열기 전에,
  현재 코드와 문서가 어디까지 완료 상태인지 한 번에 확인할 수 있게 한다.

## Phase 5에서 완료된 것

### 1. strict factor strategy library baseline 정리

현재 strict annual family는 아래 3개를 중심으로 정리되었다.
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

또한 canonical preset / period / top-N 기준을 문서로 고정했고,
single / compare 기준 baseline 연구 문서를 남겼다.

### 2. compare advanced-input parity 보강

compare 화면에서도 strict family 전략별 advanced input을 따로 조절할 수 있게 되었다.

전략별 조절 가능 항목:
- preset
- factor set
- `top_n`
- `rebalance_interval`
- trend filter on/off
- trend filter window

즉 strict family도 price-only 전략처럼
compare에서 strategy-specific override를 실사용 가능한 수준으로 가지게 되었다.

### 3. first risk overlay 구현

Phase 5 first overlay는 아래로 고정되었다.
- `month-end MA200 trend filter + cash fallback`

현재 동작:
- month-end rebalance 시점에만 체크
- `Close < MA(window)`면 해당 종목 비중은 cash로 남김
- 다음 rebalance까지 유지

즉 intramonth trigger는 아직 아니고,
strict factor family 위에 얹는 first-pass overlay로 정리되었다.

### 4. selection interpretation / stale diagnostics 강화

strict family 결과 해석용 surface가 크게 보강되었다.

현재 확인 가능한 것:
- `Selection History`
- `Selection Frequency`
- `Interpretation Summary`
- `Overlay Rejection Frequency`
- `Cash Share`
- stale / missing symbol heuristic classification

또한 주요 tooltip/help copy는 한국어 기준으로 정리되었다.

### 5. historical managed-universe policy 정리

strict managed preset은 현재 다음 정책으로 고정되었다.
- run-level static preset 유지
- selected end date stale 여부로 run 전체 universe를 미리 교체하지 않음
- 각 rebalance date마다
  - 가격이 있는 종목
  - factor snapshot이 usable한 종목
  만 자연스럽게 후보로 남김

즉 현재 strict family backtest는
historical backtest 타당성을 우선하는 방향으로 정리되어 있다.

### 6. manual QA / 운영 문서화

Phase 5 종료 시점에는
manual test checklist까지 같이 정리되었다.

관련 문서:
- `PHASE5_STRICT_FAMILY_TEST_CHECKLIST.md`

이 체크리스트는 이후 phase closeout 때도 기본 산출물로 남기도록
repository guidance에도 반영되었다.

## Phase 5 핵심 결과

### strict annual family가 “연구 가능한 전략군” 단계로 올라갔다

Phase 4에서 strict annual family는 usable public candidate 수준이었다면,
Phase 5에서는 그 위에:
- compare parity
- first overlay
- interpretation
- diagnostics

가 올라가면서,
단순 실행 가능한 전략이 아니라
**비교·해석·검증 가능한 연구 전략군**
으로 정리되었다.

### overlay 연구의 첫 기준점이 생겼다

이번 phase에서 `Trend Filter Overlay` on/off 비교가 문서화되었기 때문에,
이후 second overlay 후보를 붙일 때도
명확한 baseline 위에서 비교할 수 있게 되었다.

## 아직 남겨둔 것

아래는 이번 챕터 미완료가 아니라,
다음 챕터 후보로 넘긴 항목이다.

- `quarterly strict family` 실제 구현
- `second overlay` 실제 구현
- overlay 해석/리포트 추가 polish
- 더 넓은 strategy-library 비교 연구

## Phase 5 종료 판단

현재 기준으로는:
- Phase 5 first chapter implementation scope:
  - `completed`
- Phase 5 first chapter user validation:
  - `completed`
- 남은 것은:
  - next-phase kickoff 판단

즉 지금은
**Phase 5 first chapter를 closeout하고 다음 chapter/phase를 고를 시점**
으로 보는 것이 맞다.
