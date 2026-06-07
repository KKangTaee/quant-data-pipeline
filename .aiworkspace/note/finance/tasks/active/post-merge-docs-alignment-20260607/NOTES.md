# Post-Merge Docs Alignment 2026-06-07 Notes

## Merge-State Findings

- Recent merge brought together four major workstreams:
  - Overview / Market Intelligence: Sentiment, Futures Monitor, Why It Moved, Sector / Industry, Events, Data Health.
  - Operations: Operations Console and Portfolio Monitoring IA.
  - Backtest: Risk-On Momentum 5D V1/V2 as a Backtest Analysis research lane.
  - Validation / Monitoring: Practical Validation, Final Review, Selected Portfolio Dashboard handoff and read-only monitoring.
- Documentation drift is mainly state-model drift, not an immediate code conflict:
  - `PRODUCT_DIRECTION.md` still described Practical Validation P2/P3 as current focus.
  - `ROADMAP.md` mixed current roadmap with long completed-task history.
  - `tasks/active` and `phases/active` contain many retained completed boards, so "active" cannot be read literally without README context.
- Code path search found no broad `.note/finance` runtime recreation. `app/workspace_paths.py` remains canonical for `.aiworkspace/note/finance` paths.

## Current Product Interpretation

The current product is a DB-backed quant research workspace with this main user loop:

```text
Ingestion / Overview market context
  -> Backtest Analysis candidate creation
  -> Practical Validation evidence
  -> Final Review selection decision
  -> Operations Portfolio Monitoring
```

Market sentiment, futures macro context, and Why It Moved investigation are context surfaces. They do not create approval, broker orders, account sync, registry rewrites, saved setup mutations, or auto rebalance.
