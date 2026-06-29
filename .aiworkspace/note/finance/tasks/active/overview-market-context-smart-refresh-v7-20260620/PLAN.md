# Overview Market Context Smart Refresh V7 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Market Context keeps the top brief focused on actual market-context conclusions and makes data refresh actions run only the currently relevant collection jobs by default.

**Architecture:** `app/services/overview_market_intelligence.py` owns the read model: 3-row brief, source evidence, and a new `refresh_plan`. `app/jobs/overview_actions.py` owns the bounded action facade for smart refresh and full refresh. `app/web/overview_dashboard.py` renders the smart refresh plan and result summary without calling providers directly.

**Tech Stack:** Python, Streamlit, pandas, existing Overview action facade, service contract tests.

---

## Scope

- 1차: Remove default Events row from `오늘의 시장 브리프`.
- 2차: Classify refresh issues as resolvable, partially resolvable, or not actionable.
- 3차: Make the default refresh button run only current actionable issues.
- 4차: Keep full Market Context refresh as a secondary fallback.
- 5차: Add a dedicated `refresh_plan` payload instead of reusing `context_findings`.
- 6차: Show post-refresh reflection as brief-impact summary before raw job rows.
- 7차: Fix and test row metadata consistency, especially Futures/Macro limitation source/freshness.

## Files

- Modify `app/services/overview_market_intelligence.py`
  - remove Events from default brief rows
  - add `refresh_plan`
  - ensure Futures/Macro limitation row metadata points to Futures/Data Health evidence
- Modify `app/jobs/overview_actions.py`
  - add smart refresh action dispatch from selected action ids
  - keep current full refresh action
- Modify `app/web/overview_dashboard.py`
  - render smart refresh plan
  - add default smart refresh button and secondary full refresh button
  - improve reflection summary
- Modify `tests/test_service_contracts.py`
  - add RED/GREEN contract tests for the above behaviors
- Update finance task/docs closeout after verification.

## Steps

- [x] Write failing service contract tests for 3-row brief, `refresh_plan`, and Futures/Macro metadata.
- [x] Write failing action facade tests for smart refresh dispatch and full refresh fallback.
- [x] Write failing UI source contract tests for smart refresh default / full refresh secondary / result summary ordering.
- [x] Implement minimal service model changes.
- [x] Implement minimal action facade changes.
- [x] Implement minimal UI changes.
- [x] Run focused tests, then full service contract tests.
- [x] Run Browser QA and capture one screenshot.
- [x] Sync docs and commit only source/test/task/doc files.
