# Post-Merge Finance Handoff

Status: Complete
Last Updated: 2026-06-07

## Current State

Current active phase: none.
Current active task: none.

Master has the post-merge documentation cleanup and follow-on code boundary audit records locally. Push / PR is intentionally outside this task unless explicitly requested.

Legacy `.note/` was removed after user approval and is not part of the current local state.

## What Was Completed

| 차수 | Result | Start Here |
|---|---|---|
| 1차 | Current product / roadmap / merged work alignment | `tasks/active/post-merge-docs-alignment-20260607/` |
| 2차 | Architecture / data / flow boundary alignment | `tasks/active/post-merge-boundary-docs-alignment-20260607/`, `docs/architecture/SYSTEM_BOUNDARIES.md` |
| 3차 | Active task / phase state manifest alignment | `tasks/active/post-merge-active-state-cleanup-20260607/`, `tasks/active/STATUS_MANIFEST.md`, `phases/active/STATUS_MANIFEST.md` |
| 4차 | Verification and handoff | `tasks/active/post-merge-verification-handoff-20260607/` |
| 5차 | Code boundary / refactor baseline audit | `tasks/active/code-boundary-refactor-audit-20260607/AUDIT.md` |
| 6차 | Overview / Ingestion action boundary cleanup | `tasks/active/overview-ingestion-action-boundary-20260607/DESIGN.md` |

## Read Order For Next Work

1. `docs/INDEX.md`
2. `docs/ROADMAP.md`
3. `docs/PROJECT_MAP.md`
4. `docs/architecture/SYSTEM_BOUNDARIES.md`
5. `tasks/active/STATUS_MANIFEST.md`
6. `phases/active/STATUS_MANIFEST.md`
7. This `HANDOFF.md`
8. `tasks/active/code-boundary-refactor-audit-20260607/AUDIT.md`
9. `tasks/active/overview-ingestion-action-boundary-20260607/DESIGN.md`

## Current Product Interpretation

The merged finance product should be read as:

```text
Workspace > Ingestion
  -> Workspace > Overview market context
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

Important boundaries:

- Overview Sentiment, Futures, Macro Thermometer, and Why It Moved are context / investigation surfaces.
- Overview bounded refresh is allowed only through `app/jobs/overview_actions.py`; Overview UI should not import concrete ingestion / automation / run-history helpers directly.
- Risk-On Momentum 5D is implemented as a Backtest Analysis research lane; validation / monitoring governance is deferred.
- Practical Validation and Final Review own gate / evidence / selected-route decisions.
- Operations > Portfolio Monitoring is read-only monitoring plus explicit scenario update; no live approval, broker order, account sync, or auto rebalance.
- UI should not directly fetch provider / FRED / crawler data; use ingestion -> DB -> loader -> service / UI.

## Remaining Decisions

| Decision | Why It Remains |
|---|---|
| Physical task / phase archive migration | Current active state is manifest-clean, but retained folders still physically live under `active/`. A future migration needs link repair / redirect index checks. |
| Overview Why It Moved V2 | Durable metadata, filing/body handling, AI summary, or catalyst classifier require a storage/source policy first. |
| Risk-On Momentum 5D governance | Strategy exists as a research lane but is not connected to Practical Validation / Final Review / Portfolio Monitoring signal policy. |
| Overview scheduler hardening | Browser-session refresh exists; unattended OS scheduler operation is a separate approval. |
| Ingestion diagnostic facade | 6차 resolved Overview bounded refresh through an action facade. The next boundary cleanup is moving Ingestion read-only diagnostic orchestration behind a narrower service / job facade. |
| Second-cycle investability hardening | Phase 13 carry-forward can seed a new phase only after a user-approved scope. |

## Do Not Do By Default

- Do not rewrite `.aiworkspace/note/finance/registries/*.jsonl`.
- Do not rewrite `.aiworkspace/note/finance/saved/*.jsonl`.
- Do not commit run history, generated artifacts, temp CSV, `.DS_Store`, or `.playwright-mcp`.
- Do not treat every folder under `tasks/active` or `phases/active` as currently open work.
