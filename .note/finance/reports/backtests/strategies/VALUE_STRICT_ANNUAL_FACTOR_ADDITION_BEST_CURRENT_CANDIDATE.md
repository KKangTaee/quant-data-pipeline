# Value Strict Annual Factor Addition Best Current Candidate

## 목적

이 문서는 Phase 15 second pass에서
baseline 5-factor에 one-factor addition을 더했을 때
가장 균형이 좋았던 current candidate를 정리한다.

## 전략 한 줄 설명

`Top N = 14` downside-improved anchor에 `psr`를 추가한
가장 균형 잡힌 `Value > Strict Annual` candidate다.

쉽게 말하면:

- first-pass의 낮은 drawdown을 유지하고
- raw return을 조금 더 끌어올린
- current best practical value candidate다.

## 전략 구성

### 1. 전략 family / variant

- family: `Value`
- variant: `Strict Annual`

### 2. Universe / 기간

- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- `Start Date`: `2016-01-01`
- `End Date`: `2026-04-01`
- `Timeframe`: `1d`
- `Option`: `month_end`

### 3. 포트폴리오 구성

- `Top N`: `14`
- `Rebalance Interval`: `1`

### 4. Factor set

baseline 5-factor:

- `book_to_market`
- `earnings_yield`
- `sales_yield`
- `ocf_yield`
- `operating_income_yield`

additional factor:

- `psr`

## 실전형 입력값

- `Minimum Price`: `5.0`
- `Minimum History`: `12M`
- `Min Avg Dollar Volume 20D`: `5.0M`
- `Transaction Cost`: `10 bps`
- `Benchmark Contract`: `Ticker Benchmark`
- `Benchmark Ticker`: `SPY`
- `Min Benchmark Coverage`: `95%`
- `Min Net CAGR Spread`: `-2%`
- `Min Liquidity Clean Coverage`: `90%`
- `Max Underperformance Share`: `55%`
- `Min Worst Rolling Excess`: `-15%`
- `Max Strategy Drawdown`: `-35%`
- `Max Drawdown Gap vs Benchmark`: `8%`

## Benchmark / Overlay / Guardrail

- `Benchmark Contract`: `Ticker Benchmark`
- `Benchmark Ticker`: `SPY`
- `Trend Filter`: `off`
- `Market Regime`: `off`
- `Underperformance Guardrail`: `on`
- `Drawdown Guardrail`: `on`

guardrail 세부값:

- `Underperformance Guardrail Window`: `12M`
- `Underperformance Worst Excess Threshold`: `-10%`
- `Drawdown Guardrail Window`: `12M`
- `Drawdown Guardrail Strategy DD Threshold`: `-35%`
- `Drawdown Guardrail Gap Threshold`: `8%`

## 기대 결과

- `CAGR = 28.13%`
- `MDD = -24.55%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation = normal`
- `Validation Policy = normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = caution`

## 왜 이 후보가 좋은가

- `Top N = 14` first-pass candidate의 downside를 유지한다.
- 그 위에 `psr`를 추가했을 때 raw edge가 약간 더 좋아진다.
- 하지만 gate 상태는 그대로 유지된다.

즉:

- better return
- same practical gate state
- same drawdown regime

의 조합이다.

## 다른 addition 대비 차이

- `pcr`, `liquidation_value`는 hold / blocked로 돌아가거나 robustness가 약했다.
- `fcf_yield`는 `watchlist`로 내려갔다.
- `ev_ebit`, `por`, `per`, `pbr`는 non-hold이지만 `psr`보다 균형이 약했다.

따라서:

- current best addition = `psr`

## 같이 보면 좋은 문서

- [PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md)
- [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
- [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
