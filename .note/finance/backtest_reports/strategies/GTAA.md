# GTAA Backtest Hub

## 전략

- family: `GTAA`
- 관련 phase:
  - `Phase 12`
  - `Phase 13`

## 한 줄 요약

`GTAA`는 ETF family 중 가장 많은 universe 실험이 누적된 전략이고, 현재는 **SPY 대비 성과 우위 + non-hold 상태**를 동시에 만족하는 practical reference 후보가 하나 확보된 상태다.

## 지금 먼저 볼 문서

- [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
  - 현재 가장 실용적인 GTAA non-hold 후보를 정리한 문서

## 현재 대표 후보

- tickers:
  - `SPY, QQQ, GLD, LQD`
- `Top = 2`
- `Interval = 3`
- `Score Horizons = 1M / 3M`
- `Benchmark = SPY`
- `CAGR = 14.7671%`
- `MDD = -11.5626%`
- `Promotion = production_candidate`
- `Deployment = watchlist_only`

## 현재 해석

이 후보는:

- `hold`는 벗어났고
- `blocked`도 아니며
- `SPY`보다 `CAGR / MDD`가 모두 더 좋은 practical reference다

다만 아직:

- `real_money_candidate`까지 올라간 것은 아니고
- 운영 언어로는 `watchlist_only` 단계다

## 관련 문서

- [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
- [PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md)
- [PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md)
- [PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md)
- [PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md)
