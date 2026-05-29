# Correlation / Risk Contribution Contract V1 Runs

Status: Complete
Created: 2026-05-29

## Runs

- `.venv/bin/python -m py_compile app/services/backtest_risk_contribution_audit.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py`
  - Result: PASS
- `.venv/bin/python -m unittest tests.test_service_contracts.RiskContributionAuditContractTests`
  - Result: PASS, 4 tests
- `.venv/bin/python -m unittest tests.test_service_contracts`
  - Result: PASS, 105 tests
- `git diff --check`
  - Result: PASS
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
  - Result: PASS
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
  - Result: PASS; generated `finance/.DS_Store` remains unstaged
