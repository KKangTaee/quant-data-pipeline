# Validation Efficacy Gate Policy Refinement V2 Runs

Status: Complete
Created: 2026-05-29

## Runs

| Command | Result |
| --- | --- |
| `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py` | Pass |
| `.venv/bin/python -m unittest tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_gate_policy_surfaces_temporal_oos_and_regime_review_rows tests.test_service_contracts.FinalReviewEvidenceReadModelContractTests.test_gate_policy_blocks_selected_route_on_temporal_oos_needs_input` | Pass |
| `.venv/bin/python -m py_compile app/services/backtest_evidence_read_model.py app/services/backtest_validation_efficacy.py app/services/backtest_temporal_validation.py app/services/backtest_practical_validation_diagnostics.py` | Pass |
| `.venv/bin/python -m unittest tests.test_service_contracts` | Pass, 98 tests |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py` | Pass |
| `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py` | Pass; existing generated `finance/.DS_Store` remains unstaged |
| `git diff --check` | Pass |
