# Practical Validation Replay Service Boundary Status

Status: Complete
Created: 2026-05-20

## Progress

- Task opened as the next Practical Validation service boundary slice.
- Current replay helper is Streamlit-free but stored under `app/web`.
- Moved replay helper to `app/services/backtest_practical_validation_replay.py`.
- Updated Practical Validation UI to import replay constants / plan / runner from `app.services`.
- Added replay plan and blocked replay service contract tests.
- Updated project map, script map, flow docs, runbook, and root handoff logs.

## Result

- Practical Validation UI now owns only mode selection, button handling, session state, and result rendering.
- Replay service owns recheck plan generation and actual replay result construction.
