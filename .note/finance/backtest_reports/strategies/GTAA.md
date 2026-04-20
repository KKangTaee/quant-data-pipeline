# GTAA Backtest Hub

## 전략

- family: `GTAA`
- 관련 phase:
  - `Phase 12`
  - `Phase 13`

## 한 줄 요약

`GTAA`는 ETF family 중 가장 많은 universe 실험이 누적된 전략이고, 현재는 **current runtime 기준 `real_money_candidate`까지 올라간 compact ETF 후보**가 확보된 상태다.
2026-04-20 follow-up에서는 `TLT`를 추가한 6개 ETF 확장 후보도 확보했지만,
2개 보유 기본값은 아직 compact 후보가 더 안정적인 대표값으로 남는다.

## 지금 먼저 볼 문서

- [GTAA_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_BACKTEST_LOG.md)
  - `GTAA`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log
- [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
  - 이전 practical non-hold reference를 정리한 문서
- [GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md)
  - current DB/runtime 기준 `real_money_candidate` GTAA 후보를 다시 찾은 문서
- [GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md)
  - compact 후보의 ticker 부족 문제를 보강하기 위해 `TLT`를 추가한 6개 ETF universe를 다시 본 follow-up 문서

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

## 확장 universe 후보

- tickers:
  - `SPY, QQQ, GLD, IEF, LQD, TLT`
- `Top = 1`
- `Interval = 8`
- `Score Horizons = 1M / 3M / 6M`
- `Benchmark = SPY`
- `Risk-Off Mode = cash_only` 또는 `defensive_bond_preference`
- `CAGR = 21.4953%`
- `MDD = -6.4936%`
- `Sharpe = 3.6601`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = paper_only`

이 후보는 ticker universe 부족을 보강하지만 매 리밸런싱마다 1개 ETF만 보유한다.
또한 `Interval = 8`은 tactical allocation 관점에서는 느린 cadence다.
따라서 대표 후보 교체가 아니라 공격형 paper probation 후보로 별도 tracking한다.

같은 6개 universe에서 `Top = 2`, `Interval = 4`, `1M / 3M / 6M`로 돌린 후보는
`16.7945% / -8.3917% / production_candidate / watchlist_only`라서
실전 후보가 아니라 다음 개선 대상으로 남긴다.

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-20 - expanded universe follow-up search`
- 핵심 설정:
  - `month_end`
  - `Top = 1`
  - `Interval = 8`
  - `Score Horizons = 1M / 3M / 6M`
  - `Benchmark = SPY`
  - `Risk-Off Mode = cash_only` 또는 `defensive_bond_preference`
  - `Min ETF AUM = 1.0B`
  - `Max Bid-Ask Spread = 0.50%`
- 결과:
  - `CAGR = 21.4953%`
  - `MDD = -6.4936%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = paper_only`
- 다음에 볼 것:
  - compact `Top = 2` 대표 후보와 expanded `Top = 1` 공격형 후보를 함께 paper tracking한다
  - expanded `Top = 2`는 validation watch를 정상화할 수 있는지 별도 개선 대상으로 본다

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
- [GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md)
- [PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_GTAA_NONHOLD_SPY_OUTPERFORMANCE_SEARCH.md)
- [PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_DB_ETF_GROUP_SEARCH.md)
- [PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_INTERVAL1_UNIVERSE_VARIATION_SEARCH.md)
- [PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_VS_SPY_DOMINANCE_SEARCH.md)
- [PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase12/PHASE12_GTAA_CAGR9_MDD16_TARGET_SEARCH.md)
