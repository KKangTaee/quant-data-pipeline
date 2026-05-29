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

## Verification Plan

- `git diff --check`
- compile touched service/runtime modules
- focused Backtest Realism Audit service contracts
- full `tests.test_service_contracts`
- storage boundary review before commit
