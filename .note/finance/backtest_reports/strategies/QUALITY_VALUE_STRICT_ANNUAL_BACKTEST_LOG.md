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

### 2026-04-13 - Phase 16 strongest point downside follow-up second pass

- 목표:
  - current strongest practical point를 current code 기준으로 다시 확인하고,
    same gate를 유지하면서 더 낮은 `MDD` candidate가 있는지 본다
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - strongest point:
    - quality:
      - `roe`
      - `roa`
      - `operating_margin`
      - `asset_turnover`
      - `current_ratio`
    - value:
      - `book_to_market`
      - `earnings_yield`
      - `sales_yield`
      - `pcr`
      - `por`
      - `per`
    - `Top N = 10`
    - `Benchmark Contract = Candidate Universe Equal-Weight`
  - follow-up:
    - `Top N = 9`
    - `current_ratio -> cash_ratio`
    - `Trend Filter = on`
    - `Ticker Benchmark = SPY`
- 결과:
  - strongest point reconfirmed:
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - lower-MDD but weaker gate:
    - `Top N = 9`
    - `CAGR = 32.21%`
    - `MDD = -25.61%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
  - another lower-MDD but weaker gate:
    - `Top N = 10`
    - `current_ratio -> cash_ratio`
    - `CAGR = 31.83%`
    - `MDD = -25.79%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
  - human-readable benchmark alternative:
    - `Ticker Benchmark = SPY`
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
- 해석:
  - strongest practical point는 current code에서도 그대로 유지된다
  - lower-MDD exact hit는 없었고,
    더 방어적인 대안은 모두 gate를 조금 양보해야 했다
- 다음 액션:
  - `Quality + Value` strongest point는 current anchor로 유지
  - deeper downside improvement는 다음 phase의 structural work로 넘긴다

### 2026-04-13 - Phase 16 bounded downside refinement first pass

- 목표:
  - current strongest practical point를 기준으로
    `MDD`를 더 낮추되
    `real_money_candidate / small_capital_trial / review_required`
    를 유지할 수 있는지 확인한다
  - same gate / same `MDD`에서 `CAGR`를 더 높일 수 있는지도 같이 본다
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - quality anchor:
    - `roe`
    - `roa`
    - `operating_margin`
    - `asset_turnover`
    - `current_ratio`
  - value anchor:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `pcr`
    - `operating_income_yield`
    - `per`
  - `Top N = 10`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- 결과:
  - new strongest practical point:
    - `operating_income_yield -> por`
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - previous anchor:
    - `CAGR = 31.25%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - lower-MDD but weaker gate:
    - `Top N = 9`
    - `CAGR = 31.08%`
    - `MDD = -25.61%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
  - another lower-MDD but weaker-gate alternative:
    - `current_ratio -> cash_ratio`
    - `CAGR = 30.96%`
    - `MDD = -25.79%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
- 해석:
  - 이번 bounded search에서는 same gate를 유지하면서 `MDD`를 더 낮춘 후보는 나오지 않았다
  - 대신 same gate / same `MDD`를 유지하면서 `CAGR`를 더 높인 strongest point가 나왔다
  - 따라서 current strongest practical point는
    `operating_income_yield -> por` 조합으로 갱신된다
- 다음 액션:
  - lower-MDD weaker-gate candidate를 rescue할지
  - 아니면 current strongest point 기준으로 closeout 준비로 갈지
  판단한다
- 관련 문서:
  - [PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)

### 2026-04-13 - strongest anchor top-n search sixth pass

- 목표:
  - new strongest practical point를 anchor로 두고
    `Top N`만 다시 흔들어도 더 좋은 practical candidate가 나오는지 확인
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - quality:
    - `roe`
    - `roa`
    - `operating_margin`
    - `asset_turnover`
    - `current_ratio`
  - value:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `pcr`
    - `operating_income_yield`
    - `per`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- 결과:
  - strongest practical point 유지:
    - `Top N = 10`
    - `CAGR = 31.25%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - lower-drawdown but weaker gate:
    - `Top N = 9`
    - `CAGR = 31.08%`
    - `MDD = -25.61%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
  - high-CAGR but weaker gate:
    - `Top N = 8`
    - `CAGR = 32.47%`
    - `MDD = -30.79%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
  - collapse point:
    - `Top N = 12`
    - `CAGR = 27.17%`
    - `MDD = -27.40%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
- 해석:
  - new strongest anchor 위에서도 `Top N = 10`이 gate와 성과를 같이 만족하는 가장 좋은 practical point였다
  - `Top N = 9`는 숫자상 attractive하지만 gate가 `watchlist`로 낮아졌다
- 다음 액션:
  - current strongest point를 유지하고 Phase 15 closeout 준비로 넘긴다
- 관련 문서:
  - [PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)

### 2026-04-13 - quality-side search fifth pass

- 목표:
  - `ocf_yield -> pcr` replacement current strongest practical point를 anchor로 두고,
    quality factor 쪽 one-more bounded replacement가 실제로 더 좋은 practical candidate를 만드는지 확인
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - anchor value:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `pcr`
    - `operating_income_yield`
    - `per`
  - anchor quality:
    - `roe`
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - `Option = month_end`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- 결과:
  - previous anchor:
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - strongest replacement:
    - `net_margin -> operating_margin`
    - `CAGR = 31.25%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - notable defensive but weaker-gate alternative:
    - `current_ratio -> operating_margin`
    - `CAGR = 30.84%`
    - `MDD = -24.09%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
- 해석:
  - `net_margin -> operating_margin`은
    same gate를 유지하면서 `CAGR`와 `MDD`를 같이 개선한 bounded replacement였다
  - 따라서 current strongest practical point는
    이제 quality-side에서도 replacement가 들어간 조합으로 읽는 편이 맞다
- 다음 액션:
  - new strongest practical point를 hub와 one-pager에 반영하고,
    필요하면 다음에는 new anchor 기준 `Top N`만 다시 좁게 본다
- 관련 문서:
  - [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)

### 2026-04-13 - replacement-anchor follow-up fourth pass

- 목표:
  - `ocf_yield -> pcr` replacement current strongest practical point를 anchor로 두고
    `Top N / benchmark`를 다시 흔들어도 더 좋은 practical candidate가 나오는지 확인
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
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
    - `pcr`
    - `operating_income_yield`
    - `per`
  - `Option = month_end`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- 결과:
  - strongest practical point 유지:
    - `Top N = 10`
    - `Benchmark Contract = Candidate Universe Equal-Weight`
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - high-CAGR but weaker gate:
    - `Top N = 8`
    - `CAGR = 31.69%`
    - `MDD = -27.64%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
  - benchmark alternative:
    - `Top N = 10`
    - `Ticker Benchmark = SPY`
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - downside search takeaway:
    - `Top N >= 12` variants were all `hold / blocked`
- 해석:
  - new replacement anchor 위에서도 `Top N = 10 + Candidate Universe Equal-Weight`가 strongest practical point로 유지됐다
  - `Top N = 8`은 수익률은 더 높지만 gate tier가 낮아졌다
  - `SPY` benchmark는 same return / same drawdown이지만 shortlist를 한 단계 낮췄다
- 다음 액션:
  - current strongest practical point를 유지하고,
    필요하면 다음에는 one-more bounded replacement만 좁게 시도한다
- 관련 문서:
  - [PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)

### 2026-04-13 - value-side search third pass

- 목표:
  - `+ per` baseline candidate에서
    value factor를 제거하거나 교체했을 때 더 좋은 practical candidate가 나오는지 확인
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
  - quality baseline:
    - `roe`
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - value baseline:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `per`
  - best replacement:
    - `ocf_yield -> pcr`
- 결과:
  - baseline:
    - `CAGR = 29.43%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - strongest replacement:
    - `ocf_yield -> pcr`
    - `CAGR = 30.05%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - notable removals:
    - `remove book_to_market`
      - `CAGR = 29.18%`
      - `MDD = -27.25%`
      - `Promotion = production_candidate`
      - `Shortlist = watchlist`
    - `remove earnings_yield`
      - `CAGR = 28.57%`
      - `MDD = -27.77%`
      - `Promotion = production_candidate`
      - `Shortlist = watchlist`
- 해석:
  - value-side removal은 gate tier를 낮추는 방향으로 작동했다
  - 반대로 `ocf_yield -> pcr`는
    same gate / same MDD를 유지하면서 `CAGR`만 소폭 올렸다
  - 따라서 current strongest practical blended candidate는
    이제 `ocf_yield -> pcr` replacement로 읽는 편이 맞다
- 다음 액션:
  - new replacement anchor 기준
    `downside / benchmark / one-more replacement`
    중 무엇을 먼저 볼지 결정
- 관련 문서:
  - [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)

### 2026-04-13 - per anchor benchmark and pruning search second pass

- 목표:
  - `Quality + Value + per` strongest practical candidate anchor에서
    benchmark를 바꾸거나 quality-side pruning을 하면 더 나은 practical tradeoff가 생기는지 확인
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
  - `Trend Filter = off`
  - `Market Regime = off`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance / drawdown guardrail `on`
- factor / ticker:
  - value anchor:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
    - `per`
  - quality baseline:
    - `roe`
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - pruning variants:
    - remove `current_ratio`
    - remove `asset_turnover`
    - remove `net_margin`
- 결과:
  - current strongest practical baseline:
    - `Benchmark Contract = Candidate Universe Equal-Weight`
    - `CAGR = 29.43%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - ticker benchmark alternative:
    - `Benchmark Contract = Ticker Benchmark`
    - `Benchmark Ticker = SPY`
    - `CAGR = 29.43%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - pruning variants:
    - all fell back to `hold / blocked`
- 해석:
  - `Candidate Universe Equal-Weight` baseline이 여전히 strongest practical point였다
  - `Ticker Benchmark = SPY`는 same strategy performance라도 shortlist tier가 한 단계 낮았다
  - quality-side pruning은 이번 pass에서 useful upside/downside lever가 아니었다
- 다음 액션:
  - `quality pruning`보다
    `value-side replacement / bounded removal`
    쪽으로 다음 레버를 옮긴다
- 관련 문서:
  - [PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)

### 2026-04-13 - per strongest blended candidate downside search

- 목표:
  - `per` addition current strongest blended candidate를 anchor로 두고
    `Top N`만 바꿔도 더 좋은 downside / gate tradeoff가 생기는지 확인
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
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
    - `per`
- 결과:
  - baseline anchor:
    - `Top N = 10`
    - `CAGR = 29.43%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - notable alternatives:
    - `Top N = 8`
      - `CAGR = 31.69%`
      - `MDD = -27.64%`
      - `Promotion = production_candidate`
    - `Top N = 18`
      - `CAGR = 24.46%`
      - `MDD = -24.73%`
      - `Promotion = hold`
- 해석:
  - `Top N = 10`이 이번 pass에서도 가장 좋은 practical point였다
  - 더 좁히면 수익률은 높아도 gate가 낮아졌고
  - 더 넓히면 `MDD`는 낮아져도 validation이 `caution`이 되어 `hold`로 떨어졌다
- 다음 액션:
  - `Top N`보다
    `factor replacement / quality-side pruning / benchmark sensitivity`
    쪽이 다음 레버다
- 관련 문서:
  - [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
  - [PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md)

### 2026-04-13 - bounded addition review with current strongest blend anchor

- 목표:
  - current strongest non-hold blend anchor 위에 one-factor addition을 붙였을 때
    gate를 더 올리거나 더 나은 practical tradeoff를 만들 수 있는지 확인
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
  - anchor quality:
    - `roe`
    - `roa`
    - `net_margin`
    - `asset_turnover`
    - `current_ratio`
  - anchor value:
    - `book_to_market`
    - `earnings_yield`
    - `sales_yield`
    - `ocf_yield`
    - `operating_income_yield`
  - additions:
    - `interest_coverage`
    - `ocf_margin`
    - `fcf_margin`
    - `net_debt_to_equity`
    - `dividend_payout`
    - `gpa`
    - `per`
    - `pcr`
    - `por`
    - `liquidation_value`
- 결과:
  - baseline:
    - `CAGR = 28.51%`
    - `MDD = -28.35%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
  - best practical addition:
    - `+ per`
    - `CAGR = 29.43%`
    - `MDD = -27.43%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
- 해석:
  - `per`는 baseline 대비
    `CAGR`, `MDD`, `gate tier`를 모두 개선했다
  - 따라서 current strongest practical blended candidate로 볼 수 있다
  - `liquidation_value`는 숫자는 강했지만 `hold / blocked`로 후퇴했다
- 다음 액션:
  - `per` candidate anchor 기준
    `top_n / downside / replacement` search로 이어간다
- 관련 문서:
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
  - [PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)

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
