# Phase 12 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `recheck-readiness-freshness-contract-v1`

## TODO

- Define replay contract source priority for selected recheck readiness.
- Combine selected component contract, candidate replay contract, DB latest market date, default period, and symbol freshness into one operations preflight result or equivalent shared contract.
- Ensure missing / stale / failed / partial readiness evidence cannot look like pass.
- Keep price freshness as DB read-only evidence.
- Add focused contract tests for missing registry contract, stale / missing symbol freshness, and read-only execution boundary.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for monitoring notes or presets.
- Do not let `NOT_RUN`, stale, missing, or failed recheck evidence become pass.
