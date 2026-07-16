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
- Official vintage mode is FRED long-form `output_type=1` with explicit `1776-07-04` to `9999-12-31` real-time bounds and pagination. `series/vintagedates` partitions daily series into at most 2,000 vintage dates per request, and each observation page is normalized and UPSERTed before the next page.
- `.` and non-finite values persist as explicit missing rows; they are never coerced to zero or dropped.
- Loader applies both SQL window selection and a defensive Python as-of filter for injected/legacy duplicate readers.

## 2차 Decisions

- Transform values remain explicit monthly signals; expanding median/MAD scaling uses only values available through each origin and clamps to `[-4, 4]`.
- Every modeled factor needs at least two indicators and total available coverage must be at least 75%; stale evidence lowers status to `LIMITED`.
- Retrospective current labels use only activity/labor level and three-month momentum, with origin-eligible `USREC` as an override.
- The h0 Gaussian artifact rejects financial/inflation features by contract and cannot publish if any phase has no training support.
- Full model parameters live in `economic_cycle_model_artifact`; UI/history reads compact `economic_cycle_snapshot` rows only.

## 3차 Decisions

- h1/h2 fit direct shifted targets; the smoothed transition matrix is context/prior rather than a substitute for direct horizon evidence.
- Temperature selection uses only earlier eligible out-of-fold targets at each rolling origin and is stored separately per horizon.
- Publication gates are horizon-specific. A bundle can remain usable when h0 is READY and h1/h2 are LIMITED, but numeric fields for every LIMITED horizon are persisted as absent.
- Artifact hashes include the training cutoff, horizon parameters, and decisions; replay always passes its origin-specific artifact directly instead of selecting a later current artifact.
- Replay caches a strict vintage read only under its true forecast origin. The origin row is never bound to the preceding training cutoff.
- Manual collection and materialization jobs were added without an unattended schedule or a visible run/status panel.

## 4차 Decisions

- The Overview service parses only persisted artifact/snapshot/history rows and returns the stable `economic_cycle_v1` JSON contract; it never imports the vintage collector.
- The same-level selector order is `경제 사이클 | S&P 500 | 미국 개별주식`, with economic cycle as the default and unknown legacy values falling back safely.
- Explicit S&P 500/U.S.-stock modes build only their selected valuation model and hide the React component's internal instrument selector; legacy callers still build both.
- The main reading order is three four-phase probability cards, 18-month cycle clock, real-economy/forecast-context evidence, conditional market implications, then a 121-month regime ribbon.
- Model phase and NBER recession are visually and semantically separate. LIMITED months use a hatch, and LIMITED horizons render a reason instead of a fabricated `0%`.
- The cycle component emits no provider, materialization, refresh, or trading action; 420px CSS stacks the main regions without horizontal scroll.

## 5차 Decisions

- Schema sync succeeded for all three tables and verified the raw/artifact/snapshot unique contracts. Local row count is 0 for each table.
- `FRED_API_KEY` is absent in this worktree environment. The explicit collection wrapper failed safely before provider/DB mutation, so actual training, replay, and official metadata spot audit were not fabricated.
- `NOT_MATERIALIZED` maps to a usable `LIMITED` read model with no numeric horizons. This satisfies the approved failure branch; actual model performance remains unknown until official vintages are collected.
- Browser QA found one real Streamlit selector-state defect: the widget key was reassigned after instantiation. A RED regression test now prevents post-widget assignment and invalid legacy values are removed before widget creation without pre-seeding the key.
- Existing service contracts that described Market Context as direct valuation-only were updated to the approved outer router. The remaining Sentiment literal-source assertion fails on the pre-existing branch state and is unrelated to this feature.
- QA screenshot is a generated artifact outside git staging: `/Users/taeho/.codex/qa/economic-cycle/overview-economic-cycle-desktop-20260716.png`.
