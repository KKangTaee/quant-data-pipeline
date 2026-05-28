# Overview Market Intelligence Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Sparse latest price date creates false current ranking | High | Choose effective market date by usable row count. |
| Earnings source is unstable or unofficial | High | Keep earnings for later ingestion prototype with source confidence labels. |
| Current S&P 500 membership creates survivorship bias | Medium | Label it as a current market scan universe, not a PIT backtest universe. |
| Free intraday source is delayed or rate-limited | Medium | Start with S&P 500 only and store source label, snapshot age, and missing diagnostics. |
| Overview becomes a recommendation surface | Medium | Label market data as context and keep candidate promotion separate. |
| Large price queries slow the app | Medium | Query only selected universe and selected dates. |
| Existing candidate overview disappears | Medium | Preserve it under `Candidate Ops`. |
