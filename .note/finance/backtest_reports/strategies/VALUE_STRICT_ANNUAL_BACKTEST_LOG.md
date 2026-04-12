# Value Strict Annual Backtest Log

## 목적

이 문서는 `Value > Strict Annual` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 어떤 factor / benchmark / overlay / real-money contract 조합을 썼고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `Value > Strict Annual` run만 append 한다
- strongest raw winner, balanced near-miss, hold diagnostic run을 구분해서 적는다
- 결과는 최소한 아래를 포함한다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`

## 기록

### 2026-04-10 - strongest current candidate

- 목표:
  - current runtime practical contract 기준 strongest `Value` candidate 재고정
- 전략:
  - `Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Benchmark = SPY`
  - `Trend Filter = off`
  - `Market Regime = off`
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
  - underperformance guardrail:
    - `on`
    - `Window = 12M`
    - `Worst Excess Threshold = -10%`
  - drawdown guardrail:
    - `on`
    - `Window = 12M`
    - `Strategy DD Threshold = -35%`
    - `Gap Threshold = 8%`
- factor / ticker:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- 결과:
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
- 해석:
  - strict annual 3개 family 중 유일한 current exact candidate다
  - raw return edge가 강하지만 drawdown은 깊다
  - `Deployment = review_required`이므로 바로 live-ready로 읽는 건 아니다
  - 단순히 `guardrail on`만 맞춘다고 재현되는 값은 아니고,
    practical `Real-Money Contract` 전체와 세부 threshold를 같이 맞춰야 한다
- 다음 액션:
  - balanced near-miss와 함께 비교하면서 drawdown / consistency tradeoff를 판단
- 관련 문서:
  - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
  - [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
  - [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
