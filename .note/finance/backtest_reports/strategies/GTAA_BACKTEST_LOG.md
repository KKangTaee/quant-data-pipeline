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
