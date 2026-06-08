# Finance System Boundaries

Status: Active
Last Verified: 2026-06-07

## Purpose

이 문서는 master 병합 후 finance 프로젝트의 구조 / 책임 경계를 한 곳에서 확인하기 위한 기준 문서다.

코드 위치를 찾을 때는 [Project Map](../PROJECT_MAP.md)을 보고, table 의미를 확인할 때는 [Data Map](../data/README.md)을 본다.
이 문서는 그 사이에서 "어떤 layer가 무엇을 소유하고, 무엇을 소유하지 않는가"를 판정한다.

## Canonical Flow

```text
External Sources
  -> finance/data/* collectors
  -> MySQL finance_* tables
  -> finance/loaders/* read paths
  -> finance/* strategy / analysis runtime
  -> app/runtime/* runtime adapters and persistence helpers
  -> app/services/* Streamlit-free read models and use-case services
  -> app/web/* Streamlit UI
```

Storage side paths:

```text
workflow handoff evidence -> .aiworkspace/note/finance/registries/*.jsonl
reusable user setup      -> .aiworkspace/note/finance/saved/*.jsonl
human-readable reports   -> .aiworkspace/note/finance/reports/backtests/
local/generated artifacts -> run_history, run_artifacts, backtest_artifacts, .playwright-mcp
```

Code resolves finance workspace paths through `app/workspace_paths.py`.
New code should not recreate legacy `.note/finance` paths directly.

## Layer Responsibilities

| Layer | Owns | Does Not Own |
|---|---|---|
| External sources | yfinance, official schedules, issuer pages, SEC / EDGAR, FRED, CNN / AAII source access policy | App state, validation decisions, registry writes |
| `finance/data/*` | Collector logic, source normalization, idempotent DB UPSERT, run diagnostics | Streamlit rendering, strategy selection, final decision policy |
| `finance/data/db/*` | Schema definition, MySQL connection helpers, additive table / column sync | UI flow, workflow JSONL semantics |
| MySQL tables | Full structured provider, holdings, exposure, macro, sentiment, price, factor, lifecycle data | Compact stage handoff records or user saved setup |
| `finance/loaders/*` | DB-backed read paths, snapshot / staleness / coverage summaries, runtime-ready matrices | External HTTP fetch, DB writes, Streamlit UI calls |
| `finance/*` runtime | Strategy simulation, transforms, performance, daily swing analysis, reusable math | Streamlit session state, JSONL append, live approval |
| `app/runtime/*` | UI payload to runtime adapter, result bundle contract, registry / saved setup helpers, selected portfolio runtime models | Streamlit rendering, provider crawling, final screen layout |
| `app/services/*` | Streamlit-free use-case dispatch, read models, error normalization, evidence interpretation, surface-specific context overlays | Direct UI widgets, raw provider fetch, broker / order execution |
| `app/jobs/*` | Ingestion job wrappers, automation runner wrappers, `JobResult` normalization | Rendering, validation gate scoring, saved portfolio setup |
| `app/web/*` | Streamlit route, form, session state, layout, user feedback, button-triggered actions | Provider / FRED / crawler direct fetch, core strategy math, DB schema, background scheduling policy |
| `.aiworkspace/note/finance/registries/` | Append-only compact workflow handoff and decision evidence | Full holdings, full macro series, raw provider response, user portfolio setup |
| `.aiworkspace/note/finance/saved/` | Explicit reusable setup such as saved mixes and Portfolio Monitoring portfolio setup | Validation evidence, approval records, monitoring logs |
| `.aiworkspace/note/finance/reports/backtests/` | Human-readable results, candidate rationale, validation reports | Source-of-truth replacement for registry or saved setup |

## Product Surface Boundaries

### Workspace > Ingestion

Ingestion is the primary product surface for collector execution, data repair, and source diagnostics.
It calls `app/jobs/ingestion_jobs.py`, which calls `finance/data/*` and writes MySQL rows.

It does not produce PASS / BLOCKER validation decisions by itself.
Partial lifecycle, provider, macro, futures, or sentiment evidence must remain visibly partial in downstream read models.

### Workspace > Overview

Overview is a market context and data health surface with approved bounded refresh actions.

It reads DB-backed service models for:

- Market Movers, Sector / Industry, Events
- Futures Monitor and Macro Thermometer
- CNN Fear & Greed / AAII Sentiment
- Why It Moved investigation metadata

Overview refresh buttons must route through `app/jobs/overview_actions.py`.
The Overview UI must not import `app/jobs/ingestion_jobs.py`, `app/jobs/overview_automation.py`, `app/jobs/run_history.py`, or raw provider / FRED / crawler modules directly.
The action facade is allowed to call ingestion job wrappers, browser-session automation, and run-history append helpers for approved Overview market-context targets only.

Overview context does not create trade signals, Practical Validation PASS / BLOCKER, Final Review selected-route decisions, monitoring signals, registry rows, saved setup rows, broker orders, or auto rebalance actions.

### Backtest > Backtest Analysis

Backtest Analysis creates candidate sources.

It owns single strategy runs, Portfolio Mix Builder, saved mix replay, result bundle display, history display, and Practical Validation handoff.
Risk-On Momentum 5D currently belongs here as a research lane: `finance/swing.py`, `finance/indicators.py`, `finance/swing_macro.py`, and `finance/swing_analysis.py` can produce swing detail, generated scanner / trade artifacts, comparison, sensitivity, stability, trade-cause, and quality-warning evidence.

Backtest Analysis does not own final approval, live readiness, monitoring policy, or daily signal governance.
Risk-On Momentum 5D governance connection to Practical Validation / Final Review / Portfolio Monitoring remains a separate approved task.

### Backtest > Practical Validation

Practical Validation turns a candidate source into compact investability evidence.

It owns source confirmation, module planning, Final Review Gate, provider context, macro context, robustness, construction risk, risk contribution, component role / weight, validation efficacy, data coverage, and backtest realism evidence.

`NOT_RUN` is not pass.
Stored validation rows that fail the Final Review gate are audit trail, not Final Review candidates.
CNN / AAII sentiment overlay is context-only and cannot change PASS / BLOCKER, selected-route preflight, registry write, saved setup, live approval, broker order, or auto rebalance.

### Backtest > Final Review

Final Review owns the selection-readiness decision for monitoring candidates.

It reads Gate-passed Practical Validation rows, shows Candidate Board / Decision Cockpit / Evidence Appendix, and appends compact selected-route decisions to `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` only when the selection gate allows `SELECT_FOR_PRACTICAL_PORTFOLIO`.

Hold, reject, and re-review are current UI state guidance and compatibility read paths, not new official save actions.
Final Review does not create broker orders, live approval, account sync, auto rebalance, or automatic report files.

### Operations > Operations Console

Operations Console is the Operations entry point.

It should put Portfolio Monitoring and System / Data Health first, and treat Backtest Run History / Candidate Library as archive / recovery tools.
It can summarize today action queue and no-live boundary, but it does not create candidate sources or run validation gates.

### Operations > Portfolio Monitoring

Portfolio Monitoring is the current user-facing route for the legacy Selected Portfolio Dashboard implementation files.

It owns user-created monitoring portfolio setup, explicit scenario update, portfolio-level performance recheck, target snapshot display, selected strategy detail, continuity, timeline, review signals, provider evidence, open issues, optional allocation check, and Decision Dossier read-only display.
After a scenario update, it also owns the explicit user action to save a compact Monitoring Snapshot or Review Record and compare latest / previous saved snapshot evidence with the current session scenario.

It stores reusable setup in `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl`.
Scenario results are session state unless a user explicitly saves a compact monitoring snapshot / review record to `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`.

It does not auto-write monitoring logs, mutate Final Review decisions, approve live deployment, connect a broker account, create orders, or auto rebalance.
Sentiment context and target snapshot are context and monitoring evidence, not instructions.

## Data And Storage Boundaries

| Data Class | Canonical Place | Rule |
|---|---|---|
| Full OHLCV, futures, macro, sentiment, provider, holdings, exposure, lifecycle rows | MySQL finance DBs | Store through `finance/data/*`; read through `finance/loaders/*` |
| Backtest candidate source | `PORTFOLIO_SELECTION_SOURCES.jsonl` | Compact handoff only |
| Practical Validation result | `PRACTICAL_VALIDATION_RESULTS.jsonl` | Compact evidence, gate state, reason summary only |
| Final Review selected-route decision | `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` | Compact packet / gate snapshot / open review items only |
| Optional monitoring check | `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` | Explicit user action only |
| Portfolio Monitoring portfolio setup | `saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` | User reusable setup, not evidence or approval |
| Saved mix setup | `saved/SAVED_PORTFOLIO_MIXES.jsonl` | Reusable setup, not validation evidence |
| Reports | `reports/backtests/` | Human-readable artifacts that cite evidence but do not replace source records |
| Run history and generated artifacts | `run_history/`, `run_artifacts/`, `backtest_artifacts/`, `.playwright-mcp/` | Local/generated by default; do not stage unless explicitly requested |

## Context-Only Evidence Rules

The following are context or investigation evidence unless a later approved task explicitly changes their role:

- CNN Fear & Greed and AAII Sentiment
- Futures Macro Thermometer and historical validation
- Overview Market Movers / Why It Moved metadata
- Market event calendar
- Current listing snapshots, SEC CIK cross-checks, computed lifecycle partial rows
- Risk-On Momentum 5D Backtest Analysis swing detail and generated artifacts

Context-only evidence can explain the environment, warn about data gaps, or guide a manual next check.
It cannot silently become a validation pass, final selection reason, monitoring alert, order instruction, or automatic saved record.

## Change Checklist

Before adding a collector, loader, strategy, validation module, monitoring panel, or persistence path, answer:

| Question | Required Check |
|---|---|
| Which layer owns this behavior? | Pick one owner from the layer table. |
| Does UI need to call an external provider? | If yes, move it to `finance/data/*` plus an ingestion job unless the feature is explicitly session-only outbound link / metadata display. |
| Does this need full row storage? | Use MySQL, not workflow JSONL. |
| Does this need stage handoff evidence? | Use existing compact registry chain if possible. |
| Is this reusable user setup? | Use `saved/`, not registries. |
| Is this generated or local output? | Keep it unstaged unless explicitly promoted. |
| Can missing data be misread as pass? | Represent `NOT_RUN`, stale, partial, bridge, proxy, or missing evidence explicitly. |
| Does this imply live approval, broker order, account sync, or auto rebalance? | Current answer must be no unless a separately approved live trading scope exists. |

## Related Docs

- [Project Map](../PROJECT_MAP.md): file ownership and entry points
- [Data / DB Pipeline Flow](./DATA_DB_PIPELINE_FLOW.md): collector / DB / loader code flow
- [Backtest Runtime Flow](./BACKTEST_RUNTIME_FLOW.md): UI payload to strategy runtime flow
- [Strategy Implementation Flow](./STRATEGY_IMPLEMENTATION_FLOW.md): adding strategy families
- [Data Flow Map](../data/DATA_FLOW_MAP.md): table and data movement meaning
- [Storage Governance](../data/STORAGE_GOVERNANCE.md): DB / JSONL / saved / report persistence policy
- [Portfolio Selection Flow](../flows/PORTFOLIO_SELECTION_FLOW.md): user stage ownership from candidate to monitoring
