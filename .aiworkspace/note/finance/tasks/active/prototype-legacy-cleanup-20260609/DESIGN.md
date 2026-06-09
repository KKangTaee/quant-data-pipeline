# Prototype Legacy Cleanup / Removal Design

Status: Implemented pending verification
Last Updated: 2026-06-09

## Current Workflow Boundary

Primary workflow:

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

Legacy compatibility surfaces can remain only when they do not look like primary product flow and do not rewrite current registry / saved source-of-truth.

## Initial Inventory

| Surface | Evidence | Classification | Direction |
|---|---|---|---|
| `Backtest Analysis` route | `BACKTEST_STAGE_OPTIONS`, `render_backtest_analysis_workspace` | `KEEP_PRIMARY` | Keep as source creation stage |
| `Practical Validation` route | `BACKTEST_STAGE_OPTIONS`, `render_practical_validation_workspace` | `KEEP_PRIMARY` | Keep as evidence/gate stage |
| `Final Review` route | `BACKTEST_STAGE_OPTIONS`, `render_final_review_workspace` | `KEEP_PRIMARY` | Keep as selected-route decision stage |
| `Operations > Portfolio Monitoring` | top navigation page title is current, implementation file is legacy name | `KEEP_PRIMARY` | Keep user-facing route; do not rename file in this task |
| `Operations > System / Data Health` | Operations primary lane | `KEEP_PRIMARY` | Keep |
| Backtest Run History | Operations page label is `Archive: Backtest Runs`; supports inspect / run again / load into form | `ARCHIVE_RECOVERY` | Keep under Operations archive / recovery |
| Candidate Library | Operations page label is `Archive: Candidates`; reads old candidate registries | `ARCHIVE_RECOVERY` | Keep under Operations archive / recovery, read-only/replay meaning only |
| Candidate Review route/panel | imported and direct-dispatched from `app/web/pages/backtest.py`; route helper accepts legacy target | `HIDE_FROM_PRIMARY` first, `DEFER_DELETE` for file removal | Remove from valid primary route targets and direct dispatch; keep module files until migration proof |
| Portfolio Proposal route/panel | imported and direct-dispatched from `app/web/pages/backtest.py`; route helper accepts legacy target | `HIDE_FROM_PRIMARY` first, `DEFER_DELETE` for file removal | Remove from valid primary route targets and direct dispatch; keep module files until migration proof |
| Pre-Live registry helpers | old current/pre-live/proposal chain still used by Candidate Library / Overview helper | `DEFER_DELETE` | Keep registry helpers, stop primary UI nudges toward Pre-Live |
| Overview Candidate Ops tab | primary Overview tab loads old current/pre-live/proposal registries and links to Candidate Review / Portfolio Proposal | `HIDE_FROM_PRIMARY` | Remove from Overview primary tabs and stop snapshot load from old candidate ops |
| Candidate Review / Proposal implementation files | large old workflow modules | `DEFER_DELETE` | Do not delete in this task unless imports become fully unreferenced and tests prove safe |
| `CURRENT_CANDIDATE_REGISTRY`, `PRE_LIVE_CANDIDATE_REGISTRY`, `PORTFOLIO_PROPOSAL_REGISTRY`, paper ledger | workflow registry files / helpers | `ARCHIVE_RECOVERY` / `DEFER_DELETE` | Preserve, do not rewrite; no longer source-of-truth for current workflow |

## Implementation Direction

1. Add failing route/navigation tests that prove legacy panel targets are no longer valid primary Backtest route targets and direct active panels normalize to current stages.
2. Update Backtest route helper so valid route targets are current stages plus compatible analysis modes only. Candidate Review and Portfolio Proposal should no longer be accepted route targets.
3. Remove direct imports and direct dispatch branches for Candidate Review and Portfolio Proposal from `app/web/pages/backtest.py`.
4. Update Backtest page copy from Selected Dashboard / candidate packaging wording to Portfolio Monitoring and current workflow wording.
5. Remove Overview primary `Candidate Ops` tab and avoid loading old candidate/proposal registries in the default Overview snapshot.
6. Keep Operations archive pages for Backtest Runs and Candidates.
7. Sync durable docs so old Candidate Review / Proposal / Pre-Live text is not described as current workflow.

## Implementation Result

- Backtest route helper now exposes current stages plus compatible analysis submodes only.
- Backtest page shell dispatches only `Backtest Analysis`, `Practical Validation`, and `Final Review`.
- Overview primary tabs no longer include `Candidate Ops`.
- Archive: Backtest Runs sends selected records to Practical Validation source handoff instead of legacy Candidate Review draft state.
- Durable docs describe Candidate Review / Portfolio Proposal / Pre-Live records as legacy archive / recovery compatibility, not primary workflow.

## Testing Direction

- `tests/test_service_contracts.py`: add focused route helper tests for valid targets and legacy panel rejection.
- `py_compile`: Backtest route/page, Overview dashboard/helper, Operations overview, legacy modules if still present.
- `git diff --check`.
- Browser QA if Streamlit can run and UI navigation change is visible.
