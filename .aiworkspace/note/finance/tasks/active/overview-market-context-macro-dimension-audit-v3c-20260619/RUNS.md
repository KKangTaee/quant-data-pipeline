# Runs

Status: Complete
Last Updated: 2026-06-19

| Command | Result | Notes |
|---|---|---|
| `git status --short` | Done | Pre-work dirty tree contained generated/local items only: `finance/.DS_Store`, `.superpowers/`, and prior QA screenshots. |
| `git rev-parse --git-dir`; `git rev-parse --git-common-dir`; `git branch --show-current`; `git rev-parse --show-superproject-working-tree` | Done | Already in a linked worktree on `codex/sub-dev`; not a submodule. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_adds_macro_dimension_audit_without_hard_filtering_macro_series tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot -q` | Expected fail | RED state: service rejected `macro_series_history`; renderer did not include `맥락 차원 상태`. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_adds_macro_dimension_audit_without_hard_filtering_macro_series tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_html_renders_macro_dimension_audit_inside_pilot -q` | Pass | GREEN state: `2 passed`. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "historical_analog"` | Pass | `16 passed, 347 deselected, 3 third-party edgar deprecation warnings`. |
| `git diff --check` | Pass | No whitespace errors after first implementation pass. |
| `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard_helpers.py finance/loaders/macro.py finance/loaders/sentiment.py` | Pass | Requested compile set exited 0. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Pass | Initial full suite after 3C implementation: `363 passed, 3 third-party edgar deprecation warnings`. |
| Browser QA at `http://localhost:8525` | Found issue | Fresh local data first showed XLB short-coverage state; disabled `Macro 조건 포함 pilot` did not yet render `맥락 차원 상태`. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_keeps_macro_dimension_audit_when_broad_proxy_coverage_is_short -q` | Expected fail | RED state from Browser QA root cause: disabled pilot lacked `macro_dimension_audit` when broad proxy coverage was short. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py::OverviewMarketContextAnalogServiceContractTests::test_historical_analog_keeps_macro_dimension_audit_when_broad_proxy_coverage_is_short -q` | Pass | GREEN state after wrapping early `_base_model()` returns with the dimension audit. |
| `git diff --check` | Pass | Re-run after disabled-pilot audit fix; no whitespace errors. |
| `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard_helpers.py finance/loaders/macro.py finance/loaders/sentiment.py` | Pass | Re-run after disabled-pilot audit fix; requested compile set exited 0. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Pass | Re-run after disabled-pilot audit fix: `364 passed, 3 third-party edgar deprecation warnings`. |
| `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true` | Pass | Fresh local server started at `http://localhost:8525` after restarting once to clear stale Streamlit process cache. |
| Browser QA at `http://localhost:8525` | Pass | `Workspace > Overview > Market Context` showed `Macro 조건 포함 pilot` and `맥락 차원 상태`; visible dimensions included `T10Y3M`, `VIXCLS`, `BAA10Y`, `Events calendar`, and `CNN / AAII sentiment history`. Latest, 20D, monthly, and selected-as-of mode all preserved the audit. Checked body text for forbidden copy: no `예측`, `추천`, `매수`, `매도`, `가능성이 높다`, `trade signal`, `trading signal`, or `monitoring signal`. |
| Browser QA screenshot | Captured | `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/overview-market-context-macro-dimension-audit-v3c-qa.png`; generated artifact, not staged. |
| `git diff --check` | Pass | Final re-run after cache-key/copy adjustments. |
| `uv run python -m py_compile app/services/overview_market_context_analog.py app/services/overview_market_intelligence.py app/web/overview_ui_components.py app/web/overview_dashboard_helpers.py finance/loaders/macro.py finance/loaders/sentiment.py` | Pass | Final re-run after cache-key/copy adjustments. |
| `uv run --with pytest python -m pytest tests/test_service_contracts.py -q` | Pass | Final full suite: `364 passed, 3 third-party edgar deprecation warnings`. |
