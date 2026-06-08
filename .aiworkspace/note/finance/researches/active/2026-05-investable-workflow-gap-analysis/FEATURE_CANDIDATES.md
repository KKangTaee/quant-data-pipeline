# Feature Candidates

Status: Draft
Last Updated: 2026-06-08

Scoring: 1 low, 5 high. Priority is judgmental, using `impact + fit + confidence - effort - risk` as a starting point.

## Summary

가장 먼저 만들 것은 새 전략이나 broker 연결이 아니라 `투자 가능성 판단 packet`이다. 현재 프로젝트에는 이미 백테스트, validation, final decision, selected monitoring의 재료가 있으므로, 첫 개발은 이 재료를 더 엄격한 gate와 report contract로 묶는 것이 가장 효율적이다.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Investability Evidence Packet | Now | 5 | 3 | 2 | 5 | 5 | Backtest web workflow / app services |
| Validation Gate Hardening | Now | 5 | 3 | 3 | 5 | 5 | Backtest web workflow / service read model |
| Data Governance & Provenance Layer | Now / Next | 5 | 4 | 4 | 4 | 5 | DB pipeline / runtime registry |
| Look-Through Exposure Board | Next | 4 | 3 | 3 | 4 | 5 | Backtest web workflow + DB pipeline |
| Robustness Lab V1 | Next | 5 | 5 | 4 | 4 | 5 | Strategy implementation + Backtest web workflow |
| Persistent Monitoring Timeline | Next | 4 | 3 | 3 | 4 | 4 | Backtest web workflow / runtime registry |
| Assumption & Limitation Disclosure | Now | 4 | 2 | 2 | 5 | 5 | Backtest web workflow / docs |
| Source-Of-Truth Breadcrumb | Now | 3 | 2 | 1 | 5 | 4 | Backtest web workflow |

## Now Candidates

### Investability Evidence Packet

- Bucket: Now
- Problem: Final Review는 많은 evidence를 저장하지만, 사용자가 "이 후보를 왜 투자 가능 후보로 봤는가 / 무엇을 검증하지 못했는가"를 한 번에 확인할 packet이 없다.
- User workflow change: Final Review 전에 `Decision Packet`을 확인한다. 선택 가능한 상태인지, 보류해야 하는지, 어떤 gap을 waive했는지 한 화면에서 본다.
- Evidence:
  - Audit: current workflow already stores validation result, diagnostic rows, provider coverage, curve evidence, paper observation.
  - Benchmarks: Bloomberg / IBKR / Portfolio Lab-style reporting pattern.
- Required code/data/doc areas:
  - `app/services/backtest_evidence_read_model.py`
  - `app/web/backtest_final_review.py`
  - `app/web/backtest_final_review_helpers.py`
  - `app/runtime/portfolio_selection_v2.py`
  - `docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Dependencies: current Practical Validation V2 result shape.
- Risks: packet can become too verbose.
- Validation idea: service contract test for packet read model; render smoke for Final Review selected source.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: maximum product clarity for moderate implementation effort.

### Validation Gate Hardening

- Bucket: Now
- Problem: `NOT_RUN` and proxy evidence can still contribute partial points or pass through to Final Review, which weakens validation efficacy.
- User workflow change: critical missing evidence becomes a clear blocker or explicit waiver before `SELECT_FOR_PRACTICAL_PORTFOLIO`.
- Evidence:
  - Audit: `NOT_RUN` score weight exists; Final Review movement is allowed when there are no hard blockers but review / not-run gaps remain.
  - Benchmarks: CFA / FINRA emphasize assumptions, limitations, survivorship / look-ahead / hypothetical performance risks.
- Required code/data/doc areas:
  - `app/services/backtest_practical_validation_diagnostics.py`
  - `app/services/backtest_evidence_read_model.py`
  - `app/web/backtest_final_review_helpers.py`
  - `tests/test_service_contracts.py`
- Dependencies: define critical domains and waiver policy.
- Risks: stricter gates can frustrate exploration if every candidate blocks.
- Validation idea: tests for `critical_not_run -> cannot select unless waiver`; Final Review save evaluation cases.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: directly addresses "검증효력의 부족".

### Assumption & Limitation Disclosure

- Bucket: Now
- Problem: current code and docs know many limitations, but Final Review does not force a compact assumption disclosure before selection.
- User workflow change: each final decision includes generated assumptions / limitations and operator acknowledgement.
- Evidence:
  - Audit: no-live boundary, current snapshot limits, provider partial risk, ALFRED vintage gap are scattered across docs and runtime evidence.
  - Benchmarks: FINRA / SEC automated tool guidance and Morningstar / IBKR disclosures.
- Required code/data/doc areas:
  - `app/services/backtest_evidence_read_model.py`
  - `app/web/backtest_final_review.py`
  - `docs/flows/PORTFOLIO_SELECTION_FLOW.md`
- Dependencies: map limitation rules from validation evidence.
- Risks: disclosure fatigue.
- Validation idea: final decision row includes `assumptions_and_limits` list and selected route requires acknowledgement.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: small implementation with high safety value.

### Source-Of-Truth Breadcrumb

- Bucket: Now
- Problem: V2 and legacy registries coexist; source identity can become confusing.
- User workflow change: every major Backtest / Validation / Final Review / Dashboard screen shows source chain: source -> validation -> decision -> monitoring.
- Evidence:
  - Audit: registry README defines V2 source chain; legacy registries remain for compatibility.
  - Benchmarks: institutional reporting patterns depend on traceability.
- Required code/data/doc areas:
  - `app/web/backtest_ui_components.py`
  - `app/web/backtest_practical_validation.py`
  - `app/web/backtest_final_review.py`
  - `app/web/final_selected_portfolio_dashboard.py`
- Dependencies: stable ids in runtime payloads.
- Risks: UI clutter.
- Validation idea: component helper unit test and screen smoke.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: low effort, reduces workflow confusion.

## Next Candidates

### Data Governance & Provenance Layer

- Bucket: Now / Next
- Problem: DB snapshots, JSONL registries, generated artifacts, schema sync, source provenance, retention policy are currently documented but not enforced as a cohesive product layer.
- User workflow change: validation and Final Review show data snapshot status, provenance, stale / missing / partial states, and retention source-of-truth.
- Evidence:
  - Audit: table semantics and data quality docs warn about current snapshots, PIT, stale rows, schema sync limits.
  - Benchmarks: Bloomberg data validation service pattern; Morningstar source disclosure.
- Required code/data/doc areas:
  - `finance/data/db/schema.py`
  - `finance/data/*`
  - `finance/loaders/*`
  - `app/runtime/portfolio_selection_v2.py`
  - `.aiworkspace/note/finance/docs/data/*`
- Dependencies: decide minimum provenance fields for every persisted evidence row.
- Risks: schema / migration changes can be broad.
- Validation idea: schema map tests, loader provenance tests, registry row schema checks.
- Owner skill: `finance-db-pipeline`
- Priority rationale: central to "무분별한 데이터 저장및 보관" concern, but needs careful slicing.

### Look-Through Exposure Board

- Bucket: Next
- Problem: ETF holdings / exposure / cost data exists as foundation but is not yet a strict, user-friendly board for investment suitability.
- User workflow change: Practical Validation shows portfolio-level look-through with coverage, top holdings overlap, concentration, asset class / sector / country, expense, liquidity, leverage objective.
- Evidence:
  - Audit: provider connector plan targets diagnostics 2, 3, 5, 6, 9, 10.
  - Benchmarks: Morningstar X-Ray and IBKR Portfolio Checkup.
- Required code/data/doc areas:
  - `app/services/backtest_practical_validation_provider_context.py`
  - `app/services/backtest_practical_validation_diagnostics.py`
  - `app/web/backtest_practical_validation.py`
  - `finance/loaders/provider.py`
- Dependencies: enough provider snapshot coverage for common ETFs.
- Risks: provider coverage holes can make board look incomplete.
- Validation idea: provider context tests for full / partial / missing coverage.
- Owner skill: `finance-backtest-web-workflow` + `finance-db-pipeline`
- Priority rationale: strong fit, but depends on provider coverage.

### Robustness Lab V1

- Bucket: Next
- Problem: stress / sensitivity exists, but the system does not yet run a compact default robustness suite that challenges a selected source.
- User workflow change: Practical Validation includes a `Robustness Lab` tab with walk-forward, out-of-sample period, parameter perturbation, rebalance cadence, cost / slippage, Monte Carlo or bootstrap, and historical stress summary.
- Evidence:
  - Audit: current stress / sensitivity can remain REVIEW; out-of-sample / overfit controls are not first-class.
  - Benchmarks: CFA backtesting / simulation, QuantConnect optimization, Portfolio Lab Monte Carlo, NBER overfitting evidence.
- Required code/data/doc areas:
  - `finance/strategy.py`
  - `finance/engine.py`
  - `finance/performance.py`
  - `app/services/backtest_practical_validation_stress_sensitivity.py`
  - `app/runtime/backtest.py`
- Dependencies: strategy runtime must expose reproducible parameter / rebalance / cost variants.
- Risks: phase-sized work and computation cost.
- Validation idea: deterministic synthetic suite first, then one DB-backed smoke strategy.
- Owner skill: `finance-strategy-implementation` + `finance-backtest-web-workflow`
- Priority rationale: high impact but not the safest first slice.

### Persistent Monitoring Timeline

- Bucket: Next
- Problem: Selected Dashboard can recheck but persistent monitoring log is optional and thin.
- User workflow change: monthly/rebalance `Save Monitoring Snapshot` records performance, drift, benchmark delta, provider freshness, review signal, and operator action.
- Evidence:
  - Audit: Selected Dashboard is read-only and monitoring log is user-triggered only.
  - Benchmarks: IBKR PortfolioAnalyst reporting and allocation goals; Bloomberg reporting orchestration.
- Required code/data/doc areas:
  - `app/runtime/final_selected_portfolios.py`
  - `app/web/final_selected_portfolio_dashboard.py`
  - `app/runtime/portfolio_selection_v2.py`
  - `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`
- Dependencies: decision packet / source breadcrumb should exist first.
- Risks: can drift toward account aggregation / live management if boundary is not clear.
- Validation idea: append-only helper tests with `persist=False` / temp path.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: important after selection, but should follow gate hardening.

## Later Candidates

### Report Export / Strategy Dossier

- Bucket: Later
- Problem: human-readable backtest reports exist separately, but Final Review packet is not yet exportable as a stable report artifact.
- User workflow change: selected / held / rejected decisions can render to Markdown / PDF-like report.
- Evidence: Portfolio Lab / IBKR / Bloomberg reporting pattern; existing backtest report productization research.
- Required areas: report templates, evidence read model, docs/report index.
- Owner skill: `finance-backtest-web-workflow` plus possibly documents/reporting helpers.

### Product Surface Split

- Bucket: Later
- Problem: Streamlit mixes user-facing product and ops console controls.
- User workflow change: product-facing read models can move to API-backed UI later.
- Evidence: existing UI platform research.
- Required areas: app services, API layer, frontend.
- Owner skill: future platform phase, not this immediate research.

## Parking Lot

- Broker account connection.
- Auto rebalance / broker order generation.
- AI-generated executable strategy deployment.
- Fully licensed holdings database replacement.
- Full institutional risk model clone.
- Account aggregation and personal financial planning.

## Rejected Ideas

- "Add more strategy families first": rejected for now because the bottleneck is validation efficacy, not idea count.
- "Make Final Review a live approval screen": rejected because it violates current no-live-trading boundary.
- "Store full holdings and macro series in JSONL for convenience": rejected because current architecture correctly keeps full rows in DB and compact evidence in JSONL.

## 2026-06-08 Candidate Refresh

### Why A Refresh Is Needed

The May candidate matrix is historically useful, but several "Now" items have since become foundations in the current product: Practical Validation / Final Review evidence gates, selected-route policy, Operations Console, monitoring-first Portfolio Monitoring, Reference Center, and contextual help drift guards.

The next candidate list should therefore focus on what remains after those foundations, not repeat completed phase work.

### Updated Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Product Direction Baseline / Session Operating Model | Now | 5 | 1 | 1 | 5 | 5 | Product research workflow |
| Monitoring Snapshot / Review Loop V2 | Now | 5 | 3 | 3 | 5 | 5 | Backtest web workflow / runtime registry |
| Strategy Promotion Contract For Backtest-Dev Handoff | Now | 5 | 3 | 3 | 4 | 5 | Strategy implementation + backtest workflow |
| Robustness Experiment Registry | Next | 5 | 4 | 4 | 4 | 5 | Strategy implementation / app services |
| Data Provenance / PIT Evidence Contract | Next | 5 | 4 | 4 | 4 | 5 | DB pipeline / loaders / validation services |
| Decision Dossier / Report Artifact V2 | Next | 4 | 3 | 3 | 4 | 4 | Backtest web workflow / reports |
| Legacy Archive Demotion Matrix | Now / Next | 4 | 2 | 2 | 5 | 4 | Backtest web workflow / docs |
| Large Surface Refactor Round 2 | Next | 4 | 4 | 3 | 5 | 4 | Backtest web workflow / integration |
| UI Platform Split Feasibility Refresh | Later | 3 | 5 | 5 | 3 | 3 | Product research / platform phase |

### Now Candidates

#### Product Direction Baseline / Session Operating Model

- Problem: This main-dev session needs a clear role separate from strategy-development sessions.
- User workflow change: future broad requests start with a 1차 / 2차 / 3차 roadmap and research-bundle update before opening development sessions.
- Evidence: Current user request; local docs show no active phase and product direction research workspace is canonical.
- Required areas: current research bundle and final handoff summary.
- Dependencies: none.
- Risk: low.
- Owner skill: `finance-product-research-workflow`.

#### Monitoring Snapshot / Review Loop V2

- Problem: `Operations > Portfolio Monitoring` is read-only and monitoring-first, but durable review history is still optional / thin.
- User workflow change: after scenario update, user can record a review snapshot with benchmark delta, drift, provider freshness, review signal, open issue, operator note, and next review date.
- Evidence:
  - Local audit: scenario results are session-state unless explicitly saved.
  - Benchmark: Koyfin model portfolios emphasize drift monitoring, benchmark comparison, rolling returns, risk metrics, holdings matrix, and reports.
- Required areas:
  - `app/runtime/final_selected_portfolios.py`
  - `app/web/final_selected_portfolio_dashboard.py`
  - `app/runtime/portfolio_selection_v2.py`
  - `.aiworkspace/note/finance/registries/SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`
- Dependencies: define snapshot schema and no-live copy.
- Risk: can drift toward broker/account management if not bounded.
- Owner skill: `finance-backtest-web-workflow`.

#### Strategy Promotion Contract For Backtest-Dev Handoff

- Problem: `backtest-dev` can add or improve strategies, but main product needs an explicit promotion gate before a strategy is treated as governable product workflow input.
- User workflow change: a strategy handoff packet is required before connecting strategy output to Practical Validation / Final Review / Portfolio Monitoring.
- Evidence:
  - Local audit: Risk-On Momentum 5D governance connection remains deferred.
  - Benchmark: QuantConnect lifecycle and Portfolio123 ranking / simulation assumption patterns.
- Required areas:
  - strategy report template under `.aiworkspace/note/finance/reports/backtests/`
  - `finance/engine.py`, `finance/strategy.py`, `finance/transform.py`, strategy-specific runtime owners when implemented later
  - Practical Validation handoff docs / read model when approved
- Dependencies: coordinate with `backtest-dev` outputs.
- Risk: high enough to keep as product design before implementation.
- Owner skill: `finance-strategy-implementation` for future implementation; `finance-product-research-workflow` for current direction.

#### Legacy Archive Demotion Matrix

- Problem: legacy compatibility surfaces are useful but still create conceptual noise.
- User workflow change: every legacy surface gets one of `keep primary`, `archive / recovery`, `hide from primary nav`, `delete only after migration proof`.
- Evidence: current Operations docs already demoted Run History / Candidate Library; route helper still maps legacy panels.
- Required areas:
  - `app/web/backtest_workflow_routes.py`
  - `app/web/operations_overview.py`
  - Reference Center docs / copy
- Dependencies: no data deletion until source-of-truth proof is clear.
- Risk: low if no files are deleted in first pass.
- Owner skill: `finance-backtest-web-workflow`.

### Next Candidates

#### Robustness Experiment Registry

- Problem: robustness evidence exists, but there is no unified run-set registry for parameter sweeps, walk-forward, OOS, regime, cost/slippage, and Monte Carlo/bootstrap experiments.
- User workflow change: Practical Validation can cite a `robustness_run_set_id` instead of many disconnected audit rows.
- Evidence: QuantConnect report / walk-forward patterns; local Validation Efficacy and Backtest Realism audit rows.
- Required areas:
  - strategy runtime wrappers
  - `app/services/backtest_practical_validation_stress_sensitivity.py`
  - new or existing compact registry helper
- Dependencies: strategy family contracts and compute budget.
- Risk: broad; should be sliced by one strategy family first.

#### Data Provenance / PIT Evidence Contract

- Problem: current snapshot, provider staleness, PIT assumptions, and source availability labels are known, but not fully normalized across evidence rows.
- User workflow change: every Final Review packet and monitoring snapshot shows `source_date`, `collected_at`, `available_at_assumption`, `snapshot_kind`, `coverage_status`, and `decision_effect`.
- Evidence: local data docs, Portfolio123 simulation assumptions, Bloomberg data validation pattern.
- Required areas:
  - `finance/data/db/schema.py`
  - `finance/loaders/*`
  - Practical Validation provider / data coverage services
- Dependencies: schema migration / additive storage decision.
- Risk: broad data-model impact.

#### Decision Dossier / Report Artifact V2

- Problem: Decision Dossier download exists, but productized report artifact / report index integration is not the primary workflow.
- User workflow change: Final Review and Monitoring Snapshot can produce a human-readable report that references durable evidence ids.
- Evidence: Bloomberg / Koyfin / IBKR reporting patterns; existing backtest report workspace.
- Required areas:
  - `app/services/backtest_evidence_read_model.py`
  - `app/web/backtest_final_review.py`
  - `.aiworkspace/note/finance/reports/backtests/`
- Dependencies: stable decision packet / monitoring snapshot schema.
- Risk: moderate; report can become stale if it duplicates evidence instead of citing it.

#### Large Surface Refactor Round 2

- Problem: core files remain large after first refactor round.
- User workflow change: none directly; implementation risk decreases for approved feature work.
- Evidence: `wc -l` audit shows `backtest_compare.py`, Portfolio Monitoring UI/runtime, and evidence read model remain large.
- Required areas:
  - `app/web/backtest_compare.py`
  - `app/web/final_selected_portfolio_dashboard.py`
  - `app/runtime/final_selected_portfolios.py`
- Dependencies: choose a feature boundary first.
- Risk: medium; should run in `sub-dev` or a separate implementation session after approval.

### Later / Parking Lot

- Broker account connection.
- Auto rebalance / broker order generation.
- Composer-style automated deployment.
- Full account aggregation.
- Full institutional risk model clone.
- React / API platform migration before product contracts stabilize.
