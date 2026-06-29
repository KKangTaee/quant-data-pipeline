# Runs

## 2026-06-15

- RED:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_relabels_supporting_flow_as_next_context_reference_and_evidence tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ui_css_defines_market_context_reading_sections tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_summarizes_existing_context_snapshots tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_uses_recent_cpi_as_compact_event_cue tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_historical_analog_html_keeps_context_only_language`
  - Result: expected failures on old UI title / labels / CSS. One class-name typo in the selected unittest target was corrected for the GREEN run.
- GREEN focused:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_relabels_supporting_flow_as_next_context_reference_and_evidence tests.test_service_contracts.OverviewAutomationContractTests.test_overview_ui_css_defines_market_context_reading_sections tests.test_service_contracts.OverviewAutomationContractTests.test_overview_market_context_copy_uses_korean_summary_first_language tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_summarizes_existing_context_snapshots tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_uses_recent_cpi_as_compact_event_cue tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests.test_historical_analog_html_keeps_context_only_language`
  - Result: `Ran 6 tests in 1.287s OK`
- Regression:
  - `PYTHONWARNINGS=ignore .venv/bin/python -m unittest tests.test_service_contracts.OverviewAutomationContractTests tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests tests.test_service_contracts.OverviewMarketContextAnalogServiceContractTests`
  - Result: first run found one stale exact class-string assertion; updated it to include `is-evidence-footer`.
  - Result after update: `Ran 94 tests in 1.359s OK`
- Static checks:
  - `.venv/bin/python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py tests/test_service_contracts.py`
  - `git diff --check`
  - Result: both passed.
- Browser QA:
  - Restarted Streamlit on `http://localhost:8501/` with `.venv/bin/streamlit run app/web/streamlit_app.py --server.port 8501 --server.address 0.0.0.0`.
  - Verified live UI includes `오늘의 시장 맥락`, `다음 맥락 체크`, `참고: 과거 유사 맥락`, `근거: 자료 기준 / 출처 상태`, `이벤트 압력`, `심리 확인`, `매크로 확인`.
  - Verified live UI no longer includes `해석할 때 같이 볼 변수`, `자료 상태 주의점`, `가까운 주요 이벤트`, `심리 배경`.
  - Verified class counts: `is-evidence-footer=1`, `is-muted-reference=1`, reading sections `4`.
  - Screenshot: `overview-market-context-supporting-flow-v3-qa.png`.
