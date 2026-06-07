# Code Boundary Refactor Audit

Status: Complete
Last Updated: 2026-06-07

## Executive Summary

5차 감사 기준으로, 현재 finance app은 큰 틀의 layer 경계를 유지하고 있다.
`app/services`와 `app/runtime`은 Streamlit-free boundary check를 통과했고, `app.services / app.runtime -> app.web` 역참조도 hard violation으로 잡히지 않았다.

다만 리팩토링 기준선은 명확하다.

1. Overview refresh / automation / job trigger 정책을 먼저 결정해야 한다.
2. Ingestion diagnostics should be wrapped behind an action / service facade even when the screen remains the collector surface.
3. 대형 Streamlit 화면 파일은 행동 보존형으로 분해해야 한다.
4. `app/runtime/backtest.py`와 `app/runtime/final_selected_portfolios.py`는 public wrapper를 유지한 채 family별 runtime module로 나눠야 한다.
5. Backtest UI의 wildcard import와 web helper 테스트 의존을 줄여야 한다.
6. legacy compatibility surface는 새 workflow와 별도 카탈로그로 분리해야 한다.

이번 차수에서는 코드 변경을 하지 않았다.

## Confirmed Boundaries

| Area | Result | Evidence |
|---|---|---|
| UI / engine boundary checker | PASS | `check_ui_engine_boundary.py` hard violations none |
| Streamlit imports | PASS with expected scope | `streamlit` import는 `app/web` files에만 존재 |
| `app.services` / `app.runtime` importing `app.web` | PASS | production code에서는 hard reverse import 없음. tests는 web helper contract를 직접 import |
| Legacy `.note/finance` path recreation | PASS | code path에는 직접 재생성 흔적 없음. test contains negative assertion only |
| Generated artifact tracking | PASS with caveat | tracked generated-like path는 `run_history/README.md` only. registries / saved tracked files are source-of-truth records |
| Current local app health | PASS | `http://localhost:8501/_stcore/health` returned `ok` |

## Findings

### F1. Overview Collector Trigger Policy Drift

Severity: P2

`SYSTEM_BOUNDARIES.md` says Ingestion is the only product surface that should trigger collectors from the UI.
Actual code allows `Workspace > Overview` to trigger job wrappers for Market Movers, Futures, Events, sentiment, and browser-session automation.

Observed examples:

- `app/web/overview_dashboard.py` imports `app.jobs.ingestion_jobs` wrappers.
- Market Movers calls `run_collect_market_intraday_snapshot`.
- Futures Monitor calls `run_collect_futures_ohlcv`.
- Events refresh calls FOMC, earnings, and macro calendar jobs.
- Sentiment refresh calls `run_collect_market_sentiment`.

This is not a direct provider fetch from UI. The UI calls job wrappers, and collectors remain under `finance/data`.
The issue is policy clarity: Overview is no longer purely read-only. It is a mixed surface with bounded refresh controls.

Recommended next step:

- 6차에서 one of these policies should be chosen:
  - Document Overview refresh as an approved bounded exception.
  - Move Overview refresh orchestration behind a service/action layer and keep UI as form/session/render only.
  - Move most collection triggers back to Ingestion / automation and make Overview mostly read-only.

Recommended default:

- Keep bounded Overview refresh, but formalize it as `app/services/overview_actions.py` or `app/jobs/overview_actions.py`.
- UI should call a small action facade, not individual ingestion jobs.

### F2. Ingestion Diagnostics Bypass A Narrow Action Facade

Severity: P2

`Workspace > Ingestion` is the expected collector / diagnostic surface.
However, some diagnostic paths call data / loader helpers directly from `app/web/streamlit_app.py`, including read-only statement PIT inspection and live EDGAR source sample inspection.

This is safer than doing the same in Overview, because Ingestion owns data operations.
Still, it makes the top-level Streamlit app own too much orchestration and makes future tests heavier than necessary.

Recommended next step:

- Keep the user-facing cards in Ingestion.
- Move read-only diagnostic orchestration into an action / service module such as `app/services/ingestion_diagnostics.py` or `app/jobs/diagnostics.py`.
- Keep provider source inspection clearly marked as bounded, manual, one-symbol, read-only, and non-persistent unless a future task explicitly changes that policy.

### F3. Ingestion Console Is Too Large

Severity: P2

`app/web/streamlit_app.py` is 4,855 lines.
The largest function is `_render_ingestion_console` at about 1,911 lines.

The Ingestion console currently owns:

- job catalog text
- preflight / validation forms
- result rendering
- run history append
- source inspection diagnostics
- read-only provider / EDGAR / FRED explanations
- page-level navigation

Recommended next step:

- Extract `app/web/ingestion_console.py` for render shell.
- Extract `app/web/ingestion_result_display.py` for result rendering.
- Extract pure job catalog / action dispatch to `app/services/ingestion_console.py` or `app/jobs/ingestion_actions.py`.
- Keep `app/web/streamlit_app.py` as top navigation and page routing only.

### F4. Backtest Compare Workspace Is A Large Coupled UI Surface

Severity: P2

`app/web/backtest_compare.py` is 6,220 lines.
The largest function, `_render_strategy_compare_workspace`, is about 1,581 lines.
The file also uses wildcard imports from `backtest_common` and `backtest_result_display`.

Risk:

- Hidden dependencies make smaller refactors brittle.
- Pure readiness / handoff builders are mixed with Streamlit render.
- Tests import private helpers from web modules because some pure logic still lives in UI files.

Recommended next step:

- Extract compare model builders to `app/services/backtest_compare_read_model.py`.
- Extract portfolio mix form sections into focused `app/web/backtest_compare_*` modules.
- Replace wildcard imports with explicit imports after each extraction.
- Keep existing public render entry point until Browser smoke passes.

### F5. Runtime Backtest Wrapper Is Still A Broad Module

Severity: P2

`app/runtime/backtest.py` is 5,719 lines.
It already delegates result bundle construction, but it still owns many strategy-family wrappers and real-money / guardrail contracts.

Recommended next step:

- Split by family while preserving public imports:
  - `app/runtime/backtest_quality_value.py`
  - `app/runtime/backtest_risk_on_momentum.py`
  - `app/runtime/backtest_real_money_contracts.py`
  - `app/runtime/backtest_freshness.py`
- Keep `app/runtime/backtest.py` as compatibility facade until callers are migrated.

### F6. Selected Portfolio Runtime Is Broad But More Domain-Coherent

Severity: P3

`app/runtime/final_selected_portfolios.py` is 5,320 lines.
It is large, but the responsibility is more coherent than `streamlit_app.py`: selected portfolio saved state, dashboard model, continuity, recheck, provider evidence, review signals, drift, and timeline.

Recommended next step:

- Split after `app/runtime/backtest.py`.
- Prioritize low-risk read model slices:
  - recheck readiness
  - provider evidence
  - continuity / timeline
  - drift / allocation boundary
- Keep saved setup read / write helpers stable.

### F7. Streamlit-Free Read Models Still Live In `app/web`

Severity: P3

Some files expose pure or mostly pure builders from `app/web` modules while importing Streamlit at module level.
Example: `app/web/operations_overview.py` contains `build_operations_overview_model` but imports `streamlit`.

This is acceptable for current UI tests, but it prevents those model builders from being imported by service/runtime code without loading Streamlit.

Recommended next step:

- Move pure builders to `app/services/operations_overview.py` and similar read-model modules.
- Keep `app/web/*` as render adapters.
- Migrate tests to service modules first, then adjust UI imports.

### F8. Legacy Compatibility Is Preserved But Still Visible In Main Code

Severity: P3

Legacy compatibility is intentionally retained for Candidate Review, Portfolio Proposal, saved portfolio compatibility, and older final review handoff field names.
The risk is not data loss. The risk is future developers mistaking compatibility paths for the preferred product flow.

Recommended next step:

- Add or update a `legacy compatibility catalog`.
- Mark each compatibility path as:
  - keep for read-only archive
  - keep for migration bridge
  - candidate for UI demotion
  - candidate for code removal after migration

## Refactor Priority Matrix

| Priority | Target | Why First | Suggested Owner Skill |
|---|---|---|---|
| 1 | Overview refresh / action policy | Resolves doc-code policy drift before code movement | `finance-integration-review`, then relevant web/data skill |
| 2 | Ingestion diagnostic facade | Keeps Ingestion as data surface while removing direct orchestration from top-level UI | `finance-db-pipeline` plus web workflow judgment |
| 3 | Ingestion console split | Biggest single function and top-level app routing pressure | `finance-db-pipeline` plus web workflow judgment |
| 4 | Backtest Compare split | Biggest file and wildcard imports | `finance-backtest-web-workflow` |
| 5 | Runtime backtest family split | Core strategy runtime blast radius, needs careful facade | `finance-strategy-implementation` |
| 6 | Operations model extraction | Low-risk pure model move, improves import cleanliness | `finance-backtest-web-workflow` |
| 7 | Selected portfolio runtime split | Large but coherent, should follow boundary stabilization | `finance-backtest-web-workflow` |
| 8 | Legacy compatibility catalog | Reduces future confusion without changing behavior | `finance-doc-sync` / task doc |

## Suggested Next Stages

### 6차: Overview / Ingestion Action Boundary Decision

Goal: decide whether Overview refresh is an approved mixed-surface exception or should move behind a stronger action facade.

Completion:

- `SYSTEM_BOUNDARIES.md` and code behavior agree.
- No UI direct provider fetch is introduced.
- Existing Overview buttons either stay documented or call a single action facade.

### 7차: Ingestion Diagnostics / Console Render Split

Goal: shrink `_render_ingestion_console` without changing job or diagnostic behavior.

Completion:

- `app/web/streamlit_app.py` remains page routing.
- Ingestion render lives in a focused module.
- Job dispatch, read-only diagnostics, and result rendering are separately testable.

### 8차: Backtest Compare UI Split And Import Cleanup

Goal: reduce `backtest_compare.py` and remove wildcard import pressure.

Completion:

- Portfolio Mix Builder render remains behavior-compatible.
- Pure readiness / handoff helpers move toward service/read-model modules.
- Existing compare Browser smoke route still loads.

### 9차: Runtime Facade Split

Goal: split `app/runtime/backtest.py` by strategy family while keeping old public imports stable.

Completion:

- Existing UI and service imports continue to work.
- `app/runtime/backtest.py` becomes a compatibility facade plus shared public errors/constants.

### 10차: Legacy Compatibility And Verification Hardening

Goal: make old workflow compatibility explicit and prevent boundary regressions.

Completion:

- Legacy compatibility catalog exists.
- Boundary checker / service contract tests cover the new split.
- Generated artifacts and registry/saved boundaries remain guarded.

## Non-Goals For Refactor Work

- No live trading approval.
- No broker integration.
- No automatic rebalance.
- No registry or saved setup rewrite unless explicitly approved.
- No external benchmark or product feature expansion during structural refactor.

## Recommended First Implementation Scope

Start with 6차.
Do not split large files before deciding the Overview refresh policy, because the split destination depends on whether Overview remains a mixed read / refresh surface or becomes read-only plus Ingestion handoff.
