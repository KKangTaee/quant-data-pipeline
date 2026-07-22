# Practical Validation Final Review Route Fix V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. This workspace session executes inline; subagent dispatch is disabled.

**Goal:** `저장하고 Final Review로 이동` 한 번으로 같은 validation을 최대 한 번 저장하고, root workflow shell을 거쳐 인계한 후보의 Final Review를 연다.

**Architecture:** Practical Validation fragment callback은 replay와 local selection action만 선소비한다. Persistence/navigation intent는 fragment 본문에서 처리하고 full-app rerun으로 승격한다. Validation persistence는 stable `validation_id` 기준 idempotent save를 사용하며, handoff는 현재 Final Review React selector가 소비하는 active candidate key를 함께 설정한다.

**Tech Stack:** Python 3.12, Streamlit 1.57, Streamlit custom component v1, append-only JSONL registry, pytest, React static component.

## Global Constraints

- 기존 registry JSONL 행은 삭제하거나 rewrite하지 않는다.
- run history, saved JSONL, generated screenshot은 stage하지 않는다.
- provider 수집, replay 계산, Final Review Gate 의미는 변경하지 않는다.
- React는 presentation intent만 만들고 persistence와 route는 Python이 소유한다.
- run/job/row 중심 운영 진단 패널을 추가하지 않는다.
- 사용자가 만든 dirty worktree 변경을 되돌리지 않는다.

## 이걸 하는 이유?

현재 GTAA validation은 저장에 성공했지만 fragment callback이 navigation intent를 먼저 소비해 root route owner가 실행되지 않았다. 사용자의 반복 클릭으로 같은 JSON row가 3번 append됐다. 저장과 이동을 하나의 실제 사용자 action으로 종결하고, 중복 append가 다시 발생하지 않게 해야 한다.

---

### Task 1: Persistence Intent Lifecycle Contract

**Files:**
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`

**Interfaces:**
- Produces: `_PRACTICAL_VALIDATION_FRAGMENT_CALLBACK_ACTIONS: frozenset[str]`
- Consumes: `_consume_practical_validation_decision_workspace_intent(..., rerun_scope="fragment")`

- [ ] **Step 1: Write the failing callback ownership test**

```python
def test_fragment_callback_keeps_persistence_and_navigation_in_fragment_body(self) -> None:
    from app.web.backtest_practical_validation import page

    actions = page._PRACTICAL_VALIDATION_FRAGMENT_CALLBACK_ACTIONS
    self.assertIn("run_replay", actions)
    self.assertIn("run_resolution_action", actions)
    self.assertNotIn("save_audit_only", actions)
    self.assertNotIn("save_and_move", actions)
```

- [ ] **Step 2: Run RED test**

Run: `.venv/bin/python -m pytest -q tests/test_backtest_practical_validation_decision_workspace.py::PracticalValidationDecisionWorkspaceTests::test_fragment_callback_keeps_persistence_and_navigation_in_fragment_body`

Expected: FAIL because `_PRACTICAL_VALIDATION_FRAGMENT_CALLBACK_ACTIONS` does not exist and the current inline callback set includes both persistence actions.

- [ ] **Step 3: Implement the minimal callback action boundary**

```python
_PRACTICAL_VALIDATION_FRAGMENT_CALLBACK_ACTIONS = frozenset(
    {
        "run_replay",
        "select_recheck_mode",
        "run_resolution_action",
    }
)
```

Use this constant as the decision component callback `allowed_actions`. Keep fragment-body intent consumption and the existing explicit app rerun for `save_and_move`.

- [ ] **Step 4: Run focused GREEN tests**

Run: `.venv/bin/python -m pytest -q tests/test_backtest_practical_validation_decision_workspace.py`

Expected: all Practical Validation decision workspace tests pass.

---

### Task 2: Validation ID Idempotency

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/backtest_practical_validation.py`

**Interfaces:**
- Changes: `save_practical_validation_result(result: dict[str, Any]) -> bool`
- Consumes: `load_practical_validation_results(limit=None)`
- Returns: `True` only when a new JSONL row is appended; `False` when the stable `validation_id` already exists.

- [ ] **Step 1: Write the failing idempotency test**

```python
def test_practical_validation_save_is_idempotent_by_validation_id(self) -> None:
    result = {"validation_id": "validation-once", "selection_source_id": "source-once"}
    with (
        patch.object(service, "load_practical_validation_results", side_effect=[[], [result]]),
        patch.object(service, "append_practical_validation_result") as append,
    ):
        self.assertTrue(service.save_practical_validation_result(result))
        self.assertFalse(service.save_practical_validation_result(result))
    append.assert_called_once_with(result)
```

- [ ] **Step 2: Run RED test**

Run: `.venv/bin/python -m pytest -q tests/test_service_contracts.py::PracticalValidationServiceContractTests::test_practical_validation_save_is_idempotent_by_validation_id`

Expected: FAIL because the loader is not imported, the function returns `None`, and both calls append.

- [ ] **Step 3: Implement minimal idempotent save**

```python
def save_practical_validation_result(result: dict[str, Any]) -> bool:
    row = dict(result or {})
    validation_id = str(row.get("validation_id") or "").strip()
    if validation_id and any(
        str(existing.get("validation_id") or "").strip() == validation_id
        for existing in load_practical_validation_results(limit=None)
    ):
        return False
    append_practical_validation_result(row)
    return True
```

Set `PracticalValidationFinalReviewHandoff.persisted` from the boolean return value instead of always setting it to `True`.

- [ ] **Step 4: Run focused GREEN tests**

Run: `.venv/bin/python -m pytest -q tests/test_service_contracts.py -k 'practical_validation and (handoff or save)'`

Expected: idempotency and existing handoff contracts pass without writing the protected registry.

---

### Task 3: Current Final Review Candidate Handoff

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/backtest_practical_validation/page.py`

**Interfaces:**
- Produces session state: `final_review_active_decision_brief_source_id = "practical_validation_result:<validation_id>"`
- Preserves compatibility state: `final_review_source_selected`, `final_review_confirmed_candidate_key`

- [ ] **Step 1: Extend the existing handoff test to fail on the current selector key**

```python
stable_key = "practical_validation_result:validation-new"
self.assertEqual(
    fake_st.session_state["final_review_active_decision_brief_source_id"],
    stable_key,
)
```

- [ ] **Step 2: Run RED test**

Run: `.venv/bin/python -m pytest -q tests/test_service_contracts.py::BacktestRuntimeContractTests::test_practical_validation_save_and_move_confirms_new_validation_key`

Expected: FAIL with missing `final_review_active_decision_brief_source_id`.

- [ ] **Step 3: Set the current selector key in the successful handoff**

```python
st.session_state["final_review_active_decision_brief_source_id"] = validation_key
```

Keep the root-owned `backtest_requested_panel` request and explicit `scope="app"` rerun.

- [ ] **Step 4: Run focused GREEN tests**

Run: `.venv/bin/python -m pytest -q tests/test_service_contracts.py::BacktestRuntimeContractTests::test_practical_validation_save_and_move_confirms_new_validation_key tests/test_backtest_practical_validation_decision_workspace.py`

Expected: all selected tests pass.

---

### Task 4: Lifecycle Regression And Browser QA

**Files:**
- Modify: focused test module if lifecycle gap requires one additional assertion
- Create during QA, then delete: `.codex_practical_validation_final_route_diagnostic.py`
- Create generated artifact only: `practical-validation-final-review-route-fix-v1-qa.png`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: production Practical Validation component adapter, Python handler, and root route initialization
- Produces: browser evidence for one-click / one-save / Final Review route arrival without protected JSONL writes

- [ ] **Step 1: Run focused and boundary regression**

Run:

```bash
.venv/bin/python -m pytest -q \
  tests/test_backtest_practical_validation_decision_workspace.py \
  tests/test_backtest_refactor_boundaries.py \
  tests/test_service_contracts.py -k 'practical_validation and (handoff or save or fragment)'
```

Expected: all selected tests pass.

- [ ] **Step 2: Run isolated actual interaction QA**

Use the production component and adapter with an in-memory persistence counter. Verify:

- save button is enabled
- one click changes save count `0 -> 1`
- an outside-fragment marker proves full-app rerun
- visible active stage becomes `Final Review`
- active candidate key is `practical_validation_result:<validation_id>`
- console warning/error count is zero

- [ ] **Step 3: Capture one screenshot and remove the temporary app**

Save `practical-validation-final-review-route-fix-v1-qa.png` as a generated, uncommitted artifact. Stop the temporary Streamlit process and remove the diagnostic app.

- [ ] **Step 4: Run code verification**

Run:

```bash
.venv/bin/python -m py_compile \
  app/services/backtest_practical_validation.py \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_final_review/page.py
git diff --check
```

Expected: compile and diff checks pass.

---

### Task 5: Documentation Closeout And Commit

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-final-review-route-fix-v1-20260722/*.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: active task index/manifest files when required by the current docs contract

**Interfaces:**
- Consumes: verified implementation and QA evidence
- Produces: durable current-state handoff and one coherent implementation commit

- [ ] **Step 1: Record RED/GREEN and Browser evidence**

Update task status to overall `3/3차` only after the actual lifecycle QA succeeds. Record the existing three duplicate rows as preserved historical artifacts, not cleaned data.

- [ ] **Step 2: Sync durable flow and root handoff docs**

Document that persistence/navigation intents leave the fragment callback, validation save is stable-id idempotent, and Final Review opens the handed-off candidate. Keep root logs to 3-5 concise lines.

- [ ] **Step 3: Review and stage only owned files**

Run `git status --short`, `git diff --check`, and inspect the staged diff. Exclude registries, saved JSONL, run history, screenshots, and unrelated user files.

- [ ] **Step 4: Commit**

Commit message: `수정: Practical Validation Final Review 인계 복구`
