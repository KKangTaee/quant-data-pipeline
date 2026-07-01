# Notes

## 2026-07-01

- Ingestion action execution boundary is `app/web/ingestion_console.py -> app/jobs/ingestion_jobs.py -> finance/data/*`.
- Existing scheduled jobs preserve `collection_section` and `ui_started_at`, but read-only diagnostic cards still execute immediately with `st.spinner`.
- Existing progress callback is strongest for OHLCV and statement ingestion; several shorter or stage-oriented collectors only return a result after completion.
