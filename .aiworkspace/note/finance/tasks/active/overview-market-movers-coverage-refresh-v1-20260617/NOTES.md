# Notes

## Initial Decisions

- Use `nyse_symbol_lifecycle` latest `nasdaq_symdir_nasdaqlisted` rows directly for Nasdaq coverage instead of materializing duplicate `market_universe_member` rows.
- Treat Nasdaq Symbol Directory rows as current listing observations only, not historical membership proof.
- Keep Overview UI render path read-only; refresh actions must go through `app/jobs/overview_actions.py` or ingestion wrappers.
- Existing unrelated dirty paths observed before edits: `finance/.DS_Store`, `.superpowers/`.

## Implementation Notes

- `NASDAQ` coverage is labeled `Nasdaq-listed current snapshot` throughout read model and UI.
- Nasdaq intraday snapshot uses the same `finance_price.market_intraday_snapshot` table with `universe_code=NASDAQ`.
- Nasdaq Symbol Directory refresh is available through `run_overview_nasdaq_symbol_directory()` and automation job `nasdaq_symbol_directory`; it calls the existing ingestion wrapper, not UI direct fetch.
- `nasdaq_intraday` is exposed for `standard` / `broad` / `intraday` profiles but remains market-hours guarded.
- Coverage Diagnostics evidence strings are hints from local DB state. They avoid definitive delisting / halt / legal conclusions unless lifecycle source is actual delisting evidence.
