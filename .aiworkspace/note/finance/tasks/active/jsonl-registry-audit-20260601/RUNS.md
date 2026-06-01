# Runs

## 2026-06-01

- `find .aiworkspace/note/finance -path '*.jsonl' -type f | sort`
  - Existing JSONL files: 13.
- `.venv/bin/python` JSONL parse script over `.aiworkspace/note/finance/**/*.jsonl`
  - Result: all 13 files parsed successfully; 109 JSON object rows; 0 invalid rows.
- `rg` over `app`, `tests`, `.aiworkspace/plugins`
  - Confirmed current consumers for V2 registries, selected dashboard saved state, legacy registries, saved portfolios, and run history.
- `.venv/bin/python` read-model check using `app.runtime.portfolio_selection_v2` and `app.runtime.final_selected_portfolios`
  - Result: Final Decision V2 selected rows 4, dashboard rows 4, assigned references 4, missing references 0.
- `.venv/bin/python -m pytest ...`
  - Result: not run; `.venv` has no `pytest` module.
- `.venv/bin/python -m unittest ...`
  - Result: 6 focused service contract tests passed.
- `git diff --check`
  - Result: passed.

## 2026-06-01 Cleanup Execution

- Created archive `.aiworkspace/note/finance/archive/jsonl-registry-audit-20260601/20260601T152645KST/`.
  - Archived 13 pre-cleanup JSONL files.
  - Wrote `manifest.json` with row count, SHA-256, action, and policy metadata.
- Removed 10 active JSONL files after archive verification:
  - 8 registry files: legacy/prototype or current-but-not-selected rows.
  - 2 run history files: local/generated history.
- Active JSONL after cleanup:
  - `registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`
  - `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`
  - `saved/SAVED_PORTFOLIOS.jsonl`
- Archive manifest verification:
  - 13 entries.
  - SHA-256 and row counts matched archived files.
- Selected Dashboard read model:
  - final rows `4`, selected rows `4`, dashboard rows `4`, assigned `4`, missing `0`, duplicates `0`, handoff `HANDOFF_READY`.
- Focused service contracts:
  - 6 `unittest` tests passed.
- `git diff --check`
  - passed.

## Focused service contracts

Passed tests:

- `PracticalValidationServiceContractTests.test_practical_validation_registry_serializes_db_scalar_payloads`
- `SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_monitoring_portfolio_saved_state_crud_is_soft_delete`
- `SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_portfolio_state_joins_selected_strategy_pool`
- `SelectedPortfolioMonitoringTimelineContractTests.test_selected_dashboard_handoff_review_links_selected_final_review_rows`
- `SelectedPortfolioMonitoringTimelineContractTests.test_recheck_readiness_uses_embedded_final_decision_contract_without_registry`
- `DecisionDossierContractTests.test_decision_dossier_is_read_only_markdown_export`
