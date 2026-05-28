# Status

- 2026-05-28: Task opened after Market Event DB structure completion. Initial source selected: Fed official FOMC calendars page.
- 2026-05-28: Implemented Fed official HTML parser, FOMC event UPSERT collector, ingestion job wrapper, Ingestion button, Overview Events display, and event read model service.
- 2026-05-28: Local DB smoke stored 16 FOMC rows for 2026/2027; Overview event snapshot reads upcoming rows from `market_event_calendar`.
