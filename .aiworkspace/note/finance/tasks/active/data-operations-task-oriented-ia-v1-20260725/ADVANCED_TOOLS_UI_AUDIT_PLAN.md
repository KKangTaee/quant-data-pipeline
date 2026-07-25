# Data Operations Advanced Tools UI Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 중복된 section 제목을 제거하고 고급 도구 직접 진입 시 모든 도구를 닫은 상태로 보여주며, 수집·진단 실행 경로의 기능 위험을 비파괴적으로 점검한다.

**Architecture:** View-level heading만 제거해 기존 작업군 계층은 유지한다. `should_expand_action(focused_action, *actions)` 순수 함수를 `sections.py`에 두어 직접 진입은 모두 닫고 action-focused handoff만 펼치도록 operational/manual section이 같은 규칙을 사용한다. 수집 기능 진단은 registry, workflow ownership, renderer, dispatcher, explicit button scheduling contract를 정적·자동 테스트로 확인하며 실제 provider/DB write action은 실행하지 않는다.

**Tech Stack:** Python 3, Streamlit, unittest, in-app Browser QA

## Global Constraints

- 모든 write action은 사용자 explicit click으로만 시작한다.
- `Ingestion -> DB -> Loader -> UI` 경계를 유지한다.
- current snapshot과 PIT evidence의 의미를 바꾸지 않는다.
- registry, saved setup, run history를 수정하지 않는다.
- Browser QA에서 collector 실행 버튼을 누르지 않는다.

---

### Task 1: 제목 계층과 expander 초기 상태 contract

**Files:**
- Modify: `tests/test_data_operations_workflows.py`
- Modify: `app/web/ingestion/sections.py`
- Modify: `app/web/ingestion/views/imports.py`
- Modify: `app/web/ingestion/views/recovery.py`
- Modify: `app/web/ingestion/views/history.py`
- Modify: `app/web/ingestion/views/advanced.py`

**Interfaces:**
- Consumes: `focused_action: str | None`
- Produces: `should_expand_action(focused_action: str | None, *actions: str) -> bool`

- [ ] **Step 1: Write failing tests**

```python
def test_secondary_views_do_not_repeat_selected_section_title():
    # Four secondary view sources must not contain their selector-equivalent subheader.

def test_advanced_tools_are_closed_without_action_focus():
    assert should_expand_action(None, "daily_market_update") is False

def test_advanced_tools_open_only_matching_action_focus():
    assert should_expand_action("daily_market_update", "daily_market_update") is True
    assert should_expand_action("metadata_refresh", "daily_market_update") is False
```

- [ ] **Step 2: Run RED tests**

Run: `.venv/bin/python -m unittest tests.test_data_operations_workflows -v`

Expected: FAIL because duplicate subheaders and `should_expand_action` still exist only as nested default-aware helpers.

- [ ] **Step 3: Implement the minimal UI change**

```python
def should_expand_action(
    focused_action: str | None,
    *actions: str,
) -> bool:
    return focused_action is not None and focused_action in actions
```

Remove the four selector-equivalent `st.subheader(...)` calls and use the pure helper for every Advanced expander. Do not change captions, form inputs, buttons, dispatchers, or job parameters.

- [ ] **Step 4: Run focused tests**

Run: `.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts -v`

Expected: PASS.

### Task 2: Advanced collection contract diagnosis

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RISKS.md`

**Interfaces:**
- Consumes: active action registry, workflow ownership, section source, dispatcher source, job guides
- Produces: confirmed protections, current issues, follow-up priorities

- [ ] **Step 1: Verify active action coverage**

Run a read-only script asserting every active action is owned by a workflow, rendered in `sections.py`, supported by `dispatcher.py`, and described by `JOB_GUIDE`.

Expected: 30 active actions, zero missing entries.

- [ ] **Step 2: Verify execution safety contracts**

Inspect each `db_write` action for an explicit Streamlit button and scheduled-job path, and verify diagnostic actions return `write_behavior="read_only"`.

Expected: no collection starts during initial render; one scheduled job at a time; diagnostic results write no finance data rows.

- [ ] **Step 3: Record issues without expanding implementation scope**

Record that collapsed Streamlit expanders still evaluate their bodies, focused action state may remain sticky across reruns, and `sections.py` depends on dynamic globals from `page.py`. Keep these as performance/maintainability follow-ups unless a correctness failure is found.

### Task 3: Regression and browser verification

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/data-operations-task-oriented-ia-v1-20260725/RUNS.md`
- Create locally only: `qa_data_operations_advanced_closed.png`

**Interfaces:**
- Consumes: completed Task 1 and Task 2
- Produces: test evidence, desktop/mobile visual evidence, final handoff

- [ ] **Step 1: Run the Data Operations regression suite**

Run: `.venv/bin/python -m unittest tests.test_data_operations_workflows tests.test_ingestion_module_split_contracts tests.test_service_contracts.BoundaryContractHardeningTests tests.test_reference_contextual_help tests.test_reference_center`

Expected: all feature-specific tests PASS.

- [ ] **Step 2: Run static checks**

Run: `.venv/bin/python -m py_compile app/web/ingestion/sections.py app/web/ingestion/views/imports.py app/web/ingestion/views/recovery.py app/web/ingestion/views/history.py app/web/ingestion/views/advanced.py`

Run: `git diff --check`

Expected: both PASS.

- [ ] **Step 3: Verify in the in-app browser**

Open Data Operations, confirm `문제 복구` has no repeated page title, then open `고급 도구` and confirm every top-level expander is closed at desktop and 420px width. Do not click any run/import button.

- [ ] **Step 4: Update task documentation and commit**

Stage only the implementation, focused tests, and active task documentation. Exclude registries, saved files, run history, research bundles, and QA screenshots.

Commit message: `Data Operations 제목과 고급 도구 초기 상태 정리`
