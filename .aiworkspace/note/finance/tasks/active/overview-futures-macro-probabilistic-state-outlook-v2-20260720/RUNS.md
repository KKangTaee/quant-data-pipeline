# Overview Futures Macro Probabilistic State Outlook V2 Runs

## 2026-07-20 — Read-Only Root-Cause Reconstruction

Commands / actions:

- inspected Finance INDEX / ROADMAP / PROJECT_MAP and the completed V1 task
- inspected `futures_macro_pattern.py`, `futures_macro_pattern_validation.py`, snapshot service, React pattern map, and relevant tests
- loaded the compatible DB-only materialized snapshot
- rebuilt fixed-cutoff feature frames for 2026-07-17 and 2026-07-20
- compared common historical 5D family feature rows
- inspected current Brier, path error, and coverage metrics

Important results:

```text
2026-07-17
20D 2026-06-24  x=+0.409192 y=+0.130136
5D  2026-07-12  x=-0.227341 y=+0.437546
NOW 2026-07-17  x=-0.704503 y=-0.076243

2026-07-20
20D 2026-06-26  x=-0.426852 y=-0.298409
5D  2026-07-14  x=+0.285382 y=+0.152634
NOW 2026-07-20  x=-0.311459 y=-0.237478

PIT max difference through 2026-07-17: 0.0
```

Current compatible snapshot:

```text
source_marker: 2026-07-20 00:00:00
as_of_date: 2026-07-20
materialized_at: 2026-07-20 21:08:13
algorithm_version: pattern_outlook_v4_conservative_status_10y
```

Current validation:

```text
5D  Brier 0.690140 vs 0.697565 baseline
    path 0.735945 vs 0.735919 baseline
    nominal 50% coverage 0.267692

20D Brier 0.719307 vs 0.718834 baseline
    path 0.765790 vs 0.782831 baseline
    nominal 50% coverage 0.282828
```

No code, DB row, registry, or saved setup was modified by this analysis.

## 2026-07-20 — Design Approval And Implementation Planning

- User explicitly approved `DESIGN.md`.
- Applied `superpowers:writing-plans` to map exact files, interfaces, TDD commands, publication gates, and commit checkpoints.
- Added `IMPLEMENTATION_PLAN.md` with 3 stages and 9 implementation tasks.
- No implementation code, DB schema, or production data was changed.

## 2026-07-20 — Task 1 Completed Session Resolver

- RED: `tests.test_futures_macro_sessions` failed because the resolver module did not exist.
- GREEN: 7 resolver/loader contract tests passed.
- Regression: 28 tests in `tests.test_futures_macro_sessions` and `tests.test_futures_macro_pattern_validation` passed.
- `git diff --check`: pass.
- Current state now excludes in-progress canonical sessions and reports pending-session evidence.

## 2026-07-20 — Task 2 Canonical State And Same-State Target

- RED: canonical state/target imports were missing; old terminal delta differed from the same-state target.
- GREEN: observed path, terminal regime, and terminal displacement now reuse `S(t)`.
- Regression: 52 Futures Macro pattern/session/snapshot tests passed.
- Actual DB replay at 2026-07-20 12:00 UTC kept current at 2026-07-17 and marked 2026-07-20 pending.
- Actual DB replay after the 18:15 ET cutoff moved current to 2026-07-20; common states through 2026-07-17 had maximum x/y difference `0.0`.
- No production DB row was written.

## 2026-07-20 — Task 3 PIT Macro And Event Context

- RED: `futures_macro_context` and DB-only market-event loader did not exist; cycle history lacked a known-at boundary.
- GREEN: 4 context tests passed, including later-collected event exclusion and no pre-first-snapshot fill.
- Economic Cycle result regression: 5 pytest tests passed through `PYTHONPATH=. uv run --with pytest`.
- New modules and the modified cycle loader passed `py_compile`; `git diff --check` passed.
- No provider call, DB write, or Economic Cycle publication change was added.

## 2026-07-20 — Task 4 Reduced Momentum And Weighted Analogs

- RED: fixed predictor and weighted episode module did not exist.
- GREEN: 5 model tests passed for exact 16-feature projection, purge/spacing, future-row immunity, temperature weighting, and M2 missing-context degradation.
- Context + model regression: 9 tests passed; new module passed `py_compile` and `git diff --check`.
- M1 remains available without macro context; M2 returns an explicit unavailable reason instead of filling missing macro values.

## 2026-07-20 — Task 5 Publication Gate Slice

- RED: V2 probability, coordinate, vector, and joint-region functions did not exist.
- GREEN: 3 new publication tests passed for `VERIFIED` / `PROVISIONAL` / `NO_EDGE`, coordinate-vector independence, and weighted 50%/80% ellipses.
- Pattern validation + outlook model regression: 33 tests passed; `git diff --check` passed.
- Remaining Task 5 work is the nested chronological candidate selector and V2 horizon snapshot integration; Task 5 is not marked complete.

## 2026-07-20 — Task 5 Nested Selection And V2 Snapshot Completion

- RED: M1 winner, M2 incremental winner, deterministic simplicity tie, and incomplete shared-fold coverage selection tests failed before the selector existed.
- GREEN: candidate selection now compares B0/B1 and the fixed M1/M2 × temperature grid on past-only inner evaluations; incomplete M2 evaluation coverage is excluded.
- Outer validation uses 756-session minimum training, 63-session tests, horizon purge/sampling, and evaluates only the inner-selected configuration.
- Probability and coordinate improvements use deterministic 2,000-sample moving-block bootstrap lower bounds (`seed=20260720`, block=horizon).
- Current output is `futures_macro_pattern_outlook_v2` / `pattern_outlook_v5_same_state_nested_hybrid` with separate probability, coordinate, and vector statuses.
- The old sparse conditional path is absent from V2 horizon output; weighted 50%/80% joint terminal ellipses are retained as raw model evidence.
- Full 2차 regression: 56 tests passed across pattern, completed-session, PIT context, outlook model, and pattern validation suites.
- Additional 1,000-day synthetic smoke produced chronological evaluations for both horizons; the baseline won, so the implementation did not force an M1/M2 edge.
- `py_compile` and `git diff --check`: pass. No production DB row was written.
