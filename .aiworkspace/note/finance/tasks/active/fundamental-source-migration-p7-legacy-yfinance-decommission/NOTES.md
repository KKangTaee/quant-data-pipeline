# Notes

- Phase 7 is decommissioning of the active canonical path, not deletion of historical data structures.
- `nyse_fundamentals` and `nyse_factors` still exist for old replay and explicit compatibility comparison.
- The public yfinance package remains in use for non-financial-statement provider paths, such as price or event pilot flows, and was not removed.
- The source audit still finds broad loader / writer functions in `finance/` and handler functions in `app/jobs/ingestion_jobs.py`; these are compatibility surfaces, not new canonical financial statement paths.
- The Ingestion UI now makes EDGAR annual refresh and statement shadow rebuild the visible financial statement preparation path.
