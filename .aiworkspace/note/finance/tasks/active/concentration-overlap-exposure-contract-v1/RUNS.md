# Concentration / Overlap / Exposure Contract V1 Runs

Status: Complete
Created: 2026-05-29

## Commands

```bash
.venv/bin/python -m py_compile app/services/backtest_construction_risk_audit.py app/services/backtest_practical_validation_diagnostics.py app/services/backtest_evidence_read_model.py app/web/backtest_practical_validation.py app/web/backtest_final_review.py app/web/backtest_final_review_helpers.py
.venv/bin/python -m unittest tests.test_service_contracts.ConstructionRiskAuditContractTests
.venv/bin/python -m unittest tests.test_service_contracts
git diff --check
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py
.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py
find .aiworkspace/note/finance/tasks/active/concentration-overlap-exposure-contract-v1 .aiworkspace/note/finance/phases/active/phase11-portfolio-construction-risk-controls -type f | sort
```

## Result

- targeted py_compile: pass
- `ConstructionRiskAuditContractTests`: 3 tests pass
- full `tests.test_service_contracts`: 101 tests pass
- `git diff --check`: pass
- UI / engine boundary check: pass
- finance refinement hygiene: pass
- task / phase file list: present
