# Quality + Value Strict Annual Backtest Hub

## 전략

- family: `Quality + Value`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`

## 한 줄 요약

`Quality + Value`는 Phase 13 탐색에서 가장 공격적인 family는 아니었지만, 방어적 조합과 low-drawdown 탐색을 해볼 때 가장 자주 검토된 family였다.

다만:

- `MDD` 방어는 상대적으로 나았지만
- `SPY`를 확실히 이길 만큼의 `CAGR`가 부족한 경우가 많았다
- current runtime refresh에서는 default blend + candidate equal-weight benchmark 조합이
  `production_candidate / watchlist / review_required`까지 올라가는 stronger non-hold candidate로 확인됐다

## 지금 어떻게 읽으면 되는가

1. low-drawdown 탐색 문서를 먼저 본다
2. family summary에서 `Value`와 비교한다
3. 필요하면 `SPY` 비교 문서로 넘어간다

## 전략 log

- [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Quality + Value > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과

- strongest theme:
  - low-drawdown / defensive factor blend 탐색
- current takeaway:
  - 방어형 실험에는 여전히 의미가 있다
  - current best non-hold:
    - default blend
    - `candidate_universe_equal_weight` benchmark
    - `promotion = production_candidate`
    - `shortlist = watchlist`
    - `deployment = review_required`

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-10 - current strongest non-hold blend`
- 핵심 설정:
  - default blend
  - `Benchmark Contract = Candidate Universe Equal-Weight`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
- 결과:
  - `CAGR = 28.51%`
  - `MDD = -28.35%`
  - `Promotion = production_candidate`
  - `Shortlist = watchlist`
  - `Deployment = review_required`
- 다음에 볼 것:
  - validation consistency를 더 개선할 수 있는 blend / benchmark 조합 탐색

## 관련 결과 문서

- [PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_QUALITY_VALUE_2016_LOW_DRAWDOWN_FACTOR_OPTION_SEARCH.md)
  - `Quality + Value` low-drawdown 핵심 탐색 문서
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - family 전체 `SPY` 초과 탐색
- [PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` 조건 교집합 탐색
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 탐색
- [PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md)
  - wider coverage가 방어형 family에 주는 효과를 같이 확인한 문서
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체 summary 문서
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - current runtime 기준으로 `Quality + Value` strongest non-hold candidate를 다시 고정한 refresh 문서

## 실무 해석

지금 시점의 `Quality + Value Strict Annual`은:

- low-drawdown 연구 reference
- 방어형 factor blend 실험용 family
- 그리고 current runtime 기준으로는
  `watchlist / review_required`까지 올라가는 non-hold blended candidate family

로 보는 편이 맞고, raw winner 기준으로는 아직 `Value`보다 뒤에 있다.
