# Risks

Status: Active
Last Updated: 2026-07-05

## Open Risks

### Selected-route preflight wording may still confuse stage boundaries

Risk: Keeping selected-route preflight inside Practical Validation can still feel like Final Review is happening early.

Mitigation: V2 should rename and reposition it as `Final Review readiness preview`, with raw policy rows collapsed.

### React-first implementation would only polish the current repetition

Risk: Building React components before read-model grouping could make the existing taxonomy confusion look nicer without fixing workflow clarity.

Mitigation: V1/V3 should establish grouping contracts before V5 React work.

### Physical split of `page.py` can create churn without product clarity

Risk: Moving render functions into files before deciding ownership can produce mechanical refactor churn.

Mitigation: V4 should first define 5-flow UI ownership, then V6 should split files by that ownership.

### `Tax / account scope` and `Monitoring Baseline` may be policy-relevant later

Risk: Demoting these from stage-2 visual priority could hide useful downstream context.

Mitigation: Keep them in downstream reference / technical detail, not deleted.

### Browser QA is not needed for planning but will be mandatory for UI implementation

Risk: This planning task can close without screenshot, but V4/V5/V6 UI work must include Browser QA and screenshot.

Mitigation: Each implementation version should have its own QA / commit unit.

## Approval Required Before Implementation

Before V1 implementation starts, confirm:

- selected-route preflight should be retained as readiness preview
- `Monitoring Baseline` should move to downstream reference
- `Tax / Account Scope` should move to Final Review reference
- V1 should start with read-model grouping, not visual React work
