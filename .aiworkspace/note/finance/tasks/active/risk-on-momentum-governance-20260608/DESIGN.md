# Design

Status: Completed
Last Verified: 2026-06-08

## Ownership

| Area | File |
|---|---|
| Governance read model | `app/services/backtest_risk_on_governance.py` |
| Backtest Analysis render | `app/web/backtest_analysis.py` |
| Contract tests | `tests/test_backtest_risk_on_governance.py` |
| Durable docs | `docs/PROJECT_MAP.md`, `docs/architecture/SCRIPT_STRUCTURE_MAP.md`, `docs/flows/BACKTEST_UI_FLOW.md`, `docs/ROADMAP.md` |

## Product Shape

The panel is a read-only governance readiness board.

It should show:

- Current lane: Backtest Analysis research lane.
- Governance status: deferred / not promoted.
- Research evidence already available: Swing Detail, trade log, scanner, comparison, sensitivity, stability, trade-cause, quality warnings, generated artifacts.
- Missing governance modules:
  - Daily Swing Practical Validation module.
  - Final Review selected-route rule.
  - Portfolio Monitoring daily review cadence / signal policy.
  - Artifact / trade log storage boundary.
  - Universe / survivorship assumption review.
- Next workflow: start with review evidence, not monitoring signal.

## Boundary

The read model must not import Streamlit, call runtime, read DB, fetch providers, or write JSONL.
The UI must only render the service payload and leave existing Single Strategy / Portfolio Mix execution paths unchanged.
