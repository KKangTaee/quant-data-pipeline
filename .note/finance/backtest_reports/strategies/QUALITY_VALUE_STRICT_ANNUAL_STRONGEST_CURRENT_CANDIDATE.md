# Quality + Value Strict Annual Strongest Current Candidate

## 한 줄 설명

현재 `Quality + Value > Strict Annual` family에서 가장 강한 practical candidate는
quality-side `net_margin -> operating_margin`,
value-side `ocf_yield -> pcr`,
`Top N = 10`,
`Candidate Universe Equal-Weight`
조합입니다.

## 전략 구성

- family:
  - `Quality + Value`
- variant:
  - `Strict Annual`
- 기간:
  - `2016-01-01 ~ 2026-04-01`
- preset:
  - `US Statement Coverage 100`
- universe contract:
  - `Historical Dynamic PIT Universe`
- option:
  - `month_end`
- rebalance interval:
  - `1`
- top N:
  - `10`

## factor 구성

- quality:
  - `roe`
  - `roa`
  - `operating_margin`
  - `asset_turnover`
  - `current_ratio`
- value:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `operating_income_yield`
  - `per`

## overlay / contract

- `Trend Filter = off`
- `Market Regime = off`
- `Benchmark Contract = Candidate Universe Equal-Weight`
- `Benchmark Ticker = SPY`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- underperformance / drawdown guardrail:
  - `on`

## 기대 결과

- `CAGR = 31.25%`
- `MDD = -26.63%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation / Rolling / OOS = normal / normal / normal`

## 왜 strongest current candidate로 보나

- previous practical anchor 대비
  - `CAGR = 30.05% -> 31.25%`
  - `MDD = -27.43% -> -26.63%`
- gate tier를 떨어뜨리지 않고
  return / drawdown을 같이 개선했다
- 같은 pass에서 나온 더 방어적인 대안
  - `current_ratio -> operating_margin`
  는 `MDD`는 더 좋았지만
  `production_candidate / watchlist`로 내려가 strongest point를 대체하진 못했다
- 그리고 new anchor 기준 `Top N` follow-up sixth pass에서도
  `Top N = 10`이 그대로 strongest practical point로 유지됐다

## 해석

이 후보는

- `Value` 단독 strongest candidate만큼 공격적인 raw winner는 아니지만
- blended family 중에서는 가장 좋은 practical tradeoff에 가깝다
- current runtime 기준으로도
  `small_capital_trial`까지 올라가는 strongest blended candidate다

## 관련 문서

- [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
- [PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
