# Prototype Legacy Cleanup / Removal Notes

## Decisions

- Treat Candidate Review / Portfolio Proposal / Pre-Live / old candidate packaging as prototype legacy, not current workflow.
- Preserve registry / saved JSONL and old helper modules unless they are proven unused and safe to delete.
- Preserve Backtest Run History and Candidate Library as Operations archive / recovery.
- Remove or hide Overview primary legacy Candidate Ops because it nudges the product back to Candidate Review / Portfolio Proposal.
- Keep compatible analysis submode route requests such as `Single Strategy`, `Compare & Portfolio Builder`, and `Portfolio Mix Builder`; only legacy candidate/proposal panels are removed from primary route targets.
- Convert Archive: Backtest Runs `Practical Validation으로 보내기` into a current source handoff rather than a legacy candidate-review draft.
- Keep `Selected Portfolio Dashboard` only as a legacy implementation/file/helper term; user-facing copy should say `Operations > Portfolio Monitoring`.

## Classification Outcome

| Surface | Outcome |
|---|---|
| Backtest Analysis / Practical Validation / Final Review | `KEEP_PRIMARY` |
| Operations > Portfolio Monitoring | `KEEP_PRIMARY`; legacy implementation file name retained |
| Operations > Archive: Backtest Runs | `ARCHIVE_RECOVERY`; now sends selected record to Practical Validation source handoff |
| Operations > Archive: Candidates | `ARCHIVE_RECOVERY`; legacy current/pre-live records only |
| Candidate Review / Portfolio Proposal panels | `HIDE_FROM_PRIMARY`, `DEFER_DELETE` for physical module deletion |
| Pre-Live / proposal / paper registries | `ARCHIVE_RECOVERY` / `DEFER_DELETE`; preserved and not rewritten |
| Overview Candidate Ops | `HIDE_FROM_PRIMARY`; tab removed from default Overview |

## Dirty Tree Baseline

Existing uncommitted/untracked local artifacts observed before edits:

- Modified: `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`
- Modified: `finance/.DS_Store`
- Untracked: `.aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl`
- Untracked QA screenshots in repo root, including `data-provenance-pit-contract-qa-20260609.png`, `monitoring-snapshot-review-loop-v2-qa-20260608.png`, and multiple `why-it-moved-*` screenshots.

These are treated as pre-existing local/generated artifacts and should not be staged for this task.
