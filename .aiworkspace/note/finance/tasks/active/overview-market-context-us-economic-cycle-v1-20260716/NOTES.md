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
