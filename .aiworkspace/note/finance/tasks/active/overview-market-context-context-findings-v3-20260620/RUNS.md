# Overview Market Context Context Findings V3 Runs

## 2026-06-20

- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "context_findings or context_finding or next_checks_use_rail or wide_brief_lane or splits_dashboard or relabels_supporting or korean_summary_first_language or macro_context_cockpit_builds_summary_first_read_model or recent_cpi"`  
  Result: failed as expected before implementation; old checklist renderer lacked `맥락 검토 결과` and `context_findings`.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketIntelligenceServiceContractTests::test_overview_macro_context_cockpit_summarizes_existing_context_snapshots tests/test_service_contracts.py::OverviewMarketIntelligenceServiceContractTests::test_overview_macro_context_cockpit_uses_recent_cpi_as_compact_event_cue -q`  
  Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`  
  Result: passed, 367 tests, 3 warnings.
- `git diff --check`  
  Result: passed.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py`  
  Result: passed.
- Browser QA on `http://localhost:8525`, `Workspace > Overview > Market Context` after fresh Streamlit restart.  
  Result: `맥락 검토 결과` rendered with conclusion / interpretation / evidence rows; scoped forbidden copy check passed. Screenshot saved to `overview-market-context-context-findings-v3-qa.png` and remains generated artifact.
