# Practical Validation Audit Evidence Absorption V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Level 2의 세 raw 원본 탭을 제거하고 필요한 provenance를 Step 1, Step 2, Step 4에 compact하게 흡수한다.

**Architecture:** `app/services/backtest_practical_validation_decision_workspace.py`가 source / replay / validation raw dict를 사용자용 provenance read model로 투영한다. React one-shell과 Streamlit fallback은 이 read model만 표시하고, page 하단 raw JSON disclosure는 제거한다. Registry persistence와 Final Review handoff payload는 변경하지 않는다.

**Tech Stack:** Python 3.12, Streamlit, React 18, TypeScript, Vite, unittest/pytest.

## Global Constraints

- `Ingestion -> DB -> Loader -> UI` 경계를 유지한다.
- registry / saved JSONL을 재작성하거나 migration하지 않는다.
- raw source / replay / validation dict는 runtime과 persistence에 보존한다.
- React는 presentation과 intent만 소유한다.
- 새 provider fetch, DB schema, Final Review / Monitoring behavior를 추가하지 않는다.
- desktop 1440px과 760px에서 가로 overflow가 없어야 한다.

---

### Task 1: Compact Provenance Read Model

**Files:**
- Modify: `app/services/backtest_practical_validation_decision_workspace.py`
- Test: `tests/test_backtest_practical_validation_decision_workspace.py`

**Interfaces:**
- Consumes: source `period`, `summary`, `components`, `data_trust`; replay `attempted_at`, `period_coverage`, `market_date_contract`; validation `validation_id`; current validation profile.
- Produces: `candidate.provenance`, `replay.provenance`, `record` in `build_practical_validation_decision_workspace(...)`.

- [ ] **Step 1: Write failing candidate provenance test**

Assert the workspace projects period, formatted CAGR/MDD, component count, Data Trust status and warning count without exposing source snapshot or curve collections.

- [ ] **Step 2: Run candidate test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py -k "candidate_provenance" -q`

Expected: FAIL because `candidate.provenance` does not exist.

- [ ] **Step 3: Implement candidate provenance projection**

Add a pure helper that returns only display-safe scalar fields:

```python
{
    "period_label": "2016-08-31 → 2026-02-28",
    "cagr_label": "13.56%",
    "mdd_label": "-14.60%",
    "component_count": 3,
    "data_trust_label": "weighted_mix_snapshot",
    "warning_count": 0,
}
```

- [ ] **Step 4: Write failing replay/record provenance test**

Build a replay fixture with requested/actual period, latest common price date, end gap, limiting symbols, attempted time and replay id. Assert `replay.provenance` and top-level `record` contain only the approved compact fields.

- [ ] **Step 5: Run replay/record test and verify RED**

Run: `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py -k "replay_provenance or validation_record" -q`

Expected: FAIL because the new projections do not exist.

- [ ] **Step 6: Implement replay and validation record projection**

Project:

```python
"replay": {
    "provenance": {
        "visible": True,
        "mode_label": "최신 DB 데이터까지 확장 검증",
        "requested_period_label": "2016-08-31 → 2026-07-17",
        "actual_period_label": "2016-08-31 → 2026-07-17",
        "latest_common_price_date": "2026-07-17",
        "coverage_status": "PASS",
        "end_gap_days": 0,
        "limiting_symbols": [],
    }
},
"record": {
    "visible": True,
    "profile_label": "균형형",
    "recheck_mode_label": "최신 DB 데이터까지 확장 검증",
    "attempted_at": "...",
    "replay_id": "...",
    "validation_id": "...",
}
```

`visible` is false before replay/validation.

- [ ] **Step 7: Run focused service tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_backtest_practical_validation_decision_workspace.py -q`

Expected: all tests pass with only existing edgar deprecation warnings.

---

### Task 2: Step 1 / Step 2 / Step 4 UI Absorption

**Files:**
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/types.ts`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/PracticalValidationDecisionWorkspace.tsx`
- Modify: `app/web/components/practical_validation_decision_workspace/frontend/src/style.css`
- Modify: `app/web/backtest_practical_validation/workspace_panel.py`
- Modify: `app/web/backtest_practical_validation/page.py`
- Test: `tests/test_practical_validation_market_context_visual_contract.py`
- Test: `tests/test_backtest_refactor_boundaries.py`

**Interfaces:**
- Consumes: Task 1 `candidate.provenance`, `replay.provenance`, `record`.
- Produces: Step 1 candidate fact strip, Step 2 replay fact strip, Step 4 record disclosure; no page-level raw audit disclosure.

- [ ] **Step 1: Write failing visual ownership tests**

Assert React source contains `검증 대상 요약`, `재검증 기록`, `검증 기록`, renders the three new projections in their owning steps, and responsive classes collapse at 760px.

- [ ] **Step 2: Write failing page boundary test**

Assert current render path does not contain `원본 데이터·감사 정보`, the three raw tab labels, `_render_decision_workspace_audit_evidence`, or `st.json(source` / `st.json(replay_result` / `st.json(validation_result` in the removed helper boundary.

- [ ] **Step 3: Run visual/boundary tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py -q`

Expected: FAIL because the compact surfaces are absent and the raw disclosure still exists.

- [ ] **Step 4: Implement React types and surfaces**

Add strict types for the Task 1 projections. Render candidate facts below the Step 1 selection summary, replay facts after the Step 2 replay status only when visible, and a collapsed Step 4 `검증 기록` only when record.visible is true.

- [ ] **Step 5: Implement responsive styling**

Use four compact columns on desktop, two columns at intermediate width where existing layout permits, and one column at 760px. Preserve `overflow-wrap: anywhere` for ids and limiting symbols.

- [ ] **Step 6: Mirror the surfaces in Streamlit fallback**

Render the same compact labels from the read model. Do not render raw dicts or add download actions.

- [ ] **Step 7: Remove the page-level raw disclosure**

Delete `_render_decision_workspace_audit_evidence` and the `원본 데이터·감사 정보` expander call. Keep source/replay/validation objects passed to existing builder, save, and Final Review handoff functions.

- [ ] **Step 8: Run visual/boundary tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_practical_validation_market_context_visual_contract.py tests/test_backtest_refactor_boundaries.py -q`

Expected: all tests pass.

- [ ] **Step 9: Build React production assets**

Run: `npm --prefix app/web/components/practical_validation_decision_workspace/frontend run build`

Expected: Vite build passes and `build/index.html` references the new hashed CSS/JS assets.

---

### Task 3: Verification, Browser QA, And Durable Docs

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/INDEX.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-audit-evidence-absorption-v1-20260719/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-audit-evidence-absorption-v1-20260719/NOTES.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-audit-evidence-absorption-v1-20260719/RUNS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/practical-validation-audit-evidence-absorption-v1-20260719/RISKS.md`

**Interfaces:**
- Consumes: completed Task 1/2 behavior and actual browser output.
- Produces: durable ownership docs, QA evidence, coherent implementation commit.

- [ ] **Step 1: Run focused verification**

Run:

```bash
.venv/bin/python -m pytest \
  tests/test_backtest_practical_validation_decision_workspace.py \
  tests/test_practical_validation_market_context_visual_contract.py \
  tests/test_backtest_refactor_boundaries.py -q
.venv/bin/python -m py_compile \
  app/services/backtest_practical_validation_decision_workspace.py \
  app/web/backtest_practical_validation/page.py \
  app/web/backtest_practical_validation/workspace_panel.py
git diff --check
```

Expected: focused tests and compile pass; diff check has no output.

- [ ] **Step 2: Run actual Browser QA**

At 1440px verify Step 1 candidate facts, Step 2 replay facts after an actual replay, Step 4 record disclosure and absence of bottom raw disclosure. At 760px verify one-column compact facts, no horizontal overflow and zero browser console errors. Save one local screenshot and do not commit it.

- [ ] **Step 3: Synchronize durable docs**

Record that raw data remains in runtime/persistence while visible provenance belongs to Step 1/2/4. Keep root logs to 3–5 lines and do not rewrite registry/saved JSONL.

- [ ] **Step 4: Review staged scope**

Run: `git diff --cached --check && git diff --cached --name-only`

Expected: no registry, run history, saved JSONL, `.superpowers/`, or generated screenshot is staged.

- [ ] **Step 5: Commit**

Run: `git commit -m "Practical Validation 원본 근거를 단계별 기록으로 흡수"`

Expected: one coherent implementation commit on `codex/backtest-dev`.
