# Runs

Status: Active
Last Updated: 2026-06-18

## Verification Log

- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_builds_separate_gld_conditioned_pilot_without_changing_broad_rows tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_marks_macro_pilot_insufficient_when_gld_context_is_missing -q`
  - Result: failed as expected before implementation with `KeyError: 'macro_conditioned_analog'`.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context -q`
  - Result: failed as expected before renderer implementation because `Macro 조건 포함 pilot` was absent.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_builds_separate_gld_conditioned_pilot_without_changing_broad_rows tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_marks_macro_pilot_insufficient_when_gld_context_is_missing tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_conditioned_pilot_as_separate_context -q`
  - Result: `3 passed`.
- `uv run python -m py_compile app/services/overview_market_context_analog.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`
  - Result: pass.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result: `360 passed, 3 warnings`.
- `git status --short`
  - Result: showed intended code/docs changes plus pre-existing unrelated/generated items: `finance/.DS_Store`, `.superpowers/`, `overview-market-context-next-checks-qa.png`.
- `git diff --check`
  - Result: pass.
- `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard.py app/web/overview_dashboard_helpers.py`
  - Result: pass.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q`
  - Result after boundary-copy and renderer empty-state updates: `360 passed, 3 warnings`.
- `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
  - Result: local server started at `http://localhost:8525`.
- Browser QA via in-app browser at `http://localhost:8525`.
  - Result: `Workspace > Overview > Market Context` loaded with broad historical analog and separate `Macro 조건 포함 pilot` block.
  - Required visible terms found: `참고: 과거 유사 맥락`, `Macro 조건 포함 pilot`, `사용한 조건`, `조건 부족`, `이번 차수 제외`, `표본 품질`.
  - Forbidden visible copy not found in body: `예측`, `추천`, `매수`, `매도`, `신호`, `가능성이 높다`; also checked `trade signal`, `monitoring signal`, `trading signal` after boundary-copy cleanup.
  - Live data state: leadership proxy was Basic Materials / XLB, but XLB coverage was `63 / 756 rows`, so broad analog and pilot correctly showed insufficient context instead of forcing calculation.
- `uv run --with playwright python -m playwright install chromium`
  - Result: installed Playwright Chromium runtime for artifact capture only after in-app browser screenshot API timed out.
- `uv run --with playwright python - <<'PY' ...`
  - Result: captured QA screenshot at `overview-market-context-macro-conditioned-analog-pilot-v1-qa.png` and independently confirmed required/forbidden body text.
