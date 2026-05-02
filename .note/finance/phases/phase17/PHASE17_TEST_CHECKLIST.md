# Phase 17 Test Checklist

## 목적

- Phase 17에서 구현한 structural lever 3개와
  그 representative rerun 결과가
  UI / 문서 / 허브 / 로그에서 일관되게 다시 읽히는지 확인한다.
- 이번 checklist는
  “새 candidate를 찾았는가”보다
  **current anchor를 왜 그대로 유지하는지 이해가 되는가**
  를 보는 데 초점을 둔다.

## 추천 실행 순서

1. strict annual UI에 새 contract가 보이는지 확인
2. 각 lever의 representative rerun 결과 확인
3. strategy hub / current candidate summary 확인
4. phase closeout 문서와 index 확인

## 1. strict annual UI contract 확인

- 확인 위치:
  - `Backtest > Single Strategy > Quality / Value / Quality + Value > Strict Annual`
  - `Backtest > Compare > strict annual family override`
- 확인:
  - `Retain Rejected Slots As Cash`가 보이는지
  - `Risk-Off Fallback`과 `Defensive Sleeve Tickers`가 보이는지
  - `Weighting Contract`에서
    - `Equal Weight`
    - `Rank-Tapered`
    를 고를 수 있는지
  - history / `Load Into Form`으로 다시 불러왔을 때
    위 contract들이 유지되는지

## 2. representative rerun 결과 확인

- 확인 문서:
  - [PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_PARTIAL_CASH_RETENTION_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - [PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_DEFENSIVE_SLEEVE_RISK_OFF_REPRESENTATIVE_RERUN_FIRST_PASS.md)
  - [PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase17/PHASE17_CONCENTRATION_AWARE_WEIGHTING_REPRESENTATIVE_RERUN_FIRST_PASS.md)
- 확인:
  - `partial cash retention`이
    downside는 크게 줄이지만
    `hold / blocked`로 남는다는 설명이 보이는지
  - `defensive sleeve risk-off`가
    gate는 유지하지만 `MDD`를 더 낮추지 못했다는 설명이 보이는지
  - `concentration-aware weighting`이
    gate는 유지하지만 current anchor의 `MDD`를 더 낮추지 못했다는 설명이 보이는지

## 3. strategy hub / current summary 확인

- 확인 문서:
  - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
  - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
  - [CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/CURRENT_PRACTICAL_CANDIDATES_SUMMARY.md)
- 확인:
  - `Value` current anchor가 여전히
    `Top N = 14 + psr`
    로 보이는지
  - `Quality + Value` current strongest practical point가 여전히
    `operating_margin + pcr + por + per + Top N 10`
    로 보이는지
  - structural lever 3개가 모두
    current anchor를 대체하지 못했다는 해석이 보이는지

## 4. phase closeout 문서와 index 확인

- 확인 문서:
  - [PHASE17_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase17/PHASE17_CURRENT_CHAPTER_TODO.md)
  - [PHASE17_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase17/PHASE17_COMPLETION_SUMMARY.md)
  - [PHASE17_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phases/phase17/PHASE17_NEXT_PHASE_PREPARATION.md)
  - [BACKTEST_REPORT_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/BACKTEST_REPORT_INDEX.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
- 확인:
  - Phase 17 상태가 closeout 기준으로 보이는지
  - phase17 implementation / rerun report가 index에서 바로 찾히는지
  - roadmap에 Phase 17이 `completed`로 반영됐는지
  - next-phase direction이
    `larger structural redesign` 또는
    `candidate consolidation / operator bridge`
    로 읽히는지

## 한 줄 판단 기준

- 이번 checklist는
  “새 기능이 붙었는가”를 넘어서,
  **구조 레버 3개를 실제로 열고도 current anchor가 왜 그대로 유지되는지 이해되는가**
  를 확인하는 checklist다.
