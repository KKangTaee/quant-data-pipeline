# Finance Roadmap

Status: Active
Last Verified: 2026-06-07

## Current State After Master Merge

현재 active phase는 없다.

2026-06-07 master 병합 후 제품은 다음 네 흐름이 함께 연결된 상태다.

```text
Workspace > Ingestion
  -> Workspace > Overview market context
  -> Backtest > Backtest Analysis
  -> Backtest > Practical Validation
  -> Backtest > Final Review
  -> Operations > Operations Console
  -> Operations > Portfolio Monitoring
```

현재 7차 large Streamlit split은 7A Ingestion Console physical split과 7B Ingestion diagnostic facade까지 완료됐고,
8차 runtime 대형 파일 분해의 8A Risk-On Momentum runtime split, 8B real-money / readiness helper split, 8C strict quality / value family split도 완료 상태다.

- Latest completed task: `.aiworkspace/note/finance/tasks/active/ingestion-diagnostic-facade-20260607/`
- 목적: `app/web/ingestion_console.py`에 남아 있던 read-only diagnostic orchestration을 `app/services/ingestion_diagnostics.py`로 이동해 UI / service / data 경계를 분리한다.
- 이번 차수에서 하지 않은 일: Ingestion job execution dispatch split, DB schema / collector behavior 변경, Backtest Compare Streamlit split, generated artifact 생성/커밋, registry / saved JSONL rewrite, push / PR 생성.

## Product Tracks

| Track | Current State | Main Surfaces | Boundary |
|---|---|---|---|
| Data Collection / Data Trust | DB-backed ingestion baseline complete | `Workspace > Ingestion`, MySQL, loaders | UI에서 provider / FRED / external source를 직접 fetch하지 않는다. Overview bounded refresh는 `app/jobs/overview_actions.py` facade만 통과한다 |
| Overview / Market Context | Production baseline plus recent sentiment / Why It Moved work complete | `Workspace > Overview` | Market context and investigation only; bounded refresh action allowed through facade; no trade signal, approval, order, registry rewrite |
| Backtest Analysis | Candidate creation plus Risk-On Momentum 5D research lane complete | `Backtest > Backtest Analysis` | 후보 source 생성 단계; final decision / monitoring governance는 후속 단계 |
| Practical Validation / Final Review | Investability evidence workflow complete through P2 / P3 and first hardening cycle | `Backtest > Practical Validation`, `Backtest > Final Review` | PASS / BLOCKER / selected-route gate는 validation evidence가 소유; sentiment overlay is context-only |
| Operations / Portfolio Monitoring | Operations Console and daily-monitoring-first Portfolio Monitoring complete | `Operations > Operations Console`, `Operations > Portfolio Monitoring`, `System / Data Health`, archive lanes | Read-only monitoring and explicit scenario update; no live approval, broker order, account sync, auto rebalance |
| UI / Engine Boundary | Service/runtime boundary and lint baseline complete | `app/services`, `app/runtime`, `app/web` | UI handles render/session state; runtime / service owns engine dispatch, JSONL helpers, read models |

## Recently Merged Work

| Workstream | Status | Durable Notes |
|---|---|---|
| Overview Market Sentiment V1 | 1차~3차 complete | CNN Fear & Greed / AAII collect into `finance_meta.macro_series_observation`. Overview Sentiment, Practical Validation, Final Review, and Portfolio Monitoring read it as context-only market backdrop. |
| Operations Overview IA / Operations Console V2-V5 | Complete | Operations now has a console entry, Portfolio Monitoring and System / Data Health primary lanes, archive / recovery labels for Backtest Runs and Candidate Library, and disabled live trading boundary copy. |
| Risk-On Momentum 5D V1/V2 | Implementation / QA complete | Daily Swing research lane added under Backtest Analysis. V2 adds ATR exit, macro ranking penalty, comparison / sensitivity / stability / trade-cause / quality-warning analysis, S&P 500 universe option. Governance connection to Practical Validation / Final Review / Portfolio Monitoring is deferred. |
| Selected Dashboard Monitoring First UX V1 | Complete | Portfolio Monitoring opens with Active Portfolio Monitoring Scenario first, while portfolio setup and strategy board sit below. Scenario results stay explicit/session-based and do not auto-write monitoring logs. |
| Overview Market Movers Second Pass / Why It Moved | Current V1 complete; V2 decision pending | Return / Volume rank, previous-period context, manual investigation board, keyless Google News KR RSS metadata/snippet, compact SEC metadata table. No article body, filing body, AI summary, catalyst classifier, DB schema, registry, saved setup write. |
| Futures Market Monitoring / Macro Thermometer | Complete | yfinance futures 1m / daily OHLCV feeds Futures Monitor and Macro Thermometer. Historical validation is point-in-time read-only context, not a prediction guarantee. |

## Completed Foundations

| Foundation | Status | Closeout |
|---|---|---|
| UI Engine Boundary Foundation / Cleanup | Complete | Service/runtime boundary and `app.services/app.runtime -> app.web` import hard-fail lint baseline are in place. |
| Investability Decision Foundation | Complete | Validation gate, storage governance, data provenance, look-through, robustness, selected monitoring, decision dossier baseline complete. |
| Phase 8 Data Evidence Expansion | Complete | Provider / macro / provenance / lifecycle evidence added for investability workflow. |
| Phase 9 Cost / Slippage / Liquidity Realism | Complete | Cost model, turnover, net-cost curve, liquidity / capacity, cost / slippage sensitivity evidence added. |
| Phase 10 Walk-forward / OOS / Regime Validation | Complete | Temporal validation, holdout, macro regime evidence added and connected to selection evidence. |
| Phase 11 Portfolio Construction Risk Controls | Complete | Concentration / overlap / exposure, risk contribution, component role / weight evidence added. |
| Phase 12 Selected Monitoring / Recheck Operations | Complete | Recheck readiness, provider evidence staleness, review signals, allocation boundary, decision dossier continuity complete. |
| Phase 13 First-Cycle Hardening Closeout | Complete | Integrated QA, gate matrix, storage audit, docs/runbook alignment, residual risk carry-forward complete. |
| Practical Validation V2 P2 / P3 | Closeout complete | Provider / macro / look-through / robustness normalization and selected monitoring handoff QA complete. |
| Documentation / AI Workspace Rebuild | Practical closeout | `.aiworkspace/note/finance` and repo-local skill/plugin source are canonical. |

## Current Documentation State

`tasks/active/` and `phases/active/` still contain retained completed boards from prior worktrees.
For now, read them as detailed work records unless the current roadmap or root handoff explicitly names them as active.

Current active phase:

- none

Current active task:

- none

Recent completed docs cleanup tasks:

- `post-merge-verification-handoff-20260607`
- `post-merge-active-state-cleanup-20260607`
- `post-merge-boundary-docs-alignment-20260607`
- `post-merge-docs-alignment-20260607`

Recent completed structure audit tasks:

- `ingestion-diagnostic-facade-20260607`
- `runtime-backtest-strict-family-split-20260607`
- `runtime-backtest-real-money-split-20260607`
- `runtime-backtest-risk-on-momentum-split-20260607`
- `streamlit-ingestion-console-split-20260607`
- `overview-ingestion-action-boundary-20260607`
- `code-boundary-refactor-audit-20260607`

Retained completed boards in `phases/active/` should not be treated as newly open phase work.
Their closeout summaries live under `.aiworkspace/note/finance/phases/done/` when available.

State manifest pointers:

- task state manifest: `.aiworkspace/note/finance/tasks/active/STATUS_MANIFEST.md`
- phase state manifest: `.aiworkspace/note/finance/phases/active/STATUS_MANIFEST.md`
- post-merge handoff: `.aiworkspace/note/finance/tasks/active/post-merge-verification-handoff-20260607/HANDOFF.md`
- Ingestion Diagnostic Facade: `.aiworkspace/note/finance/tasks/active/ingestion-diagnostic-facade-20260607/DESIGN.md`
- Runtime Backtest Strict Family split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-strict-family-split-20260607/DESIGN.md`
- Runtime Backtest Real-Money split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-real-money-split-20260607/DESIGN.md`
- Runtime Backtest Risk-On Momentum split: `.aiworkspace/note/finance/tasks/active/runtime-backtest-risk-on-momentum-split-20260607/DESIGN.md`
- Streamlit Ingestion Console split: `.aiworkspace/note/finance/tasks/active/streamlit-ingestion-console-split-20260607/DESIGN.md`
- Overview / Ingestion action boundary: `.aiworkspace/note/finance/tasks/active/overview-ingestion-action-boundary-20260607/DESIGN.md`
- code refactor audit: `.aiworkspace/note/finance/tasks/active/code-boundary-refactor-audit-20260607/AUDIT.md`

Legacy `.note/` was removed after user approval and is no longer part of the current local state.

## Next Decisions

| Candidate | Why It Matters | Requires Approval Before |
|---|---|---|
| Backtest Compare Streamlit split | `app/web/backtest_compare.py` remains a large mixed render / orchestration file after the Ingestion split | Moving repeated Compare render/result sections into focused modules while preserving service/runtime boundaries |
| Physical task / phase archive migration | `tasks/active` and `phases/active` still contain retained completed folders even though current active state is now manifest-clean | Moving folders, deleting retained boards, changing archive layout, or repairing historical links |
| Overview Why It Moved V2 | Current V1 is manual/session-only; durable metadata retention or SEC financial-statement preview needs a storage/source policy | DB schema, article/filing body handling, AI summary, catalyst classification |
| Risk-On Momentum 5D governance | Strategy is implemented as research lane but not connected to validation / monitoring daily signal policy | Practical Validation module, Final Review gate, Portfolio Monitoring signal integration |
| Overview scheduler hardening | Browser-session refresh exists; OS scheduler / launchd production operation is a separate decision | Enabling unattended scheduled collection |
| UI platform split | Streamlit is workable but complex UX may eventually benefit from API + React/Next.js | Any large frontend migration or service API expansion |
| Second-cycle investability hardening | Phase 13 carry-forward material can seed another phase | Opening a new phase from carry-forward matrix |

## Work Model

| Layer | Location | Meaning |
|---|---|---|
| Phase | `.aiworkspace/note/finance/phases/active/<phase>/` | User-approved multi-task direction, design, integration owner |
| Task | `.aiworkspace/note/finance/tasks/active/<task>/` | Actual implementation, docs, QA, investigation unit |
| Research | `.aiworkspace/note/finance/researches/active/<research-id>/` | Product direction / benchmark / feature opportunity body |
| Durable Docs | `.aiworkspace/note/finance/docs/` | Stable project knowledge after implementation or approved direction |
| Root Handoff Logs | `.aiworkspace/note/finance/WORK_PROGRESS.md`, `.aiworkspace/note/finance/QUESTION_AND_ANALYSIS_LOG.md` | 3~5 line milestone / decision pointers only |

## Update Rules

- Add detailed implementation history to task docs, not this roadmap.
- Keep this roadmap focused on active state, completed foundations, and next decisions.
- Update `PRODUCT_DIRECTION.md` when the product purpose or user-facing workflow changes.
- Update `PROJECT_MAP.md` when ownership boundaries or entry points change.
- Update architecture / flow / data docs when runtime, storage, or user workflow boundaries change.
- Use `docs/architecture/SYSTEM_BOUNDARIES.md` as the first checkpoint for layer / storage / product surface boundary changes.
