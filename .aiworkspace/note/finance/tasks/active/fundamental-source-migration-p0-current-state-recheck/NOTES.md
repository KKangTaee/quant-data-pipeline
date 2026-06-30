# Notes

## Recheck Interpretation

The recheck did not reveal a blocker that changes the migration order in `DEVELOPMENT_GUIDE.md`.

The local DB coverage remains aligned with the research audit:

- broad yfinance fundamentals / factors cover roughly 5.5k symbols.
- EDGAR statement shadow covers 989 symbols.
- EDGAR raw statement values cover 989 symbols and longer history.
- quarterly statement shadow still has `10-K` / `10-K/A` form types, so quarterly must stay blocked or corrected before production promotion.

## Source Usage Pointers

- Market Movers selected-symbol research still imports `load_fundamental_snapshot`.
- Backtest strict annual strategy wrappers and statement factor loaders already exist.
- Ingestion Console still exposes broad fundamentals and broad factors refresh copy.
