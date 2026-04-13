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

### 2026-04-13 - structural rescue second pass

- 목표:
  - bounded single-factor addition 이후
    `Quality` family가 실제로 어느 구조 조합에서 다시 practical candidate로 살아나는지 current code 기준으로 확인
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
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- factor / ticker:
  - anchor:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - comparison variant:
    - `+ net_debt_to_equity`
- 결과:
  - rescued current candidate:
    - `Benchmark = LQD`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 24.28%`
    - `MDD = -31.48%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - prior reference:
    - `Benchmark = LQD`
    - `Trend Filter = on`
    - `Market Regime = on`
    - `CAGR = 14.84%`
    - `MDD = -27.97%`
    - `Promotion = production_candidate`
  - notable near-miss:
    - `+ net_debt_to_equity`
    - `Benchmark = LQD`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 20.48%`
    - `MDD = -23.52%`
    - `Promotion = hold`
- 해석:
  - `Quality`는 current practical contract 기준으로도
    구조 조합을 조정하면 `real_money_candidate / paper_probation`까지 회복될 수 있다
  - 이번 pass에서 가장 좋은 structural lever는
    `Market Regime off`였다
  - `+ net_debt_to_equity`는 drawdown은 낮췄지만 validation이 다시 깨져 `hold`로 돌아갔다
- 다음 액션:
  - rescued anchor 기준으로
    `top_n / downside / bounded factor addition`
    을 더 본다
- 관련 문서:
  - [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
  - [PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md)

### 2026-04-13 - post-PIT semantics 기준 controlled addition review

- 목표:
  - strict annual dynamic PIT preset semantics fix 이후
    `Quality` family가 current literal preset semantics에서도 non-hold candidate를 만들 수 있는지 재점검
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
  - anchor:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - additions:
    - `interest_coverage`
    - `ocf_margin`
    - `fcf_margin`
    - `net_debt_to_equity`
- 결과:
  - baseline:
    - `CAGR = 13.26%`
    - `MDD = -32.59%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
  - best near-miss:
    - `+ net_debt_to_equity`
    - `CAGR = 13.51%`
    - `MDD = -23.84%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
- 해석:
  - current literal preset semantics 기준으로는
    single-factor addition만으로 non-hold candidate를 회복하지 못했다
  - `net_debt_to_equity`가 drawdown은 가장 잘 낮췄지만
    `validation = caution`이 남아 `hold`를 못 벗어났다
- 다음 액션:
  - factor one-addition보다
    `benchmark / overlay / top_n / factor replacement` 구조 탐색이 더 우선이다
- 관련 문서:
  - [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
  - [PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)

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
