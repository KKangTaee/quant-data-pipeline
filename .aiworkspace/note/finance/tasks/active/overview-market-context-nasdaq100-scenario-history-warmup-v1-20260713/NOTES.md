# Overview Market Context Nasdaq-100 Scenario History Warmup V1 Notes

Last Updated: 2026-07-13

## Confirmed Facts

- `fomc_sep_projection` has 422 rows across 21 release vintages.
- Nasdaq monthly valuation storage has 119 rows but only 60 positive READY P/E months, spanning 2021-08 through 2026-07.
- A 60-month rolling window plus 12/36/60 visible months requires 71/95/119 positive history months.
- Current Nasdaq history options return one point and `INSUFFICIENT_HISTORY` for all 1y/3y/5y selections.
- S&P uses the same SEP input and returns 12/36/60 READY points because its loader provides a longer warmup.
- Nasdaq graph 2 currently inherits a React fallback label of `Robert Shiller TTM EPS`; the Nasdaq service must provide its actual reconstructed EPS metadata.

## Decisions

- Keep read-only render behavior; no automatic provider fetch on tab open.
- Keep synchronous user-triggered collection and existing resumable planner.
- Keep current 60-month coverage-blocker repair action separate from the 119-month history warmup action.
- Do not add a diagnostic operations panel; show only actionable required/current month evidence in the empty state.
- Nasdaq earnings source metadata is attached after the shared FOMC calculation so the shared S&P calculator remains instrument-neutral.
