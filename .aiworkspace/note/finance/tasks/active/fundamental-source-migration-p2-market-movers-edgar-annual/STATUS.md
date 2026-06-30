# Status

Status: Complete
Updated: 2026-06-30

## Summary

Phase 2 Market Movers annual EDGAR-first migration completed.

## Changed

- Market Movers selected-symbol research snapshot now loads annual `load_statement_fundamentals_shadow` first.
- Legacy broad `load_fundamental_snapshot` is used only as an annual fallback.
- Quarterly financials now require 10-Q / 10-Q/A statement rows and block 10-K/FY rows from being displayed as quarterly values.
- Research Snapshot details show source, available date, form type, and accession when present.

## Browser QA

- Local URL: `http://localhost:8525`
- Surface: `Workspace > Overview > Market Movers > 선택 종목 조사 > 기본 지표`
- Observed selected symbol: `GLW`
- Annual source displayed as EDGAR statement shadow.
- Quarterly 10-K row displayed only as blocked source evidence, not as quarterly PER/EPS/income.
- Narrow viewport overflow check passed for `.ov-mm-research-item`.

## Next

Proceed to Phase 3 quarterly correctness gate.
