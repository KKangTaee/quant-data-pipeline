# Risks

Status: Active
Last Updated: 2026-06-18

## Remaining Risks

- GLD is a price proxy, not a full macro regime explanation. It only adds a safe-haven / gold context bucket.
- Macro conditioning narrows samples. A `REVIEW` or `INSUFFICIENT_CONTEXT` pilot state should be read alongside the broad analog result.
- Live QA on 2026-06-18 showed Basic Materials / XLB as the leadership proxy with only `63 / 756` stored price rows, so the current local UI correctly displays insufficient context rather than a calculated pilot sample.
- Current as-of replay still uses current universe / sector metadata plus DB prices through selected as-of; full PIT sector membership remains out of scope.
- Stored futures daily OHLCV may be useful for 3차-B, but it was not used in this pilot.
- FRED rates, events, and sentiment conditioning are not implemented and must not be inferred from the current pilot.

## QA Risks To Check

- The pilot block should be visually separate from broad analog.
- Disabled / insufficient conditions should look natural rather than like a failed job table.
- Browser QA should confirm forbidden Market Context copy was not introduced in the historical analog area.
