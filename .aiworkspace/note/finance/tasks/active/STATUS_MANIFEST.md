# Active Task State Manifest

Status: Active
Last Verified: 2026-06-07

## Current State

Current active task: none.

Latest completed task:

- `runtime-backtest-risk-on-momentum-split-20260607`

Latest completed docs cleanup task:

- `post-merge-verification-handoff-20260607`

Recent post-merge cleanup records:

- `post-merge-docs-alignment-20260607`: 1차 product / roadmap / current state alignment
- `post-merge-boundary-docs-alignment-20260607`: 2차 architecture / data / flow boundary alignment
- `post-merge-active-state-cleanup-20260607`: 3차 active task / phase state manifest alignment
- `post-merge-verification-handoff-20260607`: 4차 verification / handoff alignment

Recent structure audit records:

- `runtime-backtest-risk-on-momentum-split-20260607`: 8차 runtime large file split 8A / Risk-On Momentum runtime slice extraction
- `streamlit-ingestion-console-split-20260607`: 7차 large Streamlit file split 7A / Ingestion Console render-state-job UI extraction
- `overview-ingestion-action-boundary-20260607`: 6차 collection / read action boundary cleanup
- `code-boundary-refactor-audit-20260607`: 5차 code boundary / refactor baseline audit

## What `tasks/active/` Means Right Now

This folder currently contains retained work records from prior active worktrees.
Do not infer that every child folder is still open work.

The current active task source of truth is:

1. this manifest
2. [README.md](./README.md)
3. [Finance Roadmap](../../docs/ROADMAP.md)
4. root handoff logs

## Review Count

Reviewed on 2026-06-07:

- `tasks/active`: 176 task folders
- `tasks/done`: README only

Because `tasks/done` has not been used as a full task folder archive, this cleanup does not move all retained task folders.

## Retained Task Groups

| Group | Meaning | Representative Folders |
|---|---|---|
| Post-merge docs cleanup | Current 1차~4차 cleanup records | `post-merge-docs-alignment-20260607`, `post-merge-boundary-docs-alignment-20260607`, `post-merge-active-state-cleanup-20260607`, `post-merge-verification-handoff-20260607` |
| Collection / read boundary cleanup | 6차 Overview / Ingestion action boundary record | `overview-ingestion-action-boundary-20260607` |
| Large Streamlit file split | 7차 Ingestion Console split record | `streamlit-ingestion-console-split-20260607` |
| Runtime large file split | 8차 Backtest runtime Risk-On Momentum split record | `runtime-backtest-risk-on-momentum-split-20260607` |
| Code structure audit | 5차 refactor baseline record | `code-boundary-refactor-audit-20260607` |
| Overview / market context | Overview Market Intelligence, Sentiment, Futures, Why It Moved, Events, automation | `overview-market-sentiment-v1`, `overview-market-movers-second-pass`, `futures-market-monitoring-mvp-v1`, `futures-macro-thermometer-validation-v1`, `overview-scheduled-refresh-automation` |
| Backtest Analysis / strategy research | Candidate source generation, portfolio mix builder, Risk-On Momentum research lane | `backtest-portfolio-mix-builder-flow-v1`, `backtest-portfolio-mix-builder-ux-v1`, `risk-on-momentum-5d-v1`, `risk-on-momentum-5d-v2` |
| Practical Validation / Final Review | Validation modules, selected-route gate, evidence read model, Final Review UX | `practical-validation-module-gate-v1`, `practical-validation-selected-route-preflight-v1`, `final-review-selection-readiness-gate-v1`, `final-review-commercial-ux-v1` |
| Operations / Portfolio Monitoring | Operations Console and selected portfolio monitoring work | `operations-console-restructure-v2-v5`, `selected-dashboard-monitoring-first-ux-v1`, `selected-dashboard-manual-scenario-run-v1`, `allocation-drift-evidence-boundary-v1` |
| Data / provider / lifecycle evidence | Provider snapshots, macro, data coverage, lifecycle, survivorship | `data-provenance-coverage-v1`, `historical-universe-survivorship-v1`, `sec-form25-delisting-backfill-v1`, `symbol-directory-snapshot-ingestion-v1` |
| Phase closeout tasks | Phase 8~13 board open / integrated QA / closeout records | `phase10-board-open`, `phase13-integrated-qa-final-closeout`, `phase13-docs-runbook-alignment-v1` |
| Workspace / tooling | AI workspace migration, plugin / skill system, service boundary, docs rebuild | `ai-workspace-migration`, `doc-system-rebuild`, `product-research-plugin-split`, `service-contract-tests` |

## Physical Migration Rule

Physical movement from `tasks/active/` to `tasks/done/` should be a separate migration task.
That task must:

- create or update a redirect / lookup index
- check references from roadmap, root logs, phase boards, reports, and docs
- avoid moving registry / saved / generated artifacts
- keep a rollback plan or at least a path map

Until then, retained task folders stay in place and are interpreted through this manifest.
