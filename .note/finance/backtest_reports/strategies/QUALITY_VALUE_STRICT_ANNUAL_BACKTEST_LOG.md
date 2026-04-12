# Quality + Value Strict Annual Backtest Log

## 목적

이 문서는 `Quality + Value > Strict Annual` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 blended factor 조합을 어떤 benchmark / overlay와 같이 돌렸고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `Quality + Value > Strict Annual` run만 append 한다
- 방어형 blend와 default blend를 구분해서 적는다
- 결과는 최소한 아래를 포함한다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`

## 기록

### 2026-04-10 - current strongest non-hold blend

- 목표:
  - Phase 14 이후 current runtime에서 strongest non-hold blended candidate 재확인
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
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
  - underperformance / drawdown guardrail `on`
- factor / ticker:
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
    - `ocf_yield`
    - `operating_income_yield`
- 결과:
  - `CAGR = 28.51%`
  - `MDD = -28.35%`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = review_required`
- 해석:
  - default blend + candidate equal-weight benchmark가 현재 strongest non-hold blend다
  - `hold`는 벗어났지만 아직 `paper_probation`까지는 못 갔다
- 다음 액션:
  - validation consistency를 개선할 수 있는 blend와 benchmark 조합을 더 본다
- 관련 문서:
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
  - [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
