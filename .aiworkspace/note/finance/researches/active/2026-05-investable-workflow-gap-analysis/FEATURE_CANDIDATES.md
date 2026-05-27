# Feature Candidates

Status: Draft
Last Updated: 2026-05-28

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
