# Practical Validation Level2 Controls / Evidence IA V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Level2의 판정 기준 조정과 재검증 범위를 각각 Step 1과 Step 2로 이동하고, 하단에는 읽기 전용 원본 데이터·감사 정보만 남긴다.

**Architecture:** Python service가 허용된 profile question/options와 recheck mode를 read model로 제공하고 intent를 검증한다. React는 Step 1/2에서 설정을 표현하고 intent만 반환하며, Streamlit 하단 disclosure는 source/replay/validation 원본을 읽기 전용으로 표시한다.

**Tech Stack:** Python 3.12, Streamlit fragment/session state, React 18, TypeScript, Vite, unittest/pytest.

## Global Constraints

- 검증 임계값 계산, audit/gate 의미, DB/registry/saved JSONL schema는 변경하지 않는다.
- profile answer 변경은 기존 replay 결과를 재사용하되 validation-result cache를 다시 계산한다.
- recheck mode 변경은 현재 source의 replay/result 상태를 무효화한 뒤 사용자가 다시 실행하게 한다.
- React는 presentation과 intent만 소유하며 Python이 option 검증과 session state 변경을 소유한다.
- `상세 검증 근거`는 Step 3의 사용자 해석 근거로 유지한다.
- 원본 disclosure는 기본 닫힘이며 write action을 만들지 않는다.
- desktop과 760px에서 horizontal overflow가 없어야 한다.

---

## 이걸 하는 이유?

현재 `고급 설정과 원본 근거`는 판정 기준, replay 범위, 후보 source, 전체 JSON을 한 곳에 섞는다. 사용자는 결과에 영향을 주는 설정을 검증이 끝난 뒤 발견하고, `상세 검증 근거`와 raw audit data를 구분하기 어렵다. 설정을 사용하는 단계에 배치하고 감사 원본만 하단에 남기면 다음 행동과 근거의 역할이 분명해진다.

## 전체 Roadmap

1. **1차 — 계약/계획:** approved IA, state invalidation, acceptance criteria를 task 문서와 failing test로 고정한다.
2. **2차 — UI 구현:** Python read model/intent/fallback, React Step 1/2, Streamlit audit disclosure를 구현한다.
3. **3차 — 검증/정렬:** focused tests, React build, py_compile, desktop/760px Browser QA, durable docs와 root handoff를 정렬한다.

## Task 1: Read Model And Intent Contract

**Files:**
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`

**Interfaces:**
- Consumes: `VALIDATION_PROFILE_QUESTIONS`, `RECHECK_MODE_LABELS`, current session profile/recheck keys.
- Produces: `profile.questions`, `profile.threshold_summary`, `replay.mode`, `replay.mode_label`, `replay.mode_options`, intents `update_profile_answer` and `select_recheck_mode`.

- [ ] **Step 1: Write failing read-model tests**

```python
model = build_practical_validation_decision_workspace(
    source=self._source(),
    validation_profile=build_validation_profile("balanced_core"),
    replay_result=None,
    validation_result=None,
    source_options=[self._source()],
    recheck_mode="stored_period",
)
self.assertEqual(len(model["profile"]["questions"]), 5)
self.assertEqual(model["replay"]["mode"], "stored_period")
```

- [ ] **Step 2: Run the focused test and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py -q`

Expected: failure because the read model has no question list/recheck mode contract.

- [ ] **Step 3: Add the minimal read-model fields**

Import the canonical option maps, project only labels/current values/options, and accept a validated `recheck_mode` parameter with `extend_to_latest` fallback.

- [ ] **Step 4: Write failing intent tests**

```python
intent = {
    "action": "update_profile_answer",
    "intent_id": "profile-answer-1",
    "selection_source_id": "source-grs-current",
    "validation_result_id": "",
    "question_id": "drawdown_tolerance",
    "answer": "dd_10",
}
```

Assert the answer is stored, decision result cache is cleared, replay state remains, and unsupported question/answer is rejected. Add the same contract for `select_recheck_mode`, asserting replay/result invalidation.

- [ ] **Step 5: Run the intent tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py -q`

Expected: failure because the two intents are not consumed.

- [ ] **Step 6: Implement Python intent validation and fallback controls**

Add the two actions to surface allow-lists. Use canonical maps for validation, keep profile answer changes on app rerun, and recheck-mode changes on the decision fragment. Mirror Step 1/2 controls in the Streamlit fallback.

- [ ] **Step 7: Run focused Python tests and confirm GREEN**

Run: `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py -q`

Expected: all tests pass.

## Task 2: React Placement And Read-Only Audit Disclosure

**Files:**
- Modify: `tests/test_practical_validation_market_context_visual_contract.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify: `app/web/backtest_practical_validation/page.py`

**Interfaces:**
- Consumes: Task 1 read-model fields/intents.
- Produces: Step 1 `판정 기준 세부 조정`, Step 2 `재검증 범위`, bottom `원본 데이터·감사 정보` tabs.

- [ ] **Step 1: Write failing visual/source-boundary tests**

Assert the React source contains `판정 기준 세부 조정`, `재검증 범위`, both new intents, responsive classes, and the page contains `원본 데이터·감사 정보` while removing `고급 설정과 원본 근거` and editable controls from the bottom disclosure.

- [ ] **Step 2: Run visual/source-boundary tests and confirm RED**

Run: `.venv/bin/python -m pytest tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py -q`

Expected: failures for the new copy and placement contract.

- [ ] **Step 3: Implement the React Step 1/2 controls**

Add a compact Step 1 details block with five select fields and applied threshold summary. Add a two-option Step 2 mode selector above the replay status/action. Emit one validated intent per changed field/mode and keep local calculations out of React.

- [ ] **Step 4: Replace the bottom mixed disclosure**

Rename the renderer to `_render_decision_workspace_audit_evidence`. Show a read-only caption and three tabs: `후보 원본`, `재검증 원본`, `판정 원본`. Preserve formatted source summary and raw JSON without any select/radio widgets.

- [ ] **Step 5: Add responsive styling**

Use two columns for profile questions and replay modes on desktop; collapse both to one column at 760px. Keep focus-visible states and `overflow-wrap: anywhere`.

- [ ] **Step 6: Run visual/source-boundary tests and confirm GREEN**

Run: `.venv/bin/python -m pytest tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py -q`

Expected: all tests pass.

- [ ] **Step 7: Build the React component**

Run: `cd app/web/components/practical_validation_decision_workspace/frontend && npm run build`

Expected: Vite build succeeds with 175 transformed modules or the current equivalent.

## Task 3: Verification, Browser QA, Docs, Commit

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: task `STATUS.md`, `NOTES.md`, `RUNS.md`, `RISKS.md`
- Create: one generated Browser QA screenshot outside staged files.

**Interfaces:**
- Consumes: Tasks 1–2 implementation.
- Produces: verified UI flow and durable handoff.

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m py_compile app/services/backtest_practical_validation_decision_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py
git diff --check
```

Expected: tests and compile pass; diff-check emits no output.

- [ ] **Step 2: Run actual Browser QA**

Verify desktop and 760px: Step 1 disclosure placement, profile answer application, Step 2 mode placement, mode-change replay reset, bottom read-only tabs, no horizontal overflow, no component error.

- [ ] **Step 3: Update durable docs and task evidence**

Record the new ownership: Step 1 profile answers, Step 2 recheck range, Step 3 detailed evidence, bottom read-only audit data. Keep root logs to 3–5 lines.

- [ ] **Step 4: Review the final diff and preserve unrelated artifacts**

Run: `git status --short` and `git diff --stat`. Confirm registry/run-history/saved JSONL and pre-existing QA artifacts are not staged.

- [ ] **Step 5: Commit the coherent implementation unit**

```bash
git add <only task docs, owned code/tests/docs, and built component assets>
git commit -m "Practical Validation 설정과 원본 근거 UI 분리"
```

## Stop Condition

Step 1/2 controls are visible where their decisions occur, their state transitions are Python-validated and tested, the bottom disclosure is read-only, desktop/760px QA passes, durable docs match the implementation, and unrelated local artifacts remain untouched.
