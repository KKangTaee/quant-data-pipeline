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
