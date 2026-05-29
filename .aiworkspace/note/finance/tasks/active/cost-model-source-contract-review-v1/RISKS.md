# Risks

- Old saved sources may not contain the new explicit cost contract. Treating them conservatively can move some rows from PASS to REVIEW, which is intended for realism hardening.
- Broad nested key search can accidentally read a component-level value in weighted sources. Phase 9-2/9-3 should refine per-component cost aggregation if needed.
- The cost model is still an estimated turnover x bps postprocess, not a full slippage / market impact simulator.
