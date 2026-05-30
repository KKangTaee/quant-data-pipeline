# Practical Validation Module Gate V1 Notes

Status: Active
Created: 2026-05-30

## Decisions

- Treat aggressive profiles as wider tolerance, not weaker evidence requirements.
- Do not remove existing diagnostics in the first implementation; classify them into module groups first.
- Latest runtime replay should be a required Practical Validation module before Final Review movement.
- Monitoring baseline belongs mostly to downstream review / Selected Dashboard context, not as a hard Practical Validation blocker.
- Conditional modules block Practical Validation handoff only on `BLOCKED`; `REVIEW` remains Final Review decision evidence.
- Single-component ETF-like candidates do not run weighted-mix-only risk contribution / component role gates.

## QA Notes

- The current GTAA candidate correctly shows `BLOCKED_FOR_FINAL_REVIEW` before latest replay is run because `latest_replay`, `validation_efficacy`, and `data_coverage` still need evidence.
- Browser QA found no console errors. Existing chart warnings remain from empty chart domains and were not introduced as gate failures.

## Dirty Tree Context

- Existing local generated changes include `BACKTEST_RUN_HISTORY.jsonl`, `PORTFOLIO_SELECTION_SOURCES.jsonl`, and `finance/.DS_Store`.
- These are not part of this implementation commit unless explicitly requested.
