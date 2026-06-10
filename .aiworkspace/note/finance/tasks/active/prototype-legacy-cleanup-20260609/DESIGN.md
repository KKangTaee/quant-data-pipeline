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
| Candidate Review route/panel | formerly imported and direct-dispatched from `app/web/pages/backtest.py`; route helper accepted legacy target | `DELETE_NOW` after 5C audit | Removed from valid primary route targets and direct dispatch; UI/helper modules deleted after current handoff extraction |
| Portfolio Proposal route/panel | formerly imported and direct-dispatched from `app/web/pages/backtest.py`; route helper accepted legacy target | `DELETE_NOW` after 5C audit | Removed from valid primary route targets and direct dispatch; UI/helper modules deleted after Final Review current helper extraction |
| Pre-Live registry helpers | old current/pre-live/proposal chain still used by Candidate Library and Portfolio Monitoring fallback compatibility | `ARCHIVE_RECOVERY` / `DEFER_DELETE` | Keep runtime registry helpers, stop primary UI nudges toward Pre-Live |
| Overview Candidate Ops tab | primary Overview tab formerly loaded old current/pre-live/proposal registries and linked to Candidate Review / Portfolio Proposal | `DELETE_NOW` for primary tab and unused snapshot helpers | Removed from Overview primary tabs and default snapshot helper |
| Candidate Review / Proposal implementation files | large old workflow modules | `DELETE_NOW` | Delete after import graph proves current workflow no longer imports them |
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

## 5C Classification Outcome

| File / Helper | Classification | Result |
|---|---|---|
| `app/web/backtest_candidate_review.py` | `DELETE_NOW` | Deleted; no current route or current import remains |
| `app/web/backtest_candidate_review_helpers.py` | `DELETE_NOW` after `EXTRACT_CURRENT_HELPER` | Deleted after Practical Validation source handoff builder moved to current service/UI helper |
| `app/web/backtest_portfolio_proposal.py` | `DELETE_NOW` | Deleted; primary Portfolio Proposal panel is not part of current workflow |
| `app/web/backtest_portfolio_proposal_helpers.py` | `DELETE_NOW` after `EXTRACT_CURRENT_HELPER` | Deleted after Final Review current selection/paper snapshot helpers moved local to Final Review helper |
| `app/web/overview_dashboard_helpers.py` legacy candidate/proposal snapshot functions | `DELETE_NOW` | Removed; Overview helper now keeps current market/context snapshot helpers only |
| `app/web/backtest_common.py` | `KEEP_CURRENT` | Removed legacy session-state/import setup; remains shared current Backtest UI helper |
| `app/web/backtest_result_display.py` | `KEEP_CURRENT` | Uses current Practical Validation handoff helper |
| `app/web/backtest_compare.py` | `KEEP_CURRENT` | Uses current Practical Validation handoff helper and preserves only read-only saved mix/archive references |
| `app/web/backtest_history.py` | `KEEP_CURRENT` / `ARCHIVE_RECOVERY` | Archive run rows can hand off to Practical Validation without legacy candidate draft state |
| `app/web/backtest_final_review.py` | `KEEP_CURRENT` | Reads Practical Validation results only as current source options |
| `app/web/backtest_final_review_helpers.py` | `KEEP_CURRENT` | Final Review helper owns current selection/paper snapshot helper logic without proposal helper import |
| `app/runtime/candidate_registry.py` | `ARCHIVE_RECOVERY` | Preserved for Candidate Library and Portfolio Monitoring fallback compatibility; JSONL not rewritten |
| `app/runtime/portfolio_proposal.py` | `ARCHIVE_RECOVERY` / `DEFER_DELETE` | Preserved as historical registry compatibility only |
| `app/runtime/paper_portfolio_ledger.py` | `ARCHIVE_RECOVERY` / `DEFER_DELETE` | Preserved as historical paper ledger compatibility only |

## Testing Direction

- `tests/test_service_contracts.py`: add focused route helper tests for valid targets and legacy panel rejection.
- `py_compile`: Backtest route/page, Overview dashboard/helper, Operations overview, legacy modules if still present.
- `git diff --check`.
- Browser QA if Streamlit can run and UI navigation change is visible.
