# Overview Market Context Source Actionability V8 Implementation Plan

**Goal:** `Overview > Market Context` should not keep showing non-actionable Events caveats or Data Health meta rows as unresolved `자료 확인 필요` after smart refresh excludes or resolves actionable items.

**Scope**

- 1차: Add source-confidence actionability metadata.
- 2차: Make top `자료 상태` depend on actionable refresh items, not all source caveats.
- 3차: Reclassify Events estimate caveats as reference limits / refresh exclusions.
- 4차: Reclassify Data Health as management meta, not a market-context source issue.
- 5차: Split evidence UI into brief sources and reference/meta items.
- 6차: Verify tests and Browser QA.

**Files**

- `app/services/overview_market_intelligence.py`
- `app/web/overview_ui_components.py`
- `tests/test_service_contracts.py`
- task/docs closeout files

**Boundary**

- No provider fetch during UI render.
- No new DB schema, loader, registry, saved JSONL, or run history writes.
- No trade signal, recommendation, validation gate, Final Review, or Operations monitoring semantics.

## Steps

- [x] Write RED tests for source-confidence actionability and UI grouping.
- [x] Update service model with `actionability`, `counts_for_status`, `source_role`, and actionable summary counts.
- [x] Update Market Context top data-state rail to use actionable refresh plan status.
- [x] Update UI summary / rows to group direct brief sources separately from reference/meta rows.
- [x] Run focused tests, full service contract tests, py_compile, diff check.
- [x] Browser QA and screenshot.
- [x] Sync durable docs and commit safe files only.
