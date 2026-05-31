# Risks

- Some legacy sources will only have cadence or old `avg_turnover` fields; the audit should treat them conservatively without breaking replay.
- Weighted / saved mix sources may need per-component turnover aggregation in later Phase 9 slices.
- The runtime estimate is still a holdings-delta approximation, not execution-level trade fill evidence.
- This task does not add slippage sensitivity; Phase 9-5 should use the compact turnover evidence as one input.
