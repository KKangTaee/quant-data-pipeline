# Quality Value Strict Annual Value Replacement Current Candidate

## 한 줄 요약

`Quality + Value > Strict Annual` current strongest practical blended candidate를
value side에서 한 단계 더 개선한 조합은
`ocf_yield -> pcr` replacement였다.

이 조합은 baseline과 같은 gate tier를 유지하면서
`CAGR`를 조금 더 높였다.

## 전략

- family: `Quality + Value`
- variant: `Strict Annual`
- role:
  - value-side replacement current candidate
  - current strongest practical blended candidate

## 전략 구성

### 기간 / universe

- `2016-01-01 ~ 2026-04-01`
- `US Statement Coverage 100`
- `Historical Dynamic PIT Universe`

### 핵심 설정

- `Option = month_end`
- `Top N = 10`
- `Rebalance Interval = 1`
- `Benchmark Contract = Candidate Universe Equal-Weight`
- `Trend Filter = off`
- `Market Regime = off`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`

### factor 조합

- quality:
  - `roe`
  - `roa`
  - `net_margin`
  - `asset_turnover`
  - `current_ratio`
- value:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `operating_income_yield`
  - `per`

### real-money / guardrail

- current strict annual practical contract defaults 유지
- underperformance guardrail `on`
- drawdown guardrail `on`

## 결과

- `CAGR = 30.05%`
- `MDD = -27.43%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation = normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

## 왜 다시 볼 가치가 있나

- baseline `+ per` candidate 대비
  - `CAGR = 29.43% -> 30.05%`
  - `MDD = -27.43% -> -27.43%`
- 즉:
  - same drawdown
  - same gate tier
  - better CAGR

이므로 current strongest practical blended candidate를
한 단계 더 끌어올린 케이스로 볼 수 있다.

## 주의점

- improvement 폭은 크지 않다.
- 따라서 next step은 이 candidate를 완전히 다른 family로 볼 것이 아니라,
  current strongest point의 refined replacement로 읽는 편이 맞다.

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
