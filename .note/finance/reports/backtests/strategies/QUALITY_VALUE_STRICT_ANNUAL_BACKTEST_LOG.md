# Quality + Value Strict Annual Backtest Log

## 목적

이 문서는 `Quality + Value > Strict Annual` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 blended factor 조합을 어떤 benchmark / overlay와 같이 돌렸고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `Quality + Value > Strict Annual` run만 append 한다
- 기록은 최신 날짜가 위로 오도록 정리한다
- 방어형 blend와 default blend를 구분해서 적는다
- 결과는 최소한 아래를 포함한다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`
- 문서 마지막에는 최근 핵심 run을 한눈에 보는 요약표를 유지한다

## 기록

### 2026-04-17 - strict annual integrated validation rerun

- 목표:
  - `Quality + Value` current strongest point와 lower-MDD alternative를
    공통 strict annual validation frame에서 다시 돌려,
    current representative anchor 유지 여부와 `Top N 9` alternative의 후보성을 재확인
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
    - `por`
    - `per`
  - `Option = month_end`
  - `Rebalance Interval = 1`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Trend Filter = off`
  - `Market Regime = off`
  - underperformance / drawdown guardrail `on`
- 결과:
  - current strongest point:
    - `Top N = 10`
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = normal / normal / normal`
  - lower-MDD alternative:
    - `Top N = 9`
    - `CAGR = 32.21%`
    - `MDD = -25.61%`
    - `Promotion = production_candidate`
    - `Shortlist = watchlist`
    - `Deployment = review_required`
    - `Validation / Rolling / OOS = watch / normal / normal`
- 해석:
  - `Top N = 9`는 `CAGR`와 `MDD`가 모두 좋아 보여도
    `small_capital_trial` gate를 유지하지 못한다
  - 따라서 current representative anchor는 여전히 `Top N = 10` strongest point다
- 다음 액션:
  - representative weighted portfolio replay validation으로 이동한다

### 2026-04-14 - next-ranked eligible fill representative rerun first pass

- 목표:
  - Phase 18 first larger-redesign slice인
    `Fill Rejected Slots With Next Ranked Names`
    contract가 current strongest practical blended point를
    non-hold 또는 stronger rescue로 끌어올릴 수 있는지 확인한다
- 전략:
  - `Quality + Value > Strict Annual`
- 실행 범위:
  - strongest point trend-on structural probe:
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
    - `Trend Filter = on`
    - `Market Regime = off`
    - underperformance / drawdown guardrail `on`
    - `partial_cash_retention_enabled = false`
    - `rejected_slot_fill_enabled = off / on`
- 결과:
  - `fill off`:
    - `CAGR = 30.01%`
    - `MDD = -29.72%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = caution`
    - `Average Cash Share = 11.40%`
  - `fill on`:
    - `CAGR = 26.64%`
    - `MDD = -28.05%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = caution`
    - `Filled Rows = 111`
    - `Filled Tickers = 328`
    - `Average Cash Share = 8.09%`
- 해석:
  - fill contract는 blended strongest point에서도 실제로 작동했고
    cash share와 `MDD`를 줄였다
  - 하지만 이번 first pass에서는
    gate recovery가 충분하지 않아
    current strongest practical point를 대체하는 rescue는 아니었다
- 다음 액션:
  - current strongest practical point는 그대로 유지
  - larger redesign lane을 계속 밀되,
    blended family에서 gate recovery까지 같이 만드는 follow-up이 필요하다

### 2026-04-14 - defensive sleeve risk-off representative rerun first pass

- 목표:
  - Phase 17 second structural lever인 `defensive sleeve risk-off`가
    current strongest practical blended point에서
    same-gate lower-MDD rescue로 이어지는지 확인한다
- 전략:
  - `Quality + Value > Strict Annual`
- 실행 범위:
  - strongest practical point:
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
    - `Market Regime = off`
    - underperformance / drawdown guardrail `on`
    - `risk_off_mode = cash_only / defensive_sleeve_preference`
    - `defensive_tickers = BIL, SHY, LQD`
- 결과:
  - `cash_only`:
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - `defensive sleeve`:
    - `CAGR = 31.79%`
    - `MDD = -27.19%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
    - `Defensive Sleeve Active Rows = 3`
- 해석:
  - `defensive sleeve`는 blended strongest point에서도 gate를 유지했다
  - 하지만 이번 first pass에서는 `MDD`를 더 낮추지 못했고,
    strongest practical point를 갱신하지도 못했다
  - activation row가 적고 전부 `drawdown_guardrail` 기반이라
    current strongest point를 바꿀 정도의 구조 변화는 아니었다
- 다음 액션:
  - current strongest practical point는 그대로 유지
  - 다음 structural lever는 `concentration-aware weighting`으로 넘긴다

### 2026-04-14 - partial cash retention representative rerun first pass

- 목표:
  - Phase 17 first structural lever인 `partial cash retention`이
    current strongest practical blended point에서
    same-gate lower-MDD rescue로 이어지는지 확인한다
- 전략:
  - `Quality + Value > Strict Annual`
- 실행 범위:
  - strongest practical point:
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
    - `Trend Filter = on`
    - `Market Regime = off`
    - `cash retention = off/on`
- 결과:
  - `cash retention off`:
    - `CAGR = 30.01%`
    - `MDD = -29.72%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = caution`
  - `cash retention on`:
    - `CAGR = 20.03%`
    - `MDD = -15.07%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
    - `Validation = caution`
    - `Partial Cash Retention Active Rows = 90`
    - `Average Cash Share = 41.41%`
- 해석:
  - `partial cash retention`은 blended strongest point에서도 실제로 작동했고
    `MDD`를 크게 낮췄다
  - 하지만 `CAGR` 손실이 커서
    current strongest practical point를 대체하진 못했다
  - 즉 이번 first pass에서는
    downside lever로는 유효하지만
    same-gate practical rescue lever는 아니었다
- 다음 액션:
  - current strongest practical point는 그대로 유지
  - 다음 structural lever는
    cash drag를 줄일 수 있는 `defensive sleeve risk-off`를 우선 검토한다

### 2026-04-14 - concentration-aware weighting representative rerun first pass

- 목표:
  - `Quality + Value` current strongest practical point에서
    equal-weight top-N을 mild rank taper로 바꾸면
    same-gate lower-MDD rescue가 가능한지 확인
- 전략:
  - `Quality + Value > Strict Annual`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - current strongest point:
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
    - `Trend Filter = off`
    - `Market Regime = off`
    - practical `Real-Money Contract` 유지
    - underperformance / drawdown guardrail 유지
  - weighting contract:
    - `equal_weight`
    - `rank_tapered`
- 결과:
  - `equal_weight`:
    - `CAGR = 31.82%`
    - `MDD = -26.63%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
  - `rank_tapered`:
    - `CAGR = 32.92%`
    - `MDD = -27.60%`
    - `Promotion = real_money_candidate`
    - `Shortlist = small_capital_trial`
    - `Deployment = review_required`
- 해석:
  - `rank_tapered`는 gate를 유지한 채 strongest blended point에 잘 적용됐다
  - `CAGR`는 더 좋아졌지만
    이번 질문인 downside 개선에는 답을 주지 못했고
    `MDD`는 오히려 더 나빠졌다
  - 즉 strongest current point를 대체하는 lower-MDD rescue는 아니었다
- 다음 액션:
  - Phase 17 first three structural lever 결과를 묶어
    closeout 또는 next structural lever 우선순위를 정리한다
- 관련 문서:
  - [PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)

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
  - [PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md)

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
  - [PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)

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
  - [PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)

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
  - [PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)

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
  - [PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md)

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
  - [PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)

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
  - [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
  - [PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md)

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
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md)
  - [PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)

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
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
  - [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/runs/2026/strategy_search/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)

### 2026-05-01 - 7단계 실습용 Quality + Value 후보 탐색

- 목표:
  - `Quality + Value > Strict Annual`에서
    `CAGR >= 25%`, `MDD >= -20%` 조건을 만족하면서
    Candidate Review / Portfolio Proposal 실습 흐름에 올릴 수 있는 후보를 찾는다
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-01`
  - `US Statement Coverage 100`
  - `Historical Dynamic PIT Universe`
- 핵심 설정:
  - `Option = month_end`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Benchmark Contract = Ticker`
  - `Benchmark Ticker = SPY`
  - `Trend Filter = off`
  - `Market Regime = off`
  - `Weighting = equal_weight`
  - `Rejected Slot Handling = reweight_survivors`
  - `Risk-Off = cash_only`
  - `Minimum Price = 5.0`
  - `Minimum History = 12M`
  - `Min Avg Dollar Volume 20D = 5.0M`
  - `Transaction Cost = 10 bps`
  - underperformance guardrail:
    - `12M / -5%`
  - drawdown guardrail:
    - `12M / -15% strategy threshold / 3% gap threshold`
- factor 구성:
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
- 결과:
  - `CAGR = 29.25%`
  - `MDD = -18.64%`
  - `Sharpe = 1.5222`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
  - `Validation = normal`
  - `Liquidity Clean Coverage = 100%`
- 해석:
  - 기존 strongest CAGR anchor(`31.82% / -26.63%`)보다
    수익률은 낮지만 MDD 목표를 만족하는 실습용 후보다.
  - `review_required`와 `monitoring = breach_watch`가 남아
    자동 실전 승인 후보는 아니지만,
    `hold / blocked`는 아니므로 Candidate Review 이후
    Portfolio Proposal 실습 후보로 사용할 수 있다.
  - Coverage 500에서도 숫자상 exact hit가 있었지만
    full runtime에서 liquidity / validation caution으로 `hold / blocked`가 되어
    실습 후보로는 제외했다.
- 다음 액션:
  - Candidate Review / Current Candidate / Pre-Live 기록까지 저장했다.
  - 저장 ID:
    - `CANDIDATE_REVIEW_NOTES.jsonl`: `candidate_review_note_qv_cov100_top10_spy_mdd20`
    - `CURRENT_CANDIDATE_REGISTRY.jsonl`: `quality_value_current_candidate_cov100_top10_spy_mdd20`
    - `PRE_LIVE_CANDIDATE_REGISTRY.jsonl`: `pre_live_quality_value_current_candidate_cov100_top10_spy_mdd20`
  - Candidate Library 목록에서는 `Quality + Value Coverage 100 Top-10 SPY MDD20 candidate`
    로 확인한다.

## 최근 판단 요약표

| 날짜 | run | 핵심 결과 | 판단 |
| --- | --- | --- | --- |
| 2026-05-01 | 7단계 실습용 Q+V 후보 탐색/저장 | Coverage 100, Top N 10, SPY benchmark, `29.25% / -18.64%`, `real_money_candidate / paper_probation / review_required` | MDD -20% 이내 실습 후보로 Current/Pre-Live 등록 완료, 자동 승인 후보는 아님 |
| 2026-04-17 | Strict annual integrated validation | current strongest `31.82% / -26.63%`, `Top N 9` alternative `32.21% / -25.61%` | current strongest 유지, `Top N 9`는 weaker-gate alternative |
| 2026-04-14 | next-ranked fill | fill on `26.64% / -28.05%`, cash share와 MDD는 줄었지만 gate는 `hold / blocked` | replacement 아님, reference contract로 보류 |
| 2026-04-14 | defensive sleeve risk-off | cash-only `31.82% / -26.63%`, sleeve `31.79% / -27.19%` | sleeve로 교체하지 않음 |
| 2026-04-14 | partial cash retention | cash retention on `20.03% / -15.07%`, drawdown은 개선됐지만 CAGR와 gate가 약함 | downside lever로만 보류 |
| 2026-04-14 | concentration-aware weighting | equal-weight `31.82% / -26.63%`, rank-tapered `32.92% / -27.60%` | CAGR는 좋지만 lower-MDD rescue 아님 |
| 2026-04-13 | strongest point downside follow-up | current strongest `31.82% / -26.63%`, `Top N 9` `32.21% / -25.61%` | lower-MDD weaker-gate alternative로 보류 |
| 2026-04-13 | bounded downside refinement | strongest practical point remains current blend | current strongest 유지 |
| 2026-04-13 | strongest anchor top-n search | `Top N 10` strongest point fixed | current representative anchor로 고정 |
| 2026-04-13 | quality-side / replacement / value-side searches | 여러 factor replacement/addition 후보 검토 | final blend 후보 압축에 사용 |
| 2026-04-10 | current strongest non-hold blend | default blend `28.51% / -28.35%` | 이후 blended search baseline |
