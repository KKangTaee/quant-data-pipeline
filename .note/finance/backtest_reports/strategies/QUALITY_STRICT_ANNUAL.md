# Quality Strict Annual Backtest Hub

## 전략

- family: `Quality`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`, `Phase 15`

## 한 줄 요약

`Quality` 단독 family는 Phase 13 탐색에서는 `SPY` dominance와 non-hold exact-hit를 동시에 만족시키는 대표 후보를 만들지 못했다.
Phase 14 refresh에서는 한때 `production_candidate / watchlist / review_required` 후보가 보였고,
Phase 15 first pass에서는 bounded addition만으로는 다시 `hold`를 못 벗어났다.
하지만 Phase 15 structural rescue second pass에서는
`LQD + trend on + regime off + capital_discipline` 조합이
`real_money_candidate / paper_probation / review_required`까지 회복됐다.
그리고 rescued anchor downside search first pass에서는
`Top N = 12`가
`CAGR = 26.02% / MDD = -25.57%`
로 현재 recommended downside-improved candidate가 됐다.

즉:

- 품질 factor 조합 실험의 reference로는 의미가 있고
- strict annual family 중 최강 후보는 아니지만
- current practical contract 기준으로도
  다시 살릴 수 있는 구조 조합이 확인된 family다

## 지금 어떻게 읽으면 되는가

- current rescued candidate를 먼저 확인
- 그 다음 rescued anchor baseline과 downside-improved candidate를 비교한다
- 이후에는 rescued anchor 기준
  `factor addition / replacement`
  으로 이어간다

## 전략 log

- [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Quality > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과

- strongest search theme:
  - `capital_discipline` structural rescue 탐색
- current takeaway:
  - current strongest practical candidate는 다시 확보됐다
  - 그 위에서 `Top N = 12` downside-improved candidate도 확보됐다
  - family 단독으로는 여전히 `Value`보다 약하지만
  - `Quality`도 current practical contract에서
    `real_money_candidate / paper_probation`까지 올라갈 수 있다

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-13 - rescued anchor downside search first pass`
- 핵심 설정:
  - `capital_discipline`:
    - `roe`
    - `roa`
    - `cash_ratio`
    - `debt_to_assets`
  - `Benchmark = LQD`
  - `Trend Filter = on`
  - `Market Regime = off`
  - `Rebalance Interval = 1`
- 결과:
  - rescued anchor baseline:
    - `Top N = 10`
    - `CAGR = 24.28%`
    - `MDD = -31.48%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
  - recommended downside-improved candidate:
    - `Top N = 12`
    - `CAGR = 26.02%`
    - `MDD = -25.57%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
    - `Rolling = watch`
  - conservative clean alternative:
    - `Top N = 16`
    - `CAGR = 20.23%`
    - `MDD = -25.73%`
    - `Promotion = real_money_candidate`
    - `Shortlist = paper_probation`
    - `Deployment = review_required`
- 다음에 볼 것:
  - rescued anchor 기준
    `bounded factor addition / replacement`

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
- [PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md)
  - `benchmark / overlay` 구조를 조정해 `Quality` current rescued candidate를 다시 확보한 문서
- [PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md)
  - rescued anchor 기준 `Top N / Rebalance Interval` downside search를 다시 본 문서
- [QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md)
  - current rescued candidate를 전략 구성 중심으로 바로 읽는 one-pager
- [QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - rescued anchor보다 `MDD`를 크게 낮춘 `Quality` downside-improved current candidate one-pager

## 실무 해석

지금 시점의 `Quality Strict Annual`은:

- 단독 운영 exact winner보다는
- factor 비교 기준점
- `Value`와 `Quality + Value`를 해석할 때의 reference family
- 그리고 current practical contract 기준으로는
  rescued structural candidate와 downside-improved candidate가 함께 확인된 family

로 읽는 편이 맞다.
