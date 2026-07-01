# Notes

## 2026-07-01

- Ingestion action execution boundary is `app/web/ingestion_console.py -> app/jobs/ingestion_jobs.py -> finance/data/*`.
- Scheduled jobs preserve `collection_section` and `ui_started_at`; read-only diagnostic cards now use the same scheduled job / result history path.
- Progress callback is event-driven. OHLCV and statement ingestion can report batch progress; shorter stage-oriented collectors emit stage start / complete events.
- Active actions and legacy compatibility actions are separated by `INGESTION_ACTION_REGISTRY` helper functions. Broad yfinance fundamentals / factors remain old replay / explicit comparison compatibility only.
