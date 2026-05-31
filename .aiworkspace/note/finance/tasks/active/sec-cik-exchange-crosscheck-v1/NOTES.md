# SEC CIK Exchange Crosscheck V1 Notes

Status: Active
Created: 2026-05-28

## Source Contract

- Source file: `https://www.sec.gov/files/company_tickers_exchange.json`
- Evidence type: current CIK / ticker / exchange association.
- It is not historical membership, delisting, or ticker action proof.
- Rows must remain `coverage_status=partial`.

## Implementation Notes

- Source writes `source=sec_company_tickers_exchange`.
- Rows use `source_type=current_listing_snapshot`, `event_type=listing_observed`, and `coverage_status=partial`.
- Existing DB symbol kind map is used when available; otherwise the row defaults to `stock` because the SEC file does not provide an ETF flag.
- Missing from the SEC current association file is not interpreted as delisting.
