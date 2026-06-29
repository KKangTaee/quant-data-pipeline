# Recommendation

Status: Active
Last Updated: 2026-06-08

## One-Line Recommendation

Use `sub-dev` as the branch for Overview / Ingestion / Operations market-context product research and sub-development, and make the next approved build an `Overview Macro Context Cockpit V1` that summarizes existing DB-backed macro, futures, sentiment, events, movers, breadth, and data-health evidence before adding new data sources.

## Why This Direction

The current Overview already has many useful pieces: Market Movers, Sector / Industry, Futures Monitor, Sentiment, Events, Data Health, and `Why It Moved`. The core weakness is not missing data volume. It is that the user must connect the macro story by moving across tabs.

External benchmarks point in the same direction: successful market dashboards start with a curated big-picture view, then let the user drill into themes, calendars, heatmaps, and source-specific details. For this project, that pattern should be adapted conservatively:

- DB-backed only.
- Source / freshness / partial states visible.
- Context-only macro evidence, not trade signal.
- Ingestion owns collection.
- Operations owns post-selection monitoring and system health.
- Backtest / Practical Validation / Final Review remain owned by `main-dev` / `backtest-dev` work.

## Recommended 1st Build Scope

### Stage 1. Overview Macro Context Cockpit V1

Goal:

- Add or reshape the top of `Workspace > Overview` into a summary-first market context cockpit.

The cockpit should answer:

- What is moving now?
- Is the move broad or concentrated?
- What do futures imply as context?
- What is the sentiment backdrop?
- What important macro / earnings events are near?
- Is the underlying data fresh, stale, partial, or missing?
- Which deep tab should the user inspect next?

Likely implementation areas:

- `app/web/overview_dashboard.py`
- `app/web/overview_dashboard_helpers.py`
- `app/web/overview_ui_components.py`
- `app/services/overview_market_intelligence.py`
- `app/services/futures_macro_thermometer.py`

Completion conditions:

- No new provider is added.
- No direct external fetch occurs during Streamlit render.
- No registry / saved JSONL write is added.
- Sentiment / futures / events remain market context only.
- Existing deep tabs still work.
- UI text clearly separates data confidence from investment judgement.

### Stage 1B. Macro Indicator / Source Confidence Catalog

This can run before or alongside Stage 1 if a docs-first task is preferred.

Goal:

- Define each Overview macro / market indicator and its source, table, collector, loader, freshness threshold, downstream surfaces, and caveats.

Likely output:

- Durable docs under `.aiworkspace/note/finance/docs/data/` or `.aiworkspace/note/finance/docs/flows/`.
- Optional future Reference companion after user approval.

## Recommended Next Phases

| Phase | Output | Why |
| --- | --- | --- |
| 2차. Data Health -> Ingestion Action Queue | Priority-ranked stale / missing / failed data targets with exact Ingestion next action | Turns Overview's data-health information into an operator workflow without breaking collection ownership. |
| 3차. Market Breadth / Heatmap Visualization | Sector / industry heatmap, breadth, concentration, and mover distribution view | Adds scan-first visual analysis after the cockpit hierarchy is stable. |
| 4차. Events Quality / Macro Week View | Summary of FOMC / CPI / PPI / employment / GDP / earnings estimate clusters with source-quality labels | Makes macro event risk easier to read without treating it as a signal. |
| 5차. Why It Moved V2 Policy Or Futures Provider Hardening | Storage/source policy for compact metadata, or official / paid futures provider decision | Only after source retention, terms, freshness, and replay semantics are approved. |

## What Not To Do Yet

- Do not change AGENTS.md or durable roadmap to make this session role canonical until the user explicitly asks.
- Do not implement backtest validation, Practical Validation, Final Review gate, or monitoring governance work in this branch unless scope is re-approved.
- Do not add live approval, broker order, broker account sync, auto rebalance, or persistent trading alerts.
- Do not add article body collection, filing body collection, AI catalyst judgement, or automatic cause classification.
- Do not rewrite registry / saved JSONL files.
- Do not migrate to React / API frontend just for Overview polish.
- Do not treat yfinance futures, CNN / AAII sentiment, event calendar rows, or market movers as investment recommendations.

## Decision Rules

Proceed to implementation when the user approves:

- `sub-dev` owns the next Overview / Ingestion / Operations sub-development slice.
- The first slice is `Overview Macro Context Cockpit V1`.
- The first slice uses existing DB-backed read models only.
- The first slice keeps macro / sentiment / futures as context-only evidence.
- Any IA change to `Candidate Ops` is either explicitly included or deferred.

## New Session Handoff Prompt

```text
작업 위치:
- worktree: /Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev
- branch/worktree role: Overview / Ingestion / Operations market-context sub-development
- research bundle: .aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/

요청:
Overview Macro Context Cockpit V1을 설계/구현해줘.

먼저 읽을 문서:
- AGENTS.md
- .aiworkspace/note/finance/docs/INDEX.md
- .aiworkspace/note/finance/docs/ROADMAP.md
- .aiworkspace/note/finance/docs/PROJECT_MAP.md
- .aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/RESEARCH_PLAN.md
- .aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/CURRENT_PROJECT_AUDIT.md
- .aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/UI_PATTERNS.md
- .aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/FEATURE_CANDIDATES.md
- .aiworkspace/note/finance/researches/active/2026-06-sub-dev-overview-macro-base/RECOMMENDATION.md

범위:
- 기존 DB-backed read model만 사용한다.
- Futures / Sentiment / Events / Market Movers / Sector-Industry / Data Health를 summary-first cockpit으로 연결한다.
- 새 provider, DB schema, registry/saved JSONL write는 추가하지 않는다.
- Overview UI에서 외부 source를 직접 fetch하지 않는다.
- macro/futures/sentiment/economic calendar context는 trade signal, validation PASS/BLOCKER, monitoring signal이 아니다.
- Candidate Ops IA 변경은 명시 승인 전에는 하지 않는다.

검증:
- 관련 py_compile
- focused service/UI helper tests if helper logic changes
- ui-engine boundary check
- git diff --check
- Browser QA screenshot if UI changes
```

## Final Recommendation

Approve a narrow Stage 1 design/build task for `Overview Macro Context Cockpit V1`. This gives the user the biggest workflow improvement with the least data-risk: it turns existing information into an analyzable market context guide, while preserving the project boundary that Overview is context and investigation, not trading approval.
