# Quality Value Strict Annual POR Replacement Current Candidate

## 한 줄 요약

`Quality + Value > Strict Annual` current strongest practical point를
value side에서 한 단계 더 개선한 조합은
`operating_income_yield -> por` replacement다.

이 조합은 previous strongest point와 같은 gate / 같은 `MDD`를 유지하면서
`CAGR`를 조금 더 높였다.

## 전략

- family: `Quality + Value`
- variant: `Strict Annual`
- role:
  - current strongest practical blended candidate
  - Phase 16 downside follow-up 기준 strongest point

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
  - `operating_margin`
  - `asset_turnover`
  - `current_ratio`
- value:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `pcr`
  - `por`
  - `per`

### real-money / guardrail

- current strict annual practical contract defaults 유지
- underperformance guardrail `on`
- drawdown guardrail `on`

## 결과

- `CAGR = 31.82%`
- `MDD = -26.63%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation = normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

## 왜 다시 볼 가치가 있나

- previous strongest practical point 대비
  - `CAGR = 31.25% -> 31.82%`
  - `MDD = -26.63% -> -26.63%`
- 즉:
  - same drawdown
  - same gate tier
  - better CAGR

이므로 current runtime 기준 strongest practical blended candidate를
한 단계 더 끌어올린 케이스로 읽는 게 맞다.

## 주의점

- 이번 bounded search 안에서는
  same gate를 유지하면서 `MDD`를 더 낮춘 후보는 나오지 않았다.
- 더 낮은 `MDD`를 주는 후보는 있었지만
  `production_candidate / watchlist`로 내려갔다.
- 따라서 이 문서는
  “더 안전한 후보”라기보다
  “같은 practical tier에서 더 좋은 strongest point”
  로 읽는 편이 맞다.

## 관련 문서

- [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.aiworkspace/note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.aiworkspace/note/finance/phases/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md)
