# Risks

## Open

- Nasdaq intraday refresh can be broad and provider-heavy; automation dry-run should expose the job, but Browser QA should not force live collection.
- Diagnostics evidence is inference from DB state and must avoid definitive legal/listing conclusions without actual delisting evidence.

## Remaining

- Local DB still may not yet have `nasdaq_symdir_nasdaqlisted` rows; Browser QA confirmed the UI shows refresh-needed guidance instead of a blank stale table.
- `pytest` is not declared in current project dependencies; requested pytest command cannot run without changing dependency files or using a transient `uv --with pytest` invocation.
- Browser QA should not execute live Nasdaq intraday collection because local DB currently lacks Symbol Directory rows and provider load could be large.
