# Economic Cycle Observed State / Transition V1 Risks

Last Updated: 2026-08-03

## Revision Sensitivity

PIT and revised-history quadrant disagreement remains material even after smoothing. The design
therefore keeps PIT as authority, exposes a separate revision-sensitivity state and never turns
confidence into a probability.

## Boundary Churn

Zero-boundary signs can change with small revisions. Three-month smoothing, two-release
persistence, breadth and the revised-history comparison address different parts of this risk;
none is allowed to silently override the actual plotted coordinate.

The headline observed phase can therefore differ temporarily from the transition anchor. The UI
must label this as an observed boundary crossing under confirmation, not present two competing
answers as if both were current-phase probabilities.

## Delayed Shock Recognition

Persistence can lag abrupt shocks. The observed quadrant is still shown immediately, while only
the transition-confirmed label waits for conditions. Historical validation must report shock
timing separately instead of loosening rules until a preferred result appears.

## Schema And Replay Migration

Existing snapshot rows lack v3 JSON fields and use `recession` in the enum. Migration must be
additive, old rows must remain readable and historical replay must backfill actual coordinates
before the graph claims a continuous path.

Closeout result: the additive columns and enum compatibility are verified, legacy rows remain
LIMITED instead of being reconstructed from probability, and the latest 12 month ends were
replayed with origin-specific observed coordinates.

## Intramonth Comparability

Monthly sources arrive on different schedules. Intramonth data cannot advance persistence or
replace the month-end headline, and source coverage below six real-economy series suppresses the
coordinate.

## Conditional Path Misinterpretation

A pressure arrow can look like a forecast. It is rendered only during WATCH, has no future point
or target month and must carry `예측 경로가 아님` copy.

## Asset Regression

Top-level phase and schema changes can accidentally alter shared types or economic-state copy in
asset cards. Same-input `market_implications` deep equality plus React markup/CSS and Browser
regression are release blockers.

## Verification Boundary

NBER chronology is not the current-state truth. It is reported as an ex-post reference alongside
PIT stability, revision matrix, transition churn and delay; no single benchmark is optimized in
isolation.

## Materialization Cost

The complete stored-vintage PIT and latest-revised panel pair takes roughly 48 seconds on the
current local DB. Normal UI render remains DB-read-only and fast. Future performance work may
cache or incrementally update the diagnostic panel, but must not weaken origin-specific PIT or
revision comparison semantics.

## Repository-Wide Test Isolation

The full repository suite is not green when all tests share one Python process because unrelated
Streamlit modules repeatedly recreate the global DeltaGenerator singleton. Representative full-
suite failures pass when rerun in a fresh process, and the complete economic-cycle selection is
green. Fixing global Streamlit test isolation is outside this task and remains a repository test-
infrastructure gap rather than an economic-cycle regression.
