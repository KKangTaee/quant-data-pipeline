# Overview Tab Helper Extraction V11-V16 Plan

## 이걸 하는 이유?

Overview active page / tab ownership is already split, but `app/web/overview/legacy_dashboard.py` still holds many tab-specific helper bodies. The goal is to remove that legacy dependency in a practical way: one active tab entrypoint plus one helper module per tab, without creating an over-fragmented file tree.

## Scope

- Keep the current user-facing Overview behavior.
- Move tab-specific UI/helper code from `legacy_dashboard.py` into `app/web/overview/*_helpers.py`.
- Keep service/read-model calculation in `app/services/overview/*` and existing Streamlit-free services.
- Keep bounded refresh actions routed through `app/jobs/overview_actions.py`.
- Preserve compatibility exports only when existing tests or public imports still require them.

## Roadmap

| Step | Goal | Files |
|---|---|---|
| V11 | Audit remaining legacy helper usage and lock the target helper structure | `tests/test_service_contracts.py`, task docs |
| V12 | Move Market Context tab helpers | `app/web/overview/market_context.py`, `app/web/overview/market_context_helpers.py`, `legacy_dashboard.py` |
| V13 | Move Events tab helpers | `app/web/overview/events.py`, `app/web/overview/events_helpers.py`, `legacy_dashboard.py` |
| V14 | Move Futures Macro tab helpers | `app/web/overview/futures_macro.py`, `app/web/overview/futures_macro_helpers.py`, `legacy_dashboard.py` |
| V15 | Move Market Movers tab helpers | `app/web/overview/market_movers.py`, `app/web/overview/market_movers_helpers.py`, `legacy_dashboard.py` |
| V16 | Move Sentiment tab helpers, sync docs, final QA | `app/web/overview/sentiment.py`, `app/web/overview/sentiment_helpers.py`, docs |

## Stop Condition

- Each primary Overview tab imports its own helper module instead of tab-specific legacy helper bodies.
- `legacy_dashboard.py` no longer owns primary tab helper groups moved in V12-V16.
- Overview contract tests and Browser QA pass after each step.
- Generated screenshots and local artifacts remain uncommitted.

