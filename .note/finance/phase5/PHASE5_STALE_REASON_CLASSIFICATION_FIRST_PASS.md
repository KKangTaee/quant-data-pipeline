# Phase 5 Stale Reason Classification First Pass

## 목적

- `Price Freshness Preflight`가 stale / missing symbol을 보여줄 때,
  사용자가 단순 경고를 넘어서
  “왜 이런 상태로 보이는지”
  를 더 쉽게 해석할 수 있도록 heuristic reason을 붙인다.

## 현재 분류 범위

이 분류는 **확정 판정이 아니라 heuristic**이다.

현재 사용 라벨:

- `likely_delisted_or_symbol_changed`
- `asset_profile_error`
- `missing_price_rows`
- `minor_source_lag`
- `source_gap_or_symbol_issue`
- `persistent_source_gap_or_symbol_issue`

## 분류 규칙

### `likely_delisted_or_symbol_changed`

- asset profile status가
  - `delisted`
  - `not_found`
  이거나
- `delisted_at` 값이 존재하는 경우

### `asset_profile_error`

- asset profile status가 `error`인 경우

### `missing_price_rows`

- strict preflight price summary에서
  latest price date 자체가 비어 있는 경우

### `minor_source_lag`

- requested end date 대비 lag가 `7`일 이하인 경우

### `source_gap_or_symbol_issue`

- requested end date 대비 lag가 `30`일 이하인 경우

### `persistent_source_gap_or_symbol_issue`

- requested end date 대비 lag가 `30`일을 초과하는 경우

## UI 노출 위치

- strict single strategy의
  `Price Freshness Preflight`
  -> `Preflight Details`
- 표시되는 것:
  - `Heuristic Reason Summary`
  - `Stale / Missing Classification`

## 해석 원칙

- 이 분류는
  “refresh를 다시 하면 해결될 가능성이 큰지”
  와
  “상폐/심볼 변경처럼 구조적 이슈일 가능성이 큰지”
  를 빠르게 가늠하기 위한 진단 레이어다
- 공식 delisting confirmation을 의미하지 않는다

## 현재 제품 철학과의 관계

- strict preset은 historical backtest 기준으로 run-level에서 고정된다
- stale symbol은 run 전체에서 미리 교체하지 않는다
- 대신 preflight에서
  - 최신성 경고
  - stale / missing list
  - heuristic reason
  을 함께 보여주고,
  실제 rebalance date마다 usable 여부로 자연스럽게 제외한다

## 향후 확장 후보

- local ingestion gap과 source gap을 더 정확히 구분하는 direct source probe
- confirmed delisted / corporate action 상태 추적
- symbol mapping / ticker change 테이블 연계

## 결론

- Phase 5 first pass에서는
  stale reason classification을
  “lightweight diagnostic layer”
  로 도입하는 것이 가장 적절하다
- 현재 구현은
  historical backtest semantics를 바꾸지 않으면서
  운영 해석력을 높이는 수준으로 제한한다
