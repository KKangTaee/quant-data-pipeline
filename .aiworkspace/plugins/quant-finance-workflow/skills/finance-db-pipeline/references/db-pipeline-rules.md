# DB Pipeline Rules

## Primary Code Areas

- `finance/data/data.py`
- `finance/data/nyse.py`
- `finance/data/nyse_db.py`
- `finance/data/asset_profile.py`
- `finance/data/fundamentals.py`
- `finance/data/factors.py`
- `finance/data/financial_statements.py`
- `finance/data/db/mysql.py`
- `finance/data/db/schema.py`
- `finance/loaders/*`

## Table And DB Design

- Reuse existing DB groupings unless there is a strong reason not to:
  - `finance_meta`
  - `finance_price`
  - `finance_fundamental`
- Add schema definitions in `finance/data/db/schema.py`.
- Prefer explicit unique keys that represent business identity.
- Add secondary indexes only for clear access paths already used by loaders or readers.
- Keep stock and ETF OHLCV together in `finance_price.nyse_price_history`.
- Treat asset-type separation as metadata/universe concern, not a separate price-table concern.

## Write Path Design

- Prefer `INSERT ... ON DUPLICATE KEY UPDATE` for repeatable ingestion.
- Convert provider null-like values before DB write.
- Keep normalization separate from SQL where practical.
- If a table has legacy mixed-state rows, prefer canonical delete + reinsert for the requested business scope and document whether refresh happens by symbol, symbol/frequency, or symbol/date-range.

## Source Handling

- Treat all external providers as unstable.
- Use bounded batch sizes for provider requests.
- Sleep with small jitter between batches if the provider is rate-sensitive.
- For yfinance OHLCV, be explicit about provider-native `end` handling and prevent blank rows from entering canonical price tables.

## Logging

For batch collectors, log start conditions, batch progress, failed symbols/batches, and missing/empty source cases that affect coverage. Keep logs operational, not verbose debugging dumps.

## Reader/Writer Alignment

- If a writer is added, define or verify the corresponding reader path.
- If a pipeline produces derived data, document the upstream dependency explicitly.
- If a writer supports DB-backed strategy/runtime parity, verify loader semantics and do not leave `close` / `adj_close` meaning ambiguous.

## Data Quality And PIT

Check whether source values are raw provider truth, inferred, approximated, or fallback-computed.

For fundamentals, factors, and financial statements:

- identify whether logic is based on `period_end` or actual filing timing
- do not describe `period_end` snapshots as point-in-time safe unless filing timing is enforced
- state market-price matching rules clearly

## New Pipeline Checklist

1. Which source owns the truth?
2. Which DB should store it?
3. What is the unique business key?
4. Is the table raw, normalized, or derived?
5. Which reader or downstream step will consume it?
6. What retry and logging behavior is appropriate?
7. Do `docs/data/README.md`, `docs/data/TABLE_SEMANTICS.md`, or `docs/architecture/DATA_DB_PIPELINE_FLOW.md` need an update?

## Done Condition

- Schema and ingestion code are aligned.
- Write paths are idempotent.
- Retry/logging behavior is reasonable for the source.
- Upstream and downstream meaning is clear.
- Canonical refresh scope is explicit when legacy cleanup is involved.
- Price-table semantics are consistent for DB-backed runtime use when touched.
- Data docs and architecture docs are updated when pipeline meaning changed.
