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

## 4차 UI / Data Trust Contract Surface

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_ui_exposes_pit_monthly_snapshot_universe_contract`
  - Expected failure: Backtest UI common contract did not expose `PIT_MONTHLY_SNAPSHOT_UNIVERSE`.
- GREEN: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_ui_exposes_pit_monthly_snapshot_universe_contract tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_preset_basis_note_is_rendered_in_single_and_compare_forms tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_factor_single_forms_keep_guidance_inside_form_surface tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_portfolio_mix_builder_remains_streamlit_owned_with_strict_preset_copy`
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_compare/page.py tests/test_service_contracts.py`
- Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8512 --server.headless true --server.runOnSave false --server.fileWatcherType none`; verified Backtest > Quality > Advanced Inputs shows the three Universe Contract options and the always-visible PIT Monthly summary.
  - Screenshot artifact: `backtest-pit-monthly-universe-ui-qa.png` (generated, not committed).

## 5차 Docs / Final QA

- Docs sync: updated data semantics, DB schema map, data quality PIT notes, runtime flow, strategy implementation flow, Backtest UI flow, roadmap / index, and root handoff logs.
- Focused PIT contract QA: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_schema_and_payload_contract_rank_month_end_members tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_loader_groups_included_members_by_snapshot_date tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_loader_is_public_loader_contract tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_monthly_pit_universe_builder_recomputes_rank_per_month_end tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_upsert_syncs_schema_and_writes_snapshot_members tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_universe_build_and_store_reads_db_sources_once tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_pit_membership_snapshots_map_to_rebalance_dates_by_previous_snapshot tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_runner_resolves_pit_monthly_universe_inputs_from_loader tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_runner_wires_pit_membership_to_statement_shadow_samples tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_ui_exposes_pit_monthly_snapshot_universe_contract`
  - Result: 10 tests passed.
- Compile: `.venv/bin/python -m py_compile finance/data/pit_universe.py finance/loaders/universe.py finance/loaders/__init__.py finance/data/db/schema.py finance/sample.py app/runtime/backtest/runners/strict_factor.py app/web/backtest_common.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_compare/page.py tests/test_service_contracts.py`
- Diff hygiene: `git diff --check`
- Doc path smoke: `find .aiworkspace/note/finance -maxdepth 3 -type f | sort >/dev/null`

## Follow-up: PIT-only Visible Universe Contract

- RED: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_ui_exposes_pit_monthly_snapshot_universe_contract`
  - Expected failure: `Static Managed Research Universe` was still part of `STRICT_ANNUAL_UNIVERSE_CONTRACT_LABELS`.
- GREEN: same focused test passed after the visible label map was narrowed to `PIT Monthly Snapshot Universe`, while Static / Historical labels remain legacy display fallbacks.
- Focused regression: `.venv/bin/python -m unittest tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_ui_exposes_pit_monthly_snapshot_universe_contract tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_dynamic_runnable_coverage_overrides_candidate_pool_warning_when_target_filled tests.test_service_contracts.BacktestCandidateAnalysisHardeningTests.test_strict_runner_wires_pit_membership_to_statement_shadow_samples`
  - Result: 3 tests passed.
- Compile: `.venv/bin/python -m py_compile app/web/backtest_common.py app/web/backtest_single_forms/__init__.py app/web/backtest_single_forms/strict_factor.py app/web/backtest_compare/page.py tests/test_service_contracts.py`
- Diff hygiene: `git diff --check`
- Browser QA: `.venv/bin/python -m streamlit run app/web/streamlit_app.py --server.port 8514 --server.headless true --server.runOnSave false --server.fileWatcherType none`; verified Backtest > Single Strategy > Quality > Strict Annual > Advanced Inputs opens `Universe Contract` with only `PIT Monthly Snapshot Universe`; DOM text check returned Static/Historical false and PIT true.
  - Screenshot artifact: `backtest-universe-contract-pit-only-qa.png` (generated, not committed).
