# Overview Tab Helper Extraction V11-V16 Design

## Target Shape

```text
app/web/overview/
  page.py
  navigation.py
  market_context.py
  market_context_helpers.py
  market_movers.py
  market_movers_helpers.py
  futures_macro.py
  futures_macro_helpers.py
  sentiment.py
  sentiment_helpers.py
  events.py
  events_helpers.py
  legacy_dashboard.py
```

The entrypoint modules keep tab flow. The helper modules hold tab-local controls, refresh/result UI, chart/table helpers, and row transformation helpers that still need Streamlit or visual rendering.

## Boundary Rules

- Helper modules may call `legacy_dashboard.py` only for not-yet-moved shared constants or lower-level helpers during the migration step.
- Helper modules should not import raw provider modules, loaders, or DB helpers.
- Service calculation and read-model ownership stays under `app/services/overview/*`, `app/services/futures_*`, and existing Streamlit-free services.
- `overview_dashboard.py` should remain a wrapper and should not regain page or tab body ownership.

## QA Per Step

- Add or update focused contract tests before moving code.
- Run focused tests for the step.
- Run `py_compile` on touched modules.
- Run `OverviewAutomationContractTests`.
- Run Browser QA on the affected tab and one adjacent tab.
- Commit one coherent step before moving to the next.

