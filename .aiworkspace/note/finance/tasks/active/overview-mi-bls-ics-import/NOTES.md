# Notes

- Current direct BLS backend fetch can fail with HTTP 403 in this environment.
- The fallback should preserve official-source semantics by requiring a user-provided BLS calendar `.ics` file downloaded from BLS.
- DB writes should stay idempotent through the existing `market_event_calendar` business key normalization.
