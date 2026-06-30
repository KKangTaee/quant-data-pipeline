# Backtest Boundary Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate Backtest UI, service, runtime runner, and validation decision ownership through seven small QA-and-commit stages.

**Architecture:** Keep existing public module paths working while extracting small, tested boundary modules. Each stage avoids behavior or threshold changes and commits after focused tests and compile checks pass.

**Tech Stack:** Python, Streamlit, pandas, pytest/unittest, finance package runtime services.

---

### Task 1: Shared State And Formatting Boundary

**Files:**
- Create: `app/web/backtest_state.py`
- Create: `app/web/backtest_formatters.py`
- Modify: `app/web/backtest_page.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

- [ ] Add a failing test that imports the new state and formatter modules.
- [ ] Extract workflow state helpers without changing rendered navigation.
- [ ] Run focused test, compile Backtest web modules, and commit.

### Task 2: Single Strategy Payload Boundary

**Files:**
- Create: `app/services/backtest_single_payload.py`
- Modify: `app/web/backtest_single_runner.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

- [ ] Add a failing test for service-owned Single Strategy payload normalization.
- [ ] Route `_handle_backtest_run` through the new service helper.
- [ ] Run focused test, compile Single Strategy modules, and commit.

### Task 3: Portfolio Mix Builder Service Boundary

**Files:**
- Create: `app/services/backtest_portfolio_mix_readiness.py`
- Modify: `app/web/backtest_compare.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

- [ ] Add a failing test for service-owned weighted role flag calculation.
- [ ] Move pure role flag logic out of the Streamlit compare module.
- [ ] Run focused test, compile compare modules, and commit.

### Task 4: Practical Validation Policy Boundary

**Files:**
- Create: `app/services/backtest_validation_status_policy.py`
- Modify: `app/services/backtest_practical_validation_modules.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

- [ ] Add a failing test for shared validation status ranking and normalization.
- [ ] Move status sets/rank/normalization helpers into the policy module.
- [ ] Run focused test, compile validation modules, and commit.

### Task 5: Final Review Gate Boundary

**Files:**
- Create: `app/services/backtest_final_review_policy.py`
- Modify: `app/services/backtest_selected_route_preflight.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

- [ ] Add a failing test for service-owned selected-route policy extraction.
- [ ] Move packet-to-preflight mapping into the Final Review policy module.
- [ ] Run focused test, compile Final Review services, and commit.

### Task 6: Runtime Runner Catalog Boundary

**Files:**
- Create: `app/runtime/backtest_runner_catalog.py`
- Modify: `app/services/backtest_execution.py`
- Modify: `app/services/backtest_compare_catalog.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

- [ ] Add a failing test for runtime strategy ownership metadata.
- [ ] Use the catalog in service entrypoints for known strategy validation and metadata.
- [ ] Run focused test, compile runtime/services, and commit.

### Task 7: Documentation And Closeout

**Files:**
- Modify: `.aiworkspace/note/finance/docs/architecture/SCRIPT_STRUCTURE_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-boundary-refactor-v1/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-boundary-refactor-v1/RUNS.md`

- [ ] Add durable notes for the new Backtest boundary modules.
- [ ] Run full focused QA for the changed Backtest files.
- [ ] Commit documentation closeout.
