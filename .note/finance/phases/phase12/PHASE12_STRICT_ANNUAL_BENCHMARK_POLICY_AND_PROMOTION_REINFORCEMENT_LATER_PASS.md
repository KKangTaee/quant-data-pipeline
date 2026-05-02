# Phase 12 Strict Annual Benchmark Policy And Promotion Reinforcement Later Pass

## 목적

Strict annual family의 `benchmark overlay`가 단순 비교용 숫자에 그치지 않고,
실제 `promotion_decision`에 직접 영향을 주도록 보강한다.

## 쉽게 말하면

이전까지는:

- benchmark가 있나
- validation이 `normal / watch / caution` 중 어디인가
- static universe인가 dynamic universe인가

정도만 보고 승격 판단을 내렸다.

이번에는 여기에 아래 기준을 더 넣었다.

- benchmark와 실제로 충분히 겹치는가
- strategy의 net CAGR이 benchmark보다 너무 약하지는 않은가

즉 "benchmark를 붙이긴 했는데, 그 benchmark가 promotion 판단에 정말 의미 있게 쓰이고 있나?"를
더 명확하게 보게 만든 later pass다.

## 추가된 계약

Strict annual 3종에 아래 입력이 추가되었다.

- `Min Benchmark Coverage (%)`
- `Min Net CAGR Spread (%)`

대상 전략:

- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

## 용어 설명

### `Benchmark Coverage`

- 기본 설명:
  전략 결과와 benchmark 결과가 실제로 같은 날짜에 얼마나 많이 겹치는지 보는 비율이다.
- 왜 사용되는지:
  benchmark overlay가 있더라도 날짜가 너무 적게 겹치면, 그 benchmark 비교는 신뢰도가 약해진다.
- 예시 / 필요 상황:
  backtest는 길게 돌렸는데 benchmark 데이터가 일부만 겹친다면, CAGR spread나 rolling underperformance 해석이 과장될 수 있다.

### `Net CAGR Spread`

- 기본 설명:
  전략의 `net CAGR`에서 benchmark의 `CAGR`를 뺀 값이다.
- 왜 사용되는지:
  실전 승격 후보라면 적어도 benchmark보다 너무 심하게 뒤처지지는 않는지 확인해야 한다.
- 예시 / 필요 상황:
  drawdown은 좋더라도 benchmark보다 CAGR이 계속 많이 낮다면, 바로 `real_money_candidate`로 올리기 어렵다.

### `Benchmark Policy`

- 기본 설명:
  benchmark 비교를 promotion 판단에 쓰기 전에 통과해야 하는 최소 기준이다.
- 왜 사용되는지:
  benchmark가 있다는 사실만으로는 충분하지 않고, coverage와 상대 성과가 최소 기준을 넘는지 봐야 하기 때문이다.
- 예시 / 필요 상황:
  benchmark는 붙었지만 coverage가 낮거나 CAGR spread가 정책 기준 아래라면 `watch` 또는 `caution`으로 둔다.

## 구현 내용

runtime은 now 아래 값을 계산하고 meta에 남긴다.

- `benchmark_policy_status`
  - `normal`
  - `watch`
  - `caution`
  - `unavailable`
- `benchmark_policy_watch_signals`
- `benchmark_policy_coverage_pass`
- `benchmark_policy_spread_pass`

그리고 `promotion_decision`은 이제 아래를 함께 본다.

- `validation_status`
- `benchmark_policy_status`
- `universe_contract`
- `price_freshness`

## 현재 판정 규칙

### `real_money_candidate`

아래가 모두 맞아야 한다.

- benchmark available
- `validation_status = normal`
- `benchmark_policy_status = normal`
- `universe_contract != static_managed_research`
- `price_freshness`가 `warning / error`가 아님

### `hold`

아래 중 하나면 `hold`로 둔다.

- benchmark unavailable
- `validation_status = caution`
- `benchmark_policy_status = caution`
- `price_freshness = error`

### `production_candidate`

위 두 경우가 아니면 중간 단계인 `production_candidate`로 둔다.

쉽게 말하면:

- 완전히 괜찮으면 `real_money_candidate`
- 명확히 위험하면 `hold`
- 그 사이면 `production_candidate`

## UI / History 반영 범위

single / compare / history 모두 같은 계약을 따른다.

- single `Real-Money`
  - `Benchmark Policy`
  - `Min Coverage`
  - `Actual Coverage`
  - `Min Net CAGR Spread`
  - `Actual Net CAGR Spread`
- single `Execution Context`
  - benchmark policy status / signals / thresholds
- compare `Strategy Highlights`
  - `Benchmark Policy`
- history / `Load Into Form`
  - 두 threshold가 다시 복원됨

## 현재 한계

- 아직 `benchmark policy`가 전략 규칙 자체를 바꾸지는 않는다.
  - 지금은 promotion / caution 판단을 강화하는 쪽이다.
- threshold는 first-pass default다.
  - 실전 운용 전에 더 보수적으로 조정할 수 있다.
- broader liquidity / spread / AUM-aware execution policy는 여전히 later pass다.

## 의미

이번 작업으로 strict annual family는
"benchmark가 붙어 있다" 수준에서 한 단계 더 가서,
"benchmark 비교가 promotion 판단에 실제로 반영된다" 수준까지 올라왔다.
