# Phase 10 Dynamic PIT Second Pass Hardening

## 목적

- Phase 10 first pass에서 annual strict family에만 열어둔 `historical_dynamic_pit` 계약을
  더 실전형 validation surface에 가깝게 보강한다.
- 이번 pass의 초점은 아래 네 가지였다.
  1. listing / delisting / symbol continuity second pass
  2. dynamic universe snapshot persistence
  3. quarterly family dynamic PIT expansion
  4. perfect constituent-history source reinforcement의 현실적 first pass

## 이번에 실제 보강된 내용

### 1. continuity / listing / delisting diagnostics 추가

`finance/sample.py`의 dynamic universe builder는
rebalance-date membership를 계산할 때 아래 continuity 진단값도 같이 남긴다.

- `continuity_ready_count`
- `pre_listing_excluded_count`
- `post_last_price_excluded_count`
- `asset_profile_delisted_count`
- `asset_profile_issue_count`

또 candidate-level 상태 표도 같이 만든다.

- `first_price_date`
- `last_price_date`
- `price_row_count`
- `profile_status`
- `profile_delisted_at`
- `profile_error`

중요한 점:

- 현재 `asset_profile` 정보는 **diagnostic only**다
- 즉 membership hard filter로 쓰는 것이 아니라,
  current-source 기준 continuity / delisting 단서를 보여주는 용도로만 쓴다

### 2. dynamic universe snapshot persistence

dynamic run을 history에 남길 때
별도 artifact를 같이 기록하도록 보강했다.

- artifact root:
  - `.note/finance/backtest_artifacts/`
- 파일:
  - `dynamic_universe_snapshot.json`

artifact에는 아래가 들어간다.

- `universe_contract`
- `dynamic_target_size`
- `dynamic_candidate_count`
- `universe_debug`
- `snapshot_rows`
- `candidate_status_rows`

history context에는 아래 preview도 함께 남긴다.

- `dynamic_universe_artifact`
- `dynamic_universe_preview_rows`

따라서 이후 history drilldown에서
run 당시 membership drift와 candidate continuity 상태를 다시 볼 수 있다.

### 3. quarterly family dynamic PIT first pass 확장

`historical_dynamic_pit` 계약을 아래 quarterly family에도 열었다.

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

이번 pass에서 quarterly는 아래 surface까지 포함한다.

- single-strategy form `Universe Contract`
- runtime dynamic membership builder
- compare override
- result/meta readout
- history artifact persistence

즉 현재 dynamic PIT 구현 범위는
annual strict only가 아니라
**annual strict + quarterly strict prototype single/compare first pass**
로 넓어졌다.

### 4. perfect constituent-history source reinforcement의 현재 수준

이번 pass에서는
licensed historical constituent DB 같은 완전한 source를 새로 붙이진 않았다.

대신 아래를 통해 현재 contract를 더 명시적으로 강화했다.

- price-window continuity diagnostics
- asset-profile status diagnostics
- candidate-level status persistence
- per-rebalance membership snapshot persistence
- warning / interpretation 문구에서
  `approximate PIT` / `not perfect constituent-history`를 계속 명시

즉 이번 pass의 강화는
**perfect constituent-history 구현**이 아니라,
현재 approximation이 어디까지 유효하고 어디서 한계가 있는지
운영자가 다시 추적할 수 있게 만든 보강이다.

## smoke validation

`.venv` 기준 small manual universe smoke에서 아래를 확인했다.

### annual strict dynamic

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

공통 확인 결과:

- `universe_contract = historical_dynamic_pit`
- `rows = 36`
- `dynamic_universe_snapshot_rows` 존재
- `dynamic_candidate_status_rows` 존재
- `universe_debug.statement_freq = annual`
- continuity diagnostic keys 존재

### quarterly strict dynamic

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

공통 확인 결과:

- `universe_contract = historical_dynamic_pit`
- `rows = 36`
- `dynamic_universe_snapshot_rows` 존재
- `dynamic_candidate_status_rows` 존재
- `universe_debug.statement_freq = quarterly`
- continuity diagnostic keys 존재

### history artifact smoke

- dynamic annual bundle을 history에 append한 뒤,
  latest record에서 아래를 확인했다.

- `dynamic_universe_artifact` 존재
- artifact json path 실제 존재
- `dynamic_universe_preview_rows = 24`

### compare smoke

- annual strict compare dynamic
- quarterly strict compare dynamic

둘 다 runtime까지 override가 내려가고,
`dynamic_universe_snapshot_rows` / `dynamic_candidate_status_rows`가 bundle에 유지되는 것을 확인했다.

## 현재 contract 해석

지금 Phase 10 dynamic PIT는 아래처럼 읽는 것이 가장 정확하다.

- current static preset을 대체한 final engine이 아니다
- 하지만 annual strict only였던 first pass보다
  **실전형 validation surface가 더 넓고 추적 가능해진 상태**다
- candidate continuity / delisting / late listing 해석이 더 쉬워졌고
- run 이후 membership snapshot을 history artifact로 다시 검토할 수 있다

다만 여전히 아래는 아니다.

- licensed perfect constituent-history
- exact historical index constituent replay
- complete symbol continuity master

따라서 real-money 판단에서는
이 mode를 현재 가장 우선하는 validation contract로 쓰되,
결과 해석 시 `approximate PIT`라는 전제를 유지하는 것이 맞다.

## 다음 순서

1. user batch QA
2. static vs dynamic preset-level interpretation 정리
3. perfect constituent-history source procurement / licensing 판단
4. 이후 productization Phase 11 재진입
