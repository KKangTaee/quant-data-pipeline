# Phase 9 Cost / Slippage / Liquidity Realism Integration

Status: Active
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

## Verification Plan

- `git diff --check`
- compile touched service/runtime modules
- focused Backtest Realism Audit service contracts
- full `tests.test_service_contracts`
- storage boundary review before commit
