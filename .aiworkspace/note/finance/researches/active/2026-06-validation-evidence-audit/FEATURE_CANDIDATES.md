# Feature Candidates

Status: Draft recommendation
Last Updated: 2026-06-01

## Summary

The validation evidence audit found that the current workflow has useful technical gates, but several user-facing labels and route states can still read stronger than the evidence supports. The first build should reduce false-positive interpretation before deeper data / execution modeling work begins.

## Candidate Matrix

| Candidate | Bucket | Impact | Effort | Risk | Confidence | Strategic Fit | Owner Area |
|---|---|---:|---:|---:|---:|---:|---|
| Evidence label and selected-route severity hardening | Now | 5 | 2 | 2 | 5 | 5 | Backtest / Final Review / Selected Dashboard UI + evidence read model |
| Replay input snapshot and source hash contract | Next | 5 | 4 | 4 | 4 | 5 | Backtest runtime + Practical Validation services |
| Historical universe / delisting / survivorship evidence expansion | Next | 5 | 5 | 5 | 4 | 5 | DB pipeline + Data Coverage audit |
| Cost / slippage / liquidity scenario model | Next | 5 | 4 | 4 | 4 | 5 | Backtest runtime + Backtest Realism audit |
| Sealed OOS / WFO provenance | Later | 4 | 4 | 4 | 3 | 4 | Strategy runtime + Practical Validation temporal validation |
| Full covariance risk contribution artifact | Later | 3 | 4 | 3 | 3 | 4 | Construction risk / Risk Contribution audit |

## Candidates

### Evidence Label And Selected-Route Severity Hardening

- Bucket: Now
- Problem: `Real-Money`, `Deployment`, `Selected`, `Normal`, and `Allowed` can read like approval even when evidence is only a policy signal, watch item, or monitoring handoff.
- User workflow change: Backtest Analysis reads as a first-pass policy signal; Final Review selected route reads as monitoring-candidate selection; WATCH rows are allowed only with an explicit watch label; Selected Dashboard normal state reads as monitoring baseline clear.
- Evidence: `CURRENT_PROJECT_AUDIT.md` marks Real-Money / deployment / dashboard status as heuristic or preflight unless stronger evidence is present.
- Required code/data/doc areas: `app/web/backtest_result_display.py`, `app/services/backtest_evidence_read_model.py`, `app/web/backtest_final_review_helpers.py`, `app/runtime/final_selected_portfolios.py`, focused service contract tests, audit/recommendation docs.
- Dependencies: none; no DB schema, JSONL registry, saved setup, live approval, order, broker, or auto rebalance changes.
- Risks: UI copy churn can break tests that assert Korean labels; storage values must remain backward compatible.
- Validation idea: `py_compile` touched files and focused `tests.test_service_contracts` gate/dashboard cases.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: Highest immediate false-positive reduction with low blast radius.

### Replay Input Snapshot And Source Hash Contract

- Bucket: Next
- Problem: runtime replay proves current reproducibility but not archival reproducibility.
- User workflow change: Practical Validation can show whether replay used the same input snapshot or a newer DB/runtime state.
- Evidence: audit found no immutable dataset/version hash.
- Required code/data/doc areas: replay service, source contract serialization, result metadata, Practical Validation evidence rows.
- Dependencies: source hash format and input snapshot policy.
- Risks: large artifact boundaries and registry payload growth.
- Validation idea: replay same candidate with fixed snapshot hash and assert source-hash match/mismatch rows.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: Unblocks stronger replay claims.

### Historical Universe / Delisting / Survivorship Evidence Expansion

- Bucket: Next
- Problem: local lifecycle evidence is mostly current-listing partial rows, not broad historical survivorship proof.
- User workflow change: Data Coverage can block broad equity-universe candidates unless historical lifecycle coverage is actual for the tested period.
- Evidence: DB spot check in `CURRENT_PROJECT_AUDIT.md` found only a tiny actual historical-listing slice.
- Required code/data/doc areas: collectors/loaders, symbol lifecycle tables, Data Coverage audit.
- Dependencies: source choice for historical listings / delisting / ticker actions.
- Risks: provider licensing, source incompleteness, backfill complexity.
- Validation idea: known delisted symbols appear in candidate universe and Data Coverage rows downgrade missing lifecycle evidence.
- Owner skill: `finance-db-pipeline`
- Priority rationale: Core data correctness risk.

### Cost / Slippage / Liquidity Scenario Model

- Bucket: Next
- Problem: fixed bps netting does not model spread, market impact, trade size, or liquidity-dependent slippage.
- User workflow change: selected route requires base / stress / severe cost-slippage scenario evidence.
- Evidence: audit marks current fixed-bps cost proof as real but incomplete for execution realism.
- Required code/data/doc areas: runtime cost model, Backtest Realism audit, liquidity capacity rows, UI tables.
- Dependencies: trade-size assumptions and provider spread/ADV availability.
- Risks: false precision if model looks more realistic than input data supports.
- Validation idea: fragile candidate fails stressed scenario while robust low-turnover candidate passes.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: Reduces execution false positives.

### Sealed OOS / WFO Provenance

- Bucket: Later
- Problem: current OOS / WFO / regime checks are post-hoc unless candidate creation and holdout sealing are recorded.
- User workflow change: temporal validation distinguishes post-hoc robustness from pre-registered OOS evidence.
- Evidence: audit marks rolling / OOS / regime as real calculations but not independent validation by default.
- Required code/data/doc areas: candidate creation metadata, temporal validation service, Final Review evidence rows.
- Dependencies: candidate search provenance and parameter sweep count.
- Risks: hard to retrofit old candidates.
- Validation idea: candidate without sealed holdout remains REVIEW; candidate with sealed holdout can PASS OOS policy.
- Owner skill: `finance-strategy-implementation`
- Priority rationale: Important but depends on upstream candidate provenance.

### Full Covariance Risk Contribution Artifact

- Bucket: Later
- Problem: current risk contribution uses proxy monthly contribution rather than full marginal covariance contribution.
- User workflow change: weighted mixes get component risk attribution with source hashes and rolling stability.
- Evidence: audit marks current risk contribution as proxy.
- Required code/data/doc areas: risk contribution audit, component return matrix persistence, Final Review appendix.
- Dependencies: stable component return matrix contract.
- Risks: complexity and interpretability.
- Validation idea: dominant risk contributor is flagged even when nominal weight is moderate.
- Owner skill: `finance-backtest-web-workflow`
- Priority rationale: Useful, but lower urgency than PIT/replay/cost gates.

## Parking Lot

- Broker/account connection, order staging, live approval, and automatic rebalancing remain out of scope.
- Tax-lot and account-specific after-tax modeling remain out of scope until execution boundary changes are explicitly approved.

## Rejected Ideas

- Treat all existing `REVIEW` items as blockers immediately. This would over-block current workflows and should be done per evidence group after user review.
- Rename storage route constants such as `SELECT_FOR_PRACTICAL_PORTFOLIO`. Storage compatibility matters more than label polish; user-facing labels can be improved without changing persisted values.
