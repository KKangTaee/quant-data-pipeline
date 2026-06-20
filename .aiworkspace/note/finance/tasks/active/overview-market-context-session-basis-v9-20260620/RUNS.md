# Runs

## 2026-06-20

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "last_market_basis_when_market_is_closed or keeps_intraday_refresh_action_when_market_is_open or brief_html_renders_session_title"`
  - Result: failed as expected. `build_overview_macro_context_cockpit` does not accept `market_session_context`, and the brief HTML title is hard-coded to `오늘의 시장 브리프`.
- GREEN focused: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "last_market_basis_when_market_is_closed or keeps_intraday_refresh_action_when_market_is_open or brief_html_renders_session_title"`
  - Result: `3 passed, 371 deselected in 0.40s`.
- Additional RED/GREEN: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "market_context_session_payload_uses_previous_trading_day_when_closed or refresh_bar_prefers_smart_refresh or last_market_basis_when_market_is_closed or keeps_intraday_refresh_action_when_market_is_open or brief_html_renders_session_title"`
  - Result after implementation: `5 passed, 370 deselected, 3 warnings in 1.38s`.
- Browser QA: `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`, then `http://localhost:8525` > `Workspace > Overview > Market Context`.
  - Result: market session banner shows `휴장`; Market Context top copy says `마지막 거래일에는 ...`; brief section title is `마지막 거래일 시장 브리프`; basis subtitle shows `기준: 2026-06-18 · 세션: 2026-06-20 · 미국장 휴장 · 주말`; top data rail shows `자료 정상 · 휴장 기준`; refresh expander shows `필요 자료 보강 · 현재 보강할 자료 이슈 없음`; no `NameError` / `Traceback`.
  - Screenshot artifact: `overview-market-context-session-basis-v9-qa.png` (generated, do not stage).
- Final verification:
  - `git diff --check`: passed.
  - `uv run python -m py_compile app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`: passed.
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`: `375 passed, 3 warnings in 12.92s`.
