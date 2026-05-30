# Notes

- 1차 자동화는 long-running daemon이 아니라 cron / launchd / Codex automation 등이 반복 호출할 수 있는 run-once CLI다.
- Intraday snapshot jobs are guarded by US market hours by default. `--force` can bypass both cadence and market-hours guard for manual smoke / recovery.
- `standard` profile includes S&P 500, Top1000, Top2000 intraday snapshots plus S&P 500 universe, FOMC, macro, and earnings refresh.
- `safe` profile excludes Top1000 / Top2000 intraday jobs for lower provider pressure.
- Event jobs are DB-writing ingestion jobs, not UI scraping. BLS `.ics` manual import remains outside automatic refresh.
- Data Health now separates scheduled vs manual run history through `run_metadata.execution_mode`.
- Quote gap issue persistence is intentionally an operating history, not a delisting / trading halt fact table.
