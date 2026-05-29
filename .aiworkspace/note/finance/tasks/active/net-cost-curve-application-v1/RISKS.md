# Risks

- Legacy sources may not contain gross / net curve proof. They should remain conservative REVIEW / NEEDS_INPUT rather than being inferred as applied.
- `estimated_cost_total` and gross-net end balance delta are related but not identical because costs compound through the net curve.
- This task does not model slippage or market impact; it only proves the current cost postprocess reached the net result curve.
- Weighted / saved mix sources still may need component-level aggregation of net cost curve proof in a later Phase 9 slice if multiple components have different evidence quality.
