# Notes

- `market_event_calendar` belongs in `finance_meta` because it is event metadata used by Overview, not price history.
- `raw_payload_json` should keep compact provider evidence for later diagnostics, while UI reads normalized columns first.
- `event_key` is generated from `event_date`, `event_type`, `symbol`, `title`, and `source`; source-specific collectors can override it if they have a stronger provider id later.
