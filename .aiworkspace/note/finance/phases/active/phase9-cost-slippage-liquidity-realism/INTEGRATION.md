# Phase 9 Cost / Slippage / Liquidity Realism Integration

Status: Complete
Created: 2026-05-29

## Integration Boundaries

| Area | Files | Risk |
| --- | --- | --- |
| Backtest Realism Audit | `app/services/backtest_realism_audit.py` | Must not treat assumptions as applied net performance |
| Practical Validation diagnostics | `app/services/backtest_practical_validation_diagnostics.py` | Operability/cost rows must remain compact and not fetch providers directly |
| Runtime execution | `app/services/backtest_execution.py`, `finance/strategy.py`, `finance/engine.py` | Cost application proof must match actual result generation |
| Provider / price loaders | `finance/loaders/provider.py`, `finance/loaders/price.py` | Full liquidity data remains DB-backed |
| Final Review gate | `app/services/backtest_evidence_read_model.py` | selected-route blockers must preserve existing gate semantics |
| Tests | `tests/test_service_contracts.py` | Contracts should prove `NOT_RUN` and assumption-only evidence do not pass |
| Docs | `docs/flows/*`, `docs/data/*`, `docs/ROADMAP.md` | Must distinguish implemented behavior from future plans |

## Integrated So Far

### cost-model-source-contract-review-v1

- Touched:
  - `app/runtime/backtest.py`
  - `app/runtime/history.py`
  - `app/services/backtest_realism_audit.py`
  - `app/services/backtest_practical_validation_source.py`
  - `app/web/backtest_candidate_review_helpers.py`
  - `tests/test_service_contracts.py`
- Runtime cost application proof is now compact metadata, not a new persistence layer.
- Backtest Realism Audit can expose `cost_model_contract` and does not pass cost bps without application proof.
- Follow-up integration risk: weighted / saved mix sources may need per-component turnover and cost aggregation in Phase 9-2 / 9-3.

### turnover-rebalance-evidence-v1

- Touched:
  - `app/runtime/backtest.py`
  - `app/runtime/history.py`
  - `app/services/backtest_realism_audit.py`
  - `app/services/backtest_practical_validation_source.py`
  - `app/web/backtest_candidate_review_helpers.py`
  - `tests/test_service_contracts.py`
- Runtime turnover evidence is now explicit compact metadata.
- Backtest Realism Audit exposes `turnover_evidence_contract` and treats cadence-only evidence as `REVIEW`.
- Follow-up integration risk: weighted / saved mix sources still need per-component turnover aggregation if the source is not a single strategy.

### net-cost-curve-application-v1

- Touched:
  - `app/runtime/backtest.py`
  - `app/runtime/history.py`
  - `app/services/backtest_realism_audit.py`
  - `app/services/backtest_practical_validation_source.py`
  - `app/web/backtest_candidate_review_helpers.py`
  - `tests/test_service_contracts.py`
- Runtime net cost curve proof is compact metadata flowing through existing source snapshots.
- Backtest Realism Audit exposes `net_cost_curve_contract` and adds a separate `Net cost curve proof` row.
- Follow-up integration risk: weighted / saved mix sources may need component-level net curve proof aggregation before final Phase 9 closeout.

### liquidity-capacity-evidence-v1

- Touched:
  - `app/services/backtest_practical_validation_provider_context.py`
  - `app/services/backtest_realism_audit.py`
  - `tests/test_service_contracts.py`
- Provider context now emits compact liquidity / capacity metrics without carrying raw provider rows into workflow JSONL.
- Backtest Realism Audit exposes `liquidity_capacity_contract` and treats fresh official actual evidence as the strong PASS path.
- Bridge / proxy, stale / unknown freshness, partial coverage, and legacy pass-only evidence remain `REVIEW` or `NEEDS_INPUT`.
- Follow-up integration risk: cost / slippage sensitivity remains separate from liquidity capacity and starts in Phase 9-5.

### cost-slippage-sensitivity-audit-v1

- Touched:
  - `app/services/backtest_realism_audit.py`
  - `tests/test_service_contracts.py`
- Backtest Realism Audit exposes `cost_slippage_sensitivity_contract` and adds a separate `Cost / slippage sensitivity evidence` row.
- Explicit cost / slippage sensitivity can PASS, generic robustness-only sensitivity stays `REVIEW`, and missing cost / net curve baseline stays `NEEDS_INPUT`.
- Follow-up integration risk: selected-route gate policy should be checked against the new row in Phase 9-6.

### backtest-realism-gate-policy-refinement-v1

- Touched:
  - `app/services/backtest_evidence_read_model.py`
  - `tests/test_service_contracts.py`
- Final Review gate policy now merges failing Backtest Realism row criteria into the `backtest_realism` policy row evidence.
- Cost / slippage sensitivity and liquidity row-level gaps are visible in selected-route gate evidence.
- Row-level `NEEDS_INPUT` maps to blocker severity and `REVIEW` maps to review-required without adding waiver, memo, or live execution behavior.

## Verification Plan

Completed on 2026-05-29:

- `.venv/bin/python -m py_compile app/services/backtest_realism_audit.py app/services/backtest_evidence_read_model.py app/services/backtest_practical_validation_provider_context.py tests/test_service_contracts.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python -m unittest tests.test_service_contracts` (90 tests)
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`

Storage boundary:

- No registry JSONL, saved setup, run history, run artifact, user memo, approval, order, or auto rebalance artifact is part of Phase 9 closeout.
- `finance/.DS_Store` remains an unstaged local generated artifact.
