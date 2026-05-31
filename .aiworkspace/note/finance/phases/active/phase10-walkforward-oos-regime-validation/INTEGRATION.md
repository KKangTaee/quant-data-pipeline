# Phase 10 Walk-forward / OOS / Regime Validation Integration

Status: Complete
Created: 2026-05-29

## Integration Order

1. 10-1 source map / gap audit
2. 10-2 walk-forward split contract - complete
3. 10-3 OOS holdout validation contract - complete
4. 10-4 regime split validation - complete
5. 10-5 selected-route gate policy refinement - complete
6. 10-6 integrated QA / closeout - complete

## Expected Touch Points

Implementation tasks may touch the following files after 10-1 confirms scope.

- `app/services/backtest_temporal_validation.py`
- `app/services/backtest_practical_validation_stress_sensitivity.py`
- `app/services/backtest_validation_efficacy.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_practical_validation.py`
- `app/web/backtest_final_review.py`
- `tests/test_service_contracts.py`
- DB / macro loader files only if regime source requires loader-backed evidence

10-1 confirmed that 10-2 should start with service-level temporal validation rather than UI-first changes.
10-2 added that service helper and connected it to Practical Validation and Validation Efficacy Audit.
10-3 extended the same helper with OOS holdout evidence and connected it to Practical Validation and Validation Efficacy Audit.
10-4 extended the helper with DB-backed macro regime split evidence and connected it to Practical Validation and Validation Efficacy Audit.
10-5 connected non-PASS Validation Efficacy row-level temporal / OOS / regime gaps to Final Review selected-route gate policy evidence.
10-6 verified compile, full service contracts, UI / engine boundary, refinement hygiene, diff check, and closeout docs.

## QA Gates

For implementation tasks, run the smallest relevant set first, then broaden for gate / shared read model changes.

- `git diff --check`
- targeted `py_compile` for touched service / web files
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

## Storage Gate

Before closeout, confirm no new workflow JSONL registry, user memo, preset persistence, approval, order, or auto rebalance path was added.
