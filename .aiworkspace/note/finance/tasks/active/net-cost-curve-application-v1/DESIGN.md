# Design

## Contract

`net_cost_curve_contract_v1` is a compact proof that existing transaction-cost postprocessing reached the net result curve.
It is read by Backtest Realism Audit and preserved through existing result metadata / source snapshot handoff.

## Fields

- `net_cost_curve_status`
- `net_cost_curve_application_target`
- `total_balance_is_net_of_cost`
- `net_cost_curve_rows`
- `estimated_cost_total`
- `estimated_cost_positive_rows`
- `gross_start_balance`
- `gross_end_balance`
- `net_end_balance`
- `gross_net_end_balance_delta`
- `turnover_estimation_status`

## Status Semantics

- `applied_with_measurable_cost`: PASS candidate; positive estimated-cost rows and measurable gross-net delta exist.
- `applied_without_turnover_estimate`: REVIEW; the postprocess ran, but turnover evidence is weak or missing.
- `applied_zero_cost_bps`: REVIEW; zero-cost assumption must be intentional.
- `applied_no_cost_impact`: REVIEW; cost input exists but measurable impact was not proven.
- missing contract / missing cost input: NEEDS_INPUT.

## Storage Boundary

This task does not create a new JSONL registry, user memo field, preset save path, broker order, live approval, or auto rebalance behavior.
It only carries compact evidence through existing runtime metadata, history context, candidate draft snapshot, and Practical Validation source snapshot.
