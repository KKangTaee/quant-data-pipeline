# Phase 9 Cost / Slippage / Liquidity Realism Status

Status: Complete
Created: 2026-05-29

## Current Status

- [x] Phase 8 closeout confirmed.
- [x] Phase 9 scope opened.
- [x] Phase 9 task board created.
- [x] Cost model source contract review complete.
- [x] Turnover / rebalance evidence refinement complete.
- [x] Net cost curve application proof complete.
- [x] Liquidity / capacity evidence refinement complete.
- [x] Cost / slippage sensitivity audit complete.
- [x] Backtest Realism gate policy refinement complete.
- [x] Phase 9 integrated QA / closeout complete.

## Latest Update

2026-05-29:

- `phase9-integrated-qa-closeout` completed.
- Integrated QA passed: Phase 9 touched service compile, UI / engine boundary checker, full `tests.test_service_contracts` 90 tests, refinement hygiene check, and `git diff --check`.
- Phase 9 closeout summary was added under `phases/done/`; next hardening target is Phase 10 walk-forward / out-of-sample / regime split validation.
- `finance/.DS_Store` remains a local generated artifact and is not part of the phase commit.

2026-05-29:

- `backtest-realism-gate-policy-refinement-v1` completed.
- Final Review gate policy now merges failing Backtest Realism row-level evidence into the `backtest_realism` policy row.
- Cost / slippage sensitivity and liquidity gaps are visible in selected-route gate evidence; row-level `NEEDS_INPUT` maps to blocker severity and `REVIEW` maps to review-required.
- No new JSONL registry, user memo, preset, waiver persistence, approval, order, or auto rebalance behavior was added.

2026-05-29:

- `cost-slippage-sensitivity-audit-v1` completed.
- Backtest Realism Audit now reads read-only `cost_slippage_sensitivity_contract_v1` and displays a separate `Cost / slippage sensitivity evidence` row.
- Explicit cost / slippage sensitivity can PASS; generic robustness sensitivity without a cost / slippage axis remains REVIEW, and missing cost / net curve baseline remains NEEDS_INPUT.
- No new JSONL registry, user memo, preset, raw run artifact, DB schema, provider fetch, approval, order, or auto rebalance behavior was added.

2026-05-29:

- `liquidity-capacity-evidence-v1` completed.
- Provider operability context now exposes compact capacity metrics and keeps bridge / proxy evidence in `REVIEW` even when coverage is high.
- Backtest Realism Audit now reads `liquidity_capacity_contract_v1`; fresh official actual capacity evidence is the strong PASS path, while stale / partial / weak source / legacy pass evidence remains REVIEW or NEEDS_INPUT.
- No new JSONL registry, user memo, preset, approval, order, auto rebalance, DB schema, or UI direct provider fetch was added.

2026-05-29:

- `net-cost-curve-application-v1` completed.
- Runtime now emits compact `net_cost_curve_contract_v1` metadata proving whether gross / net / estimated cost curve evidence is measurable.
- Practical Validation source snapshots preserve net cost curve proof, and Backtest Realism Audit separates measurable cost impact, zero-cost, missing turnover estimate, and missing proof.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.

2026-05-29:

- `turnover-rebalance-evidence-v1` completed.
- Runtime now emits compact `turnover_evidence_contract_v1` metadata and avoids fake turnover estimates when holdings columns are missing.
- Practical Validation source snapshots preserve turnover evidence, and Backtest Realism Audit separates actual holdings-derived turnover, legacy estimate, cadence-only, and missing evidence.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.

2026-05-29:

- `cost-model-source-contract-review-v1` completed.
- Runtime now marks transaction-cost postprocessing with a compact `cost_model_source_contract_v1` metadata contract.
- Practical Validation source snapshots preserve the compact cost model snapshot, and Backtest Realism Audit treats cost bps without application proof as `REVIEW`.
- No new JSONL registry, user memo, preset, approval, order, or auto rebalance behavior was added.

2026-05-29:

- Phase 9 starts after Phase 8 lifecycle evidence closeout.
- Current Backtest Realism Audit already reads cost, turnover, liquidity, net policy, rebalance timing, tax/account, and execution boundary rows.
- The next task should map the cost evidence source contract before changing runtime behavior.

## Next

- Phase 9 complete.
- Next: open Phase 10 walk-forward / out-of-sample / regime split validation when implementation resumes.
