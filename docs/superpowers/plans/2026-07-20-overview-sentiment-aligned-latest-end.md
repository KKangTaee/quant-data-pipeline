# Overview Sentiment Aligned Start And Latest End Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep CNN and AAII history charts aligned at the start while exposing every source's actual latest observation.

**Architecture:** Replace the misleading strict `common` coverage contract with `aligned` coverage. The service verifies that the sources overlap, chooses the later start and latest overall end, and the React component applies that one extent to both panels without filling missing tail dates.

**Tech Stack:** Python 3.12, pandas, `unittest`, React 18, TypeScript 5, Vite 6.

## Global Constraints

- Do not interpolate, forward-fill, or duplicate source observations.
- Keep one shared x-domain for both chart panels.
- Preserve the current 6M default and `6M / 1Y / 전체` selector.
- Do not change current evidence card values or the 180-day interpretation window.
- Do not start the postponed 3rd-stage independent-source work.

---

### Task 1: Change The Aligned Coverage Contract

**Files:**
- Modify: `tests/test_service_contracts.py`
- Modify: `app/services/overview/sentiment.py`
- Modify: `app/web/overview/sentiment_helpers.py`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentWorkbench.tsx`
- Modify: `app/web/streamlit_components/sentiment_workbench/src/SentimentHistorySection.tsx`

**Interfaces:**
- Consumes: source coverage objects with `canonical_start` and `canonical_end`.
- Produces: `history_coverage.aligned = {canonical_start, canonical_end, available}`.

- [x] **Step 1: Write failing service, payload, and React contract tests**

Expect `aligned.canonical_start == "2025-06-04"`, `aligned.canonical_end == "2026-07-20"`, both chart panels to use `buildAlignedPeriodExtent`, and the visible copy to use `전체` and `정렬 구간`.

- [x] **Step 2: Run the focused tests and confirm expected failures**

Run:

```bash
.venv/bin/python -m unittest \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_sentiment_aligned_history_coverage_uses_shared_start_and_latest_end \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_keeps_full_chart_history_but_interprets_recent_180_days \
  tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_market_sentiment_react_payload_uses_existing_snapshot_fields \
  tests.test_service_contracts.OverviewAutomationContractTests.test_sentiment_history_uses_one_shared_aligned_domain_for_both_panels
```

Expected: failures referencing the old `common` contract and intersection end date.

- [x] **Step 3: Implement the minimal aligned coverage change**

Use the later start, verify it is not after the earlier end, and then use the later end. Rename the payload and TypeScript types from `common` to `aligned`; keep point filtering unchanged so each line naturally stops at its own latest date.

- [x] **Step 4: Re-run focused tests and the component build**

Run the four focused tests above, then:

```bash
npm run build --prefix app/web/streamlit_components/sentiment_workbench
```

Expected: all tests pass and Vite completes without TypeScript errors.

- [x] **Step 5: Commit the implementation**

Stage only the focused source and test files and commit with a Korean message describing start alignment and latest-value exposure.

### Task 2: Synchronize Durable Documentation

**Files:**
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-history-pit-v2-20260720/STATUS.md`
- Modify: `.aiworkspace/note/finance/tasks/active/overview-sentiment-history-pit-v2-20260720/RUNS.md`
- Modify: `.aiworkspace/note/finance/docs/data/DATA_FLOW_MAP.md`
- Modify: `.aiworkspace/note/finance/WORK_PROGRESS.md`
- Modify: `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md`

- [x] **Step 1: Record the superseding range rule**

State that start dates align, the shared axis reaches the latest source date, and each line stops at its own observation end without interpolation.

- [x] **Step 2: Run final verification**

Run focused contracts, component build, `git diff --check`, and inspect `git status --short` so unrelated untracked artifacts remain unstaged.

- [x] **Step 3: Commit documentation**

Stage only the documentation files changed by this follow-up and commit with a Korean closeout message.
