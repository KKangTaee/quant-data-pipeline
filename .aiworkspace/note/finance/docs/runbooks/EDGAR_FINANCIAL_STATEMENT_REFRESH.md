# EDGAR Financial Statement Refresh Runbook

Status: Active
Last Verified: 2026-06-30

## Purpose

Use EDGAR detailed statement collection and statement shadow rebuild as the primary financial statement refresh path.

This runbook keeps broad yfinance fundamentals / factors as a legacy compatibility path, not the canonical financial statement source.

## When To Use

- Strict annual factor coverage needs fresh statement rows.
- Market Movers financial snapshot needs EDGAR annual statement evidence.
- Statement Coverage Diagnosis reports raw or shadow gaps.
- A saved or historical run explicitly needs legacy broad factor replay context.

## Inputs Or Prerequisites

- `SEC_USER_AGENT` should identify the operator/contact per SEC fair access expectations.
- Start with a bounded symbol set such as `Profile Filtered Stocks` or a statement coverage preset before running the full stock universe.
- Confirm the requested period type. Annual is the default primary path. Quarterly remains gated to safe `10-Q` / `10-Q/A` consumer rows.
- Do not drop statement tables to recover coverage. Use targeted collection, diagnosis, or shadow rebuild.

## UI Path

1. Open `Workspace > Ingestion`.
2. In the operational refresh section, start with `EDGAR annual 재무제표 갱신`.
3. Select the symbol source and period type.
4. Keep `EDGAR Statement Periods = 0` when you need all available periods for coverage repair.
5. Run the job and read the result by coverage, freshness, failed symbols, and next action.
6. If partial or failed, run `재무제표 coverage 원인 진단`.
7. If raw statement rows exist but shadow rows are missing, run `재무제표 shadow 재구성`.

## Expected Result

- Raw statement rows land in `finance_fundamental.nyse_financial_statement_filings`, `nyse_financial_statement_labels`, and `nyse_financial_statement_values`.
- Statement shadow rows are rebuilt in `nyse_fundamentals_statement` and `nyse_factors_statement`.
- The job result highlights processed symbol coverage, statement freshness interpretation, failed symbols, and the next action.
- Strict annual backtest paths and Market Movers annual financial snapshots can read the EDGAR statement shadow path.

## Failure Handling

- `partial_success` is not pass. Treat it as a coverage gap until diagnosis explains it.
- If failed symbols are concentrated, rerun only the affected symbols after checking CIK / ticker mapping and SEC access pacing.
- If raw rows are present but shadow rows are missing, use shadow rebuild instead of collecting the provider again.
- If quarterly data is involved, verify consumer rows are `10-Q` / `10-Q/A`; do not interpret `10-K` full-year flow values as quarterly values.
- Keep `.aiworkspace/note/finance/run_history/*.jsonl`, `run_artifacts/`, screenshots, and local `.DS_Store` unstaged unless explicitly requested.

## Legacy Broad Path

`Legacy broad yfinance fundamentals / factors` remains in the Ingestion UI for compatibility and explicit comparison.

Use it only when an old saved run, history replay, or manual broad factor comparison requires `nyse_fundamentals` / `nyse_factors`.

## Related Docs

- [DATA_FLOW_MAP.md](../data/DATA_FLOW_MAP.md)
- [TABLE_SEMANTICS.md](../data/TABLE_SEMANTICS.md)
- [DB_SCHEMA_MAP.md](../data/DB_SCHEMA_MAP.md)
- [PROJECT_MAP.md](../PROJECT_MAP.md)
