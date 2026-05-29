# Phase 12 Selected Monitoring / Recheck Operations Integration

Status: Active
Created: 2026-05-29

## Integration Order

1. 12-1 selected monitoring source map / gap audit: Next
2. 12-2 recheck readiness / freshness operations contract: Pending
3. 12-3 selected provider evidence staleness contract: Pending
4. 12-4 recheck comparison / review signal policy: Pending
5. 12-5 optional allocation drift evidence boundary: Pending
6. 12-6 decision dossier / continuity operations refinement: Pending
7. 12-7 integrated QA / closeout: Pending

## Expected Touch Points

Implementation tasks may touch the following files after 12-1 confirms scope.

- `app/runtime/final_selected_portfolios.py`
- `app/web/final_selected_portfolio_dashboard.py`
- `app/web/final_selected_portfolio_dashboard_helpers.py`
- `app/services/backtest_evidence_read_model.py`
- `app/web/backtest_final_review.py`
- `finance/loaders/prices.py` or existing price loader path if 12-1 confirms it
- `finance/loaders/provider.py`
- `tests/test_service_contracts.py`

## QA Gates

For implementation tasks, run the smallest relevant set first, then broaden for shared read model changes.

- `git diff --check`
- targeted `py_compile` for touched service / runtime / web files
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

## Storage Gate

Before closeout, confirm no new workflow JSONL registry, monitoring log automatic append, user memo, preset persistence, account integration, approval, order, or auto rebalance path was added.
