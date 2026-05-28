# Risks

| Risk | Handling |
| --- | --- |
| Free intraday source is delayed or rate-limited | Store source label and snapshot age; start with S&P 500 only. |
| S&P 500 current constituents are not PIT-correct | Label as current universe, not historical backtest universe. |
| Overview collection button blocks UI while yfinance runs | Keep manual collection explicit; read from DB for normal render. |
| Missing returnable rows are opaque | Add diagnostics table with ticker-level reason and profile metadata. |
| Wikipedia blocks default pandas fetch | Use an explicit browser-like User-Agent for the current constituents source request. |
| Full 503-symbol intraday run can be slow or rate-limited | Collector is implemented and exposed manually; this task verified the read contract with mocked snapshot and avoided an automatic full provider run during QA. |
