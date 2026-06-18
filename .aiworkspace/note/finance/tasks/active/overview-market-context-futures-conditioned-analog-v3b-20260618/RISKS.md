# Risks

Status: Complete
Last Updated: 2026-06-18

## Remaining Risks

- Stored `ZN=F` / `ZB=F` daily futures rows may be absent or too short for some selected as-of dates; in that case the pilot shows `insufficient_conditions` and leaves the GLD/broad analog readable.
- Futures continuous symbols are provider proxy rows and do not model futures roll / maturity structure exactly.
- Combining GLD and futures buckets can shrink the sample to `REVIEW` or `INSUFFICIENT_CONTEXT`; this must remain a context-only distribution, not a decision gate.
- Selected as-of replay still uses current universe / sector metadata for broad analog leadership, as documented in 2차 and 3차-A.

## QA Result

- GLD and futures conditions were visibly separate in Browser QA.
- Broad analog rows remained available with Macro sample quality shown separately.
- Selected as-of / pattern window controls rendered, and the 20D path recalculated.
- Forbidden Korean copy list was absent from the Browser QA text check.
