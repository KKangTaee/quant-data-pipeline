# PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH

## 목적

`Quality`, `Value`, `Quality + Value` strict annual family를 대상으로, 아래 조건을 동시에 만족하는 포트폴리오가 존재하는지 다시 탐색한다.

- `promotion = real_money_candidate`
- raw summary 기준 `CAGR > SPY`
- `Maximum Drawdown >= -25%`
- 기간: `2016-01-01 ~ 2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- practical UI-reproducible settings
- 비교 일관성을 위해 우선 `top_n <= 10`

이번 탐색은 family별로 서브 에이전트를 나눠 병렬로 수행했다.

## SPY 기준선

- `CAGR = 14.0899%`
- `MDD = -33.7172%`

즉 이번 exact-hit는 다음을 의미한다.

- `SPY`보다 CAGR이 높다
- drawdown은 `25%` 이내다
- `promotion`도 `real_money_candidate`다

## 1. Quality Strict Annual

### 결과

- `exact-hit`: 없음

### strongest candidate

- factor set: `capital_discipline`
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- `month_end / rebalance_interval = 1 / top_n = 10`
- `benchmark = SPY`
- `CAGR = 15.80%`
- `MDD = -27.97%`
- `promotion = hold`

### near-miss

- factor set: `balance_sheet`
  - `current_ratio`
  - `cash_ratio`
  - `debt_to_assets`
  - `debt_ratio`
- `month_end / rebalance_interval = 1 / top_n = 10`
- `benchmark = SPY`
- `CAGR = 14.46%`
- `MDD = -26.83%`
- `promotion = hold`

### blocker

- `validation = caution`
- `benchmark_policy = watch/caution`
- `liquidity_policy = caution`

### 해석

`Quality`는 raw candidate는 나왔지만, `MDD 25% 이내`와 `real_money_candidate`를 동시에 맞춘 조합은 없었다.

## 2. Value Strict Annual

### 결과

- `exact-hit`: 없음

### strongest raw candidate

- factors:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `month_end / interval 1 / top_n 10`
- `trend_filter = off`
- `market_regime = off`
- `promotion = real_money_candidate`
- `CAGR = 29.89%`
- `MDD = -29.15%`

이 후보는 `promotion = real_money_candidate`와 `SPY` 초과 CAGR은 만족하지만, `MDD 25% 이내`는 만족하지 못한다.

### strongest numeric near-miss

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

### blocker

- `validation_caution`
- `validation_policy_caution`
- `rolling_review = caution`

### 해석

`Value`는 세 family 중 가장 유망했다.

- `real_money_candidate`까지 올라간 strongest raw winner가 있었고
- `MDD 25% 이내`까지 만족하는 numeric candidate도 있었다

하지만 이 둘이 한 후보에서 동시에 만나는 조합은 이번 탐색 범위에서는 없었다.

## 3. Quality + Value Strict Annual

### 결과

- `exact-hit`: 없음

### strongest candidate

- quality set:
  - `current_ratio`
  - `cash_ratio`
  - `debt_to_assets`
  - `debt_ratio`
- value set:
  - `ocf_yield`
  - `fcf_yield`
  - `pcr`
  - `pfcr`
- `benchmark = LQD`
- `month_end / rebalance_interval = 6 / top_n = 30`
- `promotion = production_candidate`
- `CAGR = 5.89%`
- `MDD = -19.76%`

### near-miss

- 같은 factor 구조
- `benchmark = Candidate Universe Equal-Weight`
- `CAGR = 2.40%`
- `MDD = -13.57%`
- `promotion = hold`

### blocker

- drawdown은 잘 낮아지지만 `CAGR`가 너무 약함
- `LQD` benchmark로 `hold`를 일부 피할 수 있어도 `real_money_candidate`까지는 못 올라감

### 해석

`Quality + Value`는 방어형 candidate로는 의미가 있지만, 이번 조건의 exact-hit family는 아니었다.

## 통합 결론

이번 탐색에서 `Quality`, `Value`, `Quality + Value` strict annual family 모두를 다시 확인했지만, 아래 조건을 동시에 만족하는 exact-hit는 찾지 못했다.

- `promotion = real_money_candidate`
- `CAGR > SPY`
- `MDD >= -25%`

### 가장 중요한 practical conclusion

1. `Value`가 가장 가까웠다.
2. `Quality`는 raw edge는 있으나 drawdown과 promotion에서 같이 막혔다.
3. `Quality + Value`는 drawdown은 좋지만 CAGR이 약했다.

즉 지금 strict annual family에서 가장 가까운 구조는 다음 두 축으로 나뉜다.

- `Value` strongest raw winner
  - `real_money_candidate`
  - high CAGR
  - 하지만 drawdown too deep

- `Value` strongest numeric near-miss
  - good CAGR
  - `MDD 25%` 이내
  - 하지만 `hold`

## 추천 해석

이번 질문에 대해 한 개만 꼽으라면, 가장 실무적으로 의미 있는 후보는 아래다.

- family: `Value > Strict Annual`
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

이 후보를 추천하는 이유는:

- `SPY`보다 CAGR이 높고
- `MDD 25%` 이내도 만족하며
- strict annual family 중 가장 현실적인 numeric balance를 보여주기 때문이다

다만 질문의 exact 조건인 `promotion = real_money_candidate`까지는 아직 못 올라왔다.
