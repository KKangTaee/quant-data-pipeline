# Quality Strict Annual Rescued Current Candidate

## 한 줄 설명

`Quality > Strict Annual` family에서 current practical contract 기준으로
가장 잘 살아난 구조 조합은
`capital_discipline + LQD benchmark + trend on + regime off + Top N 10`
입니다.

## 전략 구성

- 전략:
  - `Quality > Strict Annual`
- 기간:
  - `2016-01-01 ~ 2026-04-01`
- preset / universe:
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- option:
  - `month_end`
- `Top N`:
  - `10`
- `Rebalance Interval`:
  - `1`

## factor

- `roe`
- `roa`
- `cash_ratio`
- `debt_to_assets`

이 조합은 실무적으로
`capital_discipline` anchor로 읽는 편이 가장 자연스럽다.

## overlay / benchmark

- `Benchmark Contract = Ticker Benchmark`
- `Benchmark Ticker = LQD`
- `Trend Filter = on`
- `Trend Filter Window = 200`
- `Market Regime = off`

## Real-Money Contract

- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- `Min Benchmark Coverage = 95%`
- `Min Net CAGR Spread = -2%`
- `Min Liquidity Clean Coverage = 90%`
- `Max Underperformance Share = 55%`
- `Min Worst Rolling Excess = -15%`
- `Max Strategy Drawdown = -35%`
- `Max Drawdown Gap vs Benchmark = 8%`
- underperformance / drawdown guardrail `on`

## current result

- `CAGR = 24.28%`
- `MDD = -31.48%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation = normal`
- `Rolling Review = normal`
- `Out-of-Sample Review = normal`

## 왜 의미가 있나

- `Quality` family는 한동안 current literal preset semantics 기준으로
  다시 `hold`에 머무는 것처럼 보였는데,
  이 조합은 그 상태를 실제로 되돌린다.
- 즉 `Quality`도 current practical contract에서
  구조를 잘 고르면 다시 `real_money_candidate`까지 올라갈 수 있다는 뜻이다.
- 다만 `MDD`는 여전히 깊기 때문에,
  다음 단계는 이 rescued anchor를 기준으로
  downside 개선을 더 시도하는 쪽이 맞다.

## 관련 문서

- [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md)
- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md)
