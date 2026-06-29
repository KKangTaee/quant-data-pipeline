# Futures Monitor UX/UI V3 Notes

## Initial Findings

- The current UI has already moved away from peer tabs into a workspace skeleton, but still exposes English labels and table-first evidence.
- `Data Actions` mixes refresh mode, provider collection, and screen reload in one popover.
- `Macro Context` renders confidence and validation cards, but the confidence label can be misread as prediction quality rather than evidence quality.
- `futures_macro_thermometer.py` already computes `5D %`, so a recent 1-week context can be built without a DB change.

## Product Boundary

- Futures Monitor remains a read-only market context / investigation surface.
- Macro Thermometer historical validation is point-in-time historical consistency evidence, not a forecast guarantee.

## Implementation Notes

- Primary watch groups were reduced to `Pre-open Core`, `Equity Index`, `Rates`, `Commodities`, `FX Futures`, and `All`; optional micro / crypto groups are no longer first-level user choices.
- `Data Actions` became `데이터 갱신` with two visible modes: `수동` and `60초 자동 확인`. The previous 20초 fast mode is not exposed in this surface.
- `weekly_context` is derived from existing stored 1D futures `5D %` values. It adds no provider fetch during render and no DB schema change.
- `evidence_reading` translates existing strong / weak / conflicting / missing evidence groups into user-facing Korean explanations before raw score / component tables.
- Browser QA found residual English labels in live stale warnings, score evidence, and validation cautions; those were fixed in UI display adapters without changing service calculation contracts.
