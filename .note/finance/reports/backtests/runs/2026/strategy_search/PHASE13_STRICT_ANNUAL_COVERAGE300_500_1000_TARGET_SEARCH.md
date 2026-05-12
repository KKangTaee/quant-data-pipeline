# PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH

## 목적

`Quality`, `Value`, `Quality + Value` strict annual family를 대상으로, `Coverage 100` 고정 탐색에서 찾지 못했던 아래 exact-hit 조건을 `Coverage 300`, `Coverage 500`, `Coverage 1000`까지 넓혀 다시 탐색한다.

- `start = 2016-01-01`
- `end = 2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`
- `CAGR >= 15%`
- `Maximum Drawdown >= -20%`
- `promotion != hold`

## 공통 전제

- variant: `Strict Annual`
- coverage preset:
  - `US Statement Coverage 300`
  - `US Statement Coverage 500`
  - `US Statement Coverage 1000`
- practical UI-reproducible search
- 조정 대상:
  - factor set
  - benchmark contract / ticker
  - `option`
  - `rebalance_interval`
  - `trend_filter`
  - `market_regime`
  - `underperformance_guardrail`
  - `drawdown_guardrail`

## preset 해석 메모

- `US Statement Coverage 300`
  - preset ticker `300`
  - dynamic PIT candidate pool `1000`
  - target size `300`
- `US Statement Coverage 500`
  - preset ticker `500`
  - dynamic PIT candidate pool `1000`
  - target size `500`
- `US Statement Coverage 1000`
  - preset ticker `1000`
  - dynamic PIT candidate pool `1000`
  - target size `1000`

## Coverage 300

서브 에이전트 병렬 탐색 기준으로, `Coverage 300`에서는 exact-hit를 찾지 못했다.

### 결과

- `exact-hit`: 없음
- strongest candidate:
  - family: `Quality > Strict Annual`
  - factor set: `q_balance_sheet`
    - `current_ratio`
    - `cash_ratio`
    - `debt_to_assets`
    - `debt_ratio`
  - `benchmark = SPY`
  - `option = month_end`
  - `top_n = 9`
  - `CAGR = 6.99%`
  - `MDD = -21.08%`
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`

### near-miss

1. `Quality > Strict Annual / q_balance_sheet / SPY / top_n = 10`
   - `CAGR = 6.83%`
   - `MDD = -22.84%`
   - `promotion = hold`

2. `Quality > Strict Annual / q_balance_sheet / LQD / top_n = 10`
   - `CAGR = 4.90%`
   - `MDD = -24.63%`
   - `promotion = hold`

### 반복된 blocker

- `validation_caution`
- `benchmark_policy_watch` 또는 `benchmark_policy_caution`
- `liquidity_policy_caution`

### 해석

`Coverage 300`에서는 `Value`보다도 `Quality`의 balance-sheet 계열이 상대적으로 덜 나빴지만, 수익률과 승격 상태 모두 목표와는 거리가 컸다.

## Coverage 500

서브 에이전트 병렬 탐색 기준으로, `Coverage 500`에서도 exact-hit를 찾지 못했다.

### 결과

- `exact-hit`: 없음
- strongest candidate:
  - family: `Value > Strict Annual`
  - factors:
    - `earnings_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `fcf_yield`
  - `benchmark = SPY`
  - `option = month_end`
  - `rebalance_interval = 1`
  - `top_n = 9`
  - `trend_filter = on`
  - `market_regime = on`
  - `underperformance_guardrail = on`
  - `drawdown_guardrail = on`
  - `CAGR = 7.66%`
  - `MDD = -20.58%`
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`

### 반복된 blocker

- `validation_status = caution`
- `validation_policy_status = caution`
- `benchmark_policy = watch`
- `liquidity_policy = caution`
- `rolling_review = caution`

### 해석

`Coverage 500`에서는 다시 `Value` family가 strongest로 돌아왔지만, `Coverage 100`에서 보였던 강한 숫자를 유지하지 못했다. wider coverage가 raw alpha를 키우기보다 validation / liquidity 부담을 더 키운 쪽에 가까웠다.

## Coverage 1000

`Coverage 1000`은 이번 탐색 pass에서 완전히 마무리하지 못했다. 서브 에이전트 병렬 탐색 기준으로 exact-hit는 표면화되지 않았고, 신뢰할 수 있는 strongest candidate를 확정할 만큼 충분한 완료 결과도 확보하지 못했다.

### 현재까지 확인된 내용

- `exact-hit`: 없음, 또는 현재 pass에서는 미확정
- strongest candidate: 확정 불가
- near-miss: 확정 불가

### 반복된 blocker

- `validation_caution`
- `validation_policy_caution`
- `liquidity_policy_caution`
- `benchmark_policy_watch / caution`
- 일부 케이스의 `price_freshness_warning`

### 해석

이번 exploratory window에서는 `Coverage 1000`이 `300 / 500`보다 훨씬 느렸고, 신뢰할 수 있게 닫힌 strongest candidate를 확보하기 전에 시간 예산이 먼저 소모됐다. 다만 중간 신호만 보면, `1000`에서 유리했던 것은 coverage 자체가 아니라 오히려 validation / liquidity 부담이 더 커진다는 점이었다.

## 통합 결론

이번 coverage expansion 탐색의 practical conclusion은 다음과 같다.

1. `Coverage 300`과 `Coverage 500`에서는 사용자가 원하는 exact-hit를 찾지 못했다.
2. `Coverage 1000`에서도 exact-hit는 표면화되지 않았고, 이번 pass에서는 신뢰 가능한 strongest candidate를 확정하지 못했다.
3. `Coverage`를 `100`에서 `300 / 500 / 1000`으로 넓힌다고 해서 자동으로 더 좋은 strict annual candidate가 나오지 않았다.
4. 오히려 wider coverage에서는 다음 병목이 더 먼저 드러났다.
   - `validation`
   - `validation policy`
   - `liquidity policy`
   - `benchmark policy`
5. 즉 지금 단계에서 다음 레버는 coverage 확대 그 자체보다:
   - factor set 재설계
   - validation / promotion contract 재해석
   - liquidity / benchmark policy 조정
   쪽이 더 유력하다.

## 현재 가장 실무적인 해석

strict annual family에서 지금까지 가장 강한 numeric reference는 여전히 `Coverage 100`에서 찾았던 `Value > Strict Annual` exact-hit numeric candidate였다.

- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `month_end / interval 1 / top_n 9`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- `CAGR = 15.84%`
- `MDD = -17.42%`
- `promotion = hold`

즉 이번 coverage 확장 탐색의 결론은:

- `Coverage 100`에서 못 찾은 exact-hit를 `300 / 500 / 1000`이 대신 해결해주지는 못했다
- coverage를 넓히는 것만으로는 `hold`와 validation 병목이 풀리지 않았다
