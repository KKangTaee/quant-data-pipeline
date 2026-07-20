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
