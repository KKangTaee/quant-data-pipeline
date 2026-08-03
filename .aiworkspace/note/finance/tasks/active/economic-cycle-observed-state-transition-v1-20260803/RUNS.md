# Economic Cycle Observed State / Transition V1 Runs

Last Updated: 2026-08-03

## Audit And Design Validation

- Inspected economic-cycle catalog, PIT feature, label, model, validation, pipeline, loader,
  result persistence, service and React workbench ownership.
- Rebuilt the PIT monthly feature panel through 2026-07-31 from stored vintage data.
- Compared raw, 3M mean, 3M median, 3M EWMA and 6M smoothing candidates.
- Measured transitions, one-month flipbacks, run duration, non-adjacent changes and current
  coordinates.
- Compared PIT-origin quadrants with a latest-revised-history reference to expose revision
  sensitivity.
- Reproduced current snapshot, artifact metrics and market implication payload from local DB.

## Existing Test Baseline

- Economic-cycle related test selection: 172 passed before production changes.
- The passing baseline includes obsolete product expectations such as provisional future
  probability display; implementation must replace those contracts instead of treating them
  as acceptance of the current behavior.

## Visual Design

- Built an interactive design review showing current state, actual path, recent changes and
  transition conditions.
- Revised the design after user feedback so the existing full asset-card structure is shown
  and explicitly frozen.
- Visual prototypes are conversation artifacts outside the repository and are not commit
  candidates.

## Git Hygiene

- Independent audit research was committed as `22d59e704`.
- Pre-existing registry, run-history, QA images and run artifacts remain untouched and are not
  part of this task.

## Written-Spec Self Review

- Placeholder and whitespace checks found no unresolved markers or malformed diff lines.
- Rechecked formula, breadth universe, revision reference, state transition, persistence,
  service, graph and frozen asset contracts against the approved scope.
- Corrected a state-machine ambiguity: observed phase changes immediately at a boundary while a
  separate anchor retains the last confirmed phase until persistence, diffusion and
  corroboration all pass.
- Confirmed current asset builder ignores the legacy horizons argument and preserves the fixed
  rates, equities, gold, dollar and commodities output order.

## Task 1 TDD — Observed State / Transition Domain

- RED: 8 formula/eligibility tests failed because the observed-state module did not exist.
- GREEN: deterministic 3M level, non-overlapping momentum, eight-series breadth, 1/3/6M change,
  revision sensitivity and confidence tests passed.
- RED: 4 transition tests failed on missing condition/state-machine behavior.
- GREEN: first boundary crossing, delayed anchor promotion, reversal, unavailable-month streak
  break and non-adjacent observation contracts passed.
- Additional RED/GREEN: a missing activity factor column initially raised instead of returning
  UNAVAILABLE; the focused test now passes.
- Verification: `13 passed` observed-state tests, `6 passed` existing feature tests, `py_compile`
  and `git diff --check` passed.

## Task 2 TDD — Snapshot / Loader / Pipeline

- RED: schema, serializer, UPSERT default and current-phase ENUM migration produced 4 expected
  failures; additive schema and round-trip implementation made all 9 result tests pass.
- RED/GREEN: persisted h0 was forced to recovery while actual coordinates were contraction;
  snapshot `current_phase` now follows observed state and stores all three canonical JSON records.
- RED/GREEN: default PIT/revised panel loader methods were removed, tested absent, and restored;
  revised diagnostic uses the materialization cutoff and strips revision intervals before rebuild.
- Additional RED/GREEN: observed JSON with unavailable phase initially fell back to h0 recovery;
  persisted `current_phase` now remains null instead.
- Verification: result + pipeline selection `27 passed`, `py_compile` and `git diff --check`
  passed. Three pre-existing edgar deprecation warnings remain.
