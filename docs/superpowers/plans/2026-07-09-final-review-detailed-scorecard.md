# Final Review Detailed Scorecard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a more trustworthy Final Review scorecard with overall score, detailed dimensions, Level2 REVIEW score impacts, score caps, and final selection rationale.

**Architecture:** Python `app/services/backtest_evidence_read_model.py` owns all score, cap, route, and rationale calculations. React `final_review_investment_report` renders the Python-owned payload only. Streamlit fallback remains available and registry / saved / provider / DB boundaries are unchanged.

**Tech Stack:** Python service read model, unittest service contracts, React / TypeScript Streamlit component, Vite build, Streamlit Final Review page fallback.

---

### Task 1: Detailed Scorecard Read Model

**Files:**
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write RED test**

Add a service contract asserting that Final Review scorecard includes five dimensions: `investment`, `risk`, `readiness`, `evidence_quality`, `monitoring_suitability`, plus weighted `overall_score` and `score_drivers`.

- [ ] **Step 2: Run RED test**

Run:

```bash
.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_final_review_detailed_scorecard_exposes_weighted_dimensions
```

Expected: FAIL because the scorecard does not yet expose those fields.

- [ ] **Step 3: Implement minimal service model**

Add score dimension helpers and extend `build_final_review_scorecard` while preserving current top-level fields.

- [ ] **Step 4: Run GREEN test and focused suite**

Run the new test and existing Final Review scorecard tests.

- [ ] **Step 5: Commit**

Commit only relevant source, tests, and task docs.

### Task 2: React Score Breakdown UI

**Files:**
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: build assets under `app/web/components/final_review_investment_report/frontend/dist/`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write RED component contract**

Assert React source and build contain user-facing labels for `세부 점수`, `점수 영향`, and `점수 제한`.

- [ ] **Step 2: Run RED test**

Run the component source/build contract test.

- [ ] **Step 3: Implement React rendering**

Render dimensions, drivers, and limits under the scorecard panel.

- [ ] **Step 4: Build and verify**

Run `npm run build`, component tests, py_compile, and diff check.

- [ ] **Step 5: Commit**

Commit React UI and build output.

### Task 3: Level2 REVIEW Score Impact

**Files:**
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: React component if additional labels are needed
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write RED test**

Assert role-specific REVIEW impact mapping:
`pv_data_caution -> evidence_quality`, `pv_practical_caution -> risk`, `final_decision_input -> investment`, `monitoring_followup -> monitoring_suitability`, `final_readiness_blocker -> readiness`.

- [ ] **Step 2: Run RED test**

Expected: FAIL because impacts are not yet exposed.

- [ ] **Step 3: Implement impact mapping**

Add `review_impacts` and connect impacts to dimension score deductions.

- [ ] **Step 4: Verify**

Run focused Final Review service tests and React build if UI labels changed.

- [ ] **Step 5: Commit**

Commit service/tests and any UI label changes.

### Task 4: Score Cap and Route Decision

**Files:**
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write RED tests**

Assert caps:
hard blocker max 55, selected-route not ready max 69, critical open review max 74, excessive open review max 79.

- [ ] **Step 2: Run RED tests**

Expected: FAIL because caps are not yet modeled as explicit `score_limits`.

- [ ] **Step 3: Implement cap policy**

Add `score_limits`, `pre_cap_score`, `cap_applied`, and route classification logic using caps.

- [ ] **Step 4: Verify**

Run scorecard tests and full Final Review contract subset.

- [ ] **Step 5: Commit**

Commit cap policy changes.

### Task 5: Selection Rationale Surface

**Files:**
- Modify: `app/services/backtest_evidence_read_model.py`
- Modify: `app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx`
- Modify: `app/web/components/final_review_investment_report/frontend/src/style.css`
- Modify: `app/web/backtest_final_review/page.py`
- Modify: `tests/test_service_contracts.py`

- [ ] **Step 1: Write RED tests**

Assert report includes `selection_rationale` and `required_final_decision_notes`, and React/fallback render those labels.

- [ ] **Step 2: Run RED tests**

Expected: FAIL because the rationale payload/UI is absent.

- [ ] **Step 3: Implement payload and UI**

Generate rationale from classification, strongest dimension, weakest dimension, blockers, review impacts, and monitoring conditions.

- [ ] **Step 4: Verify**

Run Python tests, React build, py_compile, diff check.

- [ ] **Step 5: Commit**

Commit rationale payload/UI changes.

### Task 6: Integration QA and Docs Sync

**Files:**
- Modify: task docs
- Modify: `.aiworkspace/note/finance/docs/ROADMAP.md`
- Modify: `.aiworkspace/note/finance/docs/PROJECT_MAP.md`
- Modify: `.aiworkspace/note/finance/docs/flows/BACKTEST_UI_FLOW.md`
- Modify: `.aiworkspace/note/finance/docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [ ] **Step 1: Run integration QA**

Run focused Final Review service tests, py_compile, `git diff --check`, React build, and Browser QA.

- [ ] **Step 2: Capture screenshot**

Save generated screenshot without staging it.

- [ ] **Step 3: Sync docs**

Update durable docs and task run logs only.

- [ ] **Step 4: Commit docs sync**

Commit docs sync separately.
