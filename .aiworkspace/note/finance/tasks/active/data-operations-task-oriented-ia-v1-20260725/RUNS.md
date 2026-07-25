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

## 2026-07-26 — Contextual Reference Help Removal

- Data Operations 상단 `Reference help · Ingestion`은 목적 카드와 중복되어
  `render_ingestion_page()`의 import와 호출만 제거했다.
- canonical Reference Center, Ingestion catalog item, section/action/form/dispatcher는
  변경하지 않았다.
- source contract를 RED로 확인한 뒤 minimal removal로 GREEN을 확인했다.
- focused Python 60개와 `page.py` compile, `git diff --check`를 통과했다.
- Reference 확장 회귀에서 catalog owner와 page renderer를 동일시하던 stale
  contract를 발견해, 6개 catalog는 유지하면서 Market Research와 Data Operations를
  catalog-only surface로 명시했다.
- Data Operations, Ingestion boundary, Reference contextual/catalog 확장 회귀
  85개를 최종 통과했다.
- branch finishing용 전체 `unittest discover -s tests`는 1,895개를 실행했고
  `11 failures + 294 errors`로 종료됐다. errors 대부분은 suite-wide import
  순서에서 발생하는 기존 Streamlit `DeltaGeneratorSingleton instance already
  exists` 수명 문제이며, failures는 기존 Backtest / Practical Validation /
  Futures Macro / Sentiment contract drift다. 이 후속 변경 소유 파일 밖이므로
  merge·push하지 않고 feature-owned 85개 격리 회귀를 완료 기준으로 유지한다.
- actual Browser QA:
  - 1280×720: contextual help 비노출, 5개 section 유지, document overflow 0
  - 420×900: contextual help 비노출, 첫 purpose card 노출, document overflow 0
  - console warning 1건은 QA용 서버 재시작 시점의 WebSocket 종료 기록이며
    재시작 후 app error는 없었다.
- collector write action은 실행하지 않았고 QA 이미지는 generated artifact로 남겼다.

## 2026-07-26 — Heading Hierarchy And Advanced Closed Entry

- 설계 / 계획 commit:
  - `877749a32` 제목 계층·직접 진입/집중 진입 contract
- TDD 구현 commit:
  - `6c7aa79a1` selector-equivalent 제목 제거와 focus-only expander 규칙
  - `71fee4264` 섹션 이탈 시 sticky action focus 초기화
- RED:
  - secondary view 4개 반복 `subheader`
  - `should_expand_action` 부재
  - operational 첫 두 expander의 `default=True`
  - Advanced 이탈 뒤 focused action 잔존
- GREEN:
  - `tests.test_data_operations_workflows`
  - `tests.test_ingestion_module_split_contracts`
  - 26개 통과
- active action 비파괴 audit:
  - active 30 / workflow ownership missing 0
  - renderer missing 0 / dispatcher missing 0 / guide missing 0
  - `db_write` 26개 모두 explicit button 아래 scheduling
  - button 밖 scheduling 0 / `read_only` diagnosis 4개
- 최종 회귀:
  - Data Operations / Ingestion boundary / Reference 확장 suite 91개 통과
  - 변경 Python 6개 `py_compile` 통과
  - `git diff --check` 통과
- actual Browser QA:
  - 1280×720: `문제 복구` 반복 heading 없음, Advanced open details 0,
    document horizontal overflow 0
  - 420×900: Advanced open details 0, document horizontal overflow 0
  - console warning / error 0
- collector / import / diagnosis 실행 버튼은 누르지 않았다.
- QA 이미지는 `qa_data_operations_advanced_closed.png`,
  `qa_data_operations_advanced_closed_mobile.png` local artifact로만 남겼다.
