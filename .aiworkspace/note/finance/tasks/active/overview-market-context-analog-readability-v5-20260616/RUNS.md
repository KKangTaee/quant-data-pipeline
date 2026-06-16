# Runs

## 2026-06-16

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests.test_historical_analog_html_explains_similarity_before_statistics tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ui_css_defines_market_context_reading_sections`
  - Result: expected failures before implementation.
- GREEN focused: same command
  - Result: `Ran 2 tests ... OK`.
- Focused Overview / Analog regression: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests tests.test_service_contracts.OverviewAutomationContractTests`
  - Result: `Ran 59 tests ... OK`.
- Full service contracts: `.venv/bin/python -m unittest tests.test_service_contracts`
  - First run exposed an unrelated date-sensitive Futures Macro Thermometer fixture failure (`OK` expected but stale test candles made status `REVIEW` on 2026-06-16).
  - Stabilized the fixture so synthetic daily rows end on `date.today()`.
  - Re-run result: `Ran 344 tests ... OK`.
- Compile: `.venv/bin/python -m py_compile app/web/overview_ui_components.py app/web/overview_dashboard.py app/services/overview_market_context_analog.py app/jobs/overview_actions.py`
  - Result: OK.
- Static whitespace: `git diff --check`
  - Result: OK.
- Browser QA: in-app browser `http://localhost:8501/`
  - Confirmed no Traceback.
  - Confirmed `참고: 과거 유사 맥락` OK state renders definition text, one summary strip, `먼저 읽을 결론`, and two table blocks.
  - Confirmed historical analog section no longer forces a transparent background; computed background is `rgb(255, 255, 255)`.
  - Screenshot: `overview-market-context-analog-readability-v5-qa.png` (generated artifact, not for commit).
