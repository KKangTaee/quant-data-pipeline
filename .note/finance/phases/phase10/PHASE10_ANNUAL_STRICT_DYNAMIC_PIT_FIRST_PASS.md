# Phase 10 Annual Strict Dynamic PIT First Pass

## 목적

- `managed static research universe`만으로는 부족한 실전형 검증 계약을 향해,
  annual strict family에 `Historical Dynamic PIT Universe` first pass를 연다.
- 기존 static mode는 그대로 유지하고,
  annual strict single-strategy surface에만 additive path로 붙인다.

## 이번에 실제 구현된 범위

### 1. annual strict single-strategy UI

아래 3개 form의 `Advanced Inputs` 안에 `Universe Contract` selector를 추가했다.

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

선택 가능한 mode:

- `Static Managed Research Universe`
- `Historical Dynamic PIT Universe`

### 2. dynamic PIT universe builder first pass

annual strict dynamic mode는 rebalance date마다 아래 순서로 membership를 다시 구성한다.

1. candidate pool price row 확보
2. `latest_available_at <= rebalance_date`인 최신 annual statement shadow row 선택
3. `shares_outstanding` 선택
4. rebalance-date close와 곱해 `approx_market_cap` 계산
5. target size 기준으로 top-N membership 구성

## 현재 contract

### Static Managed Research Universe

- 기존 strict annual preset 계약 유지
- preset membership 자체는 run 전체 동안 고정
- 각 rebalance date에서는 usable price / factor row만 후보로 남음

### Historical Dynamic PIT Universe

- first pass에서는 annual strict family only
- managed candidate pool 안에서
  rebalance-date 기준으로 membership를 다시 계산
- perfect constituent-history는 아니고
  `rebalance-date approximate PIT market-cap` contract다

## preset / candidate pool rule

- strict annual preset이 `US Statement Coverage 100 / 300 / 500 / 1000`이면
  dynamic PIT first pass는 현재 managed `US Statement Coverage 1000` candidate pool을 anchor로 사용한다
- target membership는 preset size를 따른다
  - `100`
  - `300`
  - `500`
  - `1000`
- manual mode에서는 current manual ticker set이 candidate pool이 된다

## dynamic preflight 의미

- dynamic PIT first pass에서는 candidate pool 전체가 requested start부터 가격 이력을 가져야 한다고 보지 않는다
- 늦게 상장된 종목과 evolving universe를 허용해야 하므로,
  dynamic preflight는 **selected end까지 usable DB price history가 존재하는지**를 기준으로 candidate를 읽는다
- 따라서 아래 두 값은 다를 수 있다
  - `dynamic_candidate_count`
  - `universe_debug.candidate_pool_count`
- 이 차이는 현재 contract에서 자연스러운 현상이며,
  candidate pool 중 일부가 selected end 시점까지 DB 가격 이력이 없어서 natural exclusion된 것으로 해석한다

## runtime / result surface 변경

### result table

아래 컬럼이 추가된다.

- `Universe Membership Count`
- `Universe Contract`

### bundle meta

아래 meta가 추가된다.

- `universe_contract`
- `dynamic_candidate_count`
- `dynamic_target_size`
- `universe_builder_scope`
- `universe_debug`

`universe_debug`에는 first-pass membership summary가 들어간다.

- `candidate_pool_count`
- `target_size`
- `first_membership_count`
- `last_membership_count`
- `min_membership_count`
- `max_membership_count`
- `avg_membership_count`
- `avg_turnover_count`
- `avg_turnover_pct`

## history / prefill

- annual strict dynamic run은 history에 `universe_contract`와 `dynamic_target_size`를 같이 남긴다
- `Load Into Form` 시 annual strict single-strategy form의 `Universe Contract`도 다시 채워진다

## compare mode first-pass extension

- annual strict compare blocks에도 `Universe Contract` selector를 추가했다
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- compare overrides는 아래 dynamic 입력을 runtime으로 넘긴다
  - `universe_contract`
  - `dynamic_candidate_tickers`
  - `dynamic_target_size`
- compare highlight table에는 아래 dynamic readout이 추가된다
  - `Universe Contract`
  - `Dynamic Candidate Pool`
  - `Membership Avg`
  - `Membership Range`

## 현재 한계

- quarterly strict family는 아직 Phase 10 범위 밖이다
- listing / delisting / symbol continuity의 perfect PIT source는 아직 없다
- therefore 이 mode는
  perfect constituent-history engine이 아니라
  **annual-first approximate PIT validation mode**
  로 읽는 것이 맞다

## smoke validation

작은 annual strict smoke에서 아래를 확인했다.

- runtime functions:
  - `run_quality_snapshot_strict_annual_backtest_from_db(...)`
  - `run_value_snapshot_strict_annual_backtest_from_db(...)`
  - `run_quality_value_snapshot_strict_annual_backtest_from_db(...)`
- mode:
  - `universe_contract = historical_dynamic_pit`
- result:
  - `Universe Membership Count`가 result row에 기록됨
  - `universe_debug`가 bundle meta에 기록됨
  - annual strict 3종 모두 bundle 반환

preset 기반 smoke에서도 아래를 확인했다.

- strategy:
  - `Quality Snapshot (Strict Annual)`
- mode:
  - `preset = US Statement Coverage 100`
  - `Universe Contract = historical_dynamic_pit`
  - candidate pool anchor = `US Statement Coverage 1000`
- result:
  - run 자체는 정상 완료
  - `dynamic_candidate_count = 1000`
  - `universe_debug.candidate_pool_count = 921`
  - 첫 `Universe Membership Count = 100`
- 해석:
  - 현재 managed 1000 candidate 중 일부는 selected end 기준 DB price history가 없어서 natural exclusion 되었고,
    이것이 dynamic first-pass contract와 맞다

## 다음 순서

1. user checklist validation
2. static vs dynamic 실제 preset 비교
3. listing / delisting / continuity second pass
4. quarterly / persistence / compare deeper pass 우선순위 재판단

## 후속 보강 현황

이 문서는 annual strict first pass 기준 요약이다.

그 이후 추가된 second-pass hardening은 별도 문서로 정리했다.

- `PHASE10_DYNAMIC_PIT_SECOND_PASS_HARDENING.md`

후속 보강 범위:

- continuity / delisting diagnostics
- dynamic universe history artifact persistence
- quarterly strict prototype dynamic PIT first pass
- perfect constituent-history 한계 명시 강화
