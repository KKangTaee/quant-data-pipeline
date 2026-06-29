# Overview Market Context Brief Flow Redesign V2 Runs

## 2026-06-20

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_market_context_v2_uses_wide_brief_lane_and_next_check_rail tests/test_service_contracts.py::OverviewAutomationContractTests::test_overview_market_context_v2_css_removes_repeated_card_grid_language -q`
  - RED result: failed as expected before implementation because `ov-market-brief-lane` and `ov-next-check-rail` did not exist.
- Same command after implementation
  - Result: 2 passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests -q`
  - Initial result: failed on old V1 card/brief placement expectations.
  - Updated tests to V2 contract.
  - Result: 61 passed, 3 warnings.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewAutomationContractTests tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests -q`
  - Result: 79 passed, 3 warnings.
- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard_helpers.py finance/loaders/macro.py finance/loaders/sentiment.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: 367 passed, 3 warnings.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Browser QA: `Workspace > Overview > Market Context`.
  - Confirmed latest view shows `오늘의 시장 브리프`, next-check rail, historical analog basis, `Macro 조건 포함 비교`, source ledger, and `필요 자료 보강`.
  - Confirmed selected as-of `2026-06-17`, `20D`, and `monthly` update the basis ledger after rerun.
  - Confirmed forbidden copy absent from visible body text.
  - Screenshot: `overview-market-context-brief-flow-redesign-v2-qa.png` (generated artifact, not staged).
