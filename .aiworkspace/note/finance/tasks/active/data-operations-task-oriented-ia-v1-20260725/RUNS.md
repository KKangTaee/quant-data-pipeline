# Runs

## 2026-07-25 — Design Intake

- Read `finance-task-intake` task document contract.
- Re-read the Data Operations product audit.
- Reviewed related completed Ingestion structure, action unification,
  module split, and UX/data-quality task plans and statuses.
- Confirmed the new task supersedes layout-only cleanup while preserving
  the existing action registry and execution boundary.

## 2026-07-26 — Implementation And QA

- TDD로 active action 30개 workflow ownership, shared action identity,
  advanced section routing, history projection, pending section focus를 고정했다.
- 구현 commit:
  - `2f4775f5d` workflow catalog
  - `82a146af1` 목적별 준비 화면
  - `6b10f5647` 공식 파일 / 복구 / advanced focus
  - `4ac867f90` compact history
  - `351f0feeb` five-section landing replacement
  - `27beeb768` Streamlit pending-state focus fix
- 검증:
  - `py_compile` for `app/web/ingestion/page.py`, sections, navigation,
    workflows, views
  - focused unittest 59개 통과
  - broad `tests.test_service_contracts` 포함 924개를 실행했고, Data Operations
    관련 회귀는 통과했다. 전체 모듈은 기존 문서에 기록된 Backtest / Practical
    Validation / AAII / Futures Macro / Sentiment 계약 drift 18건
    (`11 failures + 7 errors`)과 동일한 baseline으로 종료됐다.
  - `git diff --check` 통과
- actual Browser QA:
  - 1280×720, 420×900에서 document horizontal overflow `0`
  - 목적 카드 → Market Research steps → 시장 심리 advanced form 자동 확장
  - 공식 파일, 문제 복구, 실행 이력 section 전환
  - Runtime/Build, recent log, failure CSV, absolute history path 비노출
  - 최초 click에서 발견한 Streamlit widget-state mutation 오류는 RED test와
    pending-state 방식으로 수정 후 동일 경로 재검증
- 실제 collector write action은 실행하지 않았다.
- registry, saved JSONL, run history는 수정·stage하지 않았다.
