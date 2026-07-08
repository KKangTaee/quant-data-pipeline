# Institutional Portfolios Workspace V1 Risks

## Open Risks

- SEC Form 13F data set zip files are large. Browser/UI render paths must not download them.
- CUSIP-symbol mapping is incomplete and should not be hidden.
- Filing amendments can create multiple filings for the same manager/period. MVP chooses latest filing date / accession but must show amendment context.
- Pre-2023 13F `VALUE` units differ from newer data set value interpretation, so portfolio weights are safer than cross-period absolute value comparisons.
- Sector / industry exposure depends on optional symbol mapping or external profile joins; unmapped weight must remain visible.

## Closed / Mitigated In V1

- UI render path uses DB loaders only and does not download SEC ZIP files.
- Visible caveats cover delayed filing, 45-day timing, shorts / cash / derivatives / hedging omissions, and partial CUSIP-symbol mapping.
- Full holdings are stored in MySQL tables, not workflow registries or saved setup JSONL.
