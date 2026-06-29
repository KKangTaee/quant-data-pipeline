# Runs

- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_sector_industry_tab_renders_breadth_summary_before_trend_tabs tests.test_service_contracts.OverviewAutomationContractTests.test_overview_events_tab_renders_macro_week_lane_before_calendar_filters tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_breadth_heatmap_summary_scores_participation_and_concentration tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_week_lane_clusters_near_events_without_signal_language` -> PASS.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> PASS, 65 tests.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/web/overview_dashboard.py` -> PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS.
- `git diff --check` -> PASS.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8504 --server.headless true` + Browser QA -> PASS. Screenshot artifact: `overview-breadth-macro-week-v1-qa.png` (generated, not committed).
