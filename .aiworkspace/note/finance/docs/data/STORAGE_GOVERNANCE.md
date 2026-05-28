# Finance Storage Governance

Status: Active
Last Verified: 2026-05-28

## Purpose

이 문서는 `finance` 프로젝트에서 DB, workflow JSONL, saved setup, run history, report를 언제 써야 하는지 정한다.

목표는 저장을 무조건 줄이는 것이 아니라, 투자 판단 흐름에 필요한 최소한의 durable record만 남기고 raw data / 사용자 memo / local artifact가 registry로 번지는 일을 막는 것이다.

## Core Rules

- 저장은 stage handoff 또는 명시적 재사용 목적이 있을 때만 추가한다.
- 새 JSONL registry는 기본적으로 만들지 않는다.
- 사용자 메모를 반복 저장하는 기능은 기본적으로 만들지 않는다.
- Practical Validation과 Final Review JSONL에는 compact evidence만 둔다.
- full holdings, full macro series, full provider response, raw crawler output은 DB / ingestion 경계에 둔다.
- UI는 provider / FRED / crawler를 직접 fetch하지 않는다. `Ingestion -> DB -> Loader -> UI` 흐름을 유지한다.
- `NOT_RUN`은 pass가 아니며, 저장 record에서도 실행 불가 / 데이터 부재로 남긴다.
- Final Review와 Selected Portfolio Dashboard의 record는 live approval, broker order, auto rebalance가 아니다.

## Current Storage Model

| Storage | Role | Policy |
|---|---|---|
| `.aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl` | Backtest Analysis가 만든 validation candidate source | Keep. Main workflow source-of-truth. |
| `.aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl` | Practical Validation result and compact evidence | Keep. Final Review input. |
| `.aiworkspace/note/finance/registries/FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` | Final Review decision and compact packet / gate snapshot | Keep. Selected Portfolio Dashboard input. |
| `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | Optional selected-portfolio monitoring snapshot | Explicit user action only. No automatic log sprawl. |
| `.aiworkspace/note/finance/saved/SAVED_PORTFOLIO_MIXES.jsonl` | Reusable V2 portfolio mix setup | Keep as setup, not evidence. |
| `.aiworkspace/note/finance/saved/SAVED_PORTFOLIOS.jsonl` | Legacy reusable weighted portfolio setup | Preserve as compatibility; do not expand without migration. |
| `.aiworkspace/note/finance/run_history/*.jsonl` | Local execution history | Debug/replay artifact, not decision source-of-truth. |
| `.aiworkspace/note/finance/run_artifacts/` | Generated job result artifacts | Local/generated unless promoted to a report. |
| `.aiworkspace/note/finance/reports/backtests/` | Human-readable strategy / validation / decision reports | Reports may cite evidence, but do not replace registries. |
| MySQL finance DBs | Provider, holdings, exposure, macro, price, factor data | Source-of-truth for full structured data. |

## Legacy Registry Boundary

The following registries are preserved for compatibility but should not gain new main-flow responsibilities:

| File | Boundary |
|---|---|
| `CURRENT_CANDIDATE_REGISTRY.jsonl` | Legacy candidate library / replay compatibility |
| `CANDIDATE_REVIEW_NOTES.jsonl` | Legacy operator review note; not source-of-truth |
| `PRE_LIVE_CANDIDATE_REGISTRY.jsonl` | Legacy pre-live / paper tracking flow |
| `PORTFOLIO_PROPOSAL_REGISTRY.jsonl` | Legacy portfolio proposal drafts |
| `PAPER_PORTFOLIO_TRACKING_LEDGER.jsonl` | Legacy paper tracking ledger |
| `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | Final Review V1 history |

## New Persistence Checklist

Before adding any new persistence path, answer these questions in the task plan:

| Question | Required Answer |
|---|---|
| Which later stage reads this? | Name the screen/service. If none, do not persist. |
| Is this a source-of-truth, saved setup, local artifact, or report? | Pick exactly one primary class. |
| Can an existing registry or DB table hold it? | Prefer existing source chain or DB. |
| Does it contain raw/full provider, holdings, macro, or price data? | If yes, use DB / ingestion artifact instead of workflow JSONL. |
| Is it user memo text? | Avoid unless it is a compact final decision reason. |
| Is it automatically written? | Avoid automatic writes unless a separate automation policy exists. |
| How will stale / partial / `NOT_RUN` evidence be represented? | Do not silently convert gaps into pass. |
| What is the commit policy? | Runtime row output should usually remain unstaged. |

## Free API And Crawling Boundary

- Use free APIs or official free data sources first.
- If free API coverage is insufficient, crawler output must enter through `finance/data/*` ingestion and DB persistence.
- Parser/source metadata should include enough provenance to explain coverage and staleness.
- Practical Validation and Final Review should read crawler-derived evidence through loaders, not through UI-side HTTP calls.

## Migration Policy

- Do not delete existing registry / saved files during cleanup tasks.
- Do not rewrite append-only registry rows unless a migration task explicitly owns compatibility and rollback.
- Deprecate older storage by removing new dependencies and documenting the newer source chain.
- Promote only compact, repeatedly useful knowledge from task notes into this document.
