# Walk-forward / OOS Source Map V1

Status: Complete
Created: 2026-05-29

## Summary

Current code already has enough curve plumbing to start Phase 10 without a new storage layer.
The main gap is that rolling / OOS / regime evidence is split across runtime metadata, Robustness Lab, and market-context diagnostics, but Final Review does not yet get explicit walk-forward / OOS / regime audit rows with selected-route gate severity.

## Current Evidence Sources

| Evidence | Current Source | Reusable For Phase 10 | Gap |
| --- | --- | --- | --- |
| Portfolio curve | `app/services/backtest_practical_validation_diagnostics.py` `_build_curve_context()` reads runtime replay curve, embedded source curve, component curves, DB price proxy fallback | Yes | Need a temporal validation helper that declares source strength instead of treating all curves equally |
| Benchmark curve | `_build_curve_context()` reads runtime benchmark curve, embedded benchmark curve, or DB price proxy by benchmark ticker | Yes | Need OOS / walk-forward calculations to require benchmark parity before relative PASS |
| Runtime replay / period coverage | Practical Validation `curve_evidence` includes `replay_attempt` and `period_coverage` | Yes | Already audited, but not enough to prove OOS / walk-forward robustness |
| Rolling evidence | `_rolling_validation_evidence()` computes rolling CAGR / MDD from monthly portfolio curve | Partial | It accepts benchmark curve but currently uses only portfolio curve; no rolling excess return contract |
| Runtime rolling / OOS metadata | `app/runtime/backtest.py` `_build_rolling_and_out_of_sample_review_surface()` aligns strategy / benchmark and stores rolling / OOS status metadata | Yes | Metadata is visible in backtest result display/history but not a dedicated Practical Validation audit row |
| Regime / macro suitability | Practical Validation uses provider macro snapshot when available, otherwise recent price-action proxy | Partial | This is a current market suitability snapshot, not a historical regime split performance test |
| Validation Efficacy Audit | `build_validation_efficacy_audit()` rows cover source, data trust, runtime replay, period coverage, benchmark parity, provider freshness, robustness, PIT, survivorship, execution boundary | Yes | No explicit walk-forward / OOS / regime row yet |
| Final Review gate | `build_investability_evidence_packet()` and `build_investability_gate_policy()` merge validation checks, diagnostics, critical gaps, and audits | Yes | Gate has robustness / validation efficacy groups, but no explicit temporal validation group or row |

## Important Code Anchors

| File | Lines | Meaning |
| --- | --- | --- |
| `app/services/backtest_practical_validation_diagnostics.py` | 393-486 | Curve source hierarchy: runtime replay, embedded source, component curve, DB price proxy, benchmark proxy |
| `app/services/backtest_practical_validation_diagnostics.py` | 1540-1551 | Practical Validation already emits compact `curve_evidence` |
| `app/services/backtest_practical_validation_stress_sensitivity.py` | 269-349 | Existing rolling evidence computes portfolio-only rolling CAGR / MDD |
| `app/runtime/backtest.py` | 754-952 | Runtime already computes aligned rolling / OOS review metadata against benchmark |
| `app/services/backtest_validation_efficacy.py` | 424-482 | Validation Efficacy Audit does not yet include temporal validation rows |
| `app/services/backtest_evidence_read_model.py` | 641-821 | Final Review evidence packet reads Validation Efficacy / Data Coverage / Backtest Realism audits |
| `app/services/backtest_evidence_read_model.py` | 362-460 | Gate policy merges packet checks, diagnostics, critical gaps, and audit rows |

## Gap Audit

| Gap | Severity | Reason | Recommended Fix |
| --- | --- | --- | --- |
| Rolling evidence does not compute rolling excess return vs benchmark in Practical Validation | High | A strategy can pass absolute rolling CAGR while still underperforming benchmark | 10-2 should compute aligned rolling window return, benchmark return, excess return, strategy MDD, benchmark MDD, drawdown gap |
| OOS evidence exists in runtime metadata but is not first-class Practical Validation / Final Review audit evidence | High | Final Review selected-route can miss explicit in-sample vs out-sample degradation | 10-3 should read or recompute compact OOS holdout rows from normalized curves |
| Regime diagnostic is suitability / current macro context, not historical regime split performance | Medium | It answers "current macro context" more than "strategy worked across regimes" | 10-4 should define regime buckets and compute strategy / benchmark behavior per bucket |
| Curve source strength is mixed | Medium | Runtime replay, embedded curve, and DB price proxy are not equally strong evidence | 10-2 should include source strength in temporal validation contract |
| Validation Efficacy Audit has no explicit temporal validation row | High | Gate policy cannot treat OOS / walk-forward gap independently | 10-5 should merge temporal validation row through Validation Efficacy before selected-route gate |
| Period insufficiency semantics need to be explicit | Medium | Short histories can produce misleading split outcomes | 10-2 / 10-3 should map insufficient months to `NEEDS_INPUT` or `REVIEW`, not pass |

## Recommended Task Order

1. `walkforward-split-contract-v1`
   - Add compact walk-forward / rolling window evidence contract.
   - Reuse normalized portfolio / benchmark curves.
   - Include benchmark-aligned rolling excess return and drawdown gap.

2. `oos-holdout-validation-contract-v1`
   - Reuse runtime OOS logic where possible.
   - Build explicit in-sample / out-sample compact rows.
   - Mark insufficient split history as `NEEDS_INPUT` or `REVIEW`.

3. `regime-split-validation-v1`
   - Start from DB macro / provider macro availability.
   - If only price-action proxy exists, keep it `REVIEW`.
   - Avoid hard PASS without loader-backed regime source.

4. `validation-efficacy-gate-policy-refinement-v2`
   - Add temporal validation rows to Validation Efficacy.
   - Ensure Final Review selected-route gate sees temporal gaps as blocker or review-required.

## Test Scope For Next Implementation

For 10-2:

- Add focused unit tests in `tests/test_service_contracts.py` for:
  - enough aligned portfolio / benchmark history -> PASS or REVIEW based on rolling excess / MDD
  - missing portfolio curve -> `NEEDS_INPUT`
  - missing benchmark curve -> `NEEDS_INPUT` or `REVIEW` for relative evidence
  - short history -> not PASS
  - proxy curve source -> not stronger than REVIEW unless explicitly allowed

Run:

- `.venv/bin/python -m py_compile app/services/backtest_practical_validation_diagnostics.py app/services/backtest_validation_efficacy.py app/services/backtest_evidence_read_model.py`
- `.venv/bin/python -m pytest tests/test_service_contracts.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py`
- `.venv/bin/python .aiworkspace/plugins/quant-finance-workflow/scripts/check_finance_refinement_hygiene.py`
- `git diff --check`
