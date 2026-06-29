# Overview Futures Macro Mixed Substates V1 Runs

## Commands

- `./.venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_futures_market_brief_model_places_scenario_and_support_together tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_weak_growth_without_safe_haven_confirmation tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_explains_risk_weakness_with_easing_rates tests.test_service_contracts.FuturesMacroThermometerContractTests.test_macro_interpretation_keeps_low_signal_mixed_context_distinct`
  - RED: failed with missing `sub_scenario` fields before implementation.
  - GREEN: passed after service/UI model implementation.
- `./.venv/bin/python -m unittest tests.test_service_contracts.FuturesMacroThermometerContractTests tests.test_service_contracts.OverviewAutomationContractTests`
  - Passed: 99 tests.
- `./.venv/bin/python -m py_compile app/services/futures_macro_thermometer.py app/web/overview_dashboard.py app/web/overview_ui_components.py tests/test_service_contracts.py`
  - Passed.
- `git diff --check`
  - Passed.
- `./.venv/bin/python - <<'PY' ... load_overview_futures_macro_snapshot(force_refresh=True) ... PY`
  - Current local DB snapshot remains top-level `혼재된 매크로 흐름`.
  - Mixed subtype: `성장 약세 + 방어 확인 부족`.
  - Coverage: 16/16 symbols standardized, latest daily date `2026-06-23`.
- Browser QA: `http://localhost:8513/?overview_tab=futures-macro`
  - Confirmed subtype / reason render below the top-level scenario without duplicate copy.
  - Screenshot artifact: `overview-futures-macro-mixed-substates-v1-qa.png`.
