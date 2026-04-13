# Backtest Report Index

## 목적

이 문서는 `.note/finance/backtest_reports/` 아래의 결과 리포트 문서를 빠르게 찾기 위한 인덱스다.

## 먼저 볼 문서

- `strategies/README.md`
  - 전략별 허브 문서 안내
- `strategies/BACKTEST_LOG_TEMPLATE.md`
  - 전략별 backtest log를 append할 때 공통으로 쓰는 템플릿
- `strategies/GTAA.md`
  - `GTAA` 결과 허브
- `strategies/GTAA_BACKTEST_LOG.md`
  - `GTAA` 전략 run 기록 누적 문서
- `strategies/QUALITY_STRICT_ANNUAL.md`
  - `Quality > Strict Annual` 결과 허브
- `strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Quality > Strict Annual` 전략 run 기록 누적 문서
- `strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md`
  - `Quality > Strict Annual` structural rescue search에서 다시 확보한 current candidate one-pager
- `strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
  - rescued `Quality > Strict Annual` anchor보다 `MDD`를 크게 낮춘 downside-improved current candidate one-pager
- `strategies/VALUE_STRICT_ANNUAL.md`
  - `Value > Strict Annual` 결과 허브
- `strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Value > Strict Annual` 전략 run 기록 누적 문서
- `strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - strongest `Value > Strict Annual` 후보 하나를 전략 구성 중심으로 바로 읽는 one-pager
- `strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
  - strongest baseline보다 `MDD`를 낮춘 downside-improved `Value > Strict Annual` 후보 one-pager
- `strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md`
  - downside-improved anchor에 one-factor addition을 붙인 best current `Value > Strict Annual` 후보 one-pager
- `strategies/QUALITY_VALUE_STRICT_ANNUAL.md`
  - `Quality + Value > Strict Annual` 결과 허브
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Quality + Value > Strict Annual` 전략 run 기록 누적 문서
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_BEST_ADDITION_CURRENT_CANDIDATE.md`
  - `Quality + Value > Strict Annual` bounded addition search에서 가장 좋은 raw addition candidate one-pager

## Phase 13 Raw Archive

- `phase13/README.md`
  - Phase 13 raw report archive 안내 문서
  - 전략 허브에서 연결된 세부 report를 phase 기준으로 모아둔 위치

## Phase 14 Raw Archive

- `phase14/README.md`
  - Phase 14 current-runtime refresh archive 안내 문서
  - calibration 이후 strict annual family를 다시 돌려본 결과 문서 위치
- `phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md`
  - Phase 14 calibration 이후 `Quality / Value / Quality + Value` strict annual family를 current practical contract로 다시 돌려,
    각 family의 strongest non-hold current candidate를 고정한 refresh 문서

## Phase 15 Raw Archive

- `phase15/README.md`
  - Phase 15 candidate quality improvement archive 안내 문서
- `../phase15/PHASE15_COMPLETION_SUMMARY.md`
  - Phase 15 candidate quality improvement closeout 요약 문서
- `../phase15/PHASE15_TEST_CHECKLIST.md`
  - Phase 15 strongest/current candidate 검수 checklist 문서
- `phase15/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
  - strongest `Value` baseline에서 `MDD`를 낮추는 방향으로 practical candidate quality를 개선할 수 있는지 본 first-pass 문서
- `phase15/PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md`
  - downside-improved `Value` anchor에 one-factor addition을 붙여 current best candidate를 다시 본 second-pass 문서
- `phase15/PHASE15_QUALITY_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
  - `Quality` family에서 controlled addition이 current literal preset semantics 기준으로 왜 non-hold를 회복하지 못했는지 정리한 문서
- `phase15/PHASE15_QUALITY_STRUCTURAL_RESCUE_SEARCH_SECOND_PASS.md`
  - `Quality` family에서 `benchmark / overlay` 구조를 조정해 current rescued candidate를 다시 확보한 문서
- `phase15/PHASE15_QUALITY_RESCUED_ANCHOR_DOWNSIDE_SEARCH_FIRST_PASS.md`
  - rescued `Quality` anchor 기준 `Top N / Rebalance Interval` downside search를 다시 본 문서
- `phase15/PHASE15_QUALITY_RESCUED_ANCHOR_FACTOR_SEARCH_SECOND_PASS.md`
  - rescued `Quality` anchor 위 bounded factor addition / replacement를 다시 붙였지만 baseline을 못 넘었다는 점을 정리한 문서
- `phase15/PHASE15_QUALITY_ALTERNATE_CONTRACT_SEARCH_THIRD_PASS.md`
  - rescued `Quality` downside-improved anchor를 유지한 채 `benchmark / overlay` alternate contract를 다시 보고,
    strongest practical point와 cleaner alternative를 함께 정리한 문서
- `phase15/PHASE15_QUALITY_VALUE_CANDIDATE_IMPROVEMENT_SEARCH_FIRST_PASS.md`
  - `Quality + Value` family baseline blend에 controlled addition을 붙여 best raw addition candidate를 다시 정리한 문서
- `phase15/PHASE15_QUALITY_VALUE_PER_DOWNSIDE_SEARCH_FIRST_PASS.md`
  - `Quality + Value + per` strongest candidate를 anchor로 `Top N` downside search를 다시 본 문서
- `phase15/PHASE15_QUALITY_VALUE_PER_BENCHMARK_AND_PRUNING_SEARCH_SECOND_PASS.md`
  - `Quality + Value + per` strongest candidate를 anchor로 benchmark sensitivity와 quality-side pruning을 다시 본 문서
- `phase15/PHASE15_QUALITY_VALUE_VALUE_SIDE_SEARCH_THIRD_PASS.md`
  - `Quality + Value + per` strongest candidate에서 value-side removal / replacement를 다시 보고 `ocf_yield -> pcr` current strongest practical candidate를 고정한 문서
- `phase15/PHASE15_QUALITY_VALUE_REPLACEMENT_ANCHOR_FOLLOWUP_FOURTH_PASS.md`
  - `ocf_yield -> pcr` current strongest practical point 위에서 `Top N / benchmark` follow-up을 다시 보고,
    strongest practical point가 그대로 유지되는지 정리한 문서
- `phase15/PHASE15_QUALITY_VALUE_QUALITY_SIDE_SEARCH_FIFTH_PASS.md`
  - `ocf_yield -> pcr` anchor 위 quality-side replacement를 다시 보고,
    `net_margin -> operating_margin`가 strongest practical point를 갱신했는지 정리한 문서
- `phase15/PHASE15_QUALITY_VALUE_STRONGEST_ANCHOR_TOPN_SEARCH_SIXTH_PASS.md`
  - new strongest practical point 위에서 `Top N` follow-up을 다시 보고,
    `Top N = 10`이 strongest practical point로 유지되는지 정리한 문서
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_VALUE_REPLACEMENT_CURRENT_CANDIDATE.md`
  - `ocf_yield -> pcr` replacement 기반 current strongest practical blended candidate one-pager

## Phase 16 Raw Archive

- `phase16/README.md`
  - Phase 16 downside-focused practical refinement archive 안내 문서
- `phase16/PHASE16_CURRENT_CHAPTER_TODO.md`
  - Phase 16 current execution board
- `phase16/PHASE16_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
  - `Value > Strict Annual` current practical anchor를 기준으로 bounded downside refinement를 다시 본 first-pass 문서
- `phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
  - `Quality + Value > Strict Annual` strongest practical anchor를 기준으로 bounded downside refinement를 다시 본 first-pass 문서
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - quality/value replacement를 함께 반영한 current strongest practical blended candidate one-pager
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md`
  - `operating_income_yield -> por` replacement를 더한 Phase 16 strongest practical blended candidate one-pager

## 운영 메모

앞으로 새 report를 만들 때는:

1. 먼저 `strategies/` 아래 전략 허브에 반영한다
2. 세부 결과 원문은 phase archive에 둔다
3. 여기 index에는 허브와 archive entry를 연결한다
