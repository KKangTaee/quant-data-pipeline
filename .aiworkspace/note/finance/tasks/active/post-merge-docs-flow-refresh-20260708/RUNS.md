# Runs

## 2026-07-08

- `git status --short`: tracked 변경 없음. untracked QA screenshots 4개 확인.
- `git branch --show-current`: `master`.
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" .aiworkspace/note/finance AGENTS.md`: conflict marker 없음.
- `rg -n "Latest completed task|Current active task|Current active phase"`: Roadmap `Latest completed task` 중복 pointer 확인.
- `rg -n "Futures Monitor|Sector / Industry|Data Health|target_tab|alternate_surface|REFRESH_PLAN_BY_AREA" app/services/overview app/web/overview tests/test_service_contracts.py`: current docs와 달리 Overview service contract 일부가 legacy `Futures Monitor` / `Sector / Industry` path를 사용자-facing label로 출력하는 drift 확인.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_collection_ops_snapshot_combines_db_freshness_and_run_history tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_data_health_handoff_ranks_problem_rows_and_points_to_collection_surfaces tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_can_omit_futures_macro_for_fast_entry tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests.test_overview_macro_context_cockpit_summarizes_existing_context_snapshots`: expected fail. 새 `Futures Macro 1m OHLCV` row 미생성, handoff target fallback, futures refresh plan 누락 확인.
- GREEN: 같은 targeted unittest 4개 통과.
- `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`: 129 tests 통과. 기존 `edgar` deprecation warning과 Streamlit cache runtime warning만 출력.
- `git diff --check`: 통과.
- `.venv/bin/python -m py_compile app/services/overview/data_health.py app/services/overview/market_context.py app/web/overview/navigation.py app/web/overview/page.py app/web/overview/futures_macro.py app/web/overview/futures_macro_helpers.py app/services/futures_macro_thermometer.py app/services/futures_macro_validation.py`: 통과.
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" .aiworkspace/note/finance app tests AGENTS.md`: match 없음.
- `rg -n "Futures Monitor|Sector / Industry" app/services/overview app/web/overview app/web/overview_ui_components.py`: legacy alias / fallback copy 3건만 남음. Current output path drift는 없음.
- `rg -n "Latest completed task|Current active task|Current active phase|Latest completed docs cleanup task" ...`: `post-merge-docs-flow-refresh-20260708` latest pointer와 active none 상태 확인.
- Final `.venv/bin/python -m unittest tests.test_service_contracts.OverviewMarketIntelligenceServiceContractTests`: legacy `Futures Monitor 1m OHLCV` input alias 호환까지 포함해 129 tests 통과. 기존 `edgar` deprecation warning과 Streamlit cache runtime warning만 출력.
