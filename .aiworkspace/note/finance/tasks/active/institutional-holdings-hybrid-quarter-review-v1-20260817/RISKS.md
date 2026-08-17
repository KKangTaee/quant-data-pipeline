# Institutional Holdings Hybrid Quarter Review V1 Risks

- SEC submissions and archive structures can vary; parser fixtures must cover namespace and
  document-name differences without guessing missing holdings.
- `13F-HR/A` may restate or add holdings. Treating every latest accession as a full replacement
  would corrupt effective portfolios.
- Watchlist managers do not necessarily file on the same day; partial progress must not be
  represented as complete-quarter universe coverage.
- The full SEC bulk ZIP is large and contains millions of holding rows. Actual QA should not
  repeatedly download/rewrite it when a local verified ZIP is available.
- Existing manager `latest_accession_number` consumers assume one accession owns a complete latest
  portfolio. The implementation plan must identify and update every affected query before enabling
  amendment-composed effective quarters.
- CUSIP/ticker resolution is incomplete and current-state rather than historical PIT. Performance
  coverage must remain explicit and missing weight must not become zero return.
- 13F cannot reconstruct cash, shorts, most derivatives, fees, hedge structure or intra-quarter
  trading. The proxy must not be labeled actual manager return.
- Using quarter-end holdings to measure the already-ended quarter would introduce look-ahead.
  This design instead uses the previous report weights over the following quarter and labels the
  filing-to-filing metric separately.
