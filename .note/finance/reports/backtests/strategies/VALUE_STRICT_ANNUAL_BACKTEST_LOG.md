# Value Strict Annual Backtest Log

## 목적

이 문서는 `Value > Strict Annual` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 어떤 factor / benchmark / overlay / real-money contract 조합을 썼고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `Value > Strict Annual` run만 append 한다
- 기록은 최신 날짜가 위로 오도록 정리한다
- strongest raw winner, balanced near-miss, hold diagnostic run을 구분해서 적는다
- 결과는 최소한 아래를 포함한다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`
- 문서 마지막에는 최근 핵심 run을 한눈에 보는 요약표를 유지한다

## 기록

### 2026-04-16 - phase21 integrated validation first pass (value)

- 목표:
  - `Value > Strict Annual` current anchor와 lower-MDD alternative를
    `Phase 21` 공통 validation frame에서 다시 확인한다
- 전략:
  - `Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 공통 contract:
  - `Option = month_end`
  - `Top N = 14`
  - `Rebalance Interval = 1`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - `Benchmark = SPY`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- factor / ticker:
  - current anchor:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `psr`
  - lower-MDD alternative:
    - current anchor + `pfcr`
- 결과:
  - current anchor:
    - `CAGR = 28.13%`
    - `MDD = -24.55%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Validation = normal`
    - `Rolling Review = watch`
    - `Out-of-Sample Review = caution`
  - lower-MDD alternative:
    - `CAGR = 27.22%`
    - `MDD = -21.16%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
    - `Validation = watch`
    - `Rolling Review = caution`
    - `Out-of-Sample Review = caution`
- 해석:
  - `Value` current anchor는 `Phase 21` frame에서도 그대로 유지된다
  - `+ pfcr`는 여전히 더 낮은 `MDD`를 보여주는 near-miss지만,
    gate는 한 단계 약한 대안으로 남는다
  - 즉 same-gate replacement나 actual rescue까지는 아니다
- 다음 액션:
  - `Quality` rerun pack을 같은 frame에서 진행
  - 이후 `Quality + Value`, portfolio bridge까지 묶어 integrated 판단을 이어간다
- 관련 문서:
  - [PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/candidates/point_in_time/strategy_candidates/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
  - [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)

### 2026-04-14 - next-ranked eligible fill representative rerun first pass

- 목표:
  - Phase 18 first larger-redesign slice인
    `Fill Rejected Slots With Next Ranked Names`
    contract가 `Value` trend-on structural probe를
    meaningful rescue 또는 anchor replacement로 만들 수 있는지 확인한다
- 실행 범위:
  - current structural probe:
    - `Top N = 14 + psr`
    - `Trend Filter = on`
    - `Market Regime = off`
    - underperformance / drawdown guardrail `on`
    - `partial_cash_retention_enabled = false`
    - `risk_off_mode = cash_only`
    - `rejected_slot_fill_enabled = off / on`
- current code rerun 결과:
  - `fill off`:
    - `CAGR = 25.92%`
    - `MDD = -29.25%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = caution`
    - `Average Cash Share = 11.38%`
  - `fill on`:
    - `CAGR = 25.23%`
    - `MDD = -28.37%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = normal`
    - `Filled Rows = 117`
    - `Filled Tickers = 466`
    - `Average Cash Share = 0.00%`
- 해석:
  - 이 redesign은 `Value` trend-on probe에서
    cash drag를 없애고 validation을 개선하는 방향으로는 의미가 있었다
  - 다만 current best practical anchor(`28.13% / -24.55%`)보다
    `MDD`가 더 낮아진 것도 아니고,
    gate recovery까지 만든 것도 아니어서
    anchor replacement로 보지는 않는다
- 다음 액션:
  - current practical anchor는 그대로 유지
  - `next-ranked eligible fill`은
    larger redesign lane에서 더 밀어볼 가치가 있는 reference contract로 남긴다

### 2026-04-14 - value fill anchor-near follow-up second pass

- 목표:
  - `Value` current practical anchor 근처에서
    fill contract가 same-gate lower-MDD rescue를 만들 수 있는지
    좁게 다시 확인한다
- 실행 범위:
  - `base + psr`, `Top N = 12~16`
  - `base + psr + pfcr`, `Top N = 12~16`
  - 공통:
    - `Trend Filter = on`
    - `rejected_slot_fill_enabled = on`
    - `partial_cash_retention_enabled = false`
- current code rerun 결과:
  - best lower-MDD near-miss:
    - `base + psr + pfcr`
    - `Top N = 13`
    - `CAGR = 24.47%`
    - `MDD = -24.89%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
  - current anchor-near candidates 전체가
    still `hold / blocked`였다
- 해석:
  - fill contract를 current anchor 근처에 직접 적용해도
    same-gate lower-MDD rescue는 아직 없었다
  - current practical anchor는 그대로 유지한다
- 다음 액션:
  - Phase 18 second slice 후보 우선순위를 다시 정한다

### 2026-04-14 - defensive sleeve risk-off representative rerun first pass

- 목표:
  - Phase 17 second structural lever인 `defensive sleeve risk-off`가
    current `Value` practical anchor에서
    same-gate lower-MDD rescue로 이어지는지 확인한다
- 실행 범위:
  - current practical anchor:
    - `Top N = 14 + psr`
    - `Market Regime = off`
    - underperformance / drawdown guardrail `on`
    - `risk_off_mode = cash_only / defensive_sleeve_preference`
    - `defensive_tickers = BIL, SHY, LQD`
- current code rerun 결과:
  - `cash_only`:
    - `CAGR = 28.21%`
    - `MDD = -24.55%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - `defensive sleeve`:
    - `CAGR = 28.11%`
    - `MDD = -25.14%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Defensive Sleeve Active Rows = 2`
- 해석:
  - 구현 회귀로 sleeve ETF가 candidate-liquidity 계산에 섞이던 문제를 먼저 고쳤다
  - 회귀 수정 후 representative rerun 기준으로
    `defensive sleeve`는 gate를 깨지 않았지만
    `MDD`를 더 낮추지도 못했다
  - 이번 anchor에서는
    `cash_only`를 대체하는 stronger downside contract가 아니었다
- 다음 액션:
  - `Value` current anchor는 그대로 유지
  - 다음 structural lever는 `concentration-aware weighting` 쪽으로 넘긴다

### 2026-04-14 - partial cash retention representative rerun first pass

- 목표:
  - Phase 17 first structural lever인 `partial cash retention`이
    current `Value` practical anchor에서
    same-gate lower-MDD rescue로 이어지는지 확인한다
- 실행 범위:
  - baseline structural probe:
    - `Top N = 14 + psr`
    - `Trend Filter = on`
    - `Market Regime = off`
    - `cash retention = off/on`
- current code rerun 결과:
  - `cash retention off`:
    - `CAGR = 25.92%`
    - `MDD = -29.25%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = caution`
  - `cash retention on`:
    - `CAGR = 20.11%`
    - `MDD = -15.85%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = watch`
    - `Partial Cash Retention Active Rows = 113`
    - `Average Cash Share = 31.14%`
- 해석:
  - `partial cash retention`은 실제로 작동했고
    `MDD`를 크게 낮췄다
  - 하지만 현금 비중이 많이 남으면서 `CAGR`가 크게 낮아졌고
    `benchmark_policy / liquidity_policy = caution`이 남아
    same-gate rescue로 이어지진 못했다
- 다음 액션:
  - `Value` current anchor는 그대로 유지
  - 다음 structural lever는
    idle cash drag를 줄일 수 있는 `defensive sleeve risk-off` 쪽이 더 유력하다

### 2026-04-14 - concentration-aware weighting representative rerun first pass

- 목표:
  - `Value` current practical anchor에서
    equal-weight top-N을 mild rank taper로 바꾸면
    same-gate lower-MDD rescue가 가능한지 확인
- 전략:
  - `Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - current anchor:
    - `Top N = 14`
    - `psr` added
    - `Benchmark = SPY`
    - `Trend Filter = off`
    - `Market Regime = off`
    - practical `Real-Money Contract` 유지
    - underperformance / drawdown guardrail 유지
  - weighting contract:
    - `equal_weight`
    - `rank_tapered`
- factor / ticker:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `psr`
- 결과:
  - `equal_weight`:
    - `CAGR = 28.13%`
    - `MDD = -24.55%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Rolling Review = watch`
  - `rank_tapered`:
    - `CAGR = 27.71%`
    - `MDD = -25.87%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Rolling Review = caution`
- 해석:
  - `rank_tapered`는 gate를 유지한 채 current anchor에 잘 적용됐다
  - 하지만 이번 representative rerun에서는
    `MDD`를 더 낮추지 못했고
    rolling consistency도 한 단계 약해졌다
  - 즉 `equal_weight` current anchor를 대체하는 lower-MDD rescue는 아니었다
- 다음 액션:
  - Phase 17 first three structural lever 결과를 묶어
    closeout 또는 next structural lever 우선순위를 정리한다
- 관련 문서:
  - [PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md)

### 2026-04-13 - rescue search second pass에서 lower-MDD exact rescue는 없었음

- 목표:
  - current practical anchor인 `Top N = 14 + psr`를 다시 확인하고,
    same gate를 유지하면서 `MDD`를 더 낮출 수 있는 bounded rescue 후보가 있는지 본다
- 실행 범위:
  - baseline reconfirm:
    - `Top N = 14 + psr`
  - rescue probe:
    - `Top N = 14 + psr + pfcr`
    - `Top N = 15 + psr + pfcr`
  - sensitivity:
    - `Candidate Universe Equal-Weight`
    - `Trend Filter`
    - `Market Regime`
  - replacement recap:
    - `sales_yield -> pfcr`
- current code rerun 결과:
  - baseline reconfirm:
    - `Top N = 14 + psr`
    - `CAGR = 28.13%`
    - `MDD = -24.55%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - strongest lower-MDD near-miss:
    - `Top N = 14 + psr + pfcr`
    - `CAGR = 27.22%`
    - `MDD = -21.16%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
  - same-gate but no rescue:
    - `Top N = 15 + psr + pfcr`
    - `CAGR = 25.95%`
    - `MDD = -27.59%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - `Candidate Universe Equal-Weight`, `Trend Filter`, `Market Regime` sensitivity도
    rescue를 만들지 못했다
- 해석:
  - current practical anchor는 current code에서도 그대로 유지된다
  - `+ pfcr`는 눈에 띄게 `MDD`를 낮췄지만 gate가 약해졌다
  - `Top N = 15`는 gate를 회복했지만 downside edge를 잃어서 rescue가 아니다
  - 따라서 이번 second pass에서도 lower-MDD exact rescue는 없었다
- 다음 액션:
  - `Value`는 current best practical point를 유지한 채 closeout
  - deeper downside improvement는 다음 phase의 structural work로 넘긴다

### 2026-04-13 - Phase 16 bounded downside refinement first pass

- 목표:
  - `Value > Strict Annual` current practical anchor(`Top N = 14 + psr`)를 기준으로
    bounded하게 다시 탐색해서 `MDD`를 더 낮추되
    `Promotion = real_money_candidate`, `Shortlist >= paper_probation`, `Deployment != blocked`
    를 유지할 수 있는지 확인한다
- 전략:
  - `Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- bounded lever:
  - `Top N = 12 / 13 / 14 / 15 / 16`
  - one-factor addition:
    - `psr`
    - `per`
    - `pbr`
    - `por`
    - `ev_ebit`
    - `fcf_yield`
  - replacement probe:
    - `replace_sales_with_psr`
    - `replace_ocf_with_psr`
  - overlay sensitivity:
    - `Trend Filter on/off`
    - `Market Regime on/off`
- 결과:
  - best practical point remains `Top N = 14 + psr`
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
  - `Validation = normal`
  - `Rolling Review = watch`
  - `Out-of-Sample Review = caution`
- near alternatives:
  - `replace_sales_with_psr_t14` matched `MDD = -24.55%` but lowered CAGR and weakened rolling quality
  - `per`, `por`, `pbr`, `ev_ebit`, `fcf_yield` were all weaker on either drawdown or gate quality
  - overlay on the anchor degraded gate quality and did not produce a better practical candidate
- 해석:
  - bounded follow-up did not find a better practical candidate than `psr` addition at `Top N = 14`
  - current `Value` best practical anchor remains unchanged
- 다음 액션:
  - if needed, move the same downside refinement pattern to `Quality + Value`
  - otherwise close the phase with `Top N = 14 + psr` as the current best practical point

### 2026-04-13 - factor addition second pass에서 psr candidate를 고정함

- 목표:
  - Phase 15 downside-improvement first pass(`Top N = 14`) 위에
    one-factor addition만 붙여서 더 나은 practical candidate를 찾는다
- 전략:
  - `Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Top N = 14`
  - `Rebalance Interval = 1`
  - `Benchmark = SPY`
  - `Trend Filter = off`
  - `Market Regime = off`
  - practical `Real-Money Contract` 유지
  - underperformance / drawdown guardrail 유지
- factor / ticker:
  - base factors:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
  - additional factor:
    - `psr`
- 결과:
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
  - `Validation = normal`
  - `Validation Policy = normal`
  - `Rolling Review = watch`
  - `Out-of-Sample Review = caution`
- 해석:
  - first-pass `Top N = 14`와 같은 drawdown 수준을 유지하면서
    CAGR를 조금 더 끌어올린 best addition candidate다
  - `psr` addition이 이번 bounded search에서 가장 균형이 좋았다
- 다음 액션:
  - `Quality` / `Quality + Value` family에도 같은 controlled addition search를 적용한다
- 관련 문서:
  - [VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md)
  - [PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md)

### 2026-04-13 - downside-improved current candidate first pass

- 목표:
  - strongest baseline의 `Promotion / Shortlist / Deployment`를 유지하면서
    `MDD`를 낮출 수 있는 practical candidate를 찾는다
- 전략:
  - `Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - strongest baseline과 동일
  - 차이점은 `Top N = 14`
  - `Rebalance Interval = 1`
  - `Benchmark = SPY`
  - `Trend Filter = off`
  - `Market Regime = off`
  - practical `Real-Money Contract` 유지
  - underperformance / drawdown guardrail 유지
- factor / ticker:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- 결과:
  - `CAGR = 27.48%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
  - `Rolling Review = watch`
  - `Out-of-Sample Review = caution`
- 해석:
  - strongest baseline보다 `CAGR`는 `2.41%p` 낮지만
    `MDD`는 `4.60%p` 개선된다
  - `Promotion / Shortlist / Deployment` 상태를 그대로 유지한 채
    downside를 가장 깔끔하게 낮춘 first-pass candidate다
  - 이번 first pass에서는 overlay보다 `Top N diversification`이 더 효과적인 레버였다
- 다음 액션:
  - factor subset / controlled addition으로
    `Top N = 14`보다 더 나은 downside-improved candidate가 가능한지 본다
- 관련 문서:
  - [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - [PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md)

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
  - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md)
  - [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
  - [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)

## 최근 판단 요약표

| 날짜 | run | 핵심 결과 | 판단 |
| --- | --- | --- | --- |
| 2026-04-16 | Phase 21 integrated validation | current anchor `28.13% / -24.55%`, lower-MDD alternative `27.22% / -21.16%` | current anchor 유지, `+ pfcr`는 weaker-gate near-miss |
| 2026-04-14 | next-ranked fill | fill on `25.23% / -28.37%`, validation은 개선됐지만 gate는 `hold / blocked` | replacement 아님, reference contract로 보류 |
| 2026-04-14 | fill anchor-near follow-up | best lower-MDD near-miss `24.47% / -24.89%`, `hold / blocked` | current anchor 유지 |
| 2026-04-14 | defensive sleeve risk-off | cash-only `28.21% / -24.55%`, sleeve `28.11% / -25.14%` | sleeve로 교체하지 않음 |
| 2026-04-14 | partial cash retention | cash retention on `20.11% / -15.85%`, drawdown은 개선됐지만 CAGR와 gate가 약함 | downside lever로만 보류 |
| 2026-04-14 | concentration-aware weighting | equal-weight `28.13% / -24.55%`, rank-tapered `27.71% / -25.87%` | equal-weight current anchor 유지 |
| 2026-04-13 | rescue search second pass | current anchor `28.13% / -24.55%`, best near-miss `27.22% / -21.16%` | lower-MDD exact rescue 없음 |
| 2026-04-13 | bounded downside refinement | best practical point remains `Top N 14 + psr`, `28.13% / -24.55%` | current anchor 유지 |
| 2026-04-13 | factor addition second pass | `psr` addition `28.13% / -24.55%` | current best addition으로 고정 |
| 2026-04-13 | downside-improved first pass | `Top N 14`, `27.48% / -24.55%` | first-pass downside-improved candidate |
| 2026-04-10 | strongest current candidate | `Top N 10`, `29.89% / -29.15%` | 이후 downside 개선 탐색의 baseline |
