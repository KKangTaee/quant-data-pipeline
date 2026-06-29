# Runs

- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ui_css_defines_source_confidence_lane tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_source_confidence_catalog_surfaces_provider_caveats_and_review_items tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_summarizes_existing_context_snapshots` -> RED, expected missing function / field / CSS.
- Same focused command after implementation -> PASS.
- `uv run python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_source_confidence_catalog_surfaces_provider_caveats_and_review_items` after adding degraded sentiment-confidence contract -> RED, expected 3 review items before service adjustment; then PASS after mapping degraded confidence to REVIEW.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> PASS, 67 tests.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py` -> PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS.
- `git diff --check` -> PASS.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8505 --server.headless true` + Browser QA -> PASS. Screenshot artifact: `overview-source-confidence-catalog-v1-qa.png` (generated, not committed).
