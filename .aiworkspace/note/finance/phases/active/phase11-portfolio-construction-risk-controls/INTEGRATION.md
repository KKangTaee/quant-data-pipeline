# Phase 11 Portfolio Construction Risk Controls Integration

Status: Active
Created: 2026-05-29

## Integration Order

1. 11-1 construction risk source map / gap audit: Complete
2. 11-2 concentration / overlap / exposure contract: Complete
3. 11-3 correlation / risk contribution contract: Complete
4. 11-4 component role / weight discipline contract: Complete
5. 11-5 selected-route construction risk gate policy: Next
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

11-2 wrapped existing provider look-through evidence into `construction_risk_audit_v1`.
The new contract is read-only and does not add DB collectors or JSONL registries.
11-3 wrapped component return correlation / volatility contribution proxy / drop-one dependency evidence into `risk_contribution_audit_v1`.
11-4 wrapped explicit proposal role / target weight / weight reason / profile intent evidence into `component_role_weight_audit_v1`.
11-5 should connect the three construction risk audit routes to selected-route gate policy next.

## QA Gates

For implementation tasks, run the smallest relevant set first, then broaden for gate / shared read model changes.

- `git diff --check`
- targeted `py_compile` for touched service / web files
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

## Storage Gate

Before closeout, confirm no new workflow JSONL registry, user memo, preset persistence, approval, order, or auto rebalance path was added.
