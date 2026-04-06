# Value Strict Annual Backtest Hub

## 전략

- family: `Value`
- variant: `Strict Annual`
- 관련 phase: `Phase 13`

## 한 줄 요약

`Value`는 Phase 13 strict annual family 탐색에서 가장 강한 raw 성과를 보인 family였다.

다만:

- strongest raw winner는 `MDD`가 깊고
- 더 균형 잡힌 후보는 `hold`가 남는 패턴이 반복됐다

## 지금 어떻게 읽으면 되는가

1. strongest raw winner를 먼저 본다
2. `CAGR 15 / MDD 20` exact hit를 본다
3. 왜 `hold`가 남는지 진단 문서를 같이 본다

## 대표 결과

- strongest raw winner:
  - `CAGR = 29.89%`
  - `MDD = -29.15%`
  - `promotion = real_money_candidate`
- strongest balanced exact hit:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - 문제: `promotion = hold`

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

## 실무 해석

지금 시점의 `Value Strict Annual`은:

- strict annual 3개 family 중 가장 강한 성과 축
- 다만 validation / promotion 병목이 같이 따라오는 family

로 읽는 편이 맞다.
