# Futures Macro Decision UX V2 Risks

State: complete
Last Updated: 2026-08-17

## Active Risks

- Active trade-date resolver is not an exchange holiday calendar; a closed holiday can still trigger a bounded
  provider attempt. No eligible bars must fail closed to the latest completed session.
- Provider outage and exchange closure can both produce no current bars. UI copy must say only that no eligible
  current observation exists, not claim a specific external cause.
- Shared header CSS changes can affect other Overview research surfaces unless Futures-specific selectors win
  at desktop and responsive breakpoints.
- Deterministic narratives must not imply causal or trading conclusions beyond observed family alignment.
- Payload schema bump requires Python, TypeScript, integration, and service-contract expectations to move together.

## Preserved Boundaries

- No DB schema change.
- No validation threshold change.
- No provisional forecast publication.
- No registry or saved-state mutation.

## Closeout

- Holiday ambiguity remains a bounded provider-attempt risk, but an empty or incomplete current observation
  fails closed to the latest completed session.
- Shared header changes are restricted to `.research-header--futures` and responsive QA passed.
- No validation threshold, family membership, DB schema, or forecast-publication rule changed.
