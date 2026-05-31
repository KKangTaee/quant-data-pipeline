# Notes

## Initial Source Map

- `finance/strategy.py` strategy outputs often include `End Ticker`, `Next Ticker`, `End Balance`, `Next Balance`, and `Rebalancing`.
- `app/runtime/backtest.py` estimates turnover during `_apply_transaction_cost_postprocess(...)`.
- `app/runtime/history.py` persists compact runtime metadata into run history records.
- `app/web/backtest_candidate_review_helpers.py` and `app/services/backtest_practical_validation_source.py` move compact evidence into Practical Validation source snapshots.
- `app/services/backtest_realism_audit.py` reads existing compact evidence and renders the `Turnover evidence` row.

## Principle

- Actual holdings-derived turnover estimate is stronger than rebalance cadence.
- Rebalance cadence alone is useful but should stay `REVIEW`.
- Missing turnover and missing cadence should be `NEEDS_INPUT`.
- This remains evidence metadata, not a user memo or preset.

## Implemented Contract

- `turnover_model_contract_version`: `turnover_evidence_contract_v1`
- `turnover_estimation_status`: `estimated_from_holdings`, `not_estimated_missing_holdings`, or equivalent runtime status
- `turnover_source`: source of the estimate, currently holdings weight delta when available
- `turnover_input_missing_columns`: missing result columns when runtime cannot estimate turnover
- `turnover_observation_count`, `turnover_rebalance_rows`, `turnover_nonzero_count`
- `avg_turnover`, `max_turnover`, `avg_rebalance_turnover`
