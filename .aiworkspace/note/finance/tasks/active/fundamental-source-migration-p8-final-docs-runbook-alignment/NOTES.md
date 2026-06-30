# Notes

- The migration keeps the yfinance package and broad tables because price / event / futures pilot sources and old replay compatibility still need them.
- Canonical financial statement source now means EDGAR detailed statement ledger plus `nyse_fundamentals_statement` / `nyse_factors_statement` shadow tables.
- `nyse_fundamentals` / `nyse_factors` should be read as legacy broad compatibility unless a surface explicitly labels a fallback / comparison path.
- Quarterly remains conservative: write path blanks unsafe full-year flow metrics from 10-K / 10-K/A quarterly shadow generation, and consumer loaders return 10-Q / 10-Q/A rows only.
- Top2000 and Nasdaq broad EDGAR coverage remain expansion targets, not a completed universal coverage guarantee.
