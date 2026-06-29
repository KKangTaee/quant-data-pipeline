# Overview Market Context Events Data Trust V1 Status

Status: Completed
Created: 2026-06-12

## Current Status

- 2026-06-12: User approved 3차 scope on `sub-dev`; explicit out of scope includes similar-regime / prediction work.
- 2026-06-12: Intake docs and related 1차/2차/V3 task records read. Scope fixed to event coverage/read model, BLS parser fallback verification, Market Context event cue, and Data Health de-emphasis.
- 2026-06-12: DB coverage checked. Local `market_event_calendar` has FOMC / GDP / earnings rows, but no `MACRO_CPI` rows for `2026-06-10` or `2026-07-14`.
- 2026-06-12: RED/GREEN implementation complete. Event snapshots now default to recent 7D + upcoming horizon, major macro rows are prioritized over earnings, Macro Week Lane separates recent major and upcoming events, and BLS parser fixtures accept CPI/PPI abbreviations.
- 2026-06-12: Browser QA completed on `http://localhost:8525`. Market Context shows compact event/Data Health cues without job/raw row diagnostics; Events shows upcoming FOMC/GDP macro context and would render recent major macro section when rows exist.

## Scope State

- In scope: CPI/PPI/Employment/GDP/FOMC coverage inspection, recent+upcoming event read model, BLS HTML/ICS parser tests, compact Market Context event cues, Data Health minimal caveat, Browser QA, coherent commit.
- Out of scope: new providers, schema change, registry/saved rewrite, run-history/generated artifact staging, Backtest/Practical Validation/Final Review/Operations edits, similar-regime/prediction feature.

## Result

- `build_market_events_snapshot()` now scans from 7 days before `today` when no explicit start date is provided.
- Event snapshot rows include a `Window` field and prioritize FOMC / CPI / PPI / Employment / GDP ahead of earnings in context surfaces.
- `build_overview_macro_week_lane()` now returns `recent_items` and `upcoming_items` with schema `overview_macro_week_lane_v2`.
- Market Context event cue uses recent CPI/PPI/Employment/GDP/FOMC when present and otherwise shows the next major event compactly.
- BLS HTML / ICS parser fixtures now cover abbreviated `CPI` and `PPI` titles.
