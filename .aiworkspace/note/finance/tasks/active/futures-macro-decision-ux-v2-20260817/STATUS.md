# Futures Macro Decision UX V2 Status

State: complete
Roadmap: 3/3 implementation, actual-data QA, and documentation complete
Last Updated: 2026-08-17

## Completed

- Active trade-date 5-minute collection now runs independently from completed-daily finalization.
- The Futures-only hero is compact and distinguishes active-session observation from completed-session fallback.
- The 1D / 5D / 20D cards report deterministic observed changes without reading instructions.
- `NO_EDGE` is shown as a completed negative validation result with sample, evaluation, and Brier evidence.
- The primary `Next Check` section is removed; calculation scope remains under methodology.
- Actual DB refresh and Browser QA confirmed current-session promotion, completed-session validation, responsive layout, and no console errors.

## Roadmap Closeout

1. Diagnosis and design approval - complete
2. Refresh routing and decision-first UI implementation - complete
3. Focused regression, actual-data Browser QA, documentation and commit - complete

## Durable Documentation

- Updated `docs/runbooks/OVERVIEW_MARKET_INTELLIGENCE.md` for active-session refresh routing,
  explicit `NO_EDGE` semantics, and the relocated calculation-scope disclosure.
