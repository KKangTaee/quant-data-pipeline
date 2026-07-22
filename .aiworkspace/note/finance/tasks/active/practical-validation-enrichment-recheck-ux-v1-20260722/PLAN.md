# Practical Validation Enrichment Recheck UX V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Level2 외부 데이터 보강 뒤 현재 단계와 다음 행동을 같은 React one-shell에 유지하고, 보강된 데이터 재검증부터 새 결과 저장과 Final Review 이동까지 끊김 없이 연결한다.

**Architecture:** Python session boundary가 provider collection result, source별 enrichment progress, semantic feedback를 소유한다. Pure Decision Workspace service가 이를 JSON-safe lifecycle model로 투영하고, React와 Streamlit fallback은 같은 모델을 읽어 진행 상태와 CTA만 렌더링한다. Provider collector, replay runtime, validation Gate, append-only storage 계약은 유지한다.

**Tech Stack:** Python 3.12, Streamlit 1.57, React 18, TypeScript 5.6, Vite 5, unittest/pytest.

## Global Constraints

- 수집과 replay는 자동으로 합치지 않고 명시적인 두 작업으로 유지한다.
- provider collector, DB schema, validation threshold와 Gate 계산을 변경하지 않는다.
- raw job, row, status table을 first-read 운영 진단 panel로 추가하지 않는다.
- registry JSONL, run history, saved setup, generated QA artifact를 stage하지 않는다.
- 후보 source별 session state를 분리하고 다른 후보의 progress를 노출하지 않는다.
- React는 collection, validation, storage, route 변경을 실행하지 않고 intent만 반환한다.

## 이걸 하는 이유?

현재 데이터 보강은 stale replay와 decision result를 안전하게 지우지만, one-shell이 `recheck_required` state와 collection result를 읽지 않는다. 사용자는 녹색 완료 알림 뒤 일반 Step 2로 돌아가 작업이 끝났는지, 무엇을 눌러야 하는지 다시 판단해야 한다.

---

### Task 1: Enrichment Lifecycle Read Model And Semantic Feedback

**Files:**
- Modify: `tests/test_backtest_practical_validation_decision_workspace.py`
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Modify: `app/web/backtest_practical_validation/page.py`

**Interfaces:**
- Consumes: source별 `enrichment_progress: dict[str, Any]`, `collection_results: list[dict[str, Any]]`, current replay/validation result.
- Produces: `build_practical_validation_decision_workspace(..., enrichment_progress=None, collection_results=None) -> dict`의 `enrichment_lifecycle` 모델과 structured Practical Validation notice.

- [ ] **Step 1: Write the failing lifecycle projection test**

```python
def test_workspace_projects_collection_recheck_lifecycle_without_claiming_full_success(self) -> None:
    model = build_practical_validation_decision_workspace(
        source=self._source(),
        validation_profile={"profile_id": "balanced_core"},
        replay_result=None,
        validation_result=None,
        source_options=[self._source()],
        enrichment_progress={"status": "recheck_required", "result_count": 3},
        collection_results=[
            {"status": "SUCCESS", "run_metadata": {"input_params": {"provider_area": "operability"}}},
            {"status": "PARTIAL", "run_metadata": {"input_params": {"provider_area": "holdings"}}},
            {"status": "FAILED", "run_metadata": {"input_params": {"provider_area": "macro"}}},
        ],
    )
    lifecycle = model["enrichment_lifecycle"]
    self.assertTrue(lifecycle["visible"])
    self.assertEqual(lifecycle["state"], "recheck_required")
    self.assertEqual(lifecycle["collection_summary"]["success_count"], 1)
    self.assertEqual(lifecycle["collection_summary"]["review_count"], 1)
    self.assertEqual(lifecycle["collection_summary"]["failure_count"], 1)
    self.assertEqual(model["actions"]["run_replay"]["label"], "보강된 데이터로 재검증")
```

- [ ] **Step 2: Write the failing structured notice assertion**

Extend `test_provider_collection_completion_clears_replay_for_regular_and_final_review_origins`:

```python
notice = fake_st.session_state["backtest_practical_validation_notice"]
self.assertEqual(notice["tone"], "warning")
self.assertEqual(notice["title"], "자료 보강을 실행했습니다")
self.assertIn("재검증", notice["detail"])
```

- [ ] **Step 3: Run the RED tests**

```bash
.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py::PracticalValidationDecisionWorkspaceTests::test_workspace_projects_collection_recheck_lifecycle_without_claiming_full_success -q
.venv/bin/python -m pytest tests/test_service_contracts.py -q -k provider_collection_completion_clears_replay_for_regular_and_final_review_origins
```

Expected: the builder rejects the new lifecycle arguments and collection completion still stores a string notice.

- [ ] **Step 4: Implement the conservative collection result summary**

Add this pure interface in `app/services/backtest_practical_validation_decision_workspace.py`:

```python
def summarize_provider_collection_results(
    results: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Summarize collector outcomes without treating unknown or partial states as success."""
```

Normalize `SUCCESS/PASS/OK/COMPLETED` as success, `PARTIAL/REVIEW/WARNING` and unknown statuses as review, and `FAILED/FAILURE/ERROR/BLOCKED` as failure. Return counts, unique provider areas, outcome label, and tone.

- [ ] **Step 5: Project lifecycle state through the Decision Workspace**

Extend the builder with optional `enrichment_progress` and `collection_results`. Reuse `build_practical_validation_recovery_progress()` and return:

```python
"enrichment_lifecycle": {
    "visible": bool(enrichment_progress),
    "state": "recheck_required" | "blocked" | "save_ready" | "none",
    "headline": str,
    "next_action": str,
    "steps": list[dict[str, str]],
    "collection_summary": dict[str, Any],
}
```

When progress exists and replay is absent, label the replay action `보강된 데이터로 재검증`.

- [ ] **Step 6: Store and render semantic feedback**

In `page.py`, add `_practical_validation_notice(tone, title, detail)` and `_render_practical_validation_notice(notice)`. Structured notices use the matching Streamlit method; legacy strings default to `st.info`. Collection completion stores a warning payload because collection is not validation completion.

- [ ] **Step 7: Pass source-scoped lifecycle inputs into the fragment builder**

Read the selected source's enrichment progress and provider collection result session keys and pass them to `build_practical_validation_decision_workspace()`. Do not read another source's state.

- [ ] **Step 8: Run GREEN and focused regressions**

```bash
.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py tests/test_service_contracts.py -q -k 'practical_validation_decision_workspace or provider_collection_completion or recovery_progress or save_and_move_rejects_missing_current_replay'
```

Expected: all selected tests pass.

---

### Task 2: One-Shell Lifecycle Surface And Fallback

**Files:**
- Modify: `tests/test_practical_validation_market_context_visual_contract.py`
- Modify: `tests/test_backtest_refactor_boundaries.py`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Rebuild: `app/web/components/practical_validation_decision_workspace/frontend/component_static/`

**Interfaces:**
- Consumes: Task 1의 `workspace.enrichment_lifecycle`과 기존 `actions.run_replay` intent.
- Produces: decision surface와 Streamlit fallback의 동일한 lifecycle progress/CTA 표현.

- [ ] **Step 1: Write failing React lifecycle surface tests**

Assert the source contains `pv2-enrichment-lifecycle`, `workspace.enrichment_lifecycle.visible`, all four step labels, and renders the lifecycle before `pv2-recheck-mode-panel`. Assert `.pv2-enrichment-steps` collapses to one column at `760px`.

- [ ] **Step 2: Replace the obsolete boundary assertion**

Keep the legacy Python recovery renderer out of the main render body, but assert `enrichment_progress=` and `collection_results=` are passed into the shared Decision Workspace builder.

- [ ] **Step 3: Write the failing fallback contract test**

Assert the fallback reads `enrichment_lifecycle`, shows headline/next action/collection counts before recheck controls, and retains the existing `run_replay` intent.

- [ ] **Step 4: Run RED presentation tests**

```bash
.venv/bin/python -m pytest tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py -q -k 'lifecycle or one_decision_workspace or fallback'
```

Expected: no lifecycle surface exists yet.

- [ ] **Step 5: Extend TypeScript contract and render lifecycle**

Add lifecycle types. When visible, render one compact section inside Step 2 before replay mode with headline, next action, four step states, success/review/failure counts, and provider area labels. Do not render raw job/rows tables.

- [ ] **Step 6: Add responsive styles**

Use existing blue-gray tokens. Render four steps as a compact desktop grid and one column at `max-width: 760px`; do not add left-border risk bars.

- [ ] **Step 7: Implement the same fallback order**

Render the shared lifecycle before fallback replay controls. The fallback continues to emit existing intents and does not execute collection or validation directly.

- [ ] **Step 8: Run GREEN tests and production build**

```bash
.venv/bin/python -m pytest tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py tests/test_backtest_practical_validation_decision_workspace.py -q
npm --prefix app/web/components/practical_validation_decision_workspace/frontend run build
```

Expected: all tests and Vite build pass, updating canonical `component_static` assets.

---

### Task 3: Verification, Browser QA, Documentation And Commit

**Files:**
- Modify: task closeout files in `.aiworkspace/note/finance/tasks/active/practical-validation-enrichment-recheck-ux-v1-20260722/`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Create generated only: `practical-validation-enrichment-recheck-ux-v1-qa.png`

**Interfaces:**
- Consumes: verified lifecycle model and React/fallback surfaces.
- Produces: actual interaction evidence, durable flow documentation, and one coherent implementation commit.

- [ ] **Step 1: Run full focused verification**

```bash
.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py tests/test_service_contracts.py -q -k 'practical_validation or provider_collection_completion or recovery_progress'
.venv/bin/python -m py_compile app/services/backtest_practical_validation_decision_workspace.py app/web/backtest_practical_validation/page.py app/web/backtest_practical_validation/workspace_panel.py
npm --prefix app/web/components/practical_validation_decision_workspace/frontend run build
git diff --check
```

Expected: zero failures, Python compile success, Vite build success, no whitespace errors.

- [ ] **Step 2: Run actual Browser QA without provider writes**

Use a fixture/in-memory Streamlit route importing the production component. Verify `recheck_required`, one replay click, and `save_ready` or blocker state at desktop and `760px`; confirm no overflow/console error. Save `practical-validation-enrichment-recheck-ux-v1-qa.png` uncommitted and remove the fixture/process.

- [ ] **Step 3: Synchronize durable docs**

Update only affected flow paragraphs. Record that collection remains separate from replay, partial results are not full success, and the next CTA persists by source until replay/save transition.

- [ ] **Step 4: Close task records**

Mark roadmap `3/3차`; record RED/GREEN, build/Browser evidence, and any remaining actual-provider QA gap. Keep root logs concise.

- [ ] **Step 5: Stage only owned files and commit**

Do not stage registry JSONL, run history, saved setup, `.superpowers/`, or unrelated screenshots.

Commit message:

```text
개선: Practical Validation 보강 재검증 흐름 연결
```
