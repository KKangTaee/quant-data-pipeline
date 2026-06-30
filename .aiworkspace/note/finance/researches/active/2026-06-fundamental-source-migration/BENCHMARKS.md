# Benchmarks

## Source classes

| Source class | Strength | Weakness | Recommended role |
| --- | --- | --- | --- |
| SEC official EDGAR APIs / bulk data | Official source, filing metadata, accession, accepted time, XBRL facts | Raw facts need normalization, rate limits, taxonomy complexity | Canonical raw ledger |
| `edgartools` | Convenient Python adapter over SEC EDGAR data, already integrated | Third-party wrapper; library transforms must be verified | Collection adapter, not ultimate truth |
| `yfinance` | Fast, simple, broad convenience data | Unofficial Yahoo wrapper, provider-normalized, limited financial history, unstable fields | Non-canonical fallback / bridge only |
| Paid normalized APIs | Clean normalized statements, easier coverage, sometimes point-in-time endpoints | License/cost/vendor lock-in, definitions may differ | Optional cross-check or commercial upgrade |
| Local derived read models | Fast UI/backtest, source-aware, testable | Requires rebuild and quality contracts | Primary app-facing layer |

## SEC official path

SEC provides EDGAR data APIs such as submissions and company facts. This is the right canonical source for US listed company filings because it preserves filing identity, accepted dates, forms, and XBRL concept-level facts.

Implication for this project:

- Keep `nyse_financial_statement_filings` and `nyse_financial_statement_values` as raw source-of-truth tables.
- Build compact derived tables from the raw ledger.
- Do not let UI fetch SEC directly.
- Enforce SEC fair-access rules and clear User-Agent identity in ingestion jobs.

## `edgartools` path

`edgartools` is useful because it gives a higher-level Python interface over EDGAR companies, filings, facts, and financials. This project already uses it and stores the results into local raw/shadow tables.

Trust stance:

- Trust EDGAR / SEC source.
- Trust local raw ledger after sample verification.
- Treat `edgartools` as a replaceable adapter.
- Avoid relying on a single library-normalized statement view without accession / concept / unit / available_at evidence.

## `yfinance` path

`yfinance` is excellent for fast prototyping and convenient market-data access, but it should not be the canonical financial statement source for a production-like quant app.

Reasons:

- It is a Yahoo Finance wrapper, not an official issuer or SEC source.
- Financial statement history is shorter than EDGAR and can be provider-normalized.
- Field availability and labels can change.
- It does not naturally provide robust PIT filing availability.

Recommended role:

- Keep for non-critical prototype/pilot paths where this project already has explicit caveats, such as futures pilot or provider-estimate event rows.
- Stop using it as the canonical source for fundamentals/factors.
- Freeze broad financial statement ingestion after EDGAR annual replacement is complete.

## Paid / alternate providers

### Financial Modeling Prep

Provides normalized financial statement endpoints. Useful for fast normalized views and cross-checking, but source/license terms need to be accepted before canonical use.

### Polygon / Massive financials

Provides company financials APIs with normalized fields. Useful if the project needs commercial-grade normalized endpoints and SLA-like behavior.

### Alpha Vantage fundamentals

Provides income statement, balance sheet, and cash flow endpoints. Useful as a low-friction alternate source, but not a replacement for raw SEC lineage.

### Direct SEC API without `edgartools`

Best long-term fallback if wrapper risk becomes an issue. The project can keep the same DB tables and replace only the adapter layer.

## Benchmark conclusion

For this project, the best source architecture is:

```text
SEC EDGAR official data
  -> edgartools or direct SEC adapter
  -> raw filing/value ledger
  -> validated statement shadow
  -> factor/read models
  -> Backtest / Market Movers / UI
```

yfinance should move out of the financial-statement canonical path and remain only as explicit fallback/bridge where no official source has been implemented.
