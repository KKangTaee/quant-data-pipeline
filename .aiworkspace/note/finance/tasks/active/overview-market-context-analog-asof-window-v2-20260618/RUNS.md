# Runs

Status: Complete
Last Updated: 2026-06-18

## Verification

- `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_dashboard_helpers.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/jobs/overview_actions.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - First run: failed 3 source-inspection / fixture expectation tests after intentional renderer split and v2 metadata fallback.
  - Fixed tests.
  - Result: `357 passed, 3 warnings`.
- `git diff --check`
  - Result: passed.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Result: server started on `http://localhost:8525`.
- Browser QA
  - Confirmed controls visible: `기준 시점`, `기준일`, `패턴 기간`.
  - Confirmed latest / 5D state shows selected basis metadata and insufficient-data reason for short XLB coverage.
  - Confirmed selected 기준 시점 state changes `기준 시점` metadata.
  - Confirmed 20D pattern changes condition and table to `패턴 기간: 20D`, `SPY 대비 20D 상대강도 기준`, and OK distribution rows.
  - Confirmed early 기준일 `2016-06-20` shows clear insufficient-data reason and row evidence.
  - Confirmed Korean forbidden copy not present in Market Context body: `예측`, `추천`, `매수`, `신호`, `가능성이 높다`.
  - Screenshot artifact: `overview-market-context-analog-asof-window-qa.png`.
