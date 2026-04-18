# GTAA Backtest Hub

## 전략

- family: `GTAA`
- 관련 phase:
  - `Phase 12`
  - `Phase 13`

## 한 줄 요약

`GTAA`는 ETF family 중 가장 많은 universe 실험이 누적된 전략이고, 현재는 **current runtime 기준 `real_money_candidate`까지 올라간 compact ETF 후보**가 확보된 상태다.

## 지금 먼저 볼 문서

- [GTAA_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_BACKTEST_LOG.md)
  - `GTAA`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log
- [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
  - 이전 practical non-hold reference를 정리한 문서
- [GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md)
  - current DB/runtime 기준 `real_money_candidate` GTAA 후보를 다시 찾은 문서

## 현재 대표 후보

- tickers:
  - `SPY, QQQ, GLD, IEF`
- `Top = 2`
- `Interval = 4`
- `Score Horizons = 1M / 3M`
- `Benchmark = SPY`
- `Risk-Off Mode = defensive_bond_preference`
- `CAGR = 17.4612%`
- `MDD = -8.3917%`
- `Sharpe = 3.0717`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = paper_only`

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-18 - real-money candidate compact ETF search`
- 핵심 설정:
  - `month_end`
  - `Top = 2`
  - `Interval = 4`
  - `Score Horizons = 1M / 3M`
  - `Benchmark = SPY`
  - `Risk-Off Mode = defensive_bond_preference`
  - `Min ETF AUM = 1.0B`
  - `Max Bid-Ask Spread = 0.50%`
- 결과:
  - `CAGR = 17.4612%`
  - `MDD = -8.3917%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
- 다음에 볼 것:
  - 월별 paper tracking을 시작하고 다음 month-end에서 같은 promotion 상태가 유지되는지 확인

## 현재 해석

이 후보는:

- `hold`는 벗어났고
- current runtime 기준 `real_money_candidate`다
- `SPY` sampled benchmark보다 `CAGR / MDD`가 모두 더 좋다

다만 아직:

- 운영 언어로는 `paper_only` 단계다
- 즉 바로 live allocation이 아니라 paper probation 후보로 먼저 관리한다
- 문서 안에서 비교되는 `SPY benchmark MDD`는 raw daily `SPY`가 아니라
  `GTAA` 설정(`month_end`, `interval = 4`)에 맞춰 샘플링된 benchmark 기준이라는 점을 같이 봐야 한다

## 관련 문서

- [GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md)
- [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
- [PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md)
- [PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md)
- [PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md)
- [PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md)
