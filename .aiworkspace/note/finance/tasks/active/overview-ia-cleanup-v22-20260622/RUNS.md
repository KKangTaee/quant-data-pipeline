# Overview IA Cleanup V22 Runs

## 2026-06-22

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "overview_dashboard_uses_lazy_selected_deep_tab_rendering or overview_dashboard_primary_selector_excludes_ops_tabs or overview_data_health_is_not_a_primary_overview_tab or overview_sector_industry_tab_renders_breadth_summary_before_trend_tabs or overview_ia_closeout_model_demotes_ops_surfaces_from_primary_tabs"`
  - Result: expected failure, 5 failed. Existing code still exposed `Data Health` / `Candidate Ops` and still used top-level Trend/Table tabs in Sector / Industry.
- GREEN focused: same command.
  - Result: 5 passed, 382 deselected, 3 warnings.

- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/services/overview_market_intelligence.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: 387 passed, 3 warnings.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA: `http://localhost:8525`
  - Verified Overview selector shows only `Market Context`, `Market Movers`, `Futures Monitor`, `Sentiment`, `Sector / Industry`, `Events`.
  - Verified `Data Health` and `Candidate Ops` are absent from the selector.
  - Verified `Sector / Industry` renders summary / charts first and raw table under `상세 표`.
  - Screenshot: `overview-ia-cleanup-v22-qa.png`.
