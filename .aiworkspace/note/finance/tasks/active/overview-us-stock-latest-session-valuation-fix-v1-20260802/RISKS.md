# Risks

- The stale-DB month-boundary risk is mitigated by selecting the latest positive price-bearing row;
  existing freshness status still communicates whether that evidence is delayed.
- The as-of mismatch risk is mitigated by sourcing current price and TTM EPS from the same monthly
  row rather than mixing a newer EPS-only row with an older price row.
- Residual low-risk test gap: the new regression directly covers a missing (`None`) price/date row.
  Zero/NaN prices and positive prices without `price_basis_date` are filtered by the implementation
  but do not yet have separate focused test cases.
- Repository-wide discovery is not currently green: 12 failures and 298 errors remain in unrelated
  surfaces, chiefly because many tests reinitialize Streamlit in one discovery process. The isolated
  92-test suite covering this change is green.
