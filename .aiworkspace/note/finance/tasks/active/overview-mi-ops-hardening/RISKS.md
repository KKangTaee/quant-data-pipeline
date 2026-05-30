# Risks

- Local run history can be empty on a new machine. The UI must still show DB freshness status.
- Run history is local/generated and should not be staged.
- Data Health should not become a hidden external fetch path.
- A local DB that has not applied the latest `market_event_calendar` lifecycle columns can still be read through the legacy event query fallback, but schema migration should still be handled before relying on lifecycle audit columns.
- `Latest Success` and `Latest Issue` remain blank until a refresh button writes an Overview job result to `WEB_APP_RUN_HISTORY.jsonl`.
