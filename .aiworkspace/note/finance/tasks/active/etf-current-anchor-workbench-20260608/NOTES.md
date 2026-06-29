# Notes

Status: Completed
Last Verified: 2026-06-08

## Decisions

- 4A will not run ETF backtests or write current candidate rows.
- 4A will read actual workflow artifact rows when present, so the panel is no longer only a static direction guide.
- GRS remains the first ETF anchor target, but readiness is determined from latest run/source evidence rather than static maturity labels.

## Context

- 3D exposed ETF evidence gaps but did not connect local artifacts.
- `PORTFOLIO_SELECTION_SOURCES.jsonl` may be absent until the next Backtest Analysis source save; absence is a readiness gap, not storage drift.
- `BACKTEST_RUN_HISTORY.jsonl` is local/generated and normally not committed, but it can be read as local evidence in the UI.
- Provider / cost / benchmark evidence must remain explicit; missing fields are not treated as pass.

## Implementation Notes

- The service uses injected rows in tests to avoid dependence on local generated artifacts.
- In the live UI path, the service only reads runtime loaders for run history and portfolio selection source rows.
- `RERUN_REQUIRED` means no matching latest local DB-backed run row was found for that ETF strategy.
- `SOURCE_HANDOFF_REQUIRED` means a matching run exists but no Practical Validation source handoff row exists.
- `ANCHOR_EVIDENCE_REVIEW_REQUIRED` means run/source rows exist but provider / cost / benchmark / freshness evidence is still incomplete.
- `ANCHOR_READY_FOR_REVIEW` is a review input state only, not current-candidate promotion.
