# Runs

## 2026-06-20

- RED: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "smart_market_context_refresh or actionable_context or summarizes_existing_context_snapshots"`
  - Result: failed as expected. `run_overview_market_context_refresh_smart` did not exist and service `brief_rows` still included `이벤트 배경`.
- GREEN focused: `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "smart_market_context_refresh or actionable_context or summarizes_existing_context_snapshots or refresh_bar_prefers"`
  - Result: `4 passed, 365 deselected, 3 warnings`.
- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/services/overview_market_intelligence.py app/jobs/overview_actions.py app/web/overview_dashboard.py app/web/overview_ui_components.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: `369 passed, 3 warnings in 13.43s`.
- Browser QA: `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`, then `http://localhost:8525` > `Workspace > Overview > Market Context`.
  - Result: confirmed `오늘의 시장 브리프` renders movement / breadth / Futures-Macro only; `이벤트 배경` and `직접 원인 근거 약함` are absent from visible Market Context text; `필요 자료 보강` shows `현재 이슈만 보강`, `전체 Market Context 자료 보강`, and `보강 제외` Events copy.
  - Forbidden copy check result: no visible `예측`, `추천`, `매수`, `매도`, `신호`, `PASS`, `BLOCKER`, `Final Review decision`, or `Operations monitoring signal`.
  - Screenshot artifact: `overview-market-context-smart-refresh-v7-qa.png` (generated, do not stage).
- Final verification after docs sync:
  - `git diff --check`: passed.
  - `uv run python -m py_compile app/services/overview_market_intelligence.py app/jobs/overview_actions.py app/web/overview_dashboard.py app/web/overview_ui_components.py`: passed.
  - `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`: `369 passed, 3 warnings in 13.46s`.
