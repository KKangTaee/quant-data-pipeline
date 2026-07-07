# Runs

Command logs for this task.

## 1차 Schema / Loader

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_schema_and_payload_contract_rank_month_end_members`
  - Expected failure: `PIT_UNIVERSE_SCHEMAS` missing.
- GREEN: same focused test passed after adding `finance/data/pit_universe.py` and schema constants.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_loader_groups_included_members_by_snapshot_date`
  - Expected failure: `load_pit_universe_membership_snapshots` missing.
- GREEN: focused loader tests passed after adding loader helpers and public export.
- Compile: `.venv/bin/python -m py_compile finance/data/pit_universe.py finance/loaders/universe.py finance/loaders/__init__.py finance/data/db/schema.py tests/test_service_contracts.py`

## 2차 Monthly Builder

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_monthly_pit_universe_builder_recomputes_rank_per_month_end tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_upsert_syncs_schema_and_writes_snapshot_members`
  - Expected failure: monthly builder / upsert helpers missing.
- GREEN: monthly payload and upsert helper tests passed after adding `build_monthly_equity_universe_snapshot_payloads` and `upsert_equity_universe_snapshot_payload`.
- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_build_and_store_reads_db_sources_once`
  - Expected failure: source orchestration helper missing.
- GREEN: orchestration test passed after adding `build_and_store_monthly_equity_universe_snapshots`.
- Compile: `.venv/bin/python -m py_compile finance/data/pit_universe.py tests/test_service_contracts.py`

## 3차 Strict Runner Wiring

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_runner_wires_pit_membership_to_statement_shadow_samples`
  - Expected failure: only the Quality shared runner passed `pit_membership_snapshots`; Value and Quality+Value runners were still dynamic-only.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_membership_snapshots_map_to_rebalance_dates_by_previous_snapshot tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_runner_resolves_pit_monthly_universe_inputs_from_loader tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_runner_wires_pit_membership_to_statement_shadow_samples`
- Compile: `.venv/bin/python -m py_compile finance/sample.py app/runtime/backtest/runners/strict_factor.py tests/test_service_contracts.py`
