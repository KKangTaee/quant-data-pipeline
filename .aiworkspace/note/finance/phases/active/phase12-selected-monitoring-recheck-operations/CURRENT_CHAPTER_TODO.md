# Phase 12 Current Chapter TODO

Status: Active
Created: 2026-05-29

## Current Chapter

Next task: `decision-dossier-continuity-operations-v1`

## TODO

- Confirm Decision Dossier, Continuity, Timeline, and Review Signals read the same selected decision source.
- Check whether dossier / continuity labels still imply legacy Phase36 or monitoring history persistence.
- Ensure session-state recheck / drift / alert evidence is not described as durable monitoring history.
- Add focused contract tests if source consistency or boundary behavior changes.

## Stop Conditions

- Do not implement account integration, order draft, approval, auto rebalance, or automatic monitoring log append.
- Do not add a new JSONL registry for monitoring notes or presets.
- Do not let Decision Dossier or Continuity imply live approval, saved monitoring history, order draft, or auto rebalance.
