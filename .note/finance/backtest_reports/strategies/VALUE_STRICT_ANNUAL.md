# Value Strict Annual Backtest Hub

## 이 문서는 무엇인가

이 문서는 `Value > Strict Annual` 전략을 위한
**전략 허브 문서**다.

쉽게 말하면:

- 이 전략으로 지금까지 어떤 백테스트를 했는지
- 그중에서 지금 다시 볼 만한 후보가 무엇인지
- 먼저 어떤 문서를 열어야 하는지

를 한 페이지에서 안내하는 문서다.

즉 이 문서는:

- 실행 가이드 한 장
- 결과 요약
- 관련 문서 안내

를 한데 모아 둔 `입구 페이지`에 가깝다.

## 이 문서는 무엇을 하는가

이 문서를 보면 바로 알 수 있는 것은:

- 이 전략이 대체 어떤 전략인지
- 지금 가장 강한 후보가 무엇인지
- 더 균형 잡힌 후보가 무엇인지
- 다음에 어떤 문서를 보면 되는지

이다.

## 이 문서는 무엇을 하지 않는가

이 문서는:

- 모든 실험 과정을 처음부터 끝까지 자세히 설명하는 문서가 아니다
- 백테스트 엔진 구현 문서도 아니다
- 세부 실험 로그 원문 자체도 아니다

세부 실험 과정은 phase별 report 문서에서 보고,
실제 실행 기록 누적은 backtest log 문서에서 본다.

## 전략

- family: `Value`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`, `Phase 14`

## 이 전략 허브를 어떻게 읽으면 되는가

1. 이 문서에서 현재 strongest candidate와 balanced candidate를 먼저 본다
2. 더 구체적인 입력값이 필요하면 one-pager를 연다
3. 과거 실험 흐름이 궁금하면 phase report를 연다
4. 실제 run 기록 누적을 보려면 backtest log를 연다

## 한 줄 요약

`Value`는 Phase 13 strict annual family 탐색에서 가장 강한 raw 성과를 보인 family였다.

다만:

- strongest raw winner는 `MDD`가 깊고
- 더 균형 잡힌 후보는 `hold`가 남는 패턴이 반복됐다

## 가장 먼저 볼 문서

- [VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_STRONGEST_CURRENT_CANDIDATE.md)
  - strongest current candidate를 바로 보는 one-pager
  - 실제 입력값 / factor / overlay / 기대 결과를 한 장에 모은 문서
- [VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_DOWNSIDE_IMPROVED_CURRENT_CANDIDATE.md)
  - strongest baseline보다 `MDD`를 낮춘 더 균형 잡힌 후보 문서
- [VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_FACTOR_ADDITION_BEST_CURRENT_CANDIDATE.md)
  - downside-improved 후보를 조금 더 개선한 best-addition 후보 문서

## 전략 log

- [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - `Value > Strict Annual`를 어떤 세팅으로 돌렸고 결과가 어땠는지 누적 관리하는 전략 log

## 대표 결과

- strongest raw winner:
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
  - `promotion = real_money_candidate`
- downside-improved current candidate:
  - `CAGR = 27.48%`
  - `MDD = -24.55%`
  - `promotion = real_money_candidate`
- best addition candidate:
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `promotion = real_money_candidate`
- strongest balanced exact hit:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - 문제: `promotion = hold`

## 최근 backtest log snapshot

- 최근 기록:
  - `2026-04-13 - factor addition second pass에서 psr candidate를 고정함`
- 핵심 설정:
  - default value factors + `psr`
  - `Benchmark = SPY`
  - `Top N = 14`
  - `Rebalance Interval = 1`
  - `Trend Filter = off`
  - `Market Regime = off`
- 결과:
  - `CAGR = 28.13%`
  - `MDD = -24.55%`
  - `Promotion = real_money_candidate`
  - `Shortlist = paper_probation`
  - `Deployment = review_required`
- 다음에 볼 것:
  - strongest raw / downside-improved / best-addition 후보를
    Phase 15 checklist 기준으로 다시 검수
  - next phase에서
    candidate consolidation 또는 추가 downside follow-up 중 무엇을 먼저 할지 결정

## 관련 결과 문서

- [PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md)
  - strongest raw winner를 UI에서 다시 넣는 가이드
- [PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH.md)
  - `CAGR 15% / MDD 20%` exact hit 탐색
- [PHASE13_VALUE_STRICT_SPY_TARGET_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_SPY_TARGET_SEARCH.md)
  - `SPY` 대비 기준으로 본 `Value` family 핵심 탐색
- [PHASE13_VALUE_STRICT_HOLD_FREE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_VALUE_STRICT_HOLD_FREE_SEARCH.md)
  - `hold`를 푼 상태에서도 숫자 조건을 맞출 수 있는지 본 문서
- [PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_HOLD_DIAGNOSTIC_AND_NONHOLD_NEAR_MISS_SEARCH.md)
  - `hold` 원인을 `validation` 계층에서 진단한 문서
- [PHASE13_CAGR20_MDD25_HOLD_FREE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_CAGR20_MDD25_HOLD_FREE_SEARCH.md)
  - 더 높은 return target에서 hold-free가 가능한지 본 문서
- [PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_REAL_MONEY_CANDIDATE_SPY_MDD25_SEARCH.md)
  - `real_money_candidate + SPY 초과 + MDD 25% 이내` 조건 탐색
- [PHASE13_SPY_OUTPERFORMANCE_SEARCH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_SPY_OUTPERFORMANCE_SEARCH.md)
  - family 전체 `SPY` 초과 탐색
- [PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase13/PHASE13_STRICT_ANNUAL_FAMILY_BACKTEST_SUMMARY.md)
  - family 전체 summary
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - current runtime practical contract 기준으로 `Value` strongest exact candidate와 주변 near-miss를 다시 고정한 refresh 문서
- [PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_VALUE_DOWNSIDE_IMPROVEMENT_SEARCH_FIRST_PASS.md)
  - strongest baseline에서 `MDD`를 낮추는 방향으로 본 first-pass downside improvement search 문서
- [PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase15/PHASE15_VALUE_FACTOR_ADDITION_SECOND_PASS.md)
  - first-pass downside-improved anchor에 one-factor addition을 붙여 다시 본 second-pass 문서

## 실무 해석

지금 시점의 `Value Strict Annual`은:

- strict annual 3개 family 중 가장 강한 성과 축
- 다만 validation / promotion 병목이 같이 따라오는 family
- 그리고 current runtime refresh에서도
  `real_money_candidate / paper_probation / review_required`
  exact candidate가 다시 재현되는 family
- Phase 15 first pass에서는
  `Top N = 14`로 downside를 낮춘 more balanced current candidate도 확보한 family
- Phase 15 second pass에서는
  `psr` addition으로 같은 drawdown을 유지하면서 CAGR를 조금 더 끌어올린 current best addition candidate도 확보한 family

로 읽는 편이 맞다.
