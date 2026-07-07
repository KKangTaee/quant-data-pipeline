# Backtest Factor Readiness Panel V1 Plan

## Why

Quality / Value strict factor forms currently mix base-universe source copy, price freshness warnings, and statement shadow coverage in separate Streamlit / React surfaces. Users cannot quickly tell whether the selected preset is only a candidate pool, whether the backtest can run, or what action resolves a warning.

## Roadmap

1. Build a Streamlit-free readiness read model for strict factor forms.
   - Files: `app/web/backtest_common.py`, `tests/test_service_contracts.py`
   - Done when tests can classify base universe, price issue, statement issue, provider-gap wording, and next action.

2. Add a compact React `Factor Readiness Panel`.
   - Files: `app/web/components/backtest_factor_readiness_panel/`, `tests/test_service_contracts.py`
   - Done when component build exists, is UI-only, and renders summary / checks / actions.

3. Wire the panel into Single Strategy strict factor annual forms.
   - Files: `app/web/backtest_single_forms/strict_factor.py`, `app/web/backtest_common.py`
   - Done when annual Quality / Value / Quality+Value forms use the panel instead of scattered preset copy + price panel.

4. Enforce a five-year strict factor date window.
   - Files: `app/web/backtest_common.py`, `app/web/backtest_single_forms/strict_factor.py`, `app/web/backtest_compare/page.py`, tests
   - Done when strict annual factor payloads cannot submit windows longer than five years.

5. Apply shared readiness to Portfolio Mix Builder, update docs, and perform QA.
   - Files: `app/web/backtest_compare/page.py`, `.aiworkspace/note/finance/docs/*`, task logs
   - Done when compare strict annual blocks show the same readiness concept and browser QA confirms the first-read flow.

## Boundaries

- Keep Strategy dropdown / Single Strategy / Portfolio Mix Builder ownership in Streamlit.
- Do not change strategy runtime, factor math, DB schema, registry / saved JSONL, or live approval semantics.
- Do not stage generated screenshots or run history unless explicitly requested.

