# SEC Form 25 Delisting Backfill V1 Notes

## Source Notes

- SEC `data.sec.gov/submissions/CIK##########.json` exposes company filing history metadata.
- SEC `company_tickers.json` maps ticker to CIK and company name but is not guaranteed to cover every historical ticker.
- Form 25 is useful delisting evidence, not proof that a missing filing means the symbol is active.

## Implementation Notes

- Store only compact filing metadata in `evidence_json`.
- Keep accession number in the row source key so repeat runs are idempotent.
- Infer `kind` from current `nyse_stock` / `nyse_etf` where possible, defaulting to `stock` for unmapped DB kind.
- The collector does not write workflow JSONL, memo records, saved presets, report files, approvals, orders, or rebalance instructions.
- UI wiring was intentionally left out of this implementation slice. The callable collector and job wrapper are available first; adding a Streamlit Ingestion button can be a separate UX-scoped task if desired.
