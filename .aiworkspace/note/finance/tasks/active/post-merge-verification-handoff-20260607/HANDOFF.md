# Post-Merge Finance Handoff

Status: Complete
Last Updated: 2026-06-07

## Current State

Current active phase: none.
Current active task: none.

Master has the post-merge documentation cleanup commits locally. The branch is ahead of `origin/master`; push / PR is intentionally outside this task unless explicitly requested.

Untracked `.note/` remains local legacy material and should not be staged by default.

## What Was Completed

| 차수 | Result | Start Here |
|---|---|---|
| 1차 | Current product / roadmap / merged work alignment | `tasks/active/post-merge-docs-alignment-20260607/` |
| 2차 | Architecture / data / flow boundary alignment | `tasks/active/post-merge-boundary-docs-alignment-20260607/`, `docs/architecture/SYSTEM_BOUNDARIES.md` |
| 3차 | Active task / phase state manifest alignment | `tasks/active/post-merge-active-state-cleanup-20260607/`, `tasks/active/STATUS_MANIFEST.md`, `phases/active/STATUS_MANIFEST.md` |
| 4차 | Verification and handoff | `tasks/active/post-merge-verification-handoff-20260607/` |

## Read Order For Next Work

1. `docs/INDEX.md`
2. `docs/ROADMAP.md`
3. `docs/PROJECT_MAP.md`
4. `docs/architecture/SYSTEM_BOUNDARIES.md`
5. `tasks/active/STATUS_MANIFEST.md`
6. `phases/active/STATUS_MANIFEST.md`
7. This `HANDOFF.md`

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
| Second-cycle investability hardening | Phase 13 carry-forward can seed a new phase only after a user-approved scope. |

## Do Not Do By Default

- Do not stage `.note/`.
- Do not rewrite `.aiworkspace/note/finance/registries/*.jsonl`.
- Do not rewrite `.aiworkspace/note/finance/saved/*.jsonl`.
- Do not commit run history, generated artifacts, temp CSV, `.DS_Store`, or `.playwright-mcp`.
- Do not treat every folder under `tasks/active` or `phases/active` as currently open work.
