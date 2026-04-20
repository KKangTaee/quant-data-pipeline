# Backtest Report Index

## 목적

이 문서는 `.note/finance/backtest_reports/` 아래의 결과 리포트 문서를 빠르게 찾기 위한 인덱스다.

## 먼저 볼 문서

- `strategies/README.md`
  - 전략별 허브 문서 안내
- `strategies/BACKTEST_LOG_TEMPLATE.md`
  - 전략별 backtest log를 append할 때 공통으로 쓰는 템플릿
  - 최신 날짜순 기록과 마지막 `최근 판단 요약표` 운영 기준을 포함한다
- `strategies/GTAA.md`
  - `GTAA` 결과 허브
- `strategies/GTAA_BACKTEST_LOG.md`
  - `GTAA` 전략 run 기록 누적 문서
- `strategies/GTAA_REAL_MONEY_CANDIDATE_SEARCH_20260418.md`
  - current DB/runtime 기준 `Promotion = real_money_candidate`까지 올라간 GTAA compact ETF 후보 탐색 문서
- `strategies/GTAA_EXPANDED_UNIVERSE_FOLLOWUP_20260420.md`
  - compact GTAA 후보의 ticker 부족 문제를 보강하기 위해 `TLT`를 추가한 6개 ETF universe follow-up 백테스트 문서
  - `Interval = 6 / 8` cadence가 느린 리밸런싱이라는 운용 해석과 sensitivity table도 포함한다
- `strategies/QUALITY_STRICT_ANNUAL.md`
  - `Quality > Strict Annual` 결과 허브
- `strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Quality > Strict Annual` 전략 run 기록 누적 문서
  - 최신 날짜순으로 읽고, 마지막 요약표에서 유지 / 교체 / 보류 판단을 빠르게 확인한다
- `strategies/QUALITY_STRICT_ANNUAL_RESCUED_CURRENT_CANDIDATE.md`
  - `Quality > Strict Annual` structural rescue search에서 다시 확보한 current candidate one-pager
- `strategies/QUALITY_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md`
  - rescued `Quality > Strict Annual` anchor보다 `MDD`를 크게 낮춘 downside-improved current candidate one-pager
- `strategies/VALUE_STRICT_ANNUAL.md`
  - `Value > Strict Annual` 결과 허브
- `strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md`
  - `Value > Strict Annual` 전략 run 기록 누적 문서
  - 최신 날짜순으로 읽고, 마지막 요약표에서 유지 / 교체 / 보류 판단을 빠르게 확인한다
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
  - 최신 날짜순으로 읽고, 마지막 요약표에서 유지 / 교체 / 보류 판단을 빠르게 확인한다
- `strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md`
  - 현재 `Value / Quality / Quality + Value` family에서 다시 볼 practical candidate를 한 장으로 요약한 문서
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
- `phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md`
  - `Value > Strict Annual` lower-MDD near-miss를 rescue할 수 있는지 다시 본 second-pass 문서
- `phase16/PHASE16_QUALITY_VALUE_DOWNSIDE_REFINEMENT_FIRST_PASS.md`
  - `Quality + Value > Strict Annual` strongest practical anchor를 기준으로 bounded downside refinement를 다시 본 first-pass 문서
- `phase16/PHASE16_QUALITY_VALUE_STRONGEST_POINT_DOWNSIDE_FOLLOWUP_SECOND_PASS.md`
  - `Quality + Value > Strict Annual` strongest practical point를 current code 기준으로 다시 확인하고,
    lower-MDD but weaker-gate 대안과 `SPY` benchmark 대안을 같이 본 second-pass 문서
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md`
  - quality/value replacement를 함께 반영한 current strongest practical blended candidate one-pager
- `strategies/QUALITY_VALUE_STRICT_ANNUAL_POR_REPLACEMENT_CURRENT_CANDIDATE.md`
  - `operating_income_yield -> por` replacement를 더한 Phase 16 strongest practical blended candidate one-pager

## Phase 17 Raw Archive

- `phase17/README.md`
  - Phase 17 structural downside-improvement archive 안내 문서
- `phase17/PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `partial cash retention`을 실제 `Value` / `Quality + Value` anchor에 적용해
    same-gate lower-MDD rescue가 가능한지 본 first-pass representative rerun 문서
- `phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `defensive sleeve risk-off`를 같은 anchor에 적용해
    same-gate lower-MDD rescue가 가능한지 본 first-pass representative rerun 문서
- `phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `concentration-aware weighting`을 같은 anchor에 적용해
    same-gate lower-MDD rescue가 가능한지 본 first-pass representative rerun 문서

## Phase 18 Raw Archive

- `phase18/README.md`
  - Phase 18 larger structural redesign archive 안내 문서
- `phase18/PHASE18_NEXT_RANKED_FILL_REPRESENTATIVE_RERUN_FIRST_PASS.md`
  - strict annual `Fill Rejected Slots With Next Ranked Names` redesign을
    current `Value` / `Quality + Value` structural probe에 적용해
    meaningful rescue 또는 anchor replacement가 가능한지 본 first-pass representative rerun 문서
- `phase18/PHASE18_VALUE_FILL_ANCHOR_NEAR_FOLLOWUP_SECOND_PASS.md`
  - `Value` current practical anchor 근처에서
    fill contract를 좁게 다시 보고
    same-gate lower-MDD rescue가 실제로 있는지 본 second-pass 문서

## Phase 21 Raw Archive

- `phase21/README.md`
  - Phase 21 integrated deep validation archive 안내 문서
- `phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - `Value` current anchor와 lower-MDD alternative를 같은 validation frame에서 다시 돌려,
    current anchor 유지 여부와 alternative의 weaker-gate status가 그대로인지 확인한 first-pass 문서
- `phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - `Quality` current anchor와 cleaner alternative를 같은 validation frame에서 다시 돌려,
    current anchor 유지 여부와 cleaner alternative의 comparison-only status가 그대로인지 확인한 first-pass 문서
- `phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - `Quality + Value` current strongest point와 lower-MDD alternative를 같은 validation frame에서 다시 돌려,
    current anchor 유지 여부와 `Top N 9` alternative의 weaker-gate status가 그대로인지 확인한 first-pass 문서
- `phase21/PHASE21_PORTFOLIO_BRIDGE_VALIDATION_FIRST_PASS.md`
  - `Load Recommended Candidates -> 33/33/34 weighted portfolio -> saved portfolio replay` 흐름을 검증하고,
    portfolio bridge가 Phase 22 candidate construction 대상으로 적합한지 확인한 첫 검증 보고서
  - 최종 포트폴리오 후보 확정보다는 weighted / saved portfolio workflow 재현성 확인에 초점을 둔다

## Phase 22 Raw Archive

- `phase22/README.md`
  - Phase 22 portfolio-level candidate construction archive 안내 문서
- `phase22/PHASE22_BASELINE_PORTFOLIO_CANDIDATE_PACK_FIRST_PASS.md`
  - `Value / Quality / Quality + Value` current anchor 3개를
    saved portfolio definition 기준 개발 검증용 equal-third baseline portfolio candidate pack으로 다시 정의한 첫 report
  - `33 / 33 / 34` 표현과 `[33.33, 33.33, 33.33]` 저장 weight의 차이를 정리하고,
    현재 status를 `baseline_candidate / portfolio_watchlist / not_deployment_ready`로 고정한다
  - 이후 second work unit에서 portfolio-level primary benchmark는 이 equal-third baseline으로 두고,
    guardrail은 report-level warning으로 해석하기로 정리했다
  - 이 baseline은 투자 기준이 아니라 portfolio 구성 / 저장 / replay / 비교 workflow를 검증하기 위한 fixture 기준이다
- `phase22/PHASE22_WEIGHT_ALTERNATIVE_RERUN_FIRST_PASS.md`
  - official equal-third baseline과 `25 / 25 / 50`, `40 / 40 / 20` weight alternative를
    saved compare context 기준으로 다시 계산한 Phase 22 rerun report
  - `33 / 33 / 34` Phase 21 near-equal 수치와 `[33.33, 33.33, 33.33]` Phase 22 official baseline 수치를 분리하고,
    현재 결론을 `baseline 유지 / alternative 보류 / immediate replacement 없음`으로 정리한다

## Phase 23 Raw Archive

- `phase23/README.md`
  - Phase 23 quarterly / alternate cadence productionization report archive 안내 문서
- `phase23/PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md`
  - quarterly strict 3개 family가 non-default portfolio handling contract를 받은 상태로
    실제 DB-backed runtime에서 실행되는지 확인한 smoke validation report
  - `Weighting`, `Rejected Slot Handling`, `Risk-Off`, `Defensive Tickers` 값이
    result bundle meta에 보존되는지도 함께 확인한다

## Phase 24 Raw Archive

- `phase24/README.md`
  - Phase 24 new strategy expansion report archive 안내 문서
- `phase24/PHASE24_GLOBAL_RELATIVE_STRENGTH_CORE_RUNTIME_SMOKE_VALIDATION.md`
  - 첫 신규 전략 후보 `Global Relative Strength`의 core simulation, sample helper,
    DB-backed runtime wrapper가 compile / import / smoke run을 통과하는지 확인한 개발 검증 report
  - 아직 UI catalog, single strategy 화면, compare, history, saved replay는 연결 전이며
    다음 Phase 24 구현 단위로 남긴다

## 운영 메모

앞으로 새 report를 만들 때는:

1. 먼저 `strategies/` 아래 전략 허브에 반영한다
2. 세부 결과 원문은 phase archive에 둔다
3. 여기 index에는 허브와 archive entry를 연결한다
