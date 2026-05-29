# Phase 12 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `recheck-comparison-review-signal-policy-v1`

## TODO

- Make Recheck Comparison the policy owner for review signal performance thresholds.
- Remove or align duplicated CAGR / MDD / benchmark spread threshold logic in Review Signals.
- Ensure missing, failed, partial, or stale recheck evidence cannot become `Clear`.
- Keep Review Signals read-only and session evidence clearly separate from durable monitoring logs.
- Add focused contract tests for ready / watch / breached / needs-input signal mapping.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for monitoring notes or presets.
- Do not let `NOT_RUN`, stale, missing, or failed recheck evidence become pass.
