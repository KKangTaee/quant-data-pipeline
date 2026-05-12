# Value Strict Annual Downside-Improved Current Candidate

## 목적

이 문서는 `Value > Strict Annual` strongest baseline에서
`MDD`를 낮추는 방향으로 조정했을 때,
현재 가장 균형이 좋다고 보는 downside-improved candidate를
전략 구성 중심으로 바로 읽기 쉽게 정리한 문서다.

## 전략 한 줄 설명

strongest `Value` baseline과 같은 factor / universe / practical contract를 유지하되,
집중도를 `Top N = 10 -> 14`로 넓혀
drawdown을 줄인 stricter-diversified value 후보다.

쉽게 말하면:

- 기본 `Value` factor edge는 유지하고
- 너무 공격적인 집중도를 조금 완화해서
- `MDD`를 낮춘 current balanced candidate다.

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

즉:

- strongest baseline과 같은 cadence를 유지하되
- 포트폴리오 집중도를 조금 완화했다.

### 4. Value factor 선택

- `book_to_market`
- `earnings_yield`
- `sales_yield`
- `ocf_yield`
- `operating_income_yield`

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

## strongest baseline 대비 무엇이 달라졌는가

유일한 핵심 차이는 이거다.

- strongest baseline:
  - `Top N = 10`
- downside-improved candidate:
  - `Top N = 14`

즉:

- factor를 바꾸지 않았고
- overlay를 켜지 않았고
- cadence도 바꾸지 않았다.

이번 first pass에서는
`Top N diversification`만으로도
candidate quality를 더 좋게 만들 수 있는지 보는 데 집중했다.

## 기대 결과

- `CAGR = 27.48%`
- `MDD = -24.55%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation = normal`
- `Validation Policy = normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = caution`

## strongest baseline과 비교하면

- strongest baseline:
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
- downside-improved candidate:
  - `CAGR = 27.48%`
  - `MDD = -24.55%`

해석:

- `CAGR`는 `2.41%p` 내려간다
- `MDD`는 `4.60%p` 개선된다
- `Promotion / Shortlist / Deployment`는 그대로 유지된다

즉:

- strongest baseline보다 덜 공격적이고
- still non-hold practical candidate 상태는 유지하는 쪽이다.

## 왜 이 후보를 추천하는가

- `Top N = 15`도 비슷한 수준까지 `MDD`를 줄일 수 있었다
- 하지만 그 경우 `Rolling Review = caution`으로 내려갔다

반대로 `Top N = 14`는:

- `MDD`를 충분히 낮추고
- `Rolling Review = watch`를 유지해서
- current first pass 기준 가장 균형이 좋다

## 어떤 상황에서 먼저 보면 좋은가

- strongest `Value` 후보가 너무 공격적으로 느껴질 때
- `real_money_candidate / paper_probation`을 유지하면서
  drawdown을 조금 더 줄인 practical candidate가 필요할 때

## 같이 보면 좋은 문서

- [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
- [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- [PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
