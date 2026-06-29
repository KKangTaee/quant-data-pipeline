# Runs

## 2026-06-20

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "overview_market_context_brief_absorbs or splits_dashboard_from_reading_flow_contract or relabels_supporting_flow or copy_uses_korean_summary_first_language or summarizes_existing_context_snapshots"`
  - Result: failed as expected. Existing UI still limited brief rows to 3 and rendered `context_findings` as a separate `맥락 검토 결과` rail.
- GREEN narrow: same command
  - Result: `5 passed, 362 deselected`.
- Dashboard flow narrow: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "overview_dashboard_renders_macro_context_cockpit_inside_market_context_tab or overview_dashboard_keeps_deep_tab_guide_out_of_market_context_brief or overview_market_context_shows_historical_analog_repair_action_before_support_expander or overview_market_context_passes_historical_analog_controls_to_cockpit_loader or overview_market_context_brief_absorbs or splits_dashboard_from_reading_flow_contract or relabels_supporting_flow or copy_uses_korean_summary_first_language or summarizes_existing_context_snapshots"`
  - Result: `9 passed, 358 deselected`.

Full verification and Browser QA are recorded after final run.

- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: `367 passed, 3 warnings`.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Result: app loaded at `http://localhost:8525`.
- Browser QA:
  - Confirmed `Market Context` selected.
  - Confirmed `오늘의 시장 브리프`, `이벤트 caveat`, `자료 신뢰도 caveat`, `참고: 과거 유사 맥락`, `근거: 자료 기준 / 출처 상태` are present.
  - Confirmed `맥락 검토 결과` and `다음 맥락 체크` are not visible.
  - Confirmed forbidden copy was not detected in visible page text: `예측`, `추천`, `매수`, `매도`, `신호`, `PASS`, `BLOCKER`, `Final Review decision`, `Operations monitoring signal`.
  - Screenshot artifact: `overview-market-context-brief-findings-integration-v4-qa.png` (generated artifact, not staged).
