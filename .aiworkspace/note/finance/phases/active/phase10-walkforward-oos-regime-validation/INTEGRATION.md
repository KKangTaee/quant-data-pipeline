# Phase 10 Walk-forward / OOS / Regime Validation Integration

Status: Active
Created: 2026-05-29

## Integration Order

1. 10-1 source map / gap audit
2. 10-2 walk-forward split contract
3. 10-3 OOS holdout validation contract
4. 10-4 regime split validation
5. 10-5 selected-route gate policy refinement
6. 10-6 integrated QA / closeout

## Expected Touch Points

Implementation tasks may touch the following files after 10-1 confirms scope.

- `app/services/backtest_practical_validation_stress_sensitivity.py`
- `app/services/backtest_validation_efficacy.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_practical_validation.py`
- `app/web/backtest_final_review.py`
- `tests/test_service_contracts.py`
- DB / macro loader files only if regime source requires loader-backed evidence

## QA Gates

For implementation tasks, run the smallest relevant set first, then broaden for gate / shared read model changes.

- `git diff --check`
- targeted `py_compile` for touched service / web files
- `.venv/bin/python -m pytest tests/test_service_contracts.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

## Storage Gate

Before closeout, confirm no new workflow JSONL registry, user memo, preset persistence, approval, order, or auto rebalance path was added.
