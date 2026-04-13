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
  - [VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md)
  - [PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md)

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
  - [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - [PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md)

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
