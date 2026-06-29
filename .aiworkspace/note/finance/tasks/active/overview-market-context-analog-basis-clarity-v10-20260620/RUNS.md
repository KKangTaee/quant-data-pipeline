# Runs

## 2026-06-20

- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "historical_analog_explains_when_selected_as_of_is_bounded_by_common_price_history or historical_analog_html_names_requested_effective_dates_and_macro_condition_roles"`: RED first, then GREEN after implementation.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "historical_analog"`: 19 passed, 3 dependency deprecation warnings.
- `git diff --check`: passed.
- `uv run python -m py_compile app/services/overview_market_context_analog.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`: 377 passed, 3 dependency deprecation warnings.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`: Browser QA target.
- Browser QA:
  - latest path shows `실제 계산 기준일 2026-05-29` and explains it as latest usable common DB price basis.
  - selected `2026/06/18` shows warning that actual calculation date is `2026-05-29`, with limiting symbols.
  - 20D and monthly pattern changes recompute the analog content after rerun.
  - Macro funnel labels show `섹터 상대강도`, `GLD 배경`, `금리선물 압력`.
  - Screenshot: `overview-market-context-analog-basis-v10-qa.png` (generated artifact, not staged).
