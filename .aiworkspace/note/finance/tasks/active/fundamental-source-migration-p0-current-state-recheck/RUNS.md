# Runs

## 2026-06-30 Current-State Recheck

### `git status --short`

Result: exit 0.

Important output:

```text
 M finance/.DS_Store
?? .aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl
?? .superpowers/
```

Interpretation: these are pre-existing local/generated artifacts and were not staged.

### Financial source usage search

Command:

```bash
rg -n "load_fundamental_snapshot|load_statement_fundamentals_shadow|nyse_factors|nyse_factors_statement|quality_snapshot_strict_quarterly" app finance tests
```

Result: exit 0.

Highlights:

- `app/services/overview/why_it_moved.py` imports and defaults to `load_fundamental_snapshot`.
- `finance/loaders/factors.py` reads both `nyse_factors` and `nyse_factors_statement`.
- `app/runtime/backtest_strict.py` exposes strict annual and quarterly prototype wrappers.
- `app/web/ingestion_console.py` still labels broad `nyse_fundamentals` / `nyse_factors` refresh paths.

### Local MySQL coverage snapshot

Command: guide-provided `uv run python` query against `finance_fundamental`.

Result: exit 0.

Summary:

| Table | Freq | Rows | Symbols | Max period_end |
|---|---:|---:|---:|---|
| `nyse_fundamentals` | annual | 23,094 | 5,528 | 2025-12-31 |
| `nyse_fundamentals` | quarterly | 31,495 | 5,554 | 2026-02-28 |
| `nyse_fundamentals_statement` | annual | 10,317 | 989 | 2026-02-01 |
| `nyse_fundamentals_statement` | quarterly | 58,318 | 988 | 2026-02-28 |
| `nyse_financial_statement_values` | annual | 2,088,537 | 989 | 2026-04-30 |
| `nyse_financial_statement_values` | quarterly | 7,209,821 | 988 | 2026-04-30 |
| `nyse_factors` | annual | 22,987 | 5,528 | 2025-12-31 |
| `nyse_factors` | quarterly | 31,497 | 5,524 | 2025-12-31 |
| `nyse_factors_statement` | annual | 10,317 | 989 | 2026-02-01 |
| `nyse_factors_statement` | quarterly | 58,318 | 988 | 2026-02-28 |

Quarterly form mix:

| latest_form_type | Rows | Symbols |
|---|---:|---:|
| `10-Q` | 43,284 | 984 |
| `10-K` | 14,538 | 987 |
| `10-Q/A` | 405 | 125 |
| `10-K/A` | 91 | 46 |
