# Phase 12 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `selected-provider-evidence-staleness-contract-v1`

## TODO

- Define selected provider evidence staleness route for selected portfolios.
- Keep provider holdings / exposure / operability evidence DB-backed and read-only.
- Ensure stale provider snapshot, partial coverage, fallback symbol source, and missing holdings / exposure cannot look like pass.
- Connect provider evidence route to Phase 12 monitoring semantics without adding automatic monitoring log writes.
- Add focused contract tests for fresh actual provider evidence, stale evidence, partial coverage, missing provider DB, and read-only execution boundary.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for monitoring notes or presets.
- Do not let `NOT_RUN`, stale, missing, or failed recheck evidence become pass.
