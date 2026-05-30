# Status

- 2026-05-28: Task opened as Overview Market Intelligence 6차 `Macro Event Calendar Collector`.
- 2026-05-28: Implemented BLS / BEA macro calendar parsers, collector, ingestion job wrapper, Overview refresh button, Macro filter, and Data Health target.
- 2026-05-28: Live smoke wrote 13 BEA GDP rows. BLS returned HTTP 403 in this environment and is surfaced as partial collection failure.
- 2026-05-28: Browser smoke passed on `http://localhost:8501`; Events Macro filter and Data Health Macro status are visible.
