# Risks

## Residual

- `context_findings` and `next_checks` remain in the service payload for compatibility, so future UI work should not re-enable them as a default action checklist.
- `Futures/Macro 배경` is lowered only when a Futures / OHLCV data-health item exists in the handoff payload. Non-Futures Data Health issues should stay in source evidence rather than changing macro interpretation.

## Not Changed

- No hard conditioning was added to historical analog.
- No new data collection path or provider fetch was added.
- No validation, monitoring, or trading semantics were added.
