# Practical Validation Service Boundary Status

Status: Complete
Created: 2026-05-20

## Result

- `app/services/backtest_practical_validation.py` now owns Practical Validation source/result append and UI-neutral handoff contracts.
- `app/web/backtest_practical_validation.py`, `app/web/backtest_compare.py`, and `app/web/backtest_candidate_review_helpers.py` apply the returned handoff data to Streamlit session state.
- `app/web/backtest_practical_validation_helpers.py` no longer imports Streamlit or writes `st.session_state`.
- Provider gap collection and diagnostic formulas were intentionally left unchanged.
- Later follow-up slices moved provider gap orchestration, replay logic, and the large diagnostic builder into `app/services`.

## Next

- Further cleanup can reduce transitional dependencies from `app.services` back into `app.web.runtime` / connector helpers.
