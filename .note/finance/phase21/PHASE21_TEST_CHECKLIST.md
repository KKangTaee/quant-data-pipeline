# Phase 21 Test Checklist

## 목적

- 이번 checklist는 `Phase 21` integrated deep validation이
  실제로 같은 frame에서 다시 검증되고 있는지 확인하는 문서다.
- UI polish보다
  **rerun 대상, validation frame, 결과 기록, candidate decision이 일관되게 정리되는가**
  를 보는 checklist다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 주요 체크 항목이 모두 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 문서나 handoff에 짧게 남긴다.

## 추천 실행 순서

1. validation frame 정의 확인
2. family별 integrated rerun 결과 확인
3. portfolio bridge validation 확인
4. 문서와 closeout 확인

## 1. validation frame 정의 확인

- 확인 위치:
  - [FINANCE_TERM_GLOSSARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_TERM_GLOSSARY.md)
  - [PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_INTEGRATED_DEEP_BACKTEST_VALIDATION_PLAN.md)
  - [PHASE21_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_CURRENT_CHAPTER_TODO.md)
  - [PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_VALIDATION_FRAME_DEFINITION_FIRST_WORK_UNIT.md)
- 체크 항목:
  - [ ] `Validation Frame`이 "여러 후보를 같은 조건에서 비교하기 위해 미리 고정해 두는 검증 기준표"라는 뜻으로 이해되는지
  - [ ] 이번 phase에서 다시 볼 family와 candidate 범위가 문서에 분명히 적혀 있는지
  - [ ] 공통 기간(`2016-01-01 ~ 2026-04-01`)과 공통 universe frame(`US Statement Coverage 100`, `Historical Dynamic PIT Universe`)이 분명히 적혀 있는지
  - [ ] current anchor / lower-MDD alternative / portfolio bridge가 무엇인지 용어 설명이 충분한지
  - [ ] family별 rerun report 이름과 strategy log entry naming rule이 먼저 정리되어 있는지
  - [ ] rerun 결과를 어디에 남길지(strategy hub / backtest log / candidate summary) 기준이 보이는지

## 2. family별 integrated rerun 결과 확인

- 확인 위치:
  - 먼저 아래 archive 안내 문서를 연다.
    - [phase21/README.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/README.md)
  - 그다음 family별 rerun report 3개를 확인한다.
    - [Value rerun report](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
    - [Quality rerun report](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
    - [Quality + Value rerun report](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/phase21/PHASE21_QUALITY_VALUE_ANCHOR_AND_ALTERNATIVE_RERUN_FIRST_PASS.md)
  - 같은 결론이 전략별 장기 문서에도 반영되었는지 확인하려면 아래 문서를 본다.
    - [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL.md)
    - [VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
    - [QUALITY_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL.md)
    - [QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_STRICT_ANNUAL_BACKTEST_LOG.md)
    - [QUALITY_VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL.md)
    - [QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/backtest_reports/strategies/QUALITY_VALUE_STRICT_ANNUAL_BACKTEST_LOG.md)
- 읽는 방법:
  - `phase21/README.md`는 전체 목차다.
  - family별 rerun report는 이번 Phase 21에서 실제로 다시 돌린 결과다.
  - strategy hub와 strategy backtest log는 이번 결과가 장기 기록에 제대로 반영되었는지 확인하는 보조 위치다.
- 유지 / 교체 / 보류 판단 기준:
  - `유지`:
    - 현재 대표 후보가 여전히 가장 안정적인 기준점일 때 선택한다.
    - 확인할 것:
      - `CAGR / MDD`가 여전히 경쟁력 있는지
      - `Promotion / Shortlist / Deployment`가 대안보다 약해지지 않는지
      - `Validation / Rolling Review / Out-of-Sample Review`가 크게 나빠지지 않는지
      - report의 `해석`, annual 문서의 `실무해석`, backtest log의 `다음 액션`이 current anchor 유지로 읽히는지
  - `교체`:
    - 대안이 현재 대표 후보보다 명확히 좋아졌고, 실전 gate도 같거나 더 강할 때 선택한다.
    - 예:
      - `MDD`가 낮아졌는데 `CAGR` 손실이 과하지 않음
      - `Promotion / Shortlist / Deployment`가 current anchor와 같거나 더 좋음
      - validation이 약해지지 않음
      - report가 replacement 또는 actual rescue로 해석함
  - `보류`:
    - 대안이 일부 지표는 좋아 보이지만 아직 대표 후보를 바꾸기에는 부족할 때 선택한다.
    - 예:
      - `MDD`는 낮지만 `Promotion`이나 `Shortlist`가 약해짐
      - `CAGR` 손실이 큼
      - `Deployment = blocked` 또는 `hold`가 남음
      - report가 near-miss, comparison-only, weaker-gate alternative로 해석함
  - 즉 이 항목은 사용자가 원자료를 새로 계산하라는 뜻이 아니라,
    각 report와 annual 문서의 해석이 위 기준에 맞게 충분히 적혀 있는지 확인하는 항목이다.
- 체크 항목:
  - [ ] `Value` current anchor와 lower-MDD alternative rerun 결과를 같은 frame에서 비교할 수 있는지
  - [ ] `Quality` current anchor와 alternative rerun 결과를 같은 frame에서 비교할 수 있는지
  - [ ] `Quality + Value` strongest point와 alternative rerun 결과를 같은 frame에서 비교할 수 있는지
  - [ ] 결과를 보고 유지 / 교체 / 보류 판단이 가능한 정도로 해석이 적혀 있는지

## 3. portfolio bridge validation 확인

- 확인 위치:
  - `Compare & Portfolio Builder`
  - weighted portfolio / saved portfolio rerun report
- 체크 항목:
  - [ ] representative weighted portfolio rerun이 single-strategy rerun과 같은 phase frame에서 읽히는지
  - [ ] representative bridge가 `Load Recommended Candidates -> near-equal weighted bundle -> saved portfolio replay` 흐름으로 분명히 고정되어 있는지
  - [ ] saved portfolio replay 결과가 `CAGR / MDD / End Balance` exact match 기준으로 재현되는지
  - [ ] portfolio bridge가 다음 phase의 메인 대상이 될지 판단할 재료가 충분한지

## 4. 문서와 closeout 확인

- 확인 문서:
  - [PHASE21_CURRENT_CHAPTER_TODO.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_CURRENT_CHAPTER_TODO.md)
  - [PHASE21_COMPLETION_SUMMARY.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_COMPLETION_SUMMARY.md)
  - [PHASE21_NEXT_PHASE_PREPARATION.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/phase21/PHASE21_NEXT_PHASE_PREPARATION.md)
  - [MASTER_PHASE_ROADMAP.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/MASTER_PHASE_ROADMAP.md)
  - [FINANCE_DOC_INDEX.md](/Users/taeho/Project/quant-data-pipeline/.note/finance/FINANCE_DOC_INDEX.md)
- 체크 항목:
  - [ ] phase 상태가 현재 실제 진행 상태와 맞는지
  - [ ] 새 phase21 plan / TODO / closeout / next-phase 문서를 index에서 바로 찾을 수 있는지
  - [ ] next-phase preparation이 phase22 이후 방향을 이해하기 쉽게 정리하는지

## 한 줄 판단 기준

- 이번 checklist는
  **"이제 current annual strict 후보와 portfolio bridge를 같은 검증 frame에서 다시 보고, 다음 확장 phase로 넘어갈 만큼 판단이 정리됐는가"**
  를 확인하는 문서다.
