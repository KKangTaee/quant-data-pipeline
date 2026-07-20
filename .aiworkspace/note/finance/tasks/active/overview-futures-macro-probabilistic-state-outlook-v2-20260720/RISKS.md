# Overview Futures Macro Probabilistic State Outlook V2 Risks

## Open Risks

### R1. Provider daily finality

yfinance daily rows do not expose an authoritative settlement/final flag.
Raw UTC dates include session-boundary behavior that can produce Sunday/calendar rows.
Implementation must prove a safe canonical-session resolver before replacing the current snapshot.

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

### R5. Event schedule versus event surprise

The repository stores official event schedules but not a complete historical consensus/actual surprise ledger.
Event density can widen uncertainty; it cannot infer the surprise direction.

### R6. Small incremental edge

Current 5D Brier improvement is small and coordinate coverage is poor.
The honest V2 result may be probability-only or `NO_EDGE` for one or both horizons.

### R7. Forecast history growth

An immutable compact forecast ledger needs bounded JSON and idempotent identity.
Full OHLCV, analog path rows, or provider responses must remain in DB source tables rather than be duplicated into the compact history.

## Blocked Items

- None for written design review.
- Implementation is intentionally gated on user approval of `DESIGN.md`.
