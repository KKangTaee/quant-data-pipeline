# Backtest Level2 Fragment Handoff Fix V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GTAA를 포함한 Level1 단일 전략 결과에서 `후보로 저장하고 Level2로 이동`을 한 번 누르면 후보 source를 한 번만 저장하고 즉시 Practical Validation으로 이동한다.

**Architecture:** 결과 React 컴포넌트의 intent를 `on_change` callback에서 선소비하지 않는다. Streamlit fragment rerun 본문에서 반환 intent를 검증·소비한 뒤 `st.rerun(scope="app")`으로 승격하여 root의 `init_backtest_state()`가 `backtest_requested_panel`을 Practical Validation stage로 반영하게 한다.

**Tech Stack:** Python 3.12, Streamlit 1.57, Streamlit custom component v1, pytest, React static component.

## Global Constraints

- 후보 source append와 `backtest_requested_panel` 계약은 변경하지 않는다.
- registry JSONL과 run history는 테스트 또는 QA 산출물로 stage하지 않는다.
- React 계산·gate·저장 책임을 늘리지 않는다.
- 기존 사용자가 만든 dirty worktree 변경을 되돌리지 않는다.

## 이걸 하는 이유?

현재 버튼 클릭은 Python handler까지 도달하지만 fragment callback 재실행으로 끝난다. 후보 저장 뒤 상단 workflow shell이 Level2 이동 요청을 소비하지 못해 사용자는 클릭이 실패한 것으로 느끼고, 반복 클릭 시 append-only source가 중복 저장될 위험이 있다.

---

### Task 1: Fragment Intent Regression Contract

**Files:**
- Modify: `tests/test_backtest_analysis_result_workspace.py`
- Modify: `app/web/backtest_analysis_result_workspace.py`

**Interfaces:**
- Consumes: `render_backtest_analysis_result_workspace(is_running: bool = False) -> None`
- Produces: custom component 반환 intent를 fragment 본문에서 한 번 소비하고 full-app rerun을 요청하는 adapter 계약

- [x] **Step 1: Write the failing test**

```python
def test_result_component_defers_intent_consumption_to_fragment_body() -> None:
    # Render with a successful current workspace and a component intent.
    # Assert the component receives no on_change callback.
    # Assert the returned intent is consumed once and requests scope="app".
```

- [x] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py::test_result_component_defers_intent_consumption_to_fragment_body -q`

Expected: FAIL because the current adapter passes `on_change` into the custom component.

- [x] **Step 3: Write minimal implementation**

```python
intent = render_backtest_analysis_result_workspace_component(
    workspace=workspace,
    key=component_key,
)
consumed = consume_result_workspace_intent(intent, workspace=workspace)
if consumed.get("ok"):
    st.rerun(scope="app")
```

Remove only the now-unused callback helper and `partial` import.

- [x] **Step 4: Run focused tests**

Run: `.venv/bin/python -m pytest tests/test_backtest_analysis_result_workspace.py tests/test_backtest_analysis_decision_workspace.py -q`

Expected: all focused tests pass.

### Task 2: Actual Interaction Verification

**Files:**
- Create during QA only, then delete: `.codex_result_component_diagnostic.py`
- Create generated artifact only: `backtest-level2-fragment-handoff-fix-qa.png`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`

**Interfaces:**
- Consumes: the production result component and adapter
- Produces: browser evidence that one click executes one handler and triggers a full-app rerun

- [x] **Step 1: Run an isolated diagnostic Streamlit app**

Use a synthetic GTAA bundle and an in-memory handler; do not write registry JSONL.

- [x] **Step 2: Verify the browser flow**

Check that the button is enabled, one click changes handler count `0 -> 1`, and a marker outside the fragment is visible after the full-app rerun.

- [x] **Step 3: Capture one QA screenshot**

Save `backtest-level2-fragment-handoff-fix-qa.png` as a generated, uncommitted artifact.

- [x] **Step 4: Remove the temporary diagnostic app**

Delete `.codex_result_component_diagnostic.py` and stop its Streamlit process.

### Task 3: Closeout And Commit

**Files:**
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task closeout files

**Interfaces:**
- Consumes: verified code/test/browser results
- Produces: concise durable handoff and one coherent implementation commit

- [x] **Step 1: Run final verification**

Run focused pytest, `py_compile`, `git diff --check`, and inspect `git status --short`.

- [x] **Step 2: Sync task and root handoff docs**

Record the root cause, chosen event lifecycle, RED/GREEN evidence, Browser QA, and remaining risk without changing high-level roadmap semantics.

- [x] **Step 3: Stage only owned files and commit**

Commit message: `수정: Backtest Level2 인계 fragment 라우팅 복구`
