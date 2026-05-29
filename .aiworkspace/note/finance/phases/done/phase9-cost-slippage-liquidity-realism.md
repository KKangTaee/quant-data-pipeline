# Phase 9 Cost / Slippage / Liquidity Realism Closeout

Status: Complete
Completed: 2026-05-29

## Purpose

Phase 9 strengthened Backtest Realism evidence after Phase 8 lifecycle / survivorship hardening.
The goal was to make good-looking backtests harder to over-trust by separating cost assumptions, applied net cost proof, turnover, liquidity / capacity, cost / slippage sensitivity, and selected-route gate severity.

This phase did not add user memo storage, preset persistence, broker order behavior, live approval, or auto rebalance.

## Completed Slices

| Slice | Result |
| --- | --- |
| 9-0 Phase board | Phase 9 board opened with cost / slippage / liquidity realism scope |
| 9-1 Cost model source contract | Runtime / source snapshots expose whether transaction cost is applied to result curve |
| 9-2 Turnover / rebalance evidence | Holdings-derived turnover, legacy estimate, cadence-only, and missing evidence are separated |
| 9-3 Net cost curve application | Gross / net / estimated cost curve proof separates measurable cost impact from missing proof |
| 9-4 Liquidity / capacity evidence | Provider operability compact metrics identify fresh official evidence versus stale / partial / proxy evidence |
| 9-5 Cost / slippage sensitivity audit | Explicit cost / slippage sensitivity is required for PASS; generic robustness-only sensitivity remains REVIEW |
| 9-6 Backtest Realism gate policy | Failing Backtest Realism row criteria surface in Final Review selected-route gate evidence |
| 9-7 Integrated QA closeout | Compile, boundary, service contract, hygiene, diff, docs, and storage boundary checks completed |

## Implemented Boundary

- Backtest Realism Audit remains a read-only service read model.
- Final Review selected-route gate reads compact audit evidence and does not create a live approval.
- Full provider / liquidity data remains DB / loader backed.
- Workflow JSONL continues to store only compact validation / decision evidence through existing flows.
- `NEEDS_INPUT` / `BLOCKED` realism routes block selected-route; `REVIEW` requires review / hold before selection.

## Verification

2026-05-29:

- `py_compile` passed for Phase 9 touched service/read model files.
- UI / engine boundary checker passed.
- `tests.test_service_contracts` passed, 90 tests.
- Finance refinement hygiene check passed with only `finance/.DS_Store` reported as an unstaged generated artifact.
- `git diff --check` passed.

## Residual Risks

- Phase 9 does not implement a broker-grade execution simulator or market impact model.
- Weighted / saved mix sources may still need deeper component-level cost / turnover aggregation.
- Liquidity / capacity thresholds are not yet profile-specific.
- Cost / slippage sensitivity is audited when present; a new runtime cost bps sweep engine is future work.

## Phase 10 Handoff

Next hardening target:

- walk-forward validation
- out-of-sample split validation
- regime split / market condition robustness
- stronger separation between research-fit and deployable-fit evidence

Phase 10 should keep the same storage rule: evidence data can be DB-backed when it improves validation, but user memo / preset-like storage should not expand.
