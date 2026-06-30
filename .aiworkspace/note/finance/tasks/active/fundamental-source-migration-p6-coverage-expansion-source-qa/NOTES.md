# Phase 6. Coverage Expansion And Source QA Notes

- Broad universe QA is intentionally DB-backed. It reads universe membership, statement raw coverage, statement shadow coverage, and asset profile metadata.
- It does not call `inspect_financial_statement_source()` for every symbol. That live EDGAR source sample remains a targeted small-symbol diagnostic in `Statement Coverage Diagnosis`.
- `TOP2000` currently exposes a large second-thousand gap in this worktree because annual statement shadow coverage is concentrated in the first 953 symbols.
- `NASDAQ` currently resolves no universe rows in this worktree, so the QA reports a universe-source issue instead of pretending coverage is zero over a known symbol set.
