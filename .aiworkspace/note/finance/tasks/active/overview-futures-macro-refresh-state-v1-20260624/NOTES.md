# Overview Futures Macro Refresh State V1 Notes

## Root Cause

- The collector was not stuck at `2026-06-23`; stored 1D futures data had already advanced to `2026-06-24`.
- A still-open Streamlit process could keep a stale futures macro snapshot for up to 15 minutes because cache key did not include the latest stored daily candle marker.
- The `Futures Macro` tab rendered the macro panel directly, so users had no obvious tab-local way to trigger daily collection or clear the macro snapshot cache.

## Boundary

- `Market Context` remains light and does not default-load futures macro validation.
- `Futures Macro` owns explicit futures daily refresh and snapshot reload actions.
