# Evidence Read Model Boundary Notes

## Observations

- `app/web/backtest_final_review_helpers.py` is already Streamlit-free but lives under `app/web`.
- `app/web/final_selected_portfolio_dashboard_helpers.py` builds evidence rows from the saved final decision snapshot.
- Both areas read the same final decision row fields:
  - `decision_evidence_snapshot`
  - `risk_and_validation_snapshot`
  - `paper_tracking_snapshot`
  - `selected_components`
- The first service slice can be behavior-preserving because it only returns plain display rows.

## Decisions

- Evidence read model service returns list/dict rows only.
- DataFrame creation stays in web helper files.
- Registry load/append stays outside this service.
