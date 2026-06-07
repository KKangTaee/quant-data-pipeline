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
