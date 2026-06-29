# Design

Status: Completed
Last Verified: 2026-06-08

## Ownership

| Area | File |
|---|---|
| ETF current-anchor read model | `app/services/backtest_etf_current_anchor.py` |
| Backtest Analysis render | `app/web/backtest_analysis.py` |
| Contract tests | `tests/test_backtest_etf_current_anchor.py` |
| Durable docs | `docs/PROJECT_MAP.md`, `docs/architecture/SCRIPT_STRUCTURE_MAP.md`, `docs/flows/BACKTEST_UI_FLOW.md`, `docs/ROADMAP.md` |

## Product Shape

The panel is a read-only workbench that turns existing local evidence into actionable ETF anchor readiness.

It should show:

- Target strategies: Global Relative Strength, Risk Parity Trend, Dual Momentum.
- Latest run evidence: recorded time, result end, rows, summary highlights, data trust signals.
- Source evidence: latest Backtest Analysis source id if a Practical Validation handoff source exists.
- Evidence gaps: missing latest run, missing source, missing provider / cost / benchmark / liquidity proof.
- Anchor status: whether the strategy needs a rerun, a source handoff, or evidence review before promotion.
- Next action: the lowest-risk next workflow step.

## Boundary

The read model may read existing run history / selection source rows through Streamlit-free runtime helpers or injected test rows.
It must not import Streamlit, execute a backtest, fetch a provider, write JSONL, append registry rows, or create Practical Validation results.
The UI must only render the service payload and leave Single Strategy / Portfolio Mix execution unchanged.

## Implemented Shape

- The service accepts injected rows for tests and defaults to read-only runtime loaders in the UI.
- Latest run rows are matched by `strategy_key`; latest source rows are matched by top-level or component `strategy_key`.
- Missing latest run, selection source, price freshness, cost / net-cost curve, benchmark, and ETF provider / liquidity evidence are represented as explicit gaps.
- The UI renders metrics, a summary table, and per-strategy detail expanders.
