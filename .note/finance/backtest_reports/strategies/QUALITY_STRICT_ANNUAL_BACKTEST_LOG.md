# Quality Strict Annual Backtest Log

## 목적

이 문서는 `Quality > Strict Annual` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 어떤 factor / benchmark / overlay 조합을 썼고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `Quality > Strict Annual` run만 append 한다
- 목표, factor, benchmark, overlay를 같이 남긴다
- 결과는 최소한 아래를 포함한다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`

## 기록

### 2026-04-10 - current best non-hold candidate

- 목표:
  - Phase 14 이후 current runtime에서 `Quality` family가 `hold`를 벗어날 수 있는 strongest current candidate 재확인
- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = on`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- factor / ticker:
  - `roe`
  - `roa`
  - `cash_ratio`
  - `debt_to_assets`
- 결과:
  - `CAGR = 14.84%`
  - `MDD = -27.97%`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = review_required`
- 해석:
  - bounded practical search 안에서 `hold`를 벗어난 current candidate다
  - 다만 아직 `real_money_candidate / paper_probation`까지는 못 올라간다
  - 핵심 병목은 `validation = watch`로 읽힌다
- 다음 액션:
  - validation consistency를 더 깨끗하게 만드는 factor / benchmark 조합을 우선 탐색
- 관련 문서:
  - [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
  - [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
