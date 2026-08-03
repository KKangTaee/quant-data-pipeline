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
