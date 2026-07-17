# Risks

- EIA weekly dates and daily market dates must not be presented as the same horizon.
- `^GSPC` may be absent from local price history; `SPY` fallback must remain explicit.
- Eight actual S&P EPS quarters may be unavailable; the earnings path must fail independently.
- Copper remains partial until an approved global activity series is connected.
- Continuous futures include contract-roll effects.
