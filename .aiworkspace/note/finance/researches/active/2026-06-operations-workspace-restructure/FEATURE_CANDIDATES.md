# Feature Candidates

Scoring: 1 low, 5 high.

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | Operations Overview / Command Center | 5 | 3 | 2 | 4 | 5 | Do first. |
| P0 | Operations taxonomy and page copy cleanup | 4 | 2 | 1 | 5 | 5 | Do with Overview. |
| P1 | Archive / Recovery demotion for Run History and Candidate Library | 3 | 2 | 3 | 4 | 4 | Do after Overview copy is accepted. |
| P1 | Portfolio Monitoring cockpit V2 | 5 | 3 | 3 | 4 | 5 | Do after IA is settled. |
| P2 | Data/System Health consolidation | 3 | 3 | 3 | 3 | 4 | Pair with Ingestion/Ops Review alignment. |
| P2 | Operations report export | 3 | 4 | 3 | 3 | 3 | Defer until monitoring semantics stabilize. |

## P0. Operations Overview / Command Center

Goal:

- Make Operations answer "what should I check now?" before users choose a tool.

Evidence:

- Audit: current Operations pages are peer-level despite different roles.
- Benchmark: portfolio operations products emphasize consolidated performance/risk/health views.

Dependencies:

- Existing selected portfolio runtime summary.
- Existing run history / Ops Review helpers.
- Navigation copy update.

Success criteria:

- Selected Dashboard is clearly presented as Portfolio Monitoring.
- Ops Review is clearly presented as System/Data Health.
- Backtest Run History and Candidate Library are clearly presented as Archive/Recovery.
- No registry/saved schema changes.
- No live approval/order/rebalance behavior.

## P0. Operations Taxonomy And Page Copy Cleanup

Goal:

- Clarify the mental model without moving much code.

Evidence:

- Audit: page bodies already state their boundaries, but top navigation does not.
- Benchmark: mature products group operations around monitoring/reporting rather than legacy artifact tools.

Dependencies:

- Text-only UI updates after user approval.
- Docs sync after implementation.

Success criteria:

- User can tell which page is primary and which is archive.
- `Selected Portfolio Dashboard` remains in Operations with clear monitoring language.

## P1. Archive / Recovery Demotion

Goal:

- Preserve history/library functions while lowering their prominence.

Evidence:

- Audit: Backtest Run History and Candidate Library are useful but not the main workflow.

Dependencies:

- Operations Overview route cards.
- Possible Streamlit navigation constraints.

Success criteria:

- Archive tools are still reachable.
- They no longer compete visually with Selected Dashboard as a primary operations destination.

## P1. Portfolio Monitoring Cockpit V2

Goal:

- Improve Selected Dashboard as the primary portfolio operations surface.

Evidence:

- Benchmark: IBKR/Morningstar/Sharesight/Koyfin portfolio views lead with portfolio performance, exposures, and review context.

Dependencies:

- Existing Selected Dashboard runtime.
- No-live-boundary copy remains.

Success criteria:

- Portfolio-wide status shows stale scenario count, open review items, last scenario date, watch/blocked count, and next rebalance review date.
- Target vs actual allocation/drift relationship is clearer.

## Parking Lot

- Broker/account sync.
- Live approval or order ticket creation.
- Auto rebalance.
- Scheduler-driven automatic portfolio scenario replay that writes monitoring logs.
- Full React/API navigation rewrite as the first step.

## 2026-06-07 Candidate Refresh

The earlier P0 `Operations Overview / Command Center` has been implemented. Current candidates should therefore shift from "create IA" to "make Operations useful and less prototype-like."

| Priority | Candidate | Impact | Effort | Risk | Confidence | Fit | Recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P0 | Operations Cockpit Cleanup | 5 | 2 | 2 | 5 | 5 | Do first. |
| P0 | Portfolio Monitoring First Summary | 5 | 3 | 3 | 4 | 5 | Do with or immediately after cleanup. |
| P1 | Archive Visibility Demotion | 3 | 2 | 3 | 4 | 4 | Do after confirming Streamlit nav limits. |
| P1 | Monitoring Evidence Health Strip | 4 | 3 | 3 | 4 | 5 | Pair with Portfolio Monitoring V2. |
| P2 | Manual Monitoring Report Snapshot | 3 | 4 | 3 | 3 | 4 | Defer until semantics stabilize. |

### P0. Operations Cockpit Cleanup

Problem:

- Current Operations Overview is structurally correct but still carries development-roadmap and surface-audit artifacts in the user-facing surface.

Expected workflow change:

- User opens Operations and immediately sees portfolio monitoring state, evidence health, and next action. Development history is hidden or moved out of the operating path.

Likely code areas:

- `app/web/operations_overview.py`
- `app/web/streamlit_app.py` only if navigation order/copy changes
- docs/flows sync after approval

### P0. Portfolio Monitoring First Summary

Problem:

- Portfolio Monitoring is the anchor surface, but Operations Overview still treats it as one lane among several status cards.

Expected workflow change:

- Operations Overview shows a portfolio-first summary: active portfolio count, assigned selected strategies, stale scenario count, blocked/missing references, open review items, next review date when available.

Likely code areas:

- `app/runtime/final_selected_portfolios.py` if existing summary lacks the needed compact fields
- `app/web/operations_overview.py`
- `app/web/final_selected_portfolio_dashboard.py` only if corresponding labels need alignment

### P1. Archive Visibility Demotion

Problem:

- Archive pages are semantically demoted inside their bodies, but top navigation still makes them peer pages.

Expected workflow change:

- Archive tools remain accessible for recovery, but the main Operations user journey starts from Overview or Portfolio Monitoring.

Likely code areas:

- `app/web/streamlit_app.py`
- `app/web/operations_overview.py`

Implementation caution:

- Do not delete archive tools until registry read/write paths and recovery alternatives are audited.
