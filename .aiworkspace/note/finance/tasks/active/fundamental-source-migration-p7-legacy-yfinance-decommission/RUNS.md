# Runs

## TDD

- RED: focused tests for removing legacy broad collection cards initially failed because the cards were still present.
- GREEN: `uv run python -m unittest tests.test_service_contracts.BoundaryContractHardeningTests.test_ingestion_ui_removes_legacy_broad_collection_cards_but_keeps_compatibility_actions tests.test_service_contracts.BoundaryContractHardeningTests.test_quality_snapshot_form_marks_broad_yfinance_as_history_replay_only`
  - Result: passed, 2 tests.

## Verification

- `git diff --check`
  - Result: passed.
- `uv run python -m py_compile app/web/ingestion_console.py app/web/backtest_single_forms.py app/jobs/ingestion_jobs.py app/jobs/run_history.py app/runtime/backtest_strict.py app/runtime/candidate_library.py app/services/backtest_execution.py`
  - Result: passed.
- `uv run --with pytest python -m pytest tests/test_service_contracts.py -q -k "fundamental or factor or backtest or market_mover or ingestion"`
  - Result: 123 passed, 377 deselected, 3 warnings.
- `rg -n "load_fundamental_snapshot|load_factor_snapshot|nyse_fundamentals|nyse_factors|upsert_fundamentals|upsert_factors" app finance tests .aiworkspace/note/finance/docs`
  - Result: expected compatibility surfaces remain in loaders, data writers, ingestion job handlers, docs, and replay/evidence tests.

## Browser QA

- Server: `uv run streamlit run app/web/streamlit_app.py --server.port 8525 --server.headless true`
- Page: `http://localhost:8525/ingestion`
- Checks:
  - No Traceback / ImportError.
  - Manual tab does not show `Legacy broad yfinance fundamentals / factors`, `핵심 시장 데이터 일괄 수집`, `펀더멘털 수동 수집`, or `팩터 수동 계산`.
  - Manual tab still shows `가격 이력 수동 수집`, `상세 재무제표 수동 수집`, `재무제표 shadow 재구성`, and `재무제표 universe coverage QA`.
- Screenshot: `.aiworkspace/note/finance/run_artifacts/ingestion_legacy_broad_cards_removed_20260630.png` (generated/local artifact, not staged).
