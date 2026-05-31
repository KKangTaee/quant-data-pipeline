# Status

## 2026-05-31

- Task opened.
- Existing flow reviewed:
  - `app/runtime/final_selected_portfolios.py` already converts selected Final Decision V2 rows into Selected Dashboard rows.
  - `app/web/final_selected_portfolio_dashboard.py` already renders continuity, timeline, recheck, provider, and allocation evidence.
  - `app/web/backtest_final_review.py` already renders saved decision ledger and dossier but does not summarize dashboard handoff readiness.
- Implementation will add a read-only handoff read model and compact UI surfaces in Final Review / Selected Dashboard.
- Implemented:
  - `build_selected_dashboard_handoff_review()` in `app/runtime/final_selected_portfolios.py`.
  - Final Review Saved Decision Review now shows selected rows, dashboard rows, monitorable / blocked counts, handoff table, checklist, and storage boundary.
  - `Operations > Selected Portfolio Dashboard` now shows the same Final Review handoff state above empty / selected portfolio details.
  - service contracts cover selected row ready, no selected route, and blocked dashboard contract scenarios.
- Verification passed with focused tests, full service contracts, diff check, and Browser QA.
