# Notes

Status: Active
Last Updated: 2026-06-07

## Findings

- `tasks/active` folder count: 170.
- `phases/active` folder count: 11.
- `tasks/done` currently contains only a README, so moving all completed tasks there would create a large path churn and likely break existing references.
- `phases/done` stores closeout summaries, not full board folder copies.
- `phases/active` has retained boards for UI engine boundary, investability decision foundation, Overview market intelligence, and Phase 8~13. All should be interpreted as retained records unless the README / roadmap lists a current active phase.

## Decision

Do not mass-move task / phase folders in this pass.

Instead:

- Keep `Current Active Tasks` and `Current Active Phases` as `none`.
- Add manifest docs that classify `active/` folders as retained work records.
- Leave physical archive migration as a later, explicitly scoped migration with link repair / redirect checks.

## Follow-Up Candidates

- Physical task archive migration with generated redirect index.
- Phase board migration or closeout-summary-only pruning.
- Research active/done state review after next product direction decision.
