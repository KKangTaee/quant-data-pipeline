# GTAA Backtest Log

## 목적

이 문서는 `GTAA` 관련 백테스트를 전략 기준으로 누적 관리하는 로그다.

앞으로 `GTAA`를 어떤 universe / score horizon / top / interval / benchmark 조합으로 돌렸고,
그 결과가 어땠는지를 이 문서에 계속 append 한다.

## 작성 규칙

- 의미 있는 `GTAA` run만 append 한다
- 실험 목적과 핵심 입력값을 같이 남긴다
- 결과는 최소한 아래를 남긴다
  - `CAGR`
  - `MDD`
  - `Promotion`
  - `Shortlist`
  - `Deployment`
- `SPY` 비교가 핵심이면 그 비교 결과도 같이 적는다

## 기록

### 2026-04-20 - expanded universe follow-up search

- 목표:
  - 기존 `SPY / QQQ / GLD / IEF` compact 후보가 ticker 수가 부족하다는 사용자 피드백을 반영해,
    `GTAA` 안에서 더 넓은 ETF universe를 다시 테스트한다.
  - ticker를 늘렸을 때도 `real_money_candidate`가 유지되는지, 아니면 watchlist-only로 내려가는지 확인한다.
- 전략:
  - `GTAA`
- 기간 / universe:
  - `2016-01-01 ~ latest DB`
  - effective result window: `2016-01-29 ~ 2026-04-17`
  - manual expanded ETF universe search
- 핵심 설정:
  - `Option = month_end`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
  - `Min ETF AUM = 1.0B`
  - `Max Bid-Ask Spread = 0.50%`
  - `Market Regime = off`
  - `Crash Guardrail = off`
  - `Defensive Tickers = TLT, IEF, LQD, BIL`
- 신규 확장 후보:
  - `SPY, QQQ, GLD, IEF, LQD, TLT`
  - `Top Assets = 1`
  - `Signal Interval = 8`
  - `Score Horizons = 1M / 3M / 6M`
  - `Risk-Off Mode = cash_only` 또는 `defensive_bond_preference`
- 결과:
  - `CAGR = 21.4953%`
  - `MDD = -6.4936%`
  - `Sharpe = 3.6601`
  - `Benchmark CAGR = 13.5612%`
  - `Net CAGR Spread = +7.9341%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
  - `Rolling Review = normal`
  - `Out-Of-Sample Review = normal`
- Top-2 확장 대안:
  - `SPY, QQQ, GLD, IEF, LQD, TLT`, `Top = 2`, `Interval = 4`, `1M / 3M / 6M`
  - `CAGR = 16.7945%`
  - `MDD = -8.3917%`
  - `Sharpe = 3.0086`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = watchlist_only`
  - `Validation = watch`
- 해석:
  - `TLT`를 추가한 6개 clean ETF universe는 ticker 부족 문제를 보강하는 방향으로 타당하다.
  - 다만 `Top = 2`를 유지하면 아직 `real_money_candidate`가 아니라 `watchlist_only`다.
  - 실전 기본값은 기존 `SPY / QQQ / GLD / IEF`, `Top = 2` 후보를 유지하고,
    신규 6개 universe `Top = 1`은 공격형 paper probation 후보로 추가한다.
- 관련 문서:
  - [GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md)

### 2026-04-18 - real-money candidate compact ETF search

- 목표:
  - 기존 preset에 국한하지 않고 GTAA ETF universe를 다시 탐색해 `Promotion = hold`가 아닌 실제 투자 가능 후보를 찾는다.
  - current runtime의 ETF operability / validation / deployment metadata를 유지한 채 `real_money_candidate`가 나오는지 확인한다.
- 전략:
  - `GTAA`
- 기간 / universe:
  - `2016-01-01 ~ latest DB`
  - effective result window: `2016-01-29 ~ 2026-03-31`
  - manual ETF universe search
- 핵심 설정:
  - `Option = month_end`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
  - `Min ETF AUM = 1.0B`
  - `Max Bid-Ask Spread = 0.50%`
  - `Market Regime = off`
- 추천 후보:
  - `SPY, QQQ, GLD, IEF`
  - `Top Assets = 2`
  - `Signal Interval = 4`
  - `Score Horizons = 1M / 3M`
  - `Risk-Off Mode = defensive_bond_preference`
- 결과:
  - `CAGR = 17.4612%`
  - `MDD = -8.3917%`
  - `Sharpe = 3.0717`
  - `Benchmark CAGR = 12.6486%`
  - `Net CAGR Spread = +4.8126%p`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
  - `ETF Operability = normal`
  - `Validation = normal`
  - `Rolling Review = normal`
  - `Out-Of-Sample Review = normal`
- 대안:
  - 공격형: `SPY, QQQ, GLD, LQD`, `Top = 1`, `Interval = 4`, `1M / 3M / 6M`, `CAGR = 20.6161%`, `MDD = -10.6744%`, `real_money_candidate`
  - 낮은 MDD: `SPY, QQQ, GLD, IEF, LQD`, `Top = 2`, `Interval = 6`, `1M / 3M`, `CAGR = 15.9664%`, `MDD = -4.7476%`, `real_money_candidate`
- 해석:
  - 기존 Phase 13 reference는 `production_candidate / watchlist_only`였지만,
    이번 compact ETF 변형은 `Validation = normal`을 회복해 `real_money_candidate`까지 올라갔다.
  - broader universe는 raw CAGR이 높아도 ETF profile / AUM / spread coverage 때문에 `hold`가 반복되어 최종 추천에서 제외했다.
  - 현재 deployment는 여전히 `paper_only`이므로 바로 live allocation이 아니라 paper probation 후보로 본다.
- 관련 문서:
  - [GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md)

### 2026-04-10 - practical non-hold reference

- 목표:
  - `Promotion != hold`, `Deployment != blocked`, `SPY` 대비 `CAGR / MDD` 우위를 동시에 만족하는 GTAA practical reference 확보
- 전략:
  - `GTAA`
- 기간 / universe:
  - `2016-01-01 ~ 2026-04-02`
  - custom ETF set
- 핵심 설정:
  - `Option = month_end`
  - `Top Assets = 2`
  - `Signal Interval = 3`
  - `Score Horizons = 1M / 3M`
  - `Risk-Off Mode = cash_only`
  - `Benchmark = SPY`
  - `Minimum Price = 5.0`
  - `Transaction Cost = 10 bps`
  - `Min ETF AUM = 0.0`
  - `Max Bid-Ask Spread = 100.0`
  - `Market Regime = off`
- factor / ticker:
  - `SPY, QQQ, GLD, LQD`
- 결과:
  - `CAGR = 14.7671%`
  - `MDD = -11.5626%`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = watchlist_only`
- 해석:
  - `hold`는 벗어났고 `blocked`도 아니다
  - 동일 sampled benchmark surface 기준 `SPY`보다 `CAGR / MDD`가 모두 더 좋았다
  - 다만 아직 `real_money_candidate`는 아니므로 실전형 후보라기보다 practical reference에 가깝다
- 다음 액션:
  - ETF operability / coverage interpretation이 완화되면 더 공격형 universe를 다시 비교한다
- 관련 문서:
  - [GTAA.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA.md)
  - [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
