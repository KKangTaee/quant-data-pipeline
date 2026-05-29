# Notes

## Source Map

- Cost input comes from Backtest UI payload fields such as `transaction_cost_bps`.
- Runtime wrappers pass the value into `app/runtime/backtest.py`.
- `_apply_real_money_hardening(...)` calls `_apply_transaction_cost_postprocess(...)`.
- `_apply_transaction_cost_postprocess(...)` estimates turnover, computes `Estimated Cost`, stores gross/net columns, and replaces `Total Balance` / `Total Return` with net values.
- Candidate / Practical Validation handoff uses compact source snapshots; this is the right boundary for cost evidence because it is validation evidence, not user memo storage.

## Principle

- `transaction_cost_bps` alone is an assumption.
- A PASS candidate requires proof that cost was applied to the result curve.
- `real_money_hardening=True` is useful context, but the audit should prefer explicit cost application contract fields.

## Implemented Contract

- `cost_model_contract_version`: `cost_model_source_contract_v1`
- `cost_model_source`: runtime helper that applied the cost postprocess
- `cost_application_status`: `applied_to_result_curve` when `Total Balance` / `Total Return` are net of estimated cost
- `cost_application_target`: the affected result columns
- `cost_turnover_source`: the turnover estimate source
- `estimated_cost_total`, `avg_turnover`, `gross_end_balance`, `net_end_balance`: compact proof fields
