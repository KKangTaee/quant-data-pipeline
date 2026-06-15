# Runs

## 2026-06-15

- RED:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_action_facade_collects_historical_analog_price_gaps_with_existing_ohlcv_job tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests.test_historical_analog_exposes_generalized_repair_action_for_insufficient_proxy_or_comparison_symbols tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests.test_historical_analog_html_turns_insufficient_data_into_actionable_gap_panel`
  - Result: expected failures for missing action facade, missing `coverage_gaps`, and missing gap panel HTML.
- GREEN focused:
  - Same three tests after implementation.
  - Result: `Ran 3 tests in 0.438s OK`.
- Additional RED / GREEN:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_source_confidence_summary_exposes_scan_metrics_before_opening`
  - Result: first run failed on missing `ov-source-confidence-strip`, then passed after adding the summary strip.
- Regression:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests`
  - Result: `Ran 98 tests in 1.358s OK`.
- Static checks:
  - `.venv/bin/python -m py_compile app/services/overview_market_context_analog.py app/jobs/overview_actions.py app/web/overview_dashboard.py app/web/overview_ui_components.py tests/test_service_contracts.py`
  - `git diff --check`
  - Result: both passed.
- Browser QA:
  - Restarted Streamlit on `http://localhost:8501/` after an old process showed a stale action facade import error.
  - In-app Browser DOM verified `ov-analog-gap-panel=1`, `ov-source-confidence-strip=1`, no Traceback, and current repair target `XLC`.
  - Playwright fallback captured final QA screenshot because in-app Browser screenshot capture timed out after DOM verification.
  - Screenshot: `overview-market-context-analog-repair-v4-qa.png`.

## 2026-06-16 Follow-up

- RED:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_cue_cards_keep_left_rule_away_from_text tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_shows_historical_analog_repair_action_before_support_expander`
  - Result: expected failures for zero-left-padding cue override and repair action staying inside the support expander.
- GREEN focused:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_cue_cards_keep_left_rule_away_from_text tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_shows_historical_analog_repair_action_before_support_expander tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests.test_historical_analog_html_turns_insufficient_data_into_actionable_gap_panel`
  - Result: `Ran 3 tests in 0.074s OK`.
- Regression:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests`
  - Result: `Ran 100 tests in 1.404s OK`.
- Static checks:
  - `.venv/bin/python -m py_compile app/web/overview_dashboard.py app/web/overview_ui_components.py tests/test_service_contracts.py`
  - `git diff --check`
  - Result: both passed.
- Browser QA:
  - In-app Browser DOM verified cue padding-left `14.08px`, no Traceback, visible `과거 유사 맥락 자료 수집` heading, and hidden support expander no longer contains the historical analog repair action.
  - Playwright screenshot verified the cue-card line no longer crowds the leading text. In the final live QA state historical analog data had become sufficient, so the section rendered the analog table rather than the gap button.
  - Screenshot: `overview-market-context-cue-spacing-fix-qa.png`.
