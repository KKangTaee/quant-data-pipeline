# Phase 16 Test Checklist

## 목적

- Phase 16에서 정리한 bounded downside refinement 결과가
  전략 허브 / report / log / phase 문서에서 일관되게 다시 읽히는지 확인한다.
- 이번 checklist는
  새 기능 구현을 검수하는 checklist가 아니라,
  **current strongest point와 lower-MDD near-miss의 관계가 문서상으로 명확한지**
  를 보는 데 초점을 둔다.

## 추천 실행 순서

1. `Value` rescue 결과 확인
2. `Quality + Value` strongest-point follow-up 확인
3. current candidate summary 확인
4. phase closeout 문서와 index 확인

## 1. Value rescue 결과 확인

- 확인 문서:
  - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
  - [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - [PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase16/PHASE16_VALUE_DOWNSIDE_RESCUE_SEARCH_SECOND_PASS.md)
- 확인:
  - current best practical point가
    - `Top N = 14 + psr`
    - `CAGR ≈ 28.13%`
    - `MDD ≈ -24.55%`
    - `real_money_candidate / paper_probation / review_required`
    로 보이는지
  - lower-MDD near-miss가
    - `Top N = 14 + psr + pfcr`
    - `CAGR ≈ 27.22%`
    - `MDD ≈ -21.16%`
    - `production_candidate / watchlist`
    로 보이는지
  - `Top N = 15 + psr + pfcr`가 gate는 회복하지만 downside rescue는 아니라는 설명이 보이는지

## 2. Quality + Value strongest-point follow-up 확인

- 확인 문서:
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
  - [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
  - [PHASE16_QUALITY_VALUE_STRONGEST_POINT_DOWNSIDE_FOLLOWUP_SECOND_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase16/PHASE16_QUALITY_VALUE_STRONGEST_POINT_DOWNSIDE_FOLLOWUP_SECOND_PASS.md)
- 확인:
  - current strongest practical point가
    - `CAGR ≈ 31.82%`
    - `MDD ≈ -26.63%`
    - `real_money_candidate / small_capital_trial / review_required`
    로 보이는지
  - `Top N = 9`와 `current_ratio -> cash_ratio`가
    lower-MDD but weaker-gate candidate로 분리되어 보이는지
  - `Ticker Benchmark = SPY`가
    same `CAGR / MDD` but `paper_probation` 대안으로 읽히는지

## 3. current candidate summary 확인

- 확인 문서:
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- 확인:
  - `Value` current best practical point와 lower-MDD near-miss 해석이 보이는지
  - `Quality + Value` current strongest practical point와 lower-MDD weaker-gate 대안 해석이 보이는지
  - 다음 phase가 structural downside improvement 쪽으로 정리돼 있는지

## 4. phase closeout 문서와 index 확인

- 확인 문서:
  - [PHASE16_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_CURRENT_CHAPTER_TODO.md)
  - [PHASE16_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_COMPLETION_SUMMARY.md)
  - [PHASE16_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase16/PHASE16_NEXT_PHASE_PREPARATION.md)
  - [BACKTEST_REPORT_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
- 확인:
  - Phase 16 상태가 closeout 기준으로 보이는지
  - new second-pass report가 index에서 바로 찾히는지
  - roadmap에 Phase 16이 completed로 반영됐는지

## 한 줄 판단 기준

- 이번 checklist는
  “같은 bounded 범위를 더 돌릴 것인가”가 아니라,
  **bounded refinement가 충분히 정리됐고 다음 phase 질문이 구조 문제로 넘어갔는지**
  를 확인하는 checklist다.
