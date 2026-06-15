# Runs

## 2026-06-15

- RED: `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_splits_dashboard_from_reading_flow_contract tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ui_css_defines_market_context_reading_sections tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_summarizes_existing_context_snapshots`
  - Result: failed as expected before implementation. Missing narrative wrapper / CSS contract and old `현재 맥락:` service copy.
- GREEN focused: same command
  - Result: `Ran 3 tests ... OK`.
- Regression: `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`
  - Result: `Ran 87 tests ... OK`.
- Compile: `.venv/bin/python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py tests/test_service_contracts.py`
  - Result: OK.
- Whitespace: `git diff --check`
  - Result: OK.
- Browser QA: `http://localhost:8501`
  - Desktop DOM: narrative present, `현재 맥락:` absent, 3 sentence markers, 4 reading sections, page overflow count 0.
  - Mobile scoped DOM at 390x844: Market Context component overflow count 0. Full page overflow is Streamlit tabbar horizontal scrolling, not this component.
  - Screenshot: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/overview-market-context-copy-density-v2-qa.png`.
