# Phase 10 Completion Summary

## 목적

- Phase 10에서 진행한 `historical dynamic PIT universe` workstream을
  practical closeout 관점에서 정리한다.
- 현재 코드 기준으로
  - 무엇이 구현되었는지
  - 어디까지를 실전형 validation contract로 읽어야 하는지
  - 어떤 한계를 명시적으로 남겨야 하는지
  를 한 번에 확인할 수 있게 한다.

## Phase 10에서 완료된 것

### 1. dynamic universe contract 추가

strict family form에 `Universe Contract`가 추가되었다.

- `Static Managed Research Universe`
- `Historical Dynamic PIT Universe`

즉 현재 백테스트는
단순 static preset만이 아니라,
rebalance-date 기준으로 membership를 다시 계산하는 dynamic validation mode를 함께 가진다.

### 2. annual strict family dynamic PIT first pass

아래 annual strict 3종이 dynamic PIT mode를 지원한다.

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

지원 범위:

- single strategy
- compare
- history / prefill

### 3. quarterly strict prototype dynamic PIT first pass

아래 quarterly strict prototype 3종도 dynamic PIT mode를 지원한다.

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

단, 이 결과는 여전히 `research-only quarterly family`로 해석하는 것이 맞다.

### 4. approximate PIT membership builder 구현

current implementation은 각 rebalance date마다 다음을 사용한다.

- candidate pool의 해당 시점 price
- `latest_available_at <= rebalance_date` 조건을 만족하는 최신 statement shadow row
- 해당 row의 `shares_outstanding`

이를 바탕으로 `approx_market_cap`을 계산하고 top-N membership를 다시 구성한다.

즉 현재 dynamic PIT는
`perfect constituent-history engine`이 아니라
**current-source 기반 approximate PIT + diagnostics contract**
로 보는 것이 가장 정확하다.

### 5. continuity / profile diagnostics 추가

dynamic PIT second pass에서는
membership 변화가 왜 발생했는지 읽을 수 있도록 continuity/profile 진단을 함께 남긴다.

예:

- `continuity_ready_count`
- `pre_listing_excluded_count`
- `post_last_price_excluded_count`
- `asset_profile_delisted_count`
- `asset_profile_issue_count`

candidate-level row도 남는다.

- `first_price_date`
- `last_price_date`
- `price_row_count`
- `profile_status`
- `profile_delisted_at`
- `profile_error`

### 6. result / history surface hardening

dynamic run 결과 surface에는 아래가 함께 남는다.

- result row:
  - `Universe Membership Count`
  - `Universe Contract`
- meta:
  - `universe_contract`
  - `dynamic_candidate_count`
  - `dynamic_target_size`
  - `universe_debug`
- bundle top-level:
  - `dynamic_universe_snapshot_rows`
  - `dynamic_candidate_status_rows`

history에는 아래가 추가 저장된다.

- `dynamic_universe_preview_rows`
- `dynamic_universe_artifact`
- `.note/finance/backtest_artifacts/.../dynamic_universe_snapshot.json`

또 result UI에는 `Dynamic Universe` 탭이 추가되어
dynamic run의 membership/continuity row를 history drilldown 없이 바로 확인할 수 있다.

### 7. compare / runtime 실사용성 보강

Phase 10 후반 QA 과정에서 아래를 보강했다.

- dynamic PIT 결과 설명 문구 보강
- history artifact 설명 보강
- `Load Into Form` UX 안정화
- compare 실행에서 공통 DB 입력 재사용을 위한 small in-process cache 추가

이로써 dynamic annual/quarterly compare는 여전히 무겁지만,
같은 candidate pool / date window를 공유할 때 중복 로드를 일부 줄일 수 있게 되었다.

## 핵심 결과

### static research contract와 dynamic validation contract가 분리되었다

Phase 10의 가장 중요한 결과는
current strict preset을 그대로 덮어쓰는 것이 아니라,
**static research mode와 dynamic validation mode를 병렬로 분리했다는 점**이다.

즉 현재 해석은 다음처럼 고정된다.

- `static_managed_research`
  - 빠른 연구 / 운영 / 비교용
- `historical_dynamic_pit`
  - 실전형 검증에 더 가까운 mode

### 실전 투자 판단은 dynamic PIT를 우선 기준으로 볼 수 있게 되었다

아직 institutional-grade perfect PIT는 아니지만,
real-money 관점에서는
static preset보다 dynamic PIT 결과를 우선 해석하는 것이 맞다는 contract가 코드/문서/UI에 함께 반영되었다.

## 남겨둔 것

이번 phase에서 의도적으로 남겨둔 것:

- stronger listing / delisting source
- better symbol continuity source
- closer-to-perfect constituent-history reinforcement
- dynamic membership map 자체의 더 강한 compare-level reuse/cache
- productization workflow

즉 current dynamic PIT는 closeout 가능하지만,
장기적으로 더 높은 fidelity를 원하면 additional source hardening이 필요하다.

## validation 상태

현재 상태:

- implementation scope:
  - `completed`
- assistant-side smoke / QA fix:
  - `completed`
- user-side checklist review:
  - `partially completed`

다만 현재 phase 목표는
`perfect PIT` 달성이 아니라
**dynamic PIT validation contract first/second pass 확보**
였기 때문에,
현 시점에서는 practical closeout으로 보는 것이 맞다.

## Phase 10 종료 판단

현재 기준으로는:

- code / docs / checklist / operator readout:
  - `completed`
- dynamic PIT annual + quarterly strict prototype first/second pass:
  - `completed`
- remaining perfect-PIT reinforcement:
  - `deferred backlog`
- next phase preparation:
  - `ready`

즉 지금은
**Phase 10을 practical completion 상태로 닫고,
다음 단계는 Phase 11 productization/workflow 쪽으로 넘어가는 것이 자연스럽다**
고 본다.
