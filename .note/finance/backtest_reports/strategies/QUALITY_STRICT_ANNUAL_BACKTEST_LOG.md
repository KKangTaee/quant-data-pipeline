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

### 2026-04-16 - phase21 integrated validation first pass

- 목표:
  - `Quality` current anchor와 cleaner alternative를
    `Phase 21` 공통 validation frame에서 다시 돌려,
    current practical point 유지 여부와 comparison alternative의 현재 위치를 재확인
- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - factor:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - `Option = month_end`
  - `Top N = 12`
  - `Rebalance Interval = 1`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- 결과:
  - current anchor:
    - `Benchmark = LQD`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = normal / watch / normal`
  - cleaner alternative:
    - `Benchmark = SPY`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 25.18%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = paper_only`
    - `Validation / Rolling / OOS = normal / normal / normal`
- 해석:
  - current anchor는 `Phase 21` validation frame에서도 그대로 practical reference point로 유지된다
  - `SPY` cleaner alternative는 여전히 comparison surface로는 의미가 있지만,
    `paper_only`라서 replacement candidate는 아니다
- 다음 액션:
  - `Quality + Value` rerun pack을 같은 frame에서 실행
  - portfolio bridge validation까지 이어서 integrated comparison을 완성
- 관련 문서:
  - [PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
  - [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)

### 2026-04-13 - rescued anchor alternate contract search third pass

- 목표:
  - current downside-improved rescued anchor를 유지한 채
    `benchmark / overlay` 계약을 조금 바꿔
    더 깨끗한 validation surface나 더 실전적인 deployment 해석이 가능한지 확인
- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - factor:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - `Option = month_end`
  - `Top N = 12`
  - `Rebalance Interval = 1`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- 결과:
  - strongest practical point:
    - `Benchmark = LQD`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = normal / watch / normal`
  - cleaner alternative:
    - `Benchmark = SPY`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `CAGR = 25.18%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = paper_only`
    - `Validation / Rolling / OOS = normal / normal / normal`
  - rejected defensive variant:
    - `Benchmark = LQD`
    - `Trend Filter = off`
    - `Market Regime = off`
    - `CAGR = 17.30%`
    - `MDD = -35.84%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
- 해석:
  - current strongest practical point는 여전히 `LQD + trend on + regime off` baseline이다
  - `SPY`는 cleaner surface를 주지만 deployment는 더 보수적으로 내려간다
  - 더 방어적인 overlay는 이번 anchor에서 오히려 `hold`로 후퇴했다
- 다음 액션:
  - `Quality`는 current baseline을 유지하고
    Phase 15 리소스는 `Quality + Value` new anchor follow-up에 더 싣는다
- 관련 문서:
  - [PHASE15_QUALITY_ALTERNATE_CONTRACT_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_ALTERNATE_CONTRACT_SEARCH_THIRD_PASS.md)
  - [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)

### 2026-04-13 - rescued anchor factor search second pass

- 목표:
  - downside-improved rescued anchor 위에 factor addition / replacement를 다시 붙였을 때
    baseline보다 더 좋은 practical candidate가 나오는지 확인
- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Top N = 12`
  - `Rebalance Interval = 1`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- factor / ticker:
  - baseline:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - best addition:
    - `+ net_debt_to_equity`
  - best replacement near-miss:
    - `debt_to_assets -> net_debt_to_equity`
- 결과:
  - baseline:
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - best addition:
    - `+ net_debt_to_equity`
    - `CAGR = 20.25%`
    - `MDD = -30.32%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `OOS = caution`
  - best replacement near-miss:
    - `debt_to_assets -> net_debt_to_equity`
    - `CAGR = 16.86%`
    - `MDD = -29.49%`
    - `Promotion = hold`
- 해석:
  - 이번 pass에서는 baseline을 넘는 bounded factor change가 없었다
  - `+ net_debt_to_equity`만 non-hold를 유지했지만,
    수익률과 낙폭이 모두 baseline보다 나빠졌다
  - 따라서 current best practical point는 여전히 rescued-anchor baseline이다
- 다음 액션:
  - factor 변화보다
    weighting / structural overlay / alternate contract
    쪽으로 다음 레버를 옮긴다
- 관련 문서:
  - [PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md)
  - [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)

### 2026-04-13 - rescued anchor downside search first pass

- 목표:
  - rescued current candidate를 anchor로 두고
    `Top N / Rebalance Interval`만 바꿔도 더 좋은 downside / gate tradeoff가 나오는지 확인
- 전략:
  - `Quality > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Rebalance Interval = 1`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- factor / ticker:
  - rescued anchor:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
- 결과:
  - rescued anchor baseline:
    - `Top N = 10`
    - `CAGR = 24.28%`
    - `MDD = -31.48%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - recommended downside-improved candidate:
    - `Top N = 12`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Rolling = watch`
  - conservative clean alternative:
    - `Top N = 16`
    - `CAGR = 20.23%`
    - `MDD = -25.73%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = normal / normal / normal`
- 해석:
  - rescued anchor에서는 cadence보다 `Top N diversification`이 더 유효한 downside lever였다
  - `Top N = 12`는 수익률과 낙폭을 동시에 개선한 strongest downside-improved candidate다
  - `Top N = 16`은 수익률을 조금 더 포기하는 대신 consistency surface가 더 깨끗한 conservative alternative다
- 다음 액션:
  - rescued contract 기준
    `bounded factor addition / replacement`
    를 다시 붙여도 `real_money_candidate`를 유지하는지 확인
- 관련 문서:
  - [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - [PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md)

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
