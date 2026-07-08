# Backtest Handoff Policy Signal Action Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove duplicated Practical Validation entry judgment between Handoff and Policy Signals, then evaluate whether a small React custom component is worth using for advanced action cards.

**Architecture:** Keep Streamlit as the app shell and keep Python services as the source of truth for gate/readiness decisions. Handoff owns action and entry judgment; Policy Signals owns evidence detail. React, if added, is restricted to an isolated custom component POC and does not own registry writes or strategy/runtime logic.

**Tech Stack:** Python, Streamlit, Streamlit custom components, React/TypeScript optional POC, `tests/test_service_contracts.py`.

---

### Task 1: V1 Policy Signals Responsibility Cleanup

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/backtest_result_display.py`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-handoff-policy-signal-action-v1-v4-20260704/STATUS.md`

- [ ] **Step 1: Write the failing test**

Assert that `_render_real_money_details` no longer calls `_render_policy_signal_summary_panel(meta)`, while Handoff still calls `_render_practical_validation_handoff_panel(state)`.

- [ ] **Step 2: Run RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.BacktestRuntimeContractTests.test_policy_signal_tab_is_evidence_only_after_handoff_summary
```

Expected: FAIL because the active Policy Signals render path still calls `_render_policy_signal_summary_panel(meta)`.

- [ ] **Step 3: Implement V1**

Remove the duplicate Policy Signals entry summary from the active real-money details path. Rename the board copy so the tab reads as evidence/detail, not as another entry-judgment panel.

- [ ] **Step 4: Run QA**

Run focused tests plus compile and whitespace check.

- [ ] **Step 5: Commit V1**

Commit message: `backtest policy signals 중복 진입 요약 제거`

### Task 2: V2 Streamlit Handoff Action Integration

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/backtest_result_display.py`

- [ ] **Step 1: Write the failing test**

Assert that `_render_practical_validation_next_action` uses a single action shell class and no separate hint block outside the action surface.

- [ ] **Step 2: Run RED**

Expected: FAIL because the current button and hint are separate columns below the HTML card.

- [ ] **Step 3: Implement V2**

Keep `st.button`, but wrap it in a Streamlit action shell directly under the Handoff card with matching visual container and boundary copy.

- [ ] **Step 4: Run QA**

Run focused tests, compile, diff check, and Browser QA for the Handoff area.

- [ ] **Step 5: Commit V2**

Commit message: `backtest handoff 액션 영역을 통합`

### Task 3: V3 React Custom Component POC

**Files:**
- Create: `app/web/components/backtest_handoff_action/`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write the failing test**

Assert that the React POC is isolated under `app/web/components/backtest_handoff_action/`, has a manifest/package boundary, and does not import finance runtime code.

- [ ] **Step 2: Run RED**

Expected: FAIL because the component folder does not exist.

- [ ] **Step 3: Implement V3**

Add a minimal component wrapper and frontend source that can render status text and return an action event. Do not wire it into the production Handoff path yet.

- [ ] **Step 4: Run QA**

Run source-boundary tests and any available package metadata checks. Do not require a full node build unless dependencies are already installed.

- [ ] **Step 5: Commit V3**

Commit message: `backtest handoff react 컴포넌트 poc 추가`

### Task 4: V4 Adoption Decision And Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`
- Modify: `.aiworkspace/note/finance/tasks/active/backtest-handoff-policy-signal-action-v1-v4-20260704/STATUS.md`

- [ ] **Step 1: Write the documentation contract test or source assertion**

Assert docs mention Streamlit remains the production shell and React is limited to optional advanced action-card POC.

- [ ] **Step 2: Run RED**

Expected: FAIL until docs are updated.

- [ ] **Step 3: Implement V4**

Record the adoption decision: keep production path Streamlit-only for now, keep React POC isolated until repeated action-card needs justify wiring.

- [ ] **Step 4: Run final QA**

Run focused tests, compile, diff check, Browser QA if the Streamlit production UI changed after V2.

- [ ] **Step 5: Commit V4**

Commit message: `backtest handoff react 도입 판단 문서화`
