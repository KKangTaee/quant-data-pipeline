# Phase 9 Integrated QA Closeout Design

Status: Active
Created: 2026-05-29

## Verification Matrix

| Area | Check |
| --- | --- |
| Backtest Realism Audit | compile `app/services/backtest_realism_audit.py` |
| Final Review gate policy | compile `app/services/backtest_evidence_read_model.py` |
| Provider capacity context | compile `app/services/backtest_practical_validation_provider_context.py` |
| Service contracts | full `tests.test_service_contracts` |
| UI / service boundary | repo helper boundary checker |
| Artifact hygiene | repo helper refinement hygiene checker, `git status --short`, `git diff --check` |

## Closeout Rule

Phase 9 is complete when the above checks pass and docs show:

- Phase 9 board complete.
- Phase 9 closeout summary under `phases/done/`.
- Roadmap current work points to Phase 10 as the next hardening target.
- No generated artifact, run history, registry JSONL, saved setup, or `.DS_Store` is staged.
