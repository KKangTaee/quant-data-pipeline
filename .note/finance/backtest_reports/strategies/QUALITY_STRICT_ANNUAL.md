# Quality Strict Annual Backtest Hub

## 전략

- family: `Quality`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`, `Phase 15`

## 한 줄 요약

`Quality` 단독 family는 Phase 13 탐색에서는 `SPY` dominance와 non-hold exact-hit를 동시에 만족시키는 대표 후보를 만들지 못했다.
Phase 14 refresh에서는 한때 `production_candidate / watchlist / review_required` 후보가 보였지만,
Phase 15에서 strict annual dynamic PIT preset semantics를 literal하게 맞춘 뒤 다시 보면
current bounded addition pass에서는 다시 `hold` 상태로 돌아왔다.

즉:

- 품질 factor 조합 실험의 reference로는 의미가 있고
- strict annual family 중 최강 후보는 아니지만
- current literal preset semantics 기준으로는
  아직 stable non-hold candidate를 다시 확보하지 못한 family다

## 지금 어떻게 읽으면 되는가

- `SPY` 대비 우위가 가능한지 먼저 확인
- current literal preset semantics에서도 non-hold가 나오는지 확인
- 안 되면 `Value` 또는 `Quality + Value`와 비교하고,
  `benchmark / overlay / factor replacement`로 넘어간다

## 전략 log

- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Quality > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과

- strongest search theme:
  - `SPY` dominance 탐색
- current takeaway:
  - exact-hit 없음
  - family 단독으로는 `Value`보다 약하다
  - Phase 15 current literal preset semantics 기준으로는
    controlled one-factor addition만으로 `hold`를 못 벗어났다

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-13 - post-PIT semantics controlled addition review`
- 핵심 설정:
  - anchor:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - `Benchmark = LQD`
  - `Top N = 10`
  - `Rebalance Interval = 1`
  - `Trend Filter = on`
  - `Market Regime = on`
- 결과:
  - baseline:
    - `CAGR = 13.26%`
    - `MDD = -32.59%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
  - best near-miss:
    - `+ net_debt_to_equity`
    - `CAGR = 13.51%`
    - `MDD = -23.84%`
    - `Promotion = hold`
    - `Shortlist = hold`
    - `Deployment = blocked`
- 다음에 볼 것:
  - single-factor addition보다
    `benchmark / overlay / factor replacement / top_n` 구조 탐색

## 관련 결과 문서

- [PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_QUALITY_STRICT_SPY_DOMINANCE_SEARCH.md)
  - `Quality`만으로 `SPY`를 동시에 이길 수 있는지 본 핵심 문서
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - strict annual family 전체를 `SPY` 기준으로 비교한 문서
- [PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_AND_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` 조건까지 넣었을 때 family 비교 결과
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 조건 탐색
- [PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_COVERAGE300_500_1000_TARGET_SEARCH.md)
  - coverage 확대가 `Quality` family에도 의미가 있었는지 확인하는 공통 문서
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체를 한 장으로 요약한 summary 문서
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - Phase 14 current runtime 기준으로 `Quality` current best non-hold candidate를 다시 고정한 refresh 문서
- [PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
  - strict annual dynamic PIT preset semantics를 literal하게 맞춘 뒤,
    `Quality` bounded addition search가 왜 non-hold를 못 회복했는지 정리한 문서

## 실무 해석

지금 시점의 `Quality Strict Annual`은:

- 단독 운영 exact winner보다는
- factor 비교 기준점
- `Value`와 `Quality + Value`를 해석할 때의 reference family
- 그리고 current literal preset semantics 기준으로는
  recovery search가 더 필요한 family

로 읽는 편이 맞다.
