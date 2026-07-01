# Notes

## 2026-07-01

- Current Ingestion UI is owned by `app/web/ingestion_console.py`.
- Existing right column contains session results, persistent run history and detail, recent logs, and failure CSV preview.
- `daily_market_update` and `metadata_refresh` are operational aliases over lower-level collection jobs; UI should clarify rather than remove them.
- Broad yfinance fundamentals / factors remain archived compatibility actions and should not be re-exposed.
