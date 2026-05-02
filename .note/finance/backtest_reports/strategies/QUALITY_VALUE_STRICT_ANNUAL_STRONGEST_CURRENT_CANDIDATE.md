# Quality + Value Strict Annual Strongest Current Candidate

## 한 줄 설명

현재 `Quality + Value > Strict Annual` family에서 가장 강한 practical candidate는

- quality-side:
  - `net_margin -> operating_margin`
- value-side:
  - `ocf_yield -> pcr`
  - `operating_income_yield -> por`
- `Top N = 10`
- `Candidate Universe Equal-Weight`

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
  - `por`
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

- `CAGR = 31.82%`
- `MDD = -26.63%`
- `Promotion = real_money_candidate`
- `Shortlist = small_capital_trial`
- `Deployment = review_required`
- `Validation / Rolling / OOS = normal / normal / normal`

## 왜 strongest current candidate로 보나

- previous practical anchor 대비
  - `CAGR = 30.05% -> 31.82%`
  - `MDD = -27.43% -> -26.63%`
- Phase 15 strongest point 대비
  - `CAGR = 31.25% -> 31.82%`
  - `MDD = -26.63% -> -26.63%`
- 즉:
  - gate tier는 그대로 유지하고
  - drawdown regime도 그대로 유지하면서
  - return만 한 단계 더 끌어올렸다

같은 bounded search에서 나온 더 방어적인 대안

- `Top N = 9`
- `current_ratio -> cash_ratio`

는 `MDD`를 더 낮췄지만
`production_candidate / watchlist`로 내려가 strongest point를 대체하진 못했다.

## 해석

이 후보는

- `Value` 단독 strongest candidate만큼 공격적인 raw winner는 아니지만
- blended family 중에서는 가장 좋은 practical tradeoff에 가깝다
- current runtime 기준으로도
  `small_capital_trial`까지 올라가는 strongest blended candidate다
- Phase 16 first pass까지 반영하면
  “더 낮은 `MDD`를 만들진 못했지만,
  같은 gate에서 더 높은 `CAGR`를 만든 strongest blended candidate”
  로 읽는 편이 가장 정확하다

## 관련 문서

- [PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md)
- [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)
- [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
- [PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md)
- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
