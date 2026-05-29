# Phase 12 Selected Monitoring / Recheck Operations Integration

Status: Active
Created: 2026-05-29

## Integration Order

1. 12-1 selected monitoring source map / gap audit: Complete
2. 12-2 recheck readiness / freshness operations contract: Complete
3. 12-3 selected provider evidence staleness contract: Complete
4. 12-4 recheck comparison / review signal policy: Complete
5. 12-5 optional allocation drift evidence boundary: Complete
6. 12-6 decision dossier / continuity operations refinement: Next
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

12-2 touched `app/runtime/final_selected_portfolios.py`, `app/runtime/__init__.py`, `app/web/final_selected_portfolio_dashboard.py`, `app/web/final_selected_portfolio_dashboard_helpers.py`, and `tests/test_service_contracts.py`.
DB loader changes were not required; the existing latest market date and price freshness loaders were sufficient.

12-3 touched `app/runtime/final_selected_portfolios.py`, `app/runtime/__init__.py`, `app/web/final_selected_portfolio_dashboard.py`, `app/web/final_selected_portfolio_dashboard_helpers.py`, and `tests/test_service_contracts.py`.
Provider loader changes were not required; selected monitoring policy was applied above the existing provider context read model.

12-4 touched `app/runtime/final_selected_portfolios.py`, `app/runtime/__init__.py`, `app/web/final_selected_portfolio_dashboard.py`, `app/web/final_selected_portfolio_dashboard_helpers.py`, and `tests/test_service_contracts.py`.
Review Signals now derives performance threshold rows from Recheck Comparison and includes preflight / provider routes.

12-5 touched `app/runtime/final_selected_portfolios.py`, `app/runtime/__init__.py`, `app/web/final_selected_portfolio_dashboard.py`, `app/web/final_selected_portfolio_dashboard_helpers.py`, and `tests/test_service_contracts.py`.
Actual Allocation now exposes `selected_allocation_drift_evidence_boundary_v1` and keeps drift / alert preview evidence read-only and session-only.

12-6 is expected to touch Decision Dossier / Continuity / Timeline source consistency rather than adding persistence.

## QA Gates

For implementation tasks, run the smallest relevant set first, then broaden for shared read model changes.

- `git diff --check`
- targeted `py_compile` for touched service / runtime / web files
- `.venv/bin/python -m unittest tests.test_service_contracts`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`

## Storage Gate

Before closeout, confirm no new workflow JSONL registry, monitoring log automatic append, user memo, preset persistence, account integration, approval, order, or auto rebalance path was added.
