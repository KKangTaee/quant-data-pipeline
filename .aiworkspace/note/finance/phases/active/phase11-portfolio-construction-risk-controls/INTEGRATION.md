# Phase 11 Portfolio Construction Risk Controls Integration

Status: Active
Created: 2026-05-29

## Integration Order

1. 11-1 construction risk source map / gap audit
2. 11-2 concentration / overlap / exposure contract
3. 11-3 correlation / risk contribution contract
4. 11-4 component role / weight discipline contract
5. 11-5 selected-route construction risk gate policy
6. 11-6 integrated QA / closeout

## Expected Touch Points

Implementation tasks may touch the following files after 11-1 confirms scope.

- `app/services/backtest_practical_validation_diagnostics.py`
- `app/services/backtest_practical_validation_provider_context.py`
- `app/services/backtest_practical_validation_stress_sensitivity.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_practical_validation.py`
- `app/web/backtest_final_review.py`
- `finance/loaders/provider.py`
- `tests/test_service_contracts.py`

11-1 should confirm whether the first implementation slice should start with holdings/exposure concentration or component return matrix risk contribution.

## QA Gates

For implementation tasks, run the smallest relevant set first, then broaden for gate / shared read model changes.

- `git diff --check`
- targeted `py_compile` for touched service / web files
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

## Storage Gate

Before closeout, confirm no new workflow JSONL registry, user memo, preset persistence, approval, order, or auto rebalance path was added.
