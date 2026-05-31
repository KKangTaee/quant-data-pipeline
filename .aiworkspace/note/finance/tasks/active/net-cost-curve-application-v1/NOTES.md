# Notes

## Initial Source Map

- `app/runtime/backtest.py` applies transaction cost in `_apply_transaction_cost_postprocess(...)`.
- The helper creates `Gross Total Balance`, `Estimated Cost`, `Cumulative Estimated Cost`, `Net Total Balance`, and replaces `Total Balance` / `Total Return` with net values.
- Phase 9-1 already exposes cost source metadata.
- Phase 9-2 already exposes turnover evidence metadata.

## Principle

- `cost_application_status=applied_to_result_curve` is not enough by itself.
- Strong proof should include gross / net delta or positive estimated-cost rows.
- If turnover could not be estimated, the net curve may technically pass through the postprocess but should remain REVIEW because cost impact is not meaningfully proven.

## Implementation Notes

- Runtime contract version: `net_cost_curve_contract_v1`.
- Compact proof fields include `net_cost_curve_status`, `total_balance_is_net_of_cost`, row count, positive estimated-cost rows, `estimated_cost_total`, gross/net end balance, and gross-net end balance delta.
- `applied_with_measurable_cost` is the strong PASS path for Backtest Realism Audit.
- `applied_without_turnover_estimate`, `applied_no_cost_impact`, and zero-cost assumptions remain REVIEW.
- Missing cost input or missing net curve proof remains NEEDS_INPUT.
- The task reuses existing result bundle metadata, history record context, candidate draft snapshot, and Practical Validation source snapshot; it does not create a new JSONL registry.
