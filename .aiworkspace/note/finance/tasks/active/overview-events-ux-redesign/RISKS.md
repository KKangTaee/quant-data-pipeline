# Risks

## Open Risks

- The current yfinance adapter performs per-symbol requests. Even with sharding, rate limits and provider shape changes remain possible; partial success and retry behavior are required.
- A full S&P 500 cycle is not instant on cold start. The UI must expose incomplete coverage without presenting a run-status dashboard.
- Portfolio and watchlist symbol loaders are explicit extension boundaries today. Implementation must not infer them from unrelated registries.
- SEC CIK coverage may be incomplete. Exact listing-name fallback groups known identical names, but class-specific or differently formatted names may still remain separate; fuzzy matching is intentionally not used.
- Earnings date providers often omit an exact release time. Unknown time must remain unknown and must not be converted to a misleading KST midnight.
- Official holiday pages can change markup. Failed parsing must preserve last-known official rows and surface incomplete year coverage.
- `events_helpers.py` and `EventsWorkbench.tsx` are already large. New orchestration and interpretation should stay in data/service modules rather than increasing UI-side business logic.
- Official calendar refresh is much faster than hybrid earnings but still depends on multiple external official endpoints; partial source failure must remain visible without reintroducing the slow earnings collector into the primary action.

## Non-Blocking Follow-up

- Issuer-confirmed company IR ingestion could improve earnings authority later, but it is outside this correction.
- A broader macro / fixed-income event product audit remains separate from the FOMC / earnings / US holiday scope.
