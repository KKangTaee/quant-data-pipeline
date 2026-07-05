# Notes

## 2026-07-05 - Intake

User wants Practical Validation improvement to begin with V1 taxonomy analysis and roadmap refinement, not immediate implementation.

Main user goals:

- Practical Validation should be stage 2 evidence validation, not Final Review decision.
- Final Review selected-route judgment should not dominate the stage 2 screen.
- Current diagnostics / modules / audit boards / board map feel repetitive.
- `Monitoring Baseline` and `Tax / Account Scope` look more like stage 3 or Operations reference.
- React custom components should be used for high-interaction cards, not for a full app rewrite.

## Code Findings

Current file sizes:

- `app/web/backtest_practical_validation/page.py`: 2,586 lines.
- `app/web/backtest_practical_validation/components.py`: 500 lines.
- `source_summary.py`, `replay_panel.py`, `provider_actions.py`, `evidence_boards.py`: re-export only.
- `app/services/backtest_practical_validation_diagnostics.py`: 1,727 lines.
- `app/services/backtest_practical_validation_modules.py`: 744 lines.

Current data flow:

```text
source
  -> build_practical_validation_result
  -> 12 diagnostics
  -> data / construction / risk contribution / role-weight / realism / efficacy audits
  -> selected-route preflight
  -> validation module plan
  -> board map
  -> final review gate
```
## Stage Boundary Finding

The code already partially supports the desired boundary:

- `monitoring_baseline` is a `REFERENCE` module with `stage_owner="selected_dashboard"`.
- `tax_account_scope` is a `REFERENCE` module with `stage_owner="final_review"`.

The UI should make that distinction more visible by moving these out of the main 2단계 gate presentation.

## Selected-route Preflight Finding

`build_practical_validation_selected_route_preflight()` builds an investability evidence packet and runs Final Review selected-route policy before the user enters Final Review.

This is useful as a deterministic safety check, but the UI should not present it as the Final Review decision itself.

Recommended language:

- Good: `Final Review 준비 상태`
- Good: `선정 저장을 막을 명확한 근거 공백`
- Avoid: `Selected-route Gate` as the main stage-2 headline
- Avoid: `select_allowed` as a user-facing final decision state

## UI Duplication Finding

The current page shows:

- Final Review Gate
- Fix Queue
- validation modules
- board map
- diagnostics summary
- audit detail boards
- provider coverage
- look-through board
- robustness board
- raw diagnostics
- raw JSON

Most of this is valuable, but the first-read hierarchy should be reduced to:

```text
Gate Summary
Fix Queue
Core Evidence Workbench
Provider Actions
Save / Final Review Handoff
Technical Details
```
