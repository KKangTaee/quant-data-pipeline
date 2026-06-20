# Active Task State Manifest

Status: Active
Last Verified: 2026-06-20

## Current State

Current active task:

- None

Latest completed task:

- `overview-market-context-brief-flow-redesign-v1-20260620`

Latest completed docs cleanup task:

- `post-merge-verification-handoff-20260607`

Recent post-merge cleanup records:

- `post-merge-docs-alignment-20260607`: 1차 product / roadmap / current state alignment
- `post-merge-boundary-docs-alignment-20260607`: 2차 architecture / data / flow boundary alignment
- `post-merge-active-state-cleanup-20260607`: 3차 active task / phase state manifest alignment
- `post-merge-verification-handoff-20260607`: 4차 verification / handoff alignment

Recent structure audit records:

- `refactor-round-closeout-20260607`: 10차 structure / refactor baseline closeout, residual split decision, and handoff audit
- `backtest-compare-components-split-20260607`: 9차 Backtest Compare Streamlit split first pass / Portfolio Mix Builder visual component extraction
- `ingestion-diagnostic-facade-20260607`: 7차 large Streamlit file split 7B / Ingestion read-only diagnostic facade extraction
- `runtime-backtest-strict-family-split-20260607`: 8차 runtime large file split 8C / strict quality-value runtime wrapper extraction
- `runtime-backtest-real-money-split-20260607`: 8차 runtime large file split 8B / real-money readiness helper extraction
- `runtime-backtest-risk-on-momentum-split-20260607`: 8차 runtime large file split 8A / Risk-On Momentum runtime slice extraction
- `streamlit-ingestion-console-split-20260607`: 7차 large Streamlit file split 7A / Ingestion Console render-state-job UI extraction
- `overview-ingestion-action-boundary-20260607`: 6차 collection / read action boundary cleanup
- `code-boundary-refactor-audit-20260607`: 5차 code boundary / refactor baseline audit

Recent Reference records:

- `merge-review-fixes-20260608`: post-merge review fix / Reference page-link, V4 status, and catalog test assertion cleanup
- `reference-drift-guard-qa-polish-v5-20260608`: Reference contextual help 5차 / drift guard and QA polish
- `reference-contextual-links-v4-20260608`: Reference contextual help 4차 / workflow screen expander links
- `reference-glossary-concept-dictionary-v3-20260607`: Reference Glossary 3차 / shared concept dictionary
- `reference-guides-journey-playbooks-v2-20260607`: Reference Guides 2차 / journey playbooks and failure states
- `reference-guides-center-v1-20260607`: Reference Guides 1차 / task-first Reference Center

Recent portfolio selection records:

- `distinct-strategy-portfolio-discovery-20260609`: unique strategy family constraint / SPY superior GTAA U3 85% + GRS Compact 10% + Risk Parity Trend 5% portfolio / Final Review and Monitoring registration
- `portfolio-discovery-final-review-monitoring-20260608`: current strategy catalog exploration / all-ETF Final Review selected decision / Portfolio Monitoring registration

Recent Operations records:

- `operations-v2-closeout-20260608`: Operations Overview V2 5차 / final QA and docs closeout
- `operations-review-queue-refinement-20260608`: Operations Overview V2 4차 / priority and evidence ordered review queue
- `operations-evidence-health-strip-20260607`: Operations Overview V2 3차 / Evidence Health mini strip
- `operations-portfolio-first-summary-20260607`: Operations Overview V2 2차 / Portfolio Monitoring Status summary first-pass
- `operations-cockpit-cleanup-20260607`: Operations Overview V2 1차 cleanup / archive and development-history user-facing artifact removal

Recent Overview / Market Context records:

- `overview-market-context-brief-flow-redesign-v1-20260620`: Overview Market Context UX redesign / current brief flow split, historical analog controls inside analog flow, basis ledger, broad-vs-macro sample comparison, source ledger, and `필요 자료 보강` refresh assist
- `overview-market-context-futures-conditioned-analog-v3b-20260618`: Overview Market Context Historical Analog 3차-B / 3차-A GLD `Macro 조건 포함 pilot`에 stored futures daily OHLCV Rate Pressure proxy (`ZN=F` / `ZB=F`) 1개 추가, selected as-of / anchor-date bounded condition, sample quality 유지
- `overview-market-context-macro-conditioned-analog-pilot-v1-20260618`: Overview Market Context Historical Analog 3차-A / 기존 broad analog와 별도인 Macro 조건 포함 pilot, GLD price proxy 조건, sample quality, deferred/disabled condition 표시
- `overview-market-context-analog-asof-window-v2-20260618`: Overview Market Context Historical Analog 2차 / 기준 시점 replay, 5D / 20D / monthly pattern window, current universe metadata 기반 bounded replay 한계 문서화
- `overview-market-context-source-action-flow-v1-20260618`: Overview Market Context Source Action Flow V1 / `next_checks` source-action checklist, source confidence action footer, historical analog basis metadata, refresh assist secondary flow
- `overview-market-movers-period-refresh-v1-20260616`: Overview Market Movers Period Refresh V1 / non-daily Weekly, Monthly, and Yearly EOD price-history manual refresh action through the existing Overview action facade
- `overview-market-context-analog-readability-v5-20260616`: Overview Market Context Analog Readability V5 / Historical analog explanation, summary strip, first-read conclusion, and core/supporting asset table split
- `overview-market-context-analog-repair-v4-20260615`: Overview Market Context Analog Repair V4 / Historical analog coverage gap panel, bounded OHLCV repair action, source confidence summary strip
- `overview-market-context-historical-analog-v1-20260615`: Overview Market Context Historical Analog V1 / Sector Leadership -> Sector ETF Proxy -> context-only historical analog MVP
- `overview-market-context-events-data-trust-v1-20260612`: Overview Market Context Events Data Trust V1 / recent + upcoming major macro event trust
- `overview-data-health-ingestion-handoff-v1-20260608`: Overview Data Health Ingestion Handoff V1 / priority-ranked read-only Data Health -> collection surface handoff
- `overview-macro-context-cockpit-v1-20260608`: Overview Macro Context Cockpit V1 / summary-first DB-backed market context band

Recent Workspace / tooling records:

- `finance-integration-doc-merge-skill-20260617`: Finance integration review skill hardening / document merge conflict checklist for `.aiworkspace/note/finance`

## What `tasks/active/` Means Right Now

This folder currently contains retained work records from prior active worktrees.
Do not infer that every child folder is still open work.

The current active task source of truth is:

1. this manifest
2. [README.md](./README.md)
3. [Finance Roadmap](../../docs/ROADMAP.md)
4. root handoff logs

## Review Count

Reviewed on 2026-06-08:

- `tasks/active`: 194 task folders
- `tasks/done`: README only

Because `tasks/done` has not been used as a full task folder archive, this cleanup does not move all retained task folders.

## Retained Task Groups

| Group | Meaning | Representative Folders |
|---|---|---|
| Post-merge docs cleanup | Current 1차~4차 cleanup records | `post-merge-docs-alignment-20260607`, `post-merge-boundary-docs-alignment-20260607`, `post-merge-active-state-cleanup-20260607`, `post-merge-verification-handoff-20260607` |
| Collection / read boundary cleanup | 6차 Overview / Ingestion action boundary record | `overview-ingestion-action-boundary-20260607` |
| Large Streamlit file split | 7차 Ingestion Console and 9차 Backtest Compare split records | `backtest-compare-components-split-20260607`, `ingestion-diagnostic-facade-20260607`, `streamlit-ingestion-console-split-20260607` |
| Runtime large file split | 8차 Backtest runtime split records | `runtime-backtest-strict-family-split-20260607`, `runtime-backtest-real-money-split-20260607`, `runtime-backtest-risk-on-momentum-split-20260607` |
| Code structure audit | 5차 refactor baseline and 10차 closeout records | `refactor-round-closeout-20260607`, `code-boundary-refactor-audit-20260607` |
| Overview / market context | Overview Market Intelligence, Sentiment, Futures, Why It Moved, Events, automation | `overview-market-sentiment-v1`, `overview-market-movers-second-pass`, `futures-market-monitoring-mvp-v1`, `futures-monitor-stale-refresh-fix-20260607`, `futures-macro-thermometer-validation-v1`, `overview-scheduled-refresh-automation` |
| Backtest Analysis / strategy research | Candidate source generation, portfolio mix builder, Risk-On Momentum research lane | `backtest-portfolio-mix-builder-flow-v1`, `backtest-portfolio-mix-builder-ux-v1`, `risk-on-momentum-5d-v1`, `risk-on-momentum-5d-v2` |
| Practical Validation / Final Review | Validation modules, selected-route gate, evidence read model, Final Review UX | `practical-validation-module-gate-v1`, `practical-validation-selected-route-preflight-v1`, `final-review-selection-readiness-gate-v1`, `final-review-commercial-ux-v1` |
| Operations / Portfolio Monitoring | Operations Console and selected portfolio monitoring work | `operations-v2-closeout-20260608`, `operations-review-queue-refinement-20260608`, `operations-evidence-health-strip-20260607`, `operations-portfolio-first-summary-20260607`, `operations-cockpit-cleanup-20260607`, `operations-console-restructure-v2-v5`, `selected-dashboard-monitoring-first-ux-v1`, `selected-dashboard-manual-scenario-run-v1`, `allocation-drift-evidence-boundary-v1` |
| Reference / product guidance | Reference Center, Glossary, contextual workflow help | `merge-review-fixes-20260608`, `reference-drift-guard-qa-polish-v5-20260608`, `reference-contextual-links-v4-20260608`, `reference-glossary-concept-dictionary-v3-20260607`, `reference-guides-journey-playbooks-v2-20260607`, `reference-guides-center-v1-20260607` |
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
