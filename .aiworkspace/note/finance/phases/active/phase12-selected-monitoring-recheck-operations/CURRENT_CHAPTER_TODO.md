# Phase 12 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `selected-monitoring-source-map-v1`

## TODO

- Map current Selected Portfolio Dashboard read models.
- Identify which evidence comes from final decision row, DB loaders, runtime replay, session state, and optional user input.
- Confirm whether `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` is the canonical selected dashboard source in all relevant paths.
- Identify gaps where stale / missing / failed / partial evidence can look too permissive.
- Confirm no new persistence is required before implementation tasks.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for monitoring notes or presets.
- Do not let `NOT_RUN`, stale, missing, or failed recheck evidence become pass.
