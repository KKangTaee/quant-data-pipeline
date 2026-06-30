# Notes

## Quarterly Policy Used In This Phase

Synthetic Q4 was not implemented in this phase. The service uses the safer policy from the guide:

- annual: EDGAR statement shadow first, legacy yfinance fallback only if EDGAR annual is unavailable
- quarterly: show only 10-Q / 10-Q/A statement shadow rows
- quarterly 10-K / 10-K/A rows: block with a correction-needed reason

This keeps the UI from treating full-year 10-K flow values as quarterly values.

## Source Strip

The Market Movers research card detail now carries compact source evidence such as:

```text
연간 2025-12-31 · EDGAR statement shadow · available 2026-02-12 · 10-K · accession ...
```

If fallback is used, the source label reads `legacy yfinance fallback`.
