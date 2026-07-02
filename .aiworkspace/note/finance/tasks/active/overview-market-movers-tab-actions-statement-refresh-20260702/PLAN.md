# Overview Market Movers Tab Actions Statement Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split Market Movers investigation tab actions by purpose and let the SEC filing tab run a targeted EDGAR financial statement refresh for the selected symbol.

**Architecture:** Keep external fetches and writes out of normal render paths. News / Korean-news metadata and SEC filing metadata remain session-only service calls, while financial statement refresh goes through a bounded Overview job facade that delegates to the existing Ingestion EDGAR statement refresh job for one symbol.

**Tech Stack:** Python, Streamlit `st.fragment`, existing `app/services/overview/why_it_moved.py`, `app/jobs/overview_actions.py`, `app/jobs/ingestion_jobs.py`, `tests/test_service_contracts.py`.

---

### Task 1: Split metadata service calls

**Files:**
- Modify: `app/services/overview/why_it_moved.py`
- Test: `tests/test_service_contracts.py`

- [x] Add failing tests that news-only lookup does not call the SEC fetcher and SEC-only lookup does not call news fetchers.
- [x] Implement `fetch_market_mover_news_metadata`, `fetch_market_mover_sec_metadata`, and `merge_market_mover_metadata`.
- [x] Verify focused service tests pass.

### Task 2: Add targeted statement refresh action

**Files:**
- Modify: `app/jobs/overview_actions.py`
- Test: `tests/test_service_contracts.py`

- [x] Add failing test for `run_overview_market_mover_statement_refresh(symbol="AAA", freq="quarterly")`.
- [x] Implement the action as a thin wrapper around `run_extended_statement_refresh` for one selected symbol.
- [x] Preserve result timing and expose `source_job_name`, `freq`, `period`, and `symbols` in details.

### Task 3: Wire tab-specific UI actions

**Files:**
- Modify: `app/web/overview/market_movers_helpers.py`
- Test: `tests/test_service_contracts.py`

- [x] Add failing source-contract test for separate button labels and SEC tab statement refresh call.
- [x] Replace the combined `뉴스·공시 메타데이터 조회` button with tab-local news and SEC buttons.
- [x] Add the SEC tab `필요 재무제표 수집` action, elapsed-time result display, and session-state result retention.
- [x] Wrap the selected-symbol investigation clue area with `st.fragment` to reduce scroll reset.

### Task 4: Verification and QA

**Files:**
- Update: this task `RUNS.md`, `STATUS.md`, `RISKS.md`

- [x] Run focused tests and Overview service contract tests.
- [x] Run `py_compile` and `git diff --check`.
- [x] Run Browser QA on `Overview > Market Movers > 선택 종목 조사`, including button visibility and no horizontal overflow.
- [x] Commit only relevant source, tests, and task docs.
