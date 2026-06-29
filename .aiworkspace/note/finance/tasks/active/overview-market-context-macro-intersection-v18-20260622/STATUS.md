# Overview Market Context Macro Intersection V18 Status

Status: Complete
Date: 2026-06-22

## Current

- V18 started after user confirmed the Macro condition display should show independent condition counts and final intersection instead of an order-dependent sequence.

## Done

- Added `macro_condition_counts` to the Macro conditioned analog model:
  - `broad`: broad sector ETF vs SPY analog sample
  - `gld`: broad anchors with the same GLD bucket
  - `futures`: broad anchors with the same Rate Pressure futures bucket
  - `futures_available`: broad anchors with computable futures buckets
  - `intersection`: anchors where both GLD and futures buckets match
- Changed the Macro basis bar from sequential `GLD -> futures` copy to `기본 / GLD 같은 상태 / 금리선물 같은 상태 / 두 조건 모두`.
- Kept final conditioned rows based on the intersection sample.
- Verified focused RED/GREEN tests, full service contracts, py_compile, diff check, and Browser QA.

## Next

- No immediate follow-up required for this slice.
