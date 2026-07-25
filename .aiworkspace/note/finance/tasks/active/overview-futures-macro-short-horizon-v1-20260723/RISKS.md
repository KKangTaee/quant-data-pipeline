# Overview Futures Macro Short-Horizon V1 Risks

Last Updated: 2026-07-24

## Open Risks

- Yahoo continuous futures may revise recent adjusted/roll history, so a minimal one-day delta is unsafe; the design uses a one-year overlap.
- RTY and other symbols may have shorter provider history than the nominal ten-year request. Bootstrap completeness cannot rely only on an exact calendar start date.
- `NO_EDGE` and confirmation conflict are dynamic outputs. UI copy must not hardcode the 2026-07-22 conclusion.
- Hiding future 20D from the primary UI while retaining backend calculation creates compatibility cost, but deletion would unnecessarily broaden model/storage scope.
- Fingerprint comparison must ignore collection timestamps while detecting OHLCV revisions.
- Partial provider results must not replace a usable latest-good snapshot with a lower-coverage result.
- A genuinely new completed session still triggers the full nested validation path (about 55 seconds in the actual sample). This task removes false/repeated rebuilds; it does not weaken validation gates or redesign the nested model artifact.
- The first session after the resolver/algorithm version bump required 61.919 seconds of nested materialization and 75.645 seconds end-to-end. Same-input reruns are 8.659 seconds, but genuinely changed-session model optimization remains separate.
- Yahoo 5m continuous futures coverage can change by symbol or date. The 17/17 gate prevents partial advancement but may leave the previous date visible until provider coverage recovers.
- `yfinance_5m_session_aggregate_v1` is an exact time-window aggregate, not exchange settlement. Product copy and downstream consumers must not relabel it as official settlement.

## Deferred Decisions

- Whether silver should be removed from the shared core preset or added to a validated family is a separate dependency/model review.
- Whether DXY should enter Dollar Pressure requires a new OOS model revision; it remains Economic Cycle shared context here.
- If changed-session materialization remains the dominant latency after incremental collection, incremental validation/artifact decomposition becomes a later performance task rather than lowering publication gates.
