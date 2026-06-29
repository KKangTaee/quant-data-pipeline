# Overview Market Context Session Basis V9 Implementation Plan

**Goal:** `Overview > Market Context` should read as a current-session aware market brief. On weekends or market holidays it should anchor to the last stored market basis instead of saying `오늘의 시장 브리프` or pushing intraday refresh as if the market were open.

**Scope**

- 1차: Add Market Context session basis payload.
- 2차: Change brief title / subtitle by market session.
- 3차: Suppress intraday snapshot refresh issues when the market is closed and the source is only stale by elapsed weekend / holiday time.
- 4차: Update refresh assist copy for closed sessions.
- 5차: Clarify historical analog copy so top brief basis and analog controls are not mixed.
- 6차: Verify tests and Browser QA.

**Files**

- `app/services/overview_market_intelligence.py`
- `app/web/overview_dashboard.py`
- `app/web/overview_dashboard_helpers.py`
- `app/web/overview_ui_components.py`
- `tests/test_service_contracts.py`
- task/docs closeout files

**Boundary**

- No provider fetch during UI render.
- No NYSE calendar provider integration, DB schema, loader, registry, saved JSONL, or run history changes.
- No trade signal, recommendation, validation gate, Final Review, or Operations monitoring semantics.

## Steps

- [x] Write RED tests for closed-session Market Context title, basis, refresh suppression, and UI copy.
- [x] Add optional `market_session_context` to the cockpit service model and refresh plan.
- [x] Pass the existing Overview market session state into the cached cockpit loader.
- [x] Render session-aware brief title / subtitle and refresh assist text.
- [x] Update historical analog guidance copy.
- [x] Run focused tests, full service contract tests, py_compile, diff check.
- [x] Browser QA and screenshot.
- [x] Sync durable docs and commit safe files only.
