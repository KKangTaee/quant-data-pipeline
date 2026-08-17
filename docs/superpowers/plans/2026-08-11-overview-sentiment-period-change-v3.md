# Overview Sentiment Period Change V3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace permanently unavailable 1W·1M sentiment forecast cards with observed CNN and AAII period-change cards while preserving the strict gate against unvalidated probabilities.

**Architecture:** `app/services/overview/sentiment.py` selects the latest collected version per observation date, computes observation-lag changes, and reuses the existing CNN/AAII cross-read rules. `app/web/overview/sentiment_helpers.py` validates source-specific date ranges and serializes a fail-closed `period_changes` payload. React renders the server-owned values in a dedicated section and keeps the legacy unavailable outlook contract dormant for forward compatibility.

**Tech Stack:** Python, pandas, `unittest`, React/TypeScript, CSS, Vite, Streamlit Browser QA.

## Global Constraints

- Do not add a provider, DB table, ingestion workflow, prediction target, estimator, or probability.
- Do not merge CNN and AAII into one score.
- Preserve the existing unavailable outlook publication gate.
- Use observation lags, not calendar-day interpolation.
- Show each source's actual start/end dates because CNN and AAII have different cadence.
- Do not stage pre-existing registry, saved, run-history, `.superpowers/`, or unrelated QA artifacts.

---

### Task 1: Add The Observed Period-Change Service Contract

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/sentiment.py`

- [x] Add RED tests for 1W/1M CNN and AAII changes, units, dates, relationship transitions, and insufficient history.
- [x] Add review regressions for duplicate versions, latest-value missing, and invalid source dates.
- [x] Implement normalized series lookup and observation-lag change helpers.
- [x] Build 1W/1M `period_changes` alongside the existing fail-closed `outlook`.
- [x] Run focused service tests and confirm GREEN.

### Task 2: Serialize The New Payload Contract

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/overview/sentiment_helpers.py`

- [x] Add a RED payload test that asserts the service-owned period cards and metrics.
- [x] Add a fail-closed payload fallback for missing/invalid `period_changes`.
- [x] Preserve legacy `outlook` sanitization without using it in the new UI.
- [x] Run focused payload tests and confirm GREEN.

### Task 3: Replace The React Outlook Surface

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Add: `app/web/streamlit_components/sentiment_workbench/src/SentimentPeriodChangeSection.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/style.css`
- Regenerate: `app/web/streamlit_components/sentiment_workbench/component_static/`

- [x] Change source-contract tests to require `기간별 심리 변화` and reject root rendering of `SentimentOutlookSection`.
- [x] Add typed period-change fallback data and render server-owned period cards.
- [x] Add responsive metric/date/relationship styling with accessible labels.
- [x] Run React source-contract tests and Vite production build.

### Task 4: Synchronize Docs And Verify

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-cnn-aaii-v1-20260719/{PLAN,DESIGN,STATUS,NOTES,RUNS,RISKS}.md`
- Modify only if canonical ownership changed: `.aiworkspace/note/finance/docs/{ROADMAP,PROJECT_MAP,PRODUCT_DIRECTION}.md`
- Generate but do not commit: `overview-sentiment-period-change-v3-qa.png`

- [x] Record the approved 3/4 roadmap state and the known unrelated baseline failures.
- [x] Run focused service/frontend tests, Vite build, `git diff --check`, and scoped status review.
- [x] Run actual desktop and 420px Browser QA; verify values, dates, relationship copy, overflow, and console errors.
- [x] Save one QA screenshot outside the commit.
- [x] Stage only the coherent 3차 implementation and documentation files, then create a Korean commit.
