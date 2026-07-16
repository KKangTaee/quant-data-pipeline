# Overview Market Context U.S. Economic Cycle V1 Notes

Last Updated: 2026-07-16

## Locked Decisions

- V1 geography: United States.
- Phase order: recovery -> expansion -> slowdown -> recession -> recovery.
- Exact V1 catalog: 17 FRED/ALFRED series; ADS/WEI deferred because they need separate connector/vintage contracts.
- Storage: new raw vintage, model artifact, and snapshot tables; no overwrite of the existing macro table.
- Modeling: horizon-specific diagonal Gaussian likelihood, constrained empirical transition prior, direct h1/h2 targets, temperature calibration.
- No new sklearn/statsmodels dependency; use pandas and Python standard library.
- Validation: minimum 120 rolling origins, 2 recession episodes, 12 targets per phase, 75% complete-feature ratio, ECE <= 0.12, and no worse Brier/log loss than the better approved baseline.
- UI: separate cycle component; existing valuation component receives an optional selector-hidden mode.
- Default Market Context submode: economic cycle.
- Operations: backend manual jobs/runbook only; no visible job diagnostic panel or unattended schedule.

## Interpretation Boundary

The model estimates a data-defined macro regime with uncertainty. It does not replace the NBER chronology, predict asset returns, or produce a trade instruction. Rates/credit/inflation can change forecast odds but cannot rewrite the current real-economy phase label.

## 1차 Decisions

- Raw business key is `(series_id, observation_date, realtime_start, source)`; `realtime_end` is updateable interval metadata.
- Official vintage mode is FRED `output_type=2` with explicit `1776-07-04` to `9999-12-31` real-time bounds and pagination.
- `.` and non-finite values persist as explicit missing rows; they are never coerced to zero or dropped.
- Loader applies both SQL window selection and a defensive Python as-of filter for injected/legacy duplicate readers.

## 2차 Decisions

- Transform values remain explicit monthly signals; expanding median/MAD scaling uses only values available through each origin and clamps to `[-4, 4]`.
- Every modeled factor needs at least two indicators and total available coverage must be at least 75%; stale evidence lowers status to `LIMITED`.
- Retrospective current labels use only activity/labor level and three-month momentum, with origin-eligible `USREC` as an override.
- The h0 Gaussian artifact rejects financial/inflation features by contract and cannot publish if any phase has no training support.
- Full model parameters live in `economic_cycle_model_artifact`; UI/history reads compact `economic_cycle_snapshot` rows only.
