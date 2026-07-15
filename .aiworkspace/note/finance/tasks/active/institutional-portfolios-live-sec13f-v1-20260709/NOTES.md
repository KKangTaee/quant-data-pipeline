# Institutional Portfolios Live SEC 13F V1 Notes

- Current local DB check before this task: `finance_meta.institutional_13f_manager` table was missing, so the page fell back to preview sample.
- Existing IA: `Workspace > Institutional Portfolios` is a sibling of `Overview`, not a child of `Overview`.
- Product boundary: delayed 13F research context only. No recommendation, live buy / sell signal, broker order, auto rebalance, or approval workflow.
- Watchlist seed CIKs used for the manager rail: Berkshire Hathaway `0001067983`, Pershing Square `0001336528`, Appaloosa `0001656456`, Baupost `0001061768`.
- Conservative CUSIP-symbol enrichment only uses unique `nyse_asset_profile.long_name` matches. Ambiguous issuer names are skipped rather than guessed.
- The Institutional page can run the existing SEC 13F job wrapper from a collapsed refresh panel, but normal render does not fetch SEC or external benchmark sites.
