# Audit

Status: Completed
Last Verified: 2026-06-07

## Current Baseline

Current active phase: none.
Current active task before this closeout: none.

Completed structure sequence:

- 5차: `code-boundary-refactor-audit-20260607`
- 6차: `overview-ingestion-action-boundary-20260607`
- 7차: `streamlit-ingestion-console-split-20260607`
- 7B: `ingestion-diagnostic-facade-20260607`
- 8차: `runtime-backtest-risk-on-momentum-split-20260607`, `runtime-backtest-real-money-split-20260607`, `runtime-backtest-strict-family-split-20260607`
- 9차: `backtest-compare-components-split-20260607`

## Large File Snapshot

Largest files still require future judgement, but not all are in this closeout scope.

| File | Lines | Closeout Interpretation |
|---|---:|---|
| `app/web/backtest_compare.py` | 5,890 | Still the largest Backtest UI file. 9차 reduced visual shell only; follow-up splits remain. |
| `app/web/overview_dashboard.py` | 5,557 | Large Overview surface remains outside this structure round's chosen closeout path. |
| `app/runtime/final_selected_portfolios.py` | 5,320 | Large runtime/read-model file remains a future Operations / Portfolio Monitoring candidate. |
| `app/services/overview_market_intelligence.py` | 4,753 | Large service file remains a future Overview service candidate. |
| `app/web/ingestion_console.py` | 4,543 | Still large, but 7차/7B removed shell and diagnostic responsibilities from the highest-risk boundaries. |

## Backtest Compare Residuals

`app/web/backtest_compare.py` remains an orchestration owner, not a small component module.
The largest remaining function is `_render_strategy_compare_workspace` at about 1,581 lines.

Recommended follow-up split candidates:

| Candidate | Why It Should Be Separate |
|---|---|
| Strategy-specific Compare form body | The largest remaining render / input section and likely the next biggest readability win. |
| Saved portfolio workspace / replay panel | Already backed by `app/services/backtest_saved_portfolio_replay.py`; UI replay render can become a focused module. |
| Weighted portfolio result panel | Result rendering and Practical Validation handoff UI can be separated while keeping weighted construction service-owned. |

## Boundary Findings

- `app/web/backtest_compare_components.py` is a visual shell module only and does not own compare execution, saved replay, registry handoff, or runtime behavior.
- `app/runtime/backtest.py` is now a compatibility facade for Risk-On Momentum, real-money / readiness helpers, strict quality / value wrappers, and result bundle helpers.
- `app/services/ingestion_diagnostics.py` owns read-only Ingestion diagnostics orchestration; `app/web/ingestion_console.py` renders and stores session state.
- Overview bounded refresh uses `app/jobs/overview_actions.py`; Overview remains a context surface, not a collector owner.
- Search did not find production code recreating `.note/finance` paths. A historical `quant-research/.note/research` metadata string remains in `app/runtime/backtest.py`; this is not the finance workspace storage path and is left as a future metadata-cleanup note, not a blocker.
- UI / engine boundary checker passed with no hard violations or advisories.
- Service contract suite passed after the closeout documentation updates.

## Closeout Decision

This refactor round can close as a baseline.

Do not keep splitting inside the same broad task just because large files remain.
The next code work should be opened as a focused follow-up task or a new user-approved phase, with clear ownership and verification criteria.
