# Overview Context Refresh / Korean Copy V1 Runs

## 2026-06-10

- RED:
  - `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_action_facade_runs_market_context_refresh_bundle tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ia_closeout_model_marks_candidate_ops_transitional tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_summarizes_existing_context_snapshots`
  - Failed because bulk refresh facade was missing and cockpit / Overview Map copy was still English-first.
- GREEN:
  - Same focused tests passed after adding `run_overview_market_context_refresh_all()` and Korean copy.
- Focused regression:
  - `uv run python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests` -> 72 tests OK.
- Compile / boundary / whitespace:
  - `uv run python -m py_compile app/jobs/overview_actions.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/services/overview_market_intelligence.py tests/test_service_contracts.py` -> OK.
  - `uv run python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` -> PASS.
  - `git diff --check` -> OK.
- Browser QA:
  - URL: `http://localhost:8505/`.
  - Confirmed `Market Context 일괄 갱신` button appears above cockpit.
  - Confirmed Korean-first cockpit headline, `다음에 볼 Deep Tab`, `Source Confidence / 출처 신뢰도`, `Overview Map / 화면 지도`, and `Deep Tab 읽는 순서`.
  - QA screenshot: `overview-market-context-refresh-ko-qa.png` generated artifact, not for commit.
