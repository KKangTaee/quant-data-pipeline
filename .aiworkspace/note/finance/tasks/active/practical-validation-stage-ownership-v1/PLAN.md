# Practical Validation Stage Ownership V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flow4의 검증 카테고리, 데이터 보강, Final Review handoff 경계를 다시 분리해 사용자가 Practical Validation에서 무엇을 검증하고 무엇을 수집해야 하는지 바로 이해하게 만든다.

**Architecture:** React는 표시만 담당하고, 검증 stage role / visibility / data action 판단은 기존 Python service read model에서 만든다. 새 ingestion, DB schema, provider fetch path는 만들지 않고 기존 `Ingestion -> DB -> Loader -> Service -> UI` 경계를 유지한다.

**Tech Stack:** Python service read model, Streamlit UI, existing React Streamlit component, unittest contract tests, finance docs.

---

## 이걸 하는 이유?

Flow4에서 실제 검증 모듈은 줄지 않았지만 `REVIEW`가 모두 `Final Review review`로 해석되고, REVIEW-only 카테고리가 PV visible board에서 숨겨져 사용자에게 검증이 2개만 남은 것처럼 보인다. 이 작업은 검증 자체를 줄이거나 새 엔진을 만드는 것이 아니라, 1단계 데이터 / 2단계 실용성 / 3단계 최종 판단 / Monitoring 추적의 소유권을 read model과 UI에 명확히 드러내기 위한 것이다.

## 전체 단계

### Task 1: Active Task / Contract 정리

**Files:**
- Create: `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/DESIGN.md`
- Create: `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/STATUS.md`
- Create: `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/RUNS.md`
- Create: `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/NOTES.md`
- Create: `.aiworkspace/note/finance/tasks/active/practical-validation-stage-ownership-v1/RISKS.md`

- [x] **Step 1: Read order 확인**

Read: `INDEX.md`, `ROADMAP.md`, `PROJECT_MAP.md`, `SCRIPT_STRUCTURE_MAP.md`, `BACKTEST_UI_FLOW.md`, `PORTFOLIO_SELECTION_FLOW.md`, relevant active task tests.

- [x] **Step 2: Stage ownership matrix 작성**

Document Stage 1 / Practical Validation / Final Review / Monitoring ownership and non-goals.

### Task 2: TDD Contract Test

**Files:**
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write failing tests**

Add tests proving REVIEW-only Practical Validation categories remain visible with a PV role, and Final Review copy no longer describes every REVIEW as Final Review work.

- [ ] **Step 2: Run focused tests to verify RED**

Run: `.venv/bin/python -m unittest tests.test_service_contracts.PracticalValidationServiceContractTests.test_practical_validation_flow4_keeps_review_only_categories_visible_with_stage_role -v`

Expected: FAIL because current read model hides REVIEW-only groups and lacks `review_role`.

### Task 3: Read Model Role Taxonomy

**Files:**
- Modify: `app/services/backtest_practical_validation_workspace.py`
- Modify: `app/services/backtest_practical_validation_modules.py`

- [ ] **Step 1: Add minimal role taxonomy**

Create Python read-model fields only:
- `review_role`
- `review_role_label`
- `stage_decision_surface`
- `pv_visibility`
- `final_review_visibility`
- `monitoring_visibility`

- [ ] **Step 2: Keep REVIEW-only applied category visible**

Change `visible_in_practical_validation` to keep applied REVIEW-only groups visible while still excluding downstream-only handoff groups.

- [ ] **Step 3: Re-run focused tests**

Run the focused unittest and ensure GREEN.

### Task 4: Flow4 / Final Review UI Copy

**Files:**
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/backtest_final_review/page.py`

- [ ] **Step 1: Flow4 category board renders REVIEW cards**

Remove the blanket exclusion of REVIEW cards and display role labels such as `2단계 실용성 주의`, `최종 판단 참고`, `Monitoring 추적`.

- [ ] **Step 2: Data action language clarify provider**

Explain provider as external official/provider data and show what the collection button gathers.

- [ ] **Step 3: Final Review main copy narrow**

Describe Final Review as profitability / benchmark / candidate comparison / final monitoring-candidate decision, with PV evidence as read-only appendix.

### Task 5: Docs / QA

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Update task docs in this folder.

- [ ] **Step 1: Durable docs sync**

Update only the durable flow/stage ownership statements that changed.

- [ ] **Step 2: Verification**

Run:
- focused unittest
- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_workspace.py app/services/backtest_practical_validation_modules.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py app/web/backtest_final_review/page.py`
- `git diff --check`
- Browser QA screenshot

### Task 6: Commit

**Files:**
- Stage only code, tests, docs, task records.

- [ ] **Step 1: Review diff**

Ensure generated screenshots, run history, local artifacts are not staged.

- [ ] **Step 2: Commit**

Commit message: `Practical Validation 단계별 검증 소유권 정리`
