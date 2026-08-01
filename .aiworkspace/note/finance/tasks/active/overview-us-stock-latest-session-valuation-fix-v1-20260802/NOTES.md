# Notes

- Actual 2026-08-02 AMD payload had scenario prices and EPS ready but `current_price=None`.
- `2026-07-31` replay returned AMD current price `476.1499938964844`; `2026-08-01`
  appended a `missing_price` August row and lost Graph 2 current price.
- Graph 1 already filters complete rows. Graph 2 used the unfiltered last calendar row.
- Freshness correctly identifies 2026-07-31 as the latest completed session and should remain
  the owner of stale-price messaging.
- The default service path passes `latest_completed_nyse_session()` to the loader. Injected
  `loaded_inputs` remain unchanged so deterministic replay and tests retain their existing contract.
- The valuation basis is the latest monthly row with a positive price and `price_basis_date`;
  current price and current TTM EPS intentionally remain on the same point-in-time row.
- Canonical documentation change 없음: this restores the existing latest-completed-session and
  stale-freshness contract without changing product, schema, storage, or workflow meaning.
