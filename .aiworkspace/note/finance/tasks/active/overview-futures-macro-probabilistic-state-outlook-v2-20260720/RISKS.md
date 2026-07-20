# Overview Futures Macro Probabilistic State Outlook V2 Risks

## Residual Risks

### R1. Provider daily finality

yfinance daily rows do not expose an authoritative settlement/final flag.
Raw UTC dates include session-boundary behavior that can produce Sunday/calendar rows.
The implemented cutoff resolver excludes incomplete sessions and exposes pending evidence. Provider-native settlement flags remain unavailable, so exchange-specific calendar refinement is a future data-quality option.

### R2. Continuous futures roll artifacts

Continuous provider symbols can contain roll effects that look like state movement.
V2 must identify or bound roll-sensitive dates; back-adjusted/roll-aware source expansion is a separate decision if current data cannot support stable targets.

### R3. High feature dimension versus independent sample

The current 60 pattern features are large relative to 5D / 20D independent episodes.
Adding macro columns directly can worsen distance concentration and overfit.
V2 requires reduced, interpretable candidates and trial-count logging.

### R4. Macro PIT coverage

Economic Cycle has release-aware official history, but daily alignment and coverage may differ by series.
Missing macro context must make the hybrid unavailable rather than silently backfill revised values.
The implemented shared-fold rule prevents partial-coverage M2 candidates from winning against fully evaluated M1/B0/B1. Actual Task 9 evidence selected no 20D hybrid and published no macro-conditioned edge.

### R5. Event schedule versus event surprise

The repository stores official event schedules but not a complete historical consensus/actual surprise ledger.
Event density can widen uncertainty; it cannot infer the surprise direction.

### R6. Small incremental edge

Actual V2 resolves both horizons to `NO_EDGE`. This is the expected safe behavior and must not be changed by relaxing gates against the observed final result.

### R7. Forecast history growth

An immutable compact forecast ledger needs bounded JSON and idempotent identity.
Full OHLCV, analog path rows, or provider responses must remain in DB source tables rather than be duplicated into the compact history.

## Blocked Items

- None. Roll-aware data and broader macro PIT coverage are optional new tasks, not blockers for V2.
