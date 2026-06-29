# Runs

- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_dashboard_renders_ia_closeout_guide_between_cockpit_and_tabs tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ui_css_defines_ia_closeout_guide tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_model_marks_candidate_ops_transitional` -> RED, expected missing dashboard call / CSS / model.
- Same focused command after implementation -> PASS.
- Same focused command after copy polish (`Deep Tab Reading Order`) -> PASS.
- `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> PASS, 70 tests.
- `uv run python -m py_compile app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/services/overview_market_intelligence.py` -> PASS.
- `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS.
- `git diff --check` -> PASS.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8505 --server.headless true` + in-app Browser DOM QA -> PASS for `Overview Map`, `Candidate Ops`, `TRANSITIONAL`, and context-only boundary.
- Playwright DOM / screenshot QA after copy polish -> PASS for `Deep Tab Reading Order` and guide visibility. Screenshot artifact: `overview-ia-closeout-v1-qa.png` (generated, not committed).
