# Status

- 2026-05-28: Task opened after user confirmed S&P 500, previous-close daily basis, and S&P 500-only initial intraday scope.
- 2026-05-28: Added S&P 500 universe table, intraday snapshot table, collector job wrappers, Overview controls, yearly period, sector filter, and missing diagnostics.
- 2026-05-28: S&P 500 universe refresh smoke wrote 503 current constituents to local DB.
- 2026-05-28: Browser smoke passed for Overview Market Movers with S&P 500 daily EOD fallback and coverage diagnostics.
- 2026-05-28: Polished Market Movers top controls into a framed control bar and added 5-minute update-needed status dot / button behavior.
- 2026-05-28: Replaced default S&P 500 snapshot refresh path with Yahoo quote batch fast path, keeping yfinance 5m OHLCV as fallback.
- 2026-05-28: Browser smoke confirmed fresh quote snapshot state and disabled refresh button after the fast path run.
- 2026-05-28: Fixed Overview refresh click error by moving collection actions outside the auto-refresh fragment and making the UI call compatible with stale Streamlit job-wrapper imports.
